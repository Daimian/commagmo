"""build：由 ontology/src/*.yaml 生成 ontology/*.ttl 与 ontology/maps/*。

日常链路，不依赖 rdflib。先在内存里生成全部文本，任何一份出错就一个文件都不写。

用法：python build.py [--no-render] [--check]（仓库根）
  --no-render  只出 .dot，不出 png
  --check      不写文件，逐字节比较已提交的 ttl 与 .dot；不一致返回 1
退出码：0 成功，1 --check 不一致，2 源文件有错。
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from commagmo_build.emit import emit_module
from commagmo_build.manchester import (
    ExprError, Named, parse_class_expr, parse_restriction)
from commagmo_build.render_dot import render_module, render_png
from commagmo_build.resolve import ResolveError, Resolver, load_cache
from commagmo_build.schema import SchemaError, load_module
from commagmo_build.paths import ONTOLOGY_DIR, ONTOLOGY_SRC_DIR

# (图名, 取焦点的模块名)；合并图 simulation 在前，与 v1.1 的出图口径一致
# 新增模块要在这里加一项才会出图（模块文件本身由 glob 自动发现）
MAPS = (("material", ("material",)),
        ("simulation", ("simulation",)),
        ("commagmo", ("simulation", "material")))


class BuildError(Exception):
    pass


def _local_refs(e) -> list[tuple[str, str]]:
    """条目里所有可能指向本地命名空间的引用：[(字段, 名字)]。表达式解析不了的跳过（emit 会报）。"""
    f = e.fields
    refs: list[tuple[str, str]] = []
    for fld in ("parents", "disjoint_union", "exact_match"):
        refs += [(fld, n) for n in f.get(fld, ())]
    for fld in ("domain", "range"):
        v = f.get(fld, ())
        refs += [(fld, n) for n in ([v] if isinstance(v, str) else v)]
    try:
        for r in f.get("restrictions", ()):
            x = parse_restriction(r)
            refs += [("restrictions", x.prop), ("restrictions", x.filler)]
        if "equivalent" in f:
            x = parse_class_expr(f["equivalent"])
            for t in ([x] if isinstance(x, Named) else x.items):
                if isinstance(t, Named):
                    refs.append(("equivalent", t.name))
                else:
                    refs += [("equivalent", t.prop), ("equivalent", t.filler)]
    except ExprError:
        pass
    for prop, vals in f.get("annotations", {}).items():
        refs.append(("annotations", prop))
        refs += [("annotations", v) for v in vals if isinstance(v, str)]
    return refs


def _check_local_refs(modules: dict, cache: dict) -> None:
    """本地命名空间里的引用必须是某个模块声明的类或属性（三个模块共用 commagmo# 命名空间）。"""
    declared = {k for m in modules.values() for k in (*m.classes, *m.properties)}
    for m in modules.values():
        r = Resolver(m.prefixes, cache)
        for e in (*m.classes.values(), *m.properties.values(), *m.upstream.values()):
            for fld, name in _local_refs(e):
                try:
                    iri = r.to_iri(name)
                except ResolveError:
                    continue  # 留给 emit 报告
                if iri.startswith(r.local_ns) and iri[len(r.local_ns):] not in declared:
                    raise BuildError(f"{m.path}: {e.key}.{fld}: 未定义的本地术语 {name}")


def _generate(src_dir: Path) -> dict[str, str]:
    """{相对 out_dir 的路径: 文本}。"""
    try:
        cache = load_cache(Path(src_dir) / "upstream-cache.json")
    except OSError as e:
        raise BuildError(f"{src_dir}/upstream-cache.json: {e}") from e
    modules = {}
    for path in sorted(Path(src_dir).glob("*.yaml")):
        try:
            modules[path.stem] = load_module(path)
        except SchemaError as e:
            raise BuildError(str(e)) from e
    for needed in {"commagmo", "material", "simulation"} - set(modules):
        raise BuildError(f"{src_dir}/{needed}.yaml: 缺少模块文件")
    _check_local_refs(modules, cache)
    files: dict[str, str] = {}
    for name, m in modules.items():
        try:
            files[f"{name}.ttl"] = emit_module(m, Resolver(m.prefixes, cache))
        except (ResolveError, ExprError) as e:
            raise BuildError(f"{m.path}: {e}") from e
    resolver = Resolver(modules["simulation"].prefixes, cache)
    for title, focus in MAPS:
        try:
            files[f"maps/{title}-map.dot"] = render_module(
                list(modules.values()), resolver, [modules[n] for n in focus], title)
        except Exception as e:  # 渲染遇到意料之外的输入也按源错误报告，不吐 traceback
            srcs = ", ".join(str(modules[n].path) for n in focus)
            raise BuildError(f"{srcs}: {title}-map: {type(e).__name__}: {e}") from e
    return files


def build(src_dir: Path = ONTOLOGY_SRC_DIR, out_dir: Path = ONTOLOGY_DIR,
          render: bool = True) -> list[Path]:
    """生成并写出；返回写出的文件列表。出错抛 BuildError，此时不写任何文件。"""
    if render and shutil.which("dot") is None:
        raise BuildError("需要 graphviz 的 dot（不在 PATH 上）；可加 --no-render 只出 ttl 和 .dot")
    files = _generate(src_dir)
    written: list[Path] = []
    for rel, text in files.items():
        path = Path(out_dir) / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        written.append(path)
    if render:
        for rel in [r for r in files if r.endswith(".dot")]:
            dot = Path(out_dir) / rel
            png = dot.with_suffix(".png")
            render_png(dot, png)
            written.append(png)
    return written


def check(src_dir: Path = ONTOLOGY_SRC_DIR, out_dir: Path = ONTOLOGY_DIR) -> list[str]:
    """已提交的 ttl 与 .dot 同新生成的逐字节比较，返回不一致的文件。"""
    stale = []
    files = _generate(src_dir)
    for rel, text in files.items():
        path = Path(out_dir) / rel
        if not path.is_file() or path.read_bytes() != text.encode("utf-8"):
            stale.append(str(path))
    out = Path(out_dir)
    for pattern in ("*.ttl", "maps/*.dot"):  # build 不会产出的残留文件
        for path in sorted(out.glob(pattern)):
            if path.relative_to(out).as_posix() not in files:
                stale.append(str(path))
    return stale


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="由 ontology/src/*.yaml 生成 ttl 与概念图")
    ap.add_argument("--no-render", action="store_true", help="只出 .dot，不出 png")
    ap.add_argument("--check", action="store_true", help="只比较，不写文件；不一致返回 1")
    ap.add_argument("--src", type=Path, default=ONTOLOGY_SRC_DIR, help="YAML 源目录")
    ap.add_argument("--out", type=Path, default=ONTOLOGY_DIR, help="输出目录")
    args = ap.parse_args(argv)
    try:
        if args.check:
            stale = check(args.src, args.out)
            for p in stale:
                print(f"与源不一致：{p}", file=sys.stderr)
            return 1 if stale else 0
        for p in build(args.src, args.out, render=not args.no_render):
            print(p)
        return 0
    except BuildError as e:
        print(e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

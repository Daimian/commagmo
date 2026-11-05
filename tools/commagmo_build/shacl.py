"""shacl：用 tests/shacl/ 下的正反例检验 ontology/shapes/*.ttl。

决议见 docs/material-cross-ontology.md §6 靶子 3（M3–M8）。只在 `python build.py --check` 时运行，
依赖 rdflib 与 pyshacl（日常 build 链路不依赖它们）。

口径：
  · inference='none'（M4：开 RDFS 推理会让 hasSimulatedMaterial 的 range 把检查变成恒真）；
  · ont 图 = ontology/*.ttl ＋ upstream-cache.json 里每个上游类的具名直接父类；
  · valid.ttl 必须 conform；invalid-<Shape名>-<情形>.ttl 必须不 conform，
    且违反的顶层 shape 恰好是文件名里那一个。
"""
from __future__ import annotations

import json
from pathlib import Path

from commagmo_build.paths import (
    ONTOLOGY_DIR, SHACL_TESTS_DIR, SHAPES_DIR, UPSTREAM_CACHE)

SHAPES_NS = "https://w3id.org/emmo/domain/commagmo/shapes#"


def _ont_graph():
    from rdflib import Graph, RDFS, URIRef
    g = Graph()
    for ttl in sorted(ONTOLOGY_DIR.glob("*.ttl")):
        g.parse(ttl, format="turtle")
    axioms = json.loads(UPSTREAM_CACHE.read_text(encoding="utf-8"))["axioms"]
    for cls, items in axioms.items():
        for raw in items:
            item = json.loads(raw)
            if item[0] == "cls":
                g.add((URIRef(cls), RDFS.subClassOf, URIRef(item[1])))
    return g


def _shapes_graph():
    from rdflib import Graph
    g = Graph()
    for ttl in sorted(SHAPES_DIR.glob("*.ttl")):
        g.parse(ttl, format="turtle")
    return g


def _top_shape(shapes, shape):
    """违反结果的 sh:sourceShape 可能是匿名的属性 shape，向上找到具名的 NodeShape。"""
    from rdflib import BNode
    from rdflib.namespace import SH
    seen = set()
    while isinstance(shape, BNode) and shape not in seen:
        seen.add(shape)
        parents = list(shapes.subjects(SH.property, shape)) + list(shapes.subjects(SH.sparql, shape))
        if not parents:
            break
        shape = parents[0]
    return shape


def _violated(results, shapes) -> set[str]:
    from rdflib.namespace import SH
    out = set()
    for res in results.subjects(SH.sourceShape, None):
        top = _top_shape(shapes, results.value(res, SH.sourceShape))
        out.add(str(top).removeprefix(SHAPES_NS))
    return out


def check() -> list[str]:
    """返回错误信息列表；空列表表示全部符合预期。"""
    from pyshacl import validate
    from rdflib import Graph

    errors: list[str] = []
    shapes = _shapes_graph()
    ont = _ont_graph()
    fixtures = sorted(SHACL_TESTS_DIR.glob("*.ttl"))
    if not (SHACL_TESTS_DIR / "valid.ttl").is_file():
        errors.append(f"缺少正例：{SHACL_TESTS_DIR / 'valid.ttl'}")
    for path in fixtures:
        name = path.stem
        if name != "valid" and not name.startswith("invalid-"):
            errors.append(f"测试数据命名不合约定：{path}")
            continue
        data = Graph().parse(path, format="turtle")
        conforms, results, text = validate(
            data, shacl_graph=shapes, ont_graph=ont, inference="none",
            abort_on_first=False, allow_warnings=False)
        got = _violated(results, shapes)
        if name == "valid":
            if not conforms:
                errors.append(f"正例未通过：{path}\n{text}")
            continue
        expected = name.removeprefix("invalid-").split("-", 1)[0]
        if conforms:
            errors.append(f"反例意外通过：{path}（应违反 {expected}）")
        elif got != {expected}:
            errors.append(f"反例违反的 shape 不对：{path}：应为 {{{expected}}}，实为 {sorted(got)}\n{text}")
    return errors

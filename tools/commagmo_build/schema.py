"""本体 YAML 源的读入与校验（不解析引用，不依赖 rdflib）。

顶层键：``module``（必需）、``classes`` / ``properties`` / ``upstream``（可选，默认空）。
``Entry.kind``：classes 为 ``"class"``，upstream 为 ``"upstream"``，properties 取其
``kind`` 字段（``"object"`` | ``"annotation"``，必需）。``kind`` 只存于 ``Entry.kind``，
**不**进入 ``Entry.fields``；dump 时 properties 条目把 ``kind`` 写在最前。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


class SchemaError(Exception):
    """消息格式 ``<file>: <entry>.<field>: <reason>``。"""


@dataclass
class Note:
    before: str | None  # 条目键；None 表示文件末尾
    text: str


@dataclass
class Entry:
    key: str
    kind: str  # "class" | "object" | "annotation" | "upstream"
    fields: dict = field(default_factory=dict)


@dataclass
class Module:
    # path 只标示来源，不参与相等比较（往返比较的是内容）。
    path: Path = field(compare=False)
    header: dict  # iri, version, title, imports（prefixes、notes 另存）
    prefixes: dict[str, str]
    notes: list[Note]
    classes: dict[str, Entry]
    properties: dict[str, Entry]
    upstream: dict[str, Entry]


# ---- 字段表 ----

_COMMON = ("label", "alt_labels", "definition", "comment", "parents",
           "exact_match", "sources", "annotations", "rationale")
CLASS_FIELDS = _COMMON + ("restrictions", "equivalent", "disjoint_union")
PROPERTY_FIELDS = _COMMON + ("domain", "range")  # 另有必需的 kind
UPSTREAM_FIELDS = ("label", "parents", "restrictions", "disjoint_union", "rationale")
HEADER_FIELDS = ("iri", "version", "title", "imports", "prefixes", "notes")
TOP_KEYS = ("module", "classes", "properties", "upstream")
PROPERTY_KINDS = ("object", "annotation")

_LITERAL_FIELDS = ("label", "definition")
_STR_LIST_FIELDS = ("parents", "restrictions", "disjoint_union", "exact_match", "sources")


# ---- 读入 ----

class _UniqueKeyLoader(yaml.SafeLoader):
    """遇到重复映射键报错（PyYAML 默认后者静默覆盖前者）。"""


def _construct_mapping(loader, node, deep=False):
    seen = set()
    for key_node, _ in node.value:
        key = loader.construct_object(key_node, deep=True)
        if isinstance(key, (str, int, float, bool)) or key is None:
            if key in seen:
                raise yaml.constructor.ConstructorError(
                    None, None, f"重复的键 {key!r}", key_node.start_mark)
            seen.add(key)
    return yaml.SafeLoader.construct_mapping(loader, node, deep)


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)


def _is_literal(v) -> bool:
    if isinstance(v, str):
        return True
    return (isinstance(v, dict) and isinstance(v.get("text"), str)
            and set(v) in ({"text", "lang"}, {"text", "datatype"})
            and all(isinstance(x, str) for x in v.values()))


def _is_str_list(v) -> bool:
    return isinstance(v, list) and all(isinstance(x, str) for x in v)


def _check_field(name: str, value, fail) -> None:
    if name in _LITERAL_FIELDS:
        ok = _is_literal(value)
        want = "字符串或 {text, lang} / {text, datatype}"
    elif name == "comment":  # v1.1 有条目带多条 rdfs:comment
        ok = _is_literal(value) or (isinstance(value, list) and value
                                    and all(_is_literal(x) for x in value))
        want = "字面量或字面量列表"
    elif name == "alt_labels":
        ok = isinstance(value, list) and all(_is_literal(x) for x in value)
        want = "字面量列表"
    elif name in _STR_LIST_FIELDS:
        ok, want = _is_str_list(value), "字符串列表"
    elif name == "rationale":  # 多块时为字符串列表，每项逐字一块
        ok = isinstance(value, str) or (_is_str_list(value) and bool(value))
        want = "字符串或非空字符串列表"
    elif name == "equivalent":
        ok, want = isinstance(value, str), "字符串"
    elif name in ("domain", "range"):
        ok, want = isinstance(value, str) or _is_str_list(value), "字符串或字符串列表"
    elif name == "annotations":
        ok = (isinstance(value, dict)
              and all(isinstance(k, str) and isinstance(v, list) for k, v in value.items()))
        want = "{属性名: [值, …]}"
    else:  # 字段名已校验，不会到这里
        ok, want = True, ""
    if not ok:
        fail(name, f"类型错误，应为{want}")


def _load_section(section, raw, kind, allowed, fail_file) -> dict[str, Entry]:
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise SchemaError(f"{fail_file}: {section}: 应为映射")
    out: dict[str, Entry] = {}
    for key, body in raw.items():
        if not isinstance(key, str):
            raise SchemaError(f"{fail_file}: {section}.{key!r}: 条目键必须是字符串")

        def fail(fld, reason, key=key):
            raise SchemaError(f"{fail_file}: {key}.{fld}: {reason}")

        if body is None:
            body = {}
        if not isinstance(body, dict):
            fail("-", "条目应为映射")
        body = dict(body)
        entry_kind = kind
        if section == "properties":
            entry_kind = body.pop("kind", None)
            if entry_kind not in PROPERTY_KINDS:
                fail("kind", f"必需，取值 {'|'.join(PROPERTY_KINDS)}")
        for fld in body:
            if fld not in allowed:
                fail(fld, f"未知字段（允许：{', '.join(allowed)}）")
        for fld, value in body.items():
            _check_field(fld, value, fail)
        out[key] = Entry(key, entry_kind, body)
    return out


def _load_header(raw, f) -> tuple[dict, dict[str, str], list[Note]]:
    if not isinstance(raw, dict):
        raise SchemaError(f"{f}: module: 必需且应为映射")
    for k in raw:
        if k not in HEADER_FIELDS:
            raise SchemaError(f"{f}: module.{k}: 未知字段（允许：{', '.join(HEADER_FIELDS)}）")
    for k in ("iri", "version", "title"):
        if not isinstance(raw.get(k), str):
            raise SchemaError(f"{f}: module.{k}: 必需且应为字符串")
    imports = raw.get("imports", [])
    if not _is_str_list(imports):
        raise SchemaError(f"{f}: module.imports: 应为字符串列表")
    prefixes = raw.get("prefixes", {})
    if not (isinstance(prefixes, dict)
            and all(isinstance(k, str) and isinstance(v, str) for k, v in prefixes.items())):
        raise SchemaError(f"{f}: module.prefixes: 应为 {{前缀: IRI}} 映射")
    notes_raw = raw.get("notes", [])
    if not isinstance(notes_raw, list):
        raise SchemaError(f"{f}: module.notes: 应为列表")
    notes = []
    for i, n in enumerate(notes_raw):
        if not (isinstance(n, dict) and set(n) <= {"before", "text"} and "text" in n
                and isinstance(n["text"], str)
                and (n.get("before") is None or isinstance(n["before"], str))):
            raise SchemaError(f"{f}: module.notes[{i}]: 应为 {{before: 条目键|null, text: 字符串}}")
        notes.append(Note(n.get("before"), n["text"]))
    header = {k: raw[k] for k in ("iri", "version", "title")}
    header["imports"] = list(imports)
    return header, dict(prefixes), notes


def load_module(path: Path) -> Module:
    path = Path(path)
    f = str(path)
    try:
        with open(path, encoding="utf-8") as fh:
            data = yaml.load(fh, Loader=_UniqueKeyLoader)
    except (yaml.YAMLError, OSError, UnicodeDecodeError) as e:
        raise SchemaError(f"{f}: {e}") from e
    if not isinstance(data, dict):
        raise SchemaError(f"{f}: 顶层应为映射")
    for k in data:
        if k not in TOP_KEYS:
            raise SchemaError(f"{f}: {k}: 未知顶层键（允许：{', '.join(TOP_KEYS)}）")
    header, prefixes, notes = _load_header(data.get("module"), f)
    return Module(
        path=path, header=header, prefixes=prefixes, notes=notes,
        classes=_load_section("classes", data.get("classes"), "class", CLASS_FIELDS, f),
        properties=_load_section("properties", data.get("properties"), None,
                                 PROPERTY_FIELDS, f),
        upstream=_load_section("upstream", data.get("upstream"), "upstream",
                               UPSTREAM_FIELDS, f),
    )


# ---- 生成 ----

class _Dumper(yaml.SafeDumper):
    pass


def _represent_str(dumper, s):
    # 多行字符串用 | 风格；含行尾空格等 PyYAML 无法块写的内容会自动退回引号串，内容不变。
    style = "|" if "\n" in s else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", s, style=style)


_Dumper.add_representer(str, _represent_str)


def dump_module(module: Module) -> str:
    mod = {k: module.header[k] for k in ("iri", "version", "title", "imports")}
    mod["prefixes"] = dict(module.prefixes)
    mod["notes"] = [{"before": n.before, "text": n.text} for n in module.notes]
    doc: dict = {"module": mod}
    for name, entries in (("classes", module.classes), ("properties", module.properties),
                          ("upstream", module.upstream)):
        if not entries:
            continue
        sec = {}
        for key, e in entries.items():
            body = {"kind": e.kind} if name == "properties" else {}
            body.update(e.fields)
            sec[key] = body
        doc[name] = sec
    return yaml.dump(doc, Dumper=_Dumper, allow_unicode=True, sort_keys=False,
                     default_flow_style=False, width=10**9)

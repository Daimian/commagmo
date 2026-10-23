"""Module -> Turtle 文本（不用 rdflib；唯一的生成路径，rdf.module_graph 只是解析它的结果）。

不写注释：设计理由（rationale / notes）只留在 YAML 里，ttl 首行注明这一点。
同一 Module 生成的文本逐字节相同。
"""
from __future__ import annotations

import re

from commagmo_build.manchester import (
    And, Card, ExprError, Named, Some, parse_class_expr, parse_restriction)
from commagmo_build.resolve import ResolveError, Resolver
from commagmo_build.schema import Module

_STD_PREFIXES = {
    "dcterms": "http://purl.org/dc/terms/",
    "owl": "http://www.w3.org/2002/07/owl#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
}
# Turtle PN_LOCAL 的保守子集：不以 '-' / '.' 开头，不以 '.' 结尾。
_PN_LOCAL = re.compile(r"^[A-Za-z0-9_](?:[A-Za-z0-9_\-.]*[A-Za-z0-9_\-])?$")
_ESCAPES = {"\\": "\\\\", '"': '\\"', "\n": "\\n", "\r": "\\r", "\t": "\\t",
            "\b": "\\b", "\f": "\\f"}


def turtle_literal(text: str, lang: str | None = None, datatype: str | None = None) -> str:
    """Turtle 字面量；datatype 为已写好的项（前缀名或 <IRI>）。非 ASCII 原样保留。"""
    if lang and datatype:
        raise ValueError("lang 与 datatype 不能同时给")
    out = []
    for ch in text:
        if ch in _ESCAPES:
            out.append(_ESCAPES[ch])
        elif ord(ch) < 0x20 or ord(ch) == 0x7F:
            out.append(f"\\u{ord(ch):04X}")
        else:
            out.append(ch)
    s = '"' + "".join(out) + '"'
    if lang:
        return f"{s}@{lang}"
    if datatype:
        return f"{s}^^{datatype}"
    return s


class _Ctx:
    def __init__(self, module: Module, resolver: Resolver):
        self.resolver = resolver
        self.prefixes = {**_STD_PREFIXES, **module.prefixes}
        # 最长命名空间优先，保证选择确定
        self._by_ns = sorted(((ns, p) for p, ns in self.prefixes.items() if ns),
                             key=lambda t: (-len(t[0]), t[1]))

    def term(self, iri: str) -> str:
        for ns, p in self._by_ns:
            if iri.startswith(ns) and _PN_LOCAL.match(iri[len(ns):]):
                return f"{p}:{iri[len(ns):]}"
        return f"<{iri}>"

    def name(self, name: str) -> str:
        return self.term(self.resolver.to_iri(name))

    def literal(self, v) -> str:
        if isinstance(v, str):
            return turtle_literal(v, lang="en")
        if "lang" in v:
            return turtle_literal(v["text"], lang=v["lang"])
        return turtle_literal(v["text"], datatype=self.name(v["datatype"]))

    def restriction(self, r: Some | Card) -> str:
        parts = ["a owl:Restriction", f"owl:onProperty {self.name(r.prop)}"]
        if isinstance(r, Some):
            parts.append(f"owl:someValuesFrom {self.name(r.filler)}")
        else:
            pred = "owl:qualifiedCardinality" if r.op == "exactly" else "owl:minQualifiedCardinality"
            parts.append(f'{pred} "{r.n}"^^xsd:nonNegativeInteger')
            parts.append(f"owl:onClass {self.name(r.filler)}")
        return "[ " + " ; ".join(parts) + " ]"

    def equivalent(self, s: str) -> str:
        e = parse_class_expr(s)
        if isinstance(e, Named):
            return self.name(e.name)
        if len(e.items) < 2:
            raise ExprError(f"equivalent 的交集至少两项：{s!r}")
        items = " ".join(self.name(t.name) if isinstance(t, Named) else self.restriction(t)
                         for t in e.items)
        return f"[ a owl:Class ; owl:intersectionOf ( {items} ) ]"


def _entry_pairs(ctx: _Ctx, e) -> list[tuple[str, str]]:
    """条目的 (谓词, 宾语) 列表，顺序固定。解析出错时报 ``<条目>.<字段>: 原因``。"""
    where = [""]
    try:
        return _entry_pairs_at(ctx, e, where)
    except (ResolveError, ExprError) as err:
        raise type(err)(f"{e.key}.{where[0]}: {err}") from err


def _entry_pairs_at(ctx: _Ctx, e, where: list[str]) -> list[tuple[str, str]]:
    f = e.fields
    pairs: list[tuple[str, str]] = []
    if e.kind == "class":
        pairs.append(("a", "owl:Class"))
    elif e.kind == "object":
        pairs.append(("a", "owl:ObjectProperty"))
    elif e.kind == "annotation":
        pairs.append(("a", "owl:AnnotationProperty"))
    if "label" in f:
        pairs.append(("rdfs:label", ctx.literal(f["label"])))
    for v in f.get("alt_labels", ()):
        pairs.append(("skos:altLabel", ctx.literal(v)))
    sub = "rdfs:subPropertyOf" if e.kind in ("object", "annotation") else "rdfs:subClassOf"
    where[0] = 'parents'
    for p in f.get("parents", ()):
        pairs.append((sub, ctx.name(p)))
    where[0] = 'restrictions'
    for r in f.get("restrictions", ()):
        pairs.append(("rdfs:subClassOf", ctx.restriction(parse_restriction(r))))
    where[0] = 'equivalent'
    if "equivalent" in f:
        pairs.append(("owl:equivalentClass", ctx.equivalent(f["equivalent"])))
    where[0] = 'disjoint_union'
    if "disjoint_union" in f:
        items = " ".join(ctx.name(n) for n in f["disjoint_union"])
        pairs.append(("owl:disjointUnionOf", f"( {items} )"))
    for fld, pred in (("domain", "rdfs:domain"), ("range", "rdfs:range")):
        if fld in f:
            where[0] = fld
            vals = [f[fld]] if isinstance(f[fld], str) else f[fld]
            pairs += [(pred, ctx.name(v)) for v in vals]
    where[0] = 'exact_match'
    for v in f.get("exact_match", ()):
        pairs.append(("skos:exactMatch", ctx.name(v)))
    if "definition" in f:
        pairs.append(("skos:definition", ctx.literal(f["definition"])))
    if "comment" in f:
        vals = f["comment"] if isinstance(f["comment"], list) else [f["comment"]]
        pairs += [("rdfs:comment", ctx.literal(v)) for v in vals]
    for v in f.get("sources", ()):
        pairs.append(("dcterms:source", ctx.literal(v)))
    where[0] = "annotations"
    for prop, vals in f.get("annotations", {}).items():
        for v in vals:
            pairs.append((ctx.name(prop), ctx.literal(v) if isinstance(v, dict) else ctx.name(v)))
    return pairs


def _block(subject: str, pairs: list[tuple[str, str]]) -> str:
    lines = [f"{subject} {pairs[0][0]} {pairs[0][1]}"]
    lines += [f"    {p} {o}" for p, o in pairs[1:]]
    return " ;\n".join(lines) + " ."


def emit_module(module: Module, resolver: Resolver) -> str:
    ctx = _Ctx(module, resolver)
    h = module.header
    out = [f"# GENERATED from ontology/src/{module.path.stem}.yaml — do not edit. "
           "Design rationale lives in that file."]
    out.append("\n".join(f"@prefix {p}: <{ns}> ." for p, ns in sorted(ctx.prefixes.items())))
    iri = f"<{h['iri']}>"
    head = [("a", "owl:Ontology"), ("dcterms:title", turtle_literal(h["title"], lang="en"))]
    head += [("owl:imports", f"<{i}>") for i in h["imports"]]
    head.append(("owl:versionIRI", f"<{h['iri']}/{h['version']}>"))
    head.append(("owl:versionInfo", turtle_literal(h["version"])))
    out.append(_block(iri, head))
    for entries in (module.classes, module.properties, module.upstream):
        for e in entries.values():
            pairs = _entry_pairs(ctx, e)
            if pairs:
                out.append(_block(ctx.name(e.key), pairs))
    return "\n\n".join(out) + "\n"

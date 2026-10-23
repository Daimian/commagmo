"""YAML 源直接出概念图（.dot，可选渲染 .png），不经 ttl，不依赖 rdflib。

视觉语法与规则照搬 commagmo-legacy 的 ``viz.gen_module_maps``（按 ``--no-title --parents-up`` 那一档，
即 ontology/maps/ 的出图口径），常量逐字复制过来而**不 import 它**：那边一 import 就带进
rdflib。两边的等价在 commagmo-legacy 的 tests/test_ontology_src_render_dot.py 里按 dot 签名逐张核对过。

与旧出图器的对应关系（旧出图器读的是 rdflib 图，这里读 Module）：
    declared        焦点模块 ``classes`` 段的条目
    axiom_subjects  焦点模块里写了父类或限制、却不在 declared 里的主语（实际即 ``upstream`` 段）
    foreign         其中至少一条公理键不在上游缓存 ``axioms`` 里的
    本地 label      只取焦点模块条目的 ``label``；其余退回上游缓存 ``labels``，再退回 IRI 末段
                    —— 旧出图器只看本文件图里的 rdfs:label，隔壁模块的 label 它看不到
    隔壁父类        非焦点模块里 ``classes`` / ``upstream`` 条目的具名 ``parents``，只画一层
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from commagmo_build.manchester import Some, parse_restriction
from commagmo_build.resolve import Resolver
from commagmo_build.schema import Module

# ---- 以下常量逐字复制自 viz.gen_module_maps ----

PREFIXES = {
    "https://w3id.org/emmo/domain/computation": "comp",
    "https://w3id.org/emmo/domain/crystal-structure": "xtal",
    "https://w3id.org/emmo/domain/defect": "def",
    "https://w3id.org/emmo/domain/dft": "dft",
    "https://w3id.org/emmo/domain/magnetic-materials": "magmo",
    "https://w3id.org/emmo/domain/magnetic-structure": "magstr",
    "https://w3id.org/emmo/domain/material": "mat",
    "https://w3id.org/emmo/domain/micromagnetics": "mm",
    "https://w3id.org/emmo/domain/microstructure": "mstr",
    "https://w3id.org/emmo/domain/spin-dynamics": "asd",
    "https://w3id.org/emmo/domain/topological-defect": "topo",
    "https://w3id.org/emmo/domain/core": "core",
    "https://w3id.org/emmo/domain/core/material": "material",
    "https://w3id.org/emmo/domain/core/simulation": "sim",
    "https://w3id.org/emmo/domain/atomistic": "atom",
    "https://w3id.org/emmo/domain/crystallography": "cryst",
    "http://emmo.info/domain-crystallography/crystallography": "cryst",
    "https://w3id.org/emmo/domain/characterisation-methodology/chameo": "chameo",
    "https://w3id.org/emmo/domain/chameo": "chameo",
    "https://w3id.org/emmo#": "emmo",
    "http://purls.helmholtz-metadaten.de/cmso/": "cmso",
    "http://purls.helmholtz-metadaten.de/cdos/": "cdos",
    "http://purls.helmholtz-metadaten.de/cdos/cdco/": "cdco",
    "https://purls.helmholtz-metadaten.de/cdos/": "cdos",
    "https://purls.helmholtz-metadaten.de/cdos/cdco/": "cdco",
    "http://purls.helmholtz-metadaten.de/cdos/podo/": "podo",
    "https://purls.helmholtz-metadaten.de/cdos/podo/": "podo",
    "http://purls.helmholtz-metadaten.de/cdos/ldo/": "ldo",
    "https://purls.helmholtz-metadaten.de/cdos/ldo/": "ldo",
    "http://purls.helmholtz-metadaten.de/asmo/": "asmo",
    "https://purls.helmholtz-metadaten.de/asmo/": "asmo",
    "https://w3id.org/mdo/core/": "mdo",
    "https://w3id.org/mdo/structure/": "mdo-str",
    "https://w3id.org/mdo/calculation/": "mdo-calc",
    "https://w3id.org/mdo/provenance/": "mdo-prov",
    "http://purl.obolibrary.org/obo/": "obo",
    "https://gpo.ontology.link/": "gpo",
    "https://w3id.org/emmo/domain/manufacturing#": "manu",
    "http://www.w3.org/ns/prov#": "prov",
    "http://qudt.org/schema/qudt/": "qudt",
    "https://schema.org/": "schema",
    "http://www.w3.org/2002/07/owl#": "owl",
    "http://w3id.org/MUSICODE/Onto4OLAE/": "Onto4OLAE",
    "http://semanticscience.org/resource/": "sio",
    "https://purl.org/tema/": "tema",
    "http://w3id.org/nfdi4ing/metadata4ing#": "m4i",
}

# 限制的量词记号（gen_module_maps.QUANT 里本语法用得到的那几个）
_SOME = "∃"
_CARD = {"exactly": "=", "min": "≥"}

_SUBCLASS_DIR = ("\n       (--parents-up: the PARENT is ranked ABOVE the child, so the edge is\n"
                 "        written parent -> child with dir=back; the triangle still sits at the\n"
                 "        parent end, so the reading is the same as the default layout)")

STYLE_HEAD = """digraph {name} {{
    graph [rankdir=TB, bgcolor=white, splines=true, nodesep=0.40, ranksep=0.70,
           fontname="Helvetica"{title_block}];

    /* GENERATED from ontology/src/{source} by
       `python build.py` — do not hand-edit; edit the YAML
       and rebuild. The one hand-curated poster is
       module_material-core.dot, which spans modules and is not produced here.
       purple = declared in this module (--color-by-side 打开时改为按侧上色：暖棕 = 物质侧、
       蓝 = 描述侧、紫 = 代表侧、绿 = 缺陷（只在 Contrast）、粉 = 量（Property ⊑ Sign）），
       pale purple = our own namespace but declared in a
       sibling module, grey = someone else's ontology. A prefix on a label means ONLY
       "not our namespace" — our own classes never carry one, whichever file declares them.
       Pale-purple boxes DO get their own named parents drawn, one level, read from the
       sibling ttl — that axiom is ours, one file away. Grey boxes never do.
       solid hollow triangle = rdfs:subClassOf, triangle at the PARENT end{subclass_dir}
       dashed = class-level owl:Restriction (label: predicate + quantifier)
       dotted = rdfs:domain -> rdfs:range of an object property declared here
       green dotted "(doc)" = an owl:AnnotationProperty declared here, pointing at a
       named class: DOCUMENTATION, ZERO ENTAILMENT (--show-doc-edges only)
       red solid undirected = owl:disjointWith, a real axiom (--show-disjoint only)
       purple dashed box = declared elsewhere and given an axiom HERE THAT UPSTREAM LACKS;
       a restatement of an upstream axiom keeps the plain grey reference box */
    node [shape=box, style="rounded,filled", penwidth=1.4, margin="0.20,0.12",
          fontsize=15, fillcolor="#ebebeb", color="#a8a8a8", fontcolor="#333333",
          fontname="Helvetica-Oblique"];
    edge [color="#5a7d8c", fontcolor="#5a7d8c", fontname="Helvetica", fontsize=13,
          penwidth=1.5, arrowsize=0.9];
"""


def _prefix_of(iri: str) -> str | None:
    best = None
    for pre, tag in PREFIXES.items():
        if iri.startswith(pre) and (best is None or len(pre) > len(best[0])):
            best = (pre, tag)
    return best[1] if best else None


def _namespace_of(iri: str) -> str:
    local = iri.rsplit("#", 1)[-1].rsplit("/", 1)[-1]
    return iri[: len(iri) - len(local)]


def _local_name(iri: str) -> str:
    return iri.rsplit("#", 1)[-1].rsplit("/", 1)[-1]


def _wrap(text: str, width: int = 16) -> str:
    """在驼峰边界折行，长标签才折。"""
    if len(text) <= width:
        return text
    parts = re.findall(r"[A-Z]+(?![a-z])|[A-Z][a-z0-9]*|[a-z0-9]+|[^A-Za-z0-9]+", text)
    lines, cur = [], ""
    for p in parts:
        if cur and len(cur) + len(p) > width:
            lines.append(cur)
            cur = p
        else:
            cur += p
    if cur:
        lines.append(cur)
    return "\\n".join(lines)


def _axiom_key(item: tuple) -> str:
    """与 upstream_cache.encode_key 逐字相同的公理键（编码见 commagmo-legacy 的 upstream_cache 模块文档）。"""
    if item[0] == "cls":
        plain = ["cls", item[1]]
    else:
        _, prop, quant, filler = item
        plain = ["restr", prop, [quant, "false"], filler]
    return json.dumps(plain, ensure_ascii=False, separators=(",", ":"))


# ---- Module -> 出图要用的事实 ----

class _Facts:
    """一个或多个模块合起来、按 IRI 记的出图事实（重复的具名父类按集合去重，同 rdflib 图）。"""

    def __init__(self):
        self.declared: list[str] = []
        self.labels: dict[str, str] = {}
        # 主语 -> [("cls", 父类) | ("restr", 谓词, 量词串, 填充类)]，subClassOf 的宾语
        self.sub: dict[str, list[tuple]] = {}
        # 对象属性 -> {"parents": [...], "domain": [...], "range": [...]}
        self.objprops: dict[str, dict[str, list[str]]] = {}

    def _add_sub(self, s: str, item: tuple) -> None:
        items = self.sub.setdefault(s, [])
        if item[0] == "restr" or item not in items:
            items.append(item)

    def add(self, module: Module, base: Resolver) -> None:
        r = Resolver(module.prefixes, base.cache, base.local_ns)
        for e in (*module.classes.values(), *module.properties.values(),
                  *module.upstream.values()):
            iri = r.to_iri(e.key)
            f = e.fields
            if "label" in f and iri not in self.labels:
                lab = f["label"]
                self.labels[iri] = lab if isinstance(lab, str) else lab["text"]
            if e.kind == "class" and iri not in self.declared:
                self.declared.append(iri)
            if e.kind in ("class", "upstream"):
                for p in f.get("parents", ()):
                    self._add_sub(iri, ("cls", r.to_iri(p)))
                for text in f.get("restrictions", ()):
                    x = parse_restriction(text)
                    quant = _SOME if isinstance(x, Some) else f"{_CARD[x.op]}{x.n}"
                    self._add_sub(iri, ("restr", r.to_iri(x.prop), quant, r.to_iri(x.filler)))
            elif e.kind == "object":
                op = self.objprops.setdefault(iri, {"parents": [], "domain": [], "range": []})
                for fld, have in op.items():
                    vals = f.get(fld, [])
                    for v in [vals] if isinstance(vals, str) else vals:
                        if r.to_iri(v) not in have:
                            have.append(r.to_iri(v))


def render_module(modules: list[Module], resolver: Resolver, focus: list[Module],
                  title: str) -> str:
    """``focus`` 那几个模块的概念图 dot 文本；``modules`` 是全部模块（用来找隔壁父类）。

    ``title`` 是图名（dot 的 ``digraph`` 名；``--no-title`` 口径下图上不画标题）。
    """
    g = _Facts()
    for m in focus:
        g.add(m, resolver)
    sib = _Facts()
    for m in modules:
        if all(m is not f for f in focus):
            sib.add(m, resolver)

    declared = set(g.declared)
    own_ns = {_namespace_of(c) for c in declared}
    refs = resolver.cache.get("labels", {})
    ids: dict[str, str] = {}

    def label(iri: str) -> str:
        text = (g.labels.get(iri) or refs.get(iri) or _local_name(iri)).strip()
        if iri in declared or _namespace_of(iri) in own_ns:
            return _wrap(text)
        pre = _prefix_of(iri)
        return _wrap(f"{pre}:{text}" if pre else text)

    def node_id(iri: str) -> str:
        if iri in ids:
            return ids[iri]
        base = re.sub(r"[^A-Za-z0-9_]", "_", f"{_prefix_of(iri) or 'x'}_{_local_name(iri)}")
        name, n = base, 2
        while name in ids.values():
            name, n = f"{base}_{n}", n + 1
        ids[iri] = name
        return name

    axiom_subjects = {s for s, items in g.sub.items() if items and s not in declared}
    foreign = {c for c in axiom_subjects
               if {_axiom_key(i) for i in g.sub[c]} - resolver.upstream_axiom_keys(c)}
    edges_sub, edges_restr, edges_sig = [], [], []
    seen_restr = set()
    external = set()

    def touch(iri: str) -> None:
        if iri not in declared:
            external.add(iri)

    for c in axiom_subjects:
        touch(c)

    for c in sorted(declared | axiom_subjects):
        for item in g.sub.get(c, ()):
            if item[0] == "cls":
                touch(item[1])
                edges_sub.append((c, item[1]))
                continue
            _, prop, quant, filler = item
            touch(filler)
            rlab = f"{label(prop)} {quant}"
            if prop in g.objprops and g.objprops[prop]["parents"]:
                rlab += "\\n⊑ " + ", ".join(label(x).replace("\\n", "")
                                            for x in sorted(g.objprops[prop]["parents"]))
            if (c, filler, rlab) not in seen_restr:
                seen_restr.add((c, filler, rlab))
                edges_restr.append((c, filler, rlab))

    for p in sorted(g.objprops):
        op = g.objprops[p]
        sig_lab = label(p)
        if op["parents"]:
            sig_lab += "\\n⊑ " + ", ".join(label(x).replace("\\n", "")
                                           for x in sorted(op["parents"]))
        # 多个 domain / range：每个（domain, range）组合画一条边
        for dom in sorted(op["domain"]):
            for rng in sorted(op["range"]):
                touch(dom)
                touch(rng)
                edges_sig.append((dom, rng, sig_lab))

    # 自家隔壁模块声明的类：具名父类照画一层
    sibling_now = {c for c in external if _namespace_of(c) in own_ns}
    for c in sorted(sibling_now):
        parents = {i[1] for i in sib.sub.get(c, ()) if i[0] == "cls"}
        for parent in sorted(parents):
            touch(parent)
            edges_sub.append((c, parent))

    out = [STYLE_HEAD.format(
        name=re.sub(r"[^A-Za-z0-9]", "_", title),
        title_block="",
        source=", ".join(f"{m.path.stem}.yaml" for m in focus),
        subclass_dir=_SUBCLASS_DIR,
    )]

    out.append('\n    /* ---- declared in this module ---- */')
    out.append('    node [fillcolor="#e6dcf7", color="#6d28d9", fontname="Times-Roman", '
               'fontcolor="#111111"];')
    for c in sorted(declared, key=lambda c: (label(c), c)):
        out.append(f'    {node_id(c)} [label="{label(c)}"];')

    if foreign:
        out.append('\n    /* ---- declared elsewhere, but given a parent or a restriction '
                   'HERE that upstream does NOT have (genuine cross-module axiom, report 10 '
                   '§7.2). Axioms this file merely RESTATES from reference/ do not land here '
                   '— those subjects stay in the plain-reference lane below. ---- */')
        out.append('    node [fillcolor="#f5f0ff", color="#6d28d9", style="rounded,filled,'
                   'dashed", fontname="Times-Italic", fontcolor="#111111"];')
        for c in sorted(foreign, key=lambda c: (label(c), c)):
            out.append(f'    {node_id(c)} [label="{label(c)}"];')

    plain = external - foreign
    sibling = {c for c in plain if _namespace_of(c) in own_ns}
    if sibling:
        out.append('\n    /* ---- OUR OWN namespace, but the declaring line lives in a '
                   'sibling module of this repo (e.g. core:ComputationalSample seen from '
                   'material.ttl). No prefix on the label — the prefix marks "not ours", and '
                   'these are ours; the pale-purple box is what says "declared next door". '
                   'Their own parents are not drawn, same as the upstream lane below. ---- */')
        out.append('    node [fillcolor="#f3eefb", color="#a78bda", style="rounded,filled", '
                   'fontname="Times-Italic", fontcolor="#333333"];')
        for c in sorted(sibling, key=lambda c: (label(c), c)):
            out.append(f'    {node_id(c)} [label="{label(c)}"];')

    upstream = plain - sibling
    if upstream:
        out.append('\n    /* ---- referenced from elsewhere (upstream EMMO or another '
                   'project\'s ontology); their own parents are not drawn ---- */')
        out.append('    node [fillcolor="#ebebeb", color="#a8a8a8", style="rounded,filled", '
                   'fontname="Helvetica-Oblique", fontcolor="#333333"];')
        for c in sorted(upstream, key=lambda c: (label(c), c)):
            out.append(f'    {node_id(c)} [label="{label(c)}"];')

    if edges_restr:
        out.append('\n    /* ---- class-level restrictions ---- */')
        out.append('    edge [style=dashed, arrowhead=normal, color="#5a7d8c", '
                   'fontcolor="#5a7d8c"];')
        for s, o, lab in edges_restr:
            out.append(f'    {node_id(s)} -> {node_id(o)} [label="{lab}"];')

    if edges_sig:
        out.append('\n    /* ---- object property signatures (domain -> range) ---- */')
        out.append('    edge [style=dotted, arrowhead=vee, color="#0e7490", '
                   'fontcolor="#0e7490"];')
        for s, o, lab in edges_sig:
            out.append(f'    {node_id(s)} -> {node_id(o)} [label="{lab}"];')

    out.append('\n    /* ---- subClassOf ---- */')
    # parent -> child 决定排位（父在上），dir=back 把空心三角画回父类那一端
    out.append('    edge [style=solid, color="#9a9a9a", dir=back, arrowtail=onormal, '
               'arrowhead=none, penwidth=1.2, label=""];')
    for s, o in edges_sub:
        out.append(f'    {node_id(o)} -> {node_id(s)} [weight=8];')

    out.append("}\n")
    return "\n".join(out)


def render_png(dot_path: Path, png_path: Path, dpi: int = 200) -> None:
    """先过 unflatten 把叶子错开再交给 dot；unflatten 不在就直接出图（同 gen_module_maps.render）。"""
    try:
        staggered = subprocess.run(["unflatten", "-f", "-l", "5", "-c", "6", str(dot_path)],
                                   check=True, capture_output=True).stdout
    except (FileNotFoundError, subprocess.CalledProcessError):
        staggered = Path(dot_path).read_bytes()
    subprocess.run(["dot", "-Tpng", f"-Gdpi={dpi}", "-o", str(png_path)],
                   input=staggered, check=True)

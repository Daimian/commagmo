"""名字 <-> IRI 互转（不用 rdflib，只读上游缓存 JSON）。

约定见 YAML 约定：无前缀 = 本地；`emmo:` 经缓存按 label 解析；其他前缀按
module.prefixes 展开；`<完整 IRI>` 原样接受。IRI 一律是普通 str。
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from commagmo_build.paths import UPSTREAM_CACHE

EMMO_NS = "https://w3id.org/emmo#"
_EMMO_ID = re.compile(r"^EMMO_[0-9a-fA-F]{8}([-_][0-9a-fA-F]{4}){3}[-_][0-9a-fA-F]{12}$")
_HINT = "若 EMMO 已升级，到 commagmo-legacy 仓库运行 python -m commagmo_tools.ontology_src.upstream_cache 重建缓存"


class ResolveError(Exception):
    pass


def load_cache(path: Path = UPSTREAM_CACHE) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


class Resolver:
    def __init__(self, prefixes: dict[str, str], cache: dict,
                 local_ns: str = "https://w3id.org/emmo/domain/commagmo#"):
        self.prefixes = dict(prefixes)
        self.cache = cache
        self.local_ns = local_ns
        self._labels = cache.get("labels", {})
        self._index = cache.get("emmo_index", {})
        self._axioms = cache.get("axioms", {})

    def to_iri(self, name: str) -> str:
        if name.startswith("<") and name.endswith(">"):
            return name[1:-1]
        if ":" not in name:
            return self.local_ns + name
        prefix, _, rest = name.partition(":")
        if prefix == "emmo":
            return self._emmo_iri(rest)
        if prefix in self.prefixes:
            return self.prefixes[prefix] + rest
        raise ResolveError(f"未知前缀 {prefix!r}（名字 {name!r}）；已知前缀：{sorted(self.prefixes)}")

    def _emmo_iri(self, label: str) -> str:
        cands = self._index.get(label, [])
        if len(cands) == 1:
            return cands[0]
        if len(cands) > 1:
            raise ResolveError(
                f"emmo:{label} 有歧义，候选：{sorted(cands)}；请改写成 emmo:EMMO_<uuid>。{_HINT}")
        if _EMMO_ID.match(label):
            return EMMO_NS + label
        raise ResolveError(f"找不到 emmo:{label}（既不是已知 label，也不是 EMMO_<uuid>）。{_HINT}")

    def to_name(self, iri: str) -> str:
        if iri.startswith(self.local_ns):
            return iri[len(self.local_ns):]
        if iri.startswith(EMMO_NS):
            frag = iri[len(EMMO_NS):]
            lab = self._labels.get(iri)
            if lab is not None and self._index.get(lab) == [iri]:
                return f"emmo:{lab}"
            if _EMMO_ID.match(frag):
                return f"emmo:{frag}"
            return f"<{iri}>"
        for prefix, ns in self.prefixes.items():
            if prefix != "emmo" and ns and iri.startswith(ns):
                return f"{prefix}:{iri[len(ns):]}"
        return f"<{iri}>"

    def label(self, iri: str) -> str | None:
        return self._labels.get(iri)

    def upstream_axiom_keys(self, iri: str) -> frozenset[str]:
        return frozenset(self._axioms.get(iri, ()))

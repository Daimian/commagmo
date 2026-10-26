# ComMagMO

**Computational Magnetic Materials Ontology**: an OWL 2 domain ontology aligned to
[EMMO](https://emmo-repo.github.io/). It describes magnetic materials and the simulations
performed on them at four length scales: electronic, atomistic, mesoscopic and continuum.
Scales are assigned by the entities a model describes, following RoMM and OSMO. Micromagnetics
treats the magnetisation as a continuous field, but it is classed as mesoscopic, as both
sources do.

Current version: **1.2.0**. Namespace: `https://w3id.org/emmo/domain/commagmo#`.
It imports one upstream ontology, EMMO 1.0.4.

| File | Ontology IRI | Content |
| --- | --- | --- |
| [`ontology/commagmo.ttl`](ontology/commagmo.ttl) | `…/commagmo` | root: imports the two modules below |
| [`ontology/material.ttl`](ontology/material.ttl) | `…/commagmo/material` | 38 classes, 5 object properties |
| [`ontology/simulation.ttl`](ontology/simulation.ttl) | `…/commagmo/simulation` | 48 classes, 15 object properties |
| [`ontology/maps/`](ontology/maps/) | — | concept maps (`.dot` source + `.png`) |

## Layout

```
ontology/
  src/              YAML source (the only source of truth) + upstream-cache.json
  *.ttl, maps/      generated from src/ — do not hand-edit
tools/commagmo_build/   the generator (YAML → ttl and concept maps)
build.py            entry point
docs/
  review-criteria.md    criteria for judging a class or relation, used when reviewing the YAML
```

## Building

```bash
conda env create -f environment.yml          # once: python, pyyaml, rdflib, graphviz
conda run -n commagmo-bin python build.py          # regenerate ontology/*.ttl and ontology/maps/*
conda run -n commagmo-bin python build.py --check  # verify the committed files match the YAML and parse as Turtle
```

Without conda: `pip install -r requirements.txt` and put graphviz's `dot` on PATH, or pass
`--no-render` to skip the png maps.

## History

This repository is a lightweight restart. The full history — earlier ontology versions
(v0.0.1 – v1.1.0), the research workspace, upstream reference copies, the test suite and the
other visualisation tools — lives in the archived
[`Daimian/commagmo-legacy`](https://github.com/Daimian/commagmo-legacy). The first commit here
is the content of `commagmo-legacy@ontology-v1.2.0`. The upstream label cache
(`ontology/src/upstream-cache.json`) is rebuilt there, when EMMO is upgraded.

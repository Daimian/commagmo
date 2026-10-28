# ComMagMO

**Computational Magnetic Materials Ontology**: an OWL 2 domain ontology aligned to
[EMMO](https://emmo-repo.github.io/). It describes magnetic materials and the simulations
performed on them at four length scales: electronic, atomistic, mesoscopic and continuum.

Simulation codes at different scales (DFT, atomistic spin dynamics, micromagnetics, phase field)
each carry their own data formats and vocabularies, which makes their results hard to combine.
ComMagMO gives them a shared description: models, solvers, settings, input and calculated
properties, and the scale-bridging steps that turn the output of one scale into the input of
another, for example converting exchange constants into an exchange stiffness.

![ComMagMO concept map](ontology/maps/commagmo-map.png)

Scales are assigned by the entities a model describes, following RoMM and OSMO. Micromagnetics
treats the magnetisation as a continuous field, but it is classed as mesoscopic, as both
sources do.

Current release: **1.2.0** (tag `ontology-v1.2.0`). Namespace: `https://w3id.org/emmo/domain/commagmo#`.
It imports one upstream ontology, EMMO 1.0.4.

| File | Ontology IRI | Content |
| --- | --- | --- |
| [`ontology/commagmo.ttl`](ontology/commagmo.ttl) | `…/commagmo` | root: imports the two modules below |
| [`ontology/material.ttl`](ontology/material.ttl) | `…/commagmo/material` | 38 classes, 5 object properties |
| [`ontology/simulation.ttl`](ontology/simulation.ttl) | `…/commagmo/simulation` | 48 classes, 15 object properties |
| [`ontology/maps/`](ontology/maps/) | — | concept maps (`.dot` source + `.png`) |

## Using the ontology

Open `ontology/commagmo.ttl` in [Protégé](https://protege.stanford.edu/), or load it with rdflib:

```python
from rdflib import Graph

g = Graph().parse("ontology/commagmo.ttl")
g.parse("ontology/material.ttl")
g.parse("ontology/simulation.ttl")
print(len(g), "triples")
```

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

The ontology is authored in YAML and compiled to Turtle; edit `ontology/src/*.yaml`, never the
`.ttl` files.

```bash
conda env create -f environment.yml          # once: python, pyyaml, rdflib, graphviz
conda run -n commagmo-bin python build.py          # regenerate ontology/*.ttl and ontology/maps/*
conda run -n commagmo-bin python build.py --check  # verify the committed files match the YAML and parse as Turtle
```

Without conda: `pip install -r requirements.txt` and put graphviz's `dot` on PATH, or pass
`--no-render` to skip the png maps.

Earlier versions (v0.0.1 – v1.1.0) were developed in a separate research repository; this
repository starts from v1.2.0.

## License

The ontology (`ontology/`) is licensed under [CC BY 4.0](LICENSE-ONTOLOGY).
The build tooling (`tools/`, `build.py`) is licensed under the [MIT License](LICENSE).

## Author

[Mian Dai](https://github.com/Daimian), Institute of Materials Science, TU Darmstadt.

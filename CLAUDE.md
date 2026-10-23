# CLAUDE.md

Conventions for working in this repository. The layout is described in `README.md`.

## Ontology

- `ontology/src/*.yaml` is the only source of truth. Never hand-edit `ontology/*.ttl` or
  `ontology/maps/*`; edit the YAML and run `python build.py`.
- `python build.py --check` must pass before committing ontology changes.
- A release is a git tag `ontology-vX.Y.Z` on the commit that bumps the version in the YAML.
  There is no archive directory: earlier versions are retrieved from their tags.
- Versions up to v1.2.0, and everything that was trimmed away (research notes, reference
  copies, tests, other plotting tools), are in the archived repository
  `Daimian/commagmo-legacy`. Pull files back from there when needed instead of re-creating them.

## Code

- The generator lives in `tools/commagmo_build/`. Find repository paths through
  `commagmo_build.paths`; do not count `Path(__file__).parents[N]` elsewhere.
- Run the build in the conda env `commagmo-bin` (`environment.yml`; it carries graphviz for the png
  maps): `conda run -n commagmo-bin python build.py`. Keep `environment.yml` and
  `requirements.txt` in step and minimal.

## Naming

- File and directory names: English, lower-case kebab-case. Python modules use snake_case.
- Document text can be in whichever language suits its readers.

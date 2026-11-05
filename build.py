"""由 ontology/src/*.yaml 生成 ontology/*.ttl 与 ontology/maps/*。

用法：python build.py [--no-render] [--check]
  --check 时额外用 rdflib 解析每个 ttl，确认语法无误；
          再用 pyshacl 拿 tests/shacl/ 的正反例检验 ontology/shapes/。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "tools"))

from commagmo_build.build import main  # noqa: E402
from commagmo_build.paths import ONTOLOGY_DIR  # noqa: E402


def parse_ttl() -> int:
    from rdflib import Graph
    bad = 0
    for ttl in sorted(ONTOLOGY_DIR.glob("*.ttl")):
        try:
            Graph().parse(ttl, format="turtle")
        except Exception as e:
            print(f"ttl 解析失败：{ttl}: {e}", file=sys.stderr)
            bad = 1
    return bad


def check_shacl() -> int:
    from commagmo_build.shacl import check
    errors = check()
    for e in errors:
        print(f"SHACL：{e}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    code = main()
    if code == 0 and "--check" in sys.argv[1:]:
        code = parse_ttl() or check_shacl()
    sys.exit(code)

"""仓库内路径的唯一口径。"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]  # tools/commagmo_build/paths.py → 仓库根

ONTOLOGY_DIR = REPO_ROOT / "ontology"            # 生成的 ttl 与 maps/
ONTOLOGY_SRC_DIR = ONTOLOGY_DIR / "src"          # YAML 源与上游缓存
UPSTREAM_CACHE = ONTOLOGY_SRC_DIR / "upstream-cache.json"

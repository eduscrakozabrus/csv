from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Dict

from .data_models import BlocksBundle


class DataStore:
    """Loads and caches resume blocks."""

    def __init__(self, blocks_path: Path) -> None:
        self._blocks_path = blocks_path

    @lru_cache(maxsize=1)
    def bundle(self) -> BlocksBundle:
        raw: Dict[str, object] = json.loads(self._blocks_path.read_text(encoding="utf-8"))
        return BlocksBundle.from_dict(raw)


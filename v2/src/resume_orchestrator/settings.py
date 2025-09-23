from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Settings:
    """Runtime settings for the orchestrator."""

    root_dir: Path
    configs_dir: Path | None = None

    @classmethod
    def from_project_root(cls, root: Path | None = None) -> "Settings":
        root_dir = root or Path(__file__).resolve().parents[2]
        configs_dir = root_dir / "configs"
        return cls(root_dir=root_dir, configs_dir=configs_dir)

    def blocks_path(self) -> Path:
        path = (self.configs_dir or self.root_dir / "configs") / "blocks.json"
        if not path.exists():
            raise FileNotFoundError(f"Blocks file not found at {path}")
        return path

    def templates_dir(self) -> Path:
        path = (self.configs_dir or self.root_dir / "configs") / "templates"
        if not path.exists():
            raise FileNotFoundError(f"Templates directory not found at {path}")
        return path

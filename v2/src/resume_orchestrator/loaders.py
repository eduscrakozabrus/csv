from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import yaml

from .data_models import TemplateConfig


class TemplateLoader:
    def __init__(self, templates_dir: Path) -> None:
        self._templates_dir = templates_dir

    def list_templates(self) -> List[str]:
        return sorted(path.stem for path in self._templates_dir.glob("*.yaml"))

    def load(self, template_name: str) -> TemplateConfig:
        path = self._templates_dir / f"{template_name}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Template '{template_name}' not found")
        data: Dict[str, object] = yaml.safe_load(path.read_text(encoding="utf-8"))
        return TemplateConfig(**data)

    def iter_configs(self):
        for name in self.list_templates():
            yield self.load(name)


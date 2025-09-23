from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from ..composer import ComposedResume


class Exporter(ABC):
    format: str

    @abstractmethod
    def export(self, resume: ComposedResume, destination: Path | None = None) -> str:
        """Render the resume and return the output path or textual representation."""


class ExporterRegistry:
    def __init__(self) -> None:
        self._exporters: dict[str, type[Exporter]] = {}

    def register(self, exporter_cls: type[Exporter]) -> None:
        self._exporters[exporter_cls.format] = exporter_cls

    def create(self, format_name: str) -> Exporter:
        try:
            exporter_cls = self._exporters[format_name]
        except KeyError as exc:
            raise ValueError(f"Unsupported export format '{format_name}'") from exc
        return exporter_cls()

    def available_formats(self) -> list[str]:
        return sorted(self._exporters.keys())


registry = ExporterRegistry()


def register_exporter(cls: type[Exporter]) -> type[Exporter]:
    registry.register(cls)
    return cls


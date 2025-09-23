from __future__ import annotations

from pathlib import Path
from textwrap import indent

from ..composer import ComposedResume
from .base import Exporter, register_exporter


@register_exporter
class MarkdownExporter(Exporter):
    format = "markdown"

    def export(self, resume: ComposedResume, destination: Path | None = None) -> str:
        body = self._render(resume)
        if destination:
            destination.write_text(body, encoding="utf-8")
            return str(destination)
        return body

    def _render(self, resume: ComposedResume) -> str:
        lines: list[str] = []
        personal = resume.personal_info

        lines.append(f"# {personal['name']}")
        lines.append(f"**{personal['headline']}**")
        contacts = " | ".join(f"{k.title()}: {v}" for k, v in personal["contacts"].items())
        lines.append(contacts)
        lines.append("")

        lines.append("## Professional Summary")
        lines.append(resume.summary)
        lines.append("")

        lines.append("## Technical Skills")
        for category, skills in resume.skills.items():
            lines.append(f"- **{category}:** {', '.join(skills)}")
        lines.append("")

        lines.append("## Work Experience")
        for block in resume.experience:
            lines.append(f"### {block.title} — {block.company}")
            lines.append(f"*{block.period}*")
            lines.append("")
            for resp in block.responsibilities:
                lines.append(f"- {resp}")
            if block.achievements:
                lines.append("  ")
                lines.append("_Achievements:_")
                for achievement in block.achievements:
                    lines.append(f"  - {achievement}")
            lines.append("")

        return "\n".join(lines).rstrip() + "\n"


from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    ListFlowable,
    ListItem,
    HRFlowable,
)

from ..composer import ComposedResume
from .base import Exporter, register_exporter


@register_exporter
class PdfExporter(Exporter):
    format = "pdf"

    def export(self, resume: ComposedResume, destination: Path | None = None) -> str:
        if destination is None:
            raise ValueError("PDF exporter requires a destination path")
        doc = SimpleDocTemplate(
            str(destination),
            pagesize=A4,
            leftMargin=20 * mm,
            rightMargin=20 * mm,
            topMargin=20 * mm,
            bottomMargin=20 * mm,
        )
        styles = self._build_styles()
        story = self._build_story(resume, styles)
        doc.build(story)
        return str(destination)

    def _build_styles(self):
        styles = getSampleStyleSheet()
        styles.add(
            ParagraphStyle(
                name="Name",
                parent=styles["Heading1"],
                fontSize=24,
                textColor=colors.HexColor("#1a1a1a"),
                alignment=TA_CENTER,
                spaceAfter=6,
            )
        )
        styles.add(
            ParagraphStyle(
                name="Headline",
                parent=styles["Heading2"],
                fontSize=14,
                textColor=colors.HexColor("#333333"),
                alignment=TA_CENTER,
                spaceAfter=10,
            )
        )
        styles.add(
            ParagraphStyle(
                name="Contacts",
                parent=styles["BodyText"],
                fontSize=10,
                leading=12,
                alignment=TA_CENTER,
                textColor=colors.HexColor("#3d464f"),
            )
        )
        styles.add(
            ParagraphStyle(
                name="Section",
                parent=styles["Heading2"],
                fontSize=14,
                textColor=colors.HexColor("#2c3e50"),
                spaceBefore=10,
                spaceAfter=6,
            )
        )
        styles.add(
            ParagraphStyle(
                name="Body",
                parent=styles["BodyText"],
                fontSize=10,
                leading=14,
            )
        )
        styles.add(
            ParagraphStyle(
                name="BodySmall",
                parent=styles["Body"],
                fontSize=9,
                leading=12,
                textColor=colors.HexColor("#4f5b66"),
            )
        )
        styles.add(
            ParagraphStyle(
                name="BodyItalic",
                parent=styles["Body"],
                fontSize=10,
                leading=13,
                textColor=colors.HexColor("#1a1a1a"),
                fontName="Times-Italic",
            )
        )
        styles.add(
            ParagraphStyle(
                name="ExperienceTitle",
                parent=styles["Heading3"],
                fontSize=12,
                textColor=colors.HexColor("#2c3e50"),
                spaceAfter=4,
            )
        )
        return styles

    def _build_story(self, resume: ComposedResume, styles):
        story = []
        personal = resume.personal_info

        story.append(Paragraph(personal["name"], styles["Name"]))
        story.append(Paragraph(personal["headline"], styles["Headline"]))
        contacts = " | ".join(f"{k.title()}: {v}" for k, v in personal["contacts"].items())
        story.append(Paragraph(contacts, styles["Contacts"]))
        story.append(HRFlowable(width="100%", thickness=1, lineCap="round", color=colors.HexColor("#d0d6dc")))
        story.append(Spacer(1, 6 * mm))

        story.append(Paragraph("PROFESSIONAL SUMMARY", styles["Section"]))
        story.append(Paragraph(resume.summary, styles["Body"]))
        story.append(Spacer(1, 6 * mm))

        story.append(Paragraph("TECHNICAL SKILLS", styles["Section"]))
        story.extend(self._skills_table(resume, styles))
        story.append(Spacer(1, 6 * mm))

        story.append(Paragraph("WORK EXPERIENCE", styles["Section"]))
        story.extend(self._experience_blocks(resume, styles))

        return story

    def _skills_table(self, resume: ComposedResume, styles):
        table_data = []
        for category, skills in resume.skills.items():
            table_data.append(
                [Paragraph(f"<b>{category}</b>", styles["Body"]), Paragraph(", ".join(skills), styles["BodySmall"])]
            )
        if not table_data:
            return []
        table = Table(table_data, colWidths=[55 * mm, 115 * mm])
        table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        return [table]

    def _experience_blocks(self, resume: ComposedResume, styles):
        elements = []
        options = resume.meta.get("options", {})

        for idx, block in enumerate(resume.experience):
            elements.append(Paragraph(f"{block.title}", styles["ExperienceTitle"]))
            elements.append(Paragraph(f"{block.company} | {block.period}", styles["BodySmall"]))

            responsibilities = [
                ListItem(Paragraph(item, styles["Body"]), leftIndent=4 * mm)
                for item in block.responsibilities
            ]
            if responsibilities:
                elements.append(
                    ListFlowable(
                        responsibilities,
                        bulletType="bullet",
                        start="•",
                        bulletFontName=styles["Body"].fontName,
                        bulletFontSize=styles["Body"].fontSize,
                        bulletColor=colors.HexColor("#2c3e50"),
                        leftIndent=4 * mm,
                    )
                )

            if block.achievements and options.get("highlight_achievements", True):
                ach_items = [
                    ListItem(Paragraph(text, styles["BodyItalic"]), leftIndent=6 * mm)
                    for text in block.achievements
                ]
                elements.append(
                    ListFlowable(
                        ach_items,
                        bulletType="bullet",
                        start="→",
                        bulletFontName=styles["BodyItalic"].fontName,
                        bulletFontSize=styles["BodyItalic"].fontSize,
                        bulletColor=colors.HexColor("#1a7f9f"),
                        leftIndent=6 * mm,
                    )
                )

            if idx < len(resume.experience) - 1:
                elements.append(Spacer(1, 5 * mm))
        return elements

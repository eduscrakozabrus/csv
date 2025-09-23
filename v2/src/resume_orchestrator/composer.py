from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .data_models import BlocksBundle, ExperienceBlock, TemplateConfig
from .filters import apply_experience_filters


@dataclass
class ComposedResume:
    meta: Dict[str, object]
    personal_info: Dict[str, object]
    summary: str
    skills: Dict[str, List[str]]
    experience: List[ExperienceBlock]


class ResumeComposer:
    def __init__(self, bundle: BlocksBundle) -> None:
        self._bundle = bundle

    def compose(self, config: TemplateConfig) -> ComposedResume:
        info = self._bundle.personal_info
        summary = self._resolve_summary(config)
        skills = self._collect_skills(config)
        exp = self._collect_experience(config)

        meta = {
            "template": config.template,
            "name": config.name,
            "options": config.options,
        }

        personal = {
            "name": info.name,
            "headline": info.headline(config.headline_variant, fallback="senior"),
            "contacts": info.contacts,
            "availability": info.availability,
        }

        return ComposedResume(
            meta=meta,
            personal_info=personal,
            summary=summary,
            skills=skills,
            experience=exp,
        )

    def _resolve_summary(self, config: TemplateConfig) -> str:
        try:
            return self._bundle.summaries[config.summary_key]
        except KeyError as exc:
            raise KeyError(f"summary '{config.summary_key}' not found in blocks") from exc

    def _collect_skills(self, config: TemplateConfig) -> Dict[str, List[str]]:
        skills: Dict[str, List[str]] = {}
        for key in config.skill_categories:
            category = self._bundle.skills.get(key)
            if not category:
                continue
            values = category.collect(config.skill_levels)
            if values:
                skills[category.category] = sorted(values)
        return skills

    def _collect_experience(self, config: TemplateConfig) -> List[ExperienceBlock]:
        filters_cfg = config.filters
        include_tags = filters_cfg.get("include_tags")
        exclude_tags = filters_cfg.get("exclude_tags")
        priority_tags = filters_cfg.get("priority_tags")
        limit_years = filters_cfg.get("limit_years")
        max_blocks = config.options.get("max_experience_blocks") if config.options else None

        return apply_experience_filters(
            self._bundle.experience,
            include_tags=include_tags,
            exclude_tags=exclude_tags,
            priority_tags=priority_tags,
            limit_years=limit_years,
            max_items=max_blocks,
            template_key=config.template,
        )

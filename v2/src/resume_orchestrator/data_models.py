from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional
import re
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

SkillLevel = Literal["expert", "proficient", "familiar"]


class PersonalInfo(BaseModel):
    name: str
    title_variants: Dict[str, str] = Field(default_factory=dict)
    headline_variants: Dict[str, str] = Field(default_factory=dict)
    contacts: Dict[str, str]
    availability: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(populate_by_name=True, extra='ignore')

    def _variants(self) -> Dict[str, str]:
        variants = self.headline_variants or self.title_variants
        if not variants:
            return {}
        return variants

    def headline(self, key: str, fallback: str | None = None) -> str:
        variants = self._variants()
        if key in variants:
            return variants[key]
        if fallback and fallback in variants:
            return variants[fallback]
        return next(iter(variants.values()), '')


class SkillCategory(BaseModel):
    category: str
    levels: Dict[SkillLevel, List[str]]

    def collect(self, allowed_levels: Optional[List[SkillLevel]] = None) -> List[str]:
        levels = allowed_levels or ["expert", "proficient", "familiar"]
        result: List[str] = []
        for level in levels:
            result.extend(self.levels.get(level, []))
        return result


class ExperienceBlock(BaseModel):
    id: str
    title: str
    company: str
    period: str
    tags: List[str]
    responsibilities: List[str]
    achievements: List[str] = Field(default_factory=list)
    hidden_for: List[str] = Field(default_factory=list)

    def matches_tags(self, include: List[str] | None, exclude: List[str] | None) -> bool:
        tags_set = set(self.tags)
        if exclude and any(tag in tags_set for tag in exclude):
            return False
        if include and not any(tag in tags_set for tag in include):
            return False
        return True

    def is_current(self) -> bool:
        period_lower = self.period.lower()
        return "present" in period_lower or "current" in period_lower or "current" in self.tags

    def start_year(self) -> int:
        years = re.findall(r"(?:19|20)\d{2}", self.period)
        if years:
            try:
                return int(years[0])
            except ValueError:
                pass
        return datetime.now().year


class BlocksBundle(BaseModel):
    personal_info: PersonalInfo
    summaries: Dict[str, str]
    skills: Dict[str, SkillCategory]
    experience: List[ExperienceBlock]

    @classmethod
    def from_dict(cls, raw: Dict[str, object]) -> "BlocksBundle":
        skills = {key: SkillCategory(**value) for key, value in raw["skills"].items()}
        experience = [ExperienceBlock(**item) for item in raw["experience"]]
        return cls(
            personal_info=PersonalInfo(**raw["personal_info"]),
            summaries=raw["summaries"],
            skills=skills,
            experience=experience,
        )


class TemplateConfig(BaseModel):
    template: str
    name: str
    headline_variant: str
    summary_key: str
    skill_categories: List[str]
    skill_levels: List[SkillLevel]
    filters: Dict[str, object] = Field(default_factory=dict)
    options: Dict[str, object] = Field(default_factory=dict)
    closing_statement: Optional[str] = None
    output: Optional[Dict[str, object]] = None

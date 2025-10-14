from __future__ import annotations

import re
from datetime import datetime
from typing import Iterable, List

from .data_models import ExperienceBlock


def apply_experience_filters(
    blocks: Iterable[ExperienceBlock],
    *,
    include_tags=None,
    exclude_tags=None,
    priority_tags=None,
    limit_years=None,
    max_items=None,
    template_key: str | None = None,
) -> List[ExperienceBlock]:
    result: List[ExperienceBlock] = []
    current_year = datetime.now().year

    template_tokens: set[str] = set()
    if template_key:
        lowered = template_key.lower()
        template_tokens = {lowered}
        template_tokens.update(part for part in lowered.replace("-", "_").split("_") if part)

    for block in blocks:
        if template_tokens and block.hidden_for:
            hidden_tokens = {tag.lower() for tag in block.hidden_for}
            if template_tokens & hidden_tokens:
                continue
        if exclude_tags and any(tag in block.tags for tag in exclude_tags):
            continue
        if include_tags and not any(tag in block.tags for tag in include_tags):
            continue
        if limit_years is not None:
            years = re.findall(r"(?:19|20)\\d{2}", block.period)
            if years:
                try:
                    start_year = int(years[0])
                    if current_year - start_year > limit_years:
                        continue
                except ValueError:
                    pass
        result.append(block)

    priorities = set(priority_tags or [])

    def sort_key(block: ExperienceBlock):
        priority_score = sum(tag in priorities for tag in block.tags)
        return (
            0 if block.is_current() else 1,
            -block.start_year(),
            -priority_score,
        )

    result.sort(key=sort_key)

    if max_items:
        result = result[:max_items]

    return result

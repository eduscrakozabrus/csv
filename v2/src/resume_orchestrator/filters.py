from __future__ import annotations

import re
from datetime import datetime
from typing import Iterable, List

from .data_models import ExperienceBlock


def apply_experience_filters(blocks: Iterable[ExperienceBlock], *, include_tags=None, exclude_tags=None, priority_tags=None, limit_years=None, max_items=None) -> List[ExperienceBlock]:
    result: List[ExperienceBlock] = []
    current_year = datetime.now().year

    for block in blocks:
        if exclude_tags and any(tag in block.tags for tag in exclude_tags):
            continue
        if include_tags and not any(tag in block.tags for tag in include_tags):
            continue
        if limit_years is not None:
            years = re.findall(r"(19|20)\\d{2}", block.period)
            if years:
                try:
                    start_year = int(years[0])
                    if current_year - start_year > limit_years:
                        continue
                except ValueError:
                    pass
        result.append(block)

    if priority_tags:
        priorities = set(priority_tags)
        result.sort(key=lambda block: sum(tag in priorities for tag in block.tags), reverse=True)

    if max_items:
        result = result[:max_items]

    return result


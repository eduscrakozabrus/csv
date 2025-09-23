from resume_orchestrator.data_models import ExperienceBlock
from resume_orchestrator.filters import apply_experience_filters


def make_block(**kwargs):
    defaults = {
        "id": "test",
        "title": "DevOps",
        "company": "Test Co",
        "period": "2022 – 2024",
        "tags": ["devops"],
        "responsibilities": ["Did things"],
        "achievements": [],
    }
    defaults.update(kwargs)
    return ExperienceBlock(**defaults)


def test_include_tags_filter():
    block = make_block(tags=["devops", "fintech"])
    result = apply_experience_filters([block], include_tags=["fintech"])
    assert result == [block]


def test_exclude_tags_filter():
    block = make_block(tags=["legacy"])
    result = apply_experience_filters([block], exclude_tags=["legacy"])
    assert result == []


def test_priority_sorting():
    a = make_block(id="a", tags=["blockchain"])
    b = make_block(id="b", tags=["fintech", "security"])
    result = apply_experience_filters([a, b], priority_tags=["fintech", "security"])
    assert result[0].id == "b"


"""Tests for JD skill extraction and multi-JD aggregation."""

from __future__ import annotations

from typing import Any

import pytest

from core.db import Job, Source
from resume.skills import (
    AggregatedSkill,
    JdSkill,
    SkillCategory,
    aggregate_role_skills,
    extract_top_skills,
    extract_top_skills_deterministic,
    parse_skills_json,
)


def _job(
    *,
    title: str = "Product Manager",
    description: str = "",
    external_id: str = "j1",
) -> Job:
    return Job(
        source=Source.linkedin,
        external_id=external_id,
        title=title,
        company="Acme",
        url="https://example.com/jobs/1",
        description_clean=description,
    )


class FakeSkillClient:
    def __init__(self, payload: str, *, fail: bool = False) -> None:
        self.payload = payload
        self.fail = fail
        self.calls: list[dict[str, Any]] = []

    async def complete(
        self,
        *,
        model: str,
        system_blocks: list[dict[str, Any]],
        user: str,
        max_tokens: int,
        temperature: float,
        json_mode: bool = False,
        **_kwargs: Any,
    ) -> str:
        self.calls.append({"model": model, "user": user, "json_mode": json_mode})
        if self.fail:
            raise RuntimeError("simulated failure")
        return self.payload


def test_parse_skills_json_plain() -> None:
    raw = (
        '[{"name":"Python","category":"tool","importance":5},'
        '{"name":"SQL","category":"hard","importance":4}]'
    )
    skills = parse_skills_json(raw)
    assert len(skills) == 2
    assert skills[0].name == "Python"
    assert skills[0].category == SkillCategory.tool
    assert skills[0].importance == 5


def test_parse_skills_json_repairs_truncated_array() -> None:
    raw = (
        '[{"name":"Agile","category":"hard","importance":4},'
        '{"name":"APIs","category":"hard","imp'
    )
    skills = parse_skills_json(raw)
    assert [s.name for s in skills] == ["Agile"]


def test_parse_skills_json_fenced_and_dedupes() -> None:
    raw = """```json
[{"name":"Roadmapping","category":"hard","importance":5},
 {"name":"roadmapping","category":"hard","importance":4},
 {"name":"Agile","category":"soft","importance":3}]
```"""
    skills = parse_skills_json(raw)
    assert [s.name for s in skills] == ["Roadmapping", "Agile"]


def test_parse_skills_json_clamps_importance() -> None:
    skills = parse_skills_json('[{"name":"X","importance":99}]')
    assert skills[0].importance == 5


def test_deterministic_extract_ranks_frequent_terms() -> None:
    job = _job(
        title="Backend Engineer Python",
        description=(
            "We need Python Python Python FastAPI experience. "
            "Also Kubernetes and Postgres SQL. Mentorship is nice."
        ),
    )
    skills = extract_top_skills_deterministic(job, top_n=10)
    names = [s.name.lower() for s in skills]
    assert any("python" in n for n in names)
    assert len(skills) <= 10
    assert all(1 <= s.importance <= 5 for s in skills)


@pytest.mark.asyncio
async def test_extract_top_skills_uses_llm() -> None:
    client = FakeSkillClient(
        '[{"name":"Product Strategy","category":"hard","importance":5},'
        '{"name":"SQL","category":"tool","importance":4}]'
    )
    job = _job(description="Looking for product strategy and SQL skills.")
    skills = await extract_top_skills(job, client=client, model="fake-model")
    assert len(skills) == 2
    assert skills[0].name == "Product Strategy"
    assert client.calls and client.calls[0]["json_mode"] is True


@pytest.mark.asyncio
async def test_extract_top_skills_falls_back_on_failure() -> None:
    client = FakeSkillClient("not-json", fail=True)
    job = _job(
        title="Data Analyst SQL",
        description="SQL SQL Tableau Tableau Excel required for analysis.",
    )
    skills = await extract_top_skills(job, client=client)
    assert skills  # deterministic fallback produced something
    assert all(isinstance(s, JdSkill) for s in skills)


@pytest.mark.asyncio
async def test_extract_top_skills_no_client_is_deterministic() -> None:
    job = _job(title="PM Roadmap", description="roadmap prioritization stakeholder management")
    skills = await extract_top_skills(job, client=None)
    assert isinstance(skills, list)


def test_aggregate_role_skills_prevalence_and_ranking() -> None:
    jd1 = [
        JdSkill(name="Python", category=SkillCategory.tool, importance=5),
        JdSkill(name="SQL", category=SkillCategory.hard, importance=4),
    ]
    jd2 = [
        JdSkill(name="python", category=SkillCategory.tool, importance=5),
        JdSkill(name="Agile", category=SkillCategory.soft, importance=3),
    ]
    jd3 = [
        JdSkill(name="Python", category=SkillCategory.tool, importance=4),
        JdSkill(name="SQL", category=SkillCategory.hard, importance=5),
    ]
    profile = aggregate_role_skills([jd1, jd2, jd3], role="Software Engineer", top_n=10)
    assert profile.role == "Software Engineer"
    assert profile.jd_count == 3
    assert profile.skills
    # Python mentioned in all 3
    python = next(s for s in profile.skills if s.name.lower() == "python")
    assert isinstance(python, AggregatedSkill)
    assert python.prevalence_pct == 100.0
    assert python.mention_count == 3
    assert python.avg_importance == pytest.approx(4.67, abs=0.01)
    # SQL in 2 of 3
    sql = next(s for s in profile.skills if s.name.lower() == "sql")
    assert sql.prevalence_pct == pytest.approx(66.7, abs=0.1)
    # Python should rank above Agile (higher prevalence * importance)
    assert profile.skills[0].name.lower() == "python"


def test_aggregate_empty() -> None:
    profile = aggregate_role_skills([], role="X")
    assert profile.skills == []
    assert profile.jd_count == 0

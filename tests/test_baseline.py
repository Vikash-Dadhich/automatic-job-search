"""Tests for role baseline builder and get_jobs_for_role."""

from __future__ import annotations

from typing import Any

import pytest

from config.profile import (
    Address,
    Education,
    Experience,
    Identity,
    Preferences,
    Profile,
    WorkAuthorization,
)
from core.db import (
    Job,
    RoleBaseline,
    Source,
    Status,
    get_jobs_for_role,
    get_role_baseline_by_role,
    session_scope,
    upsert_job,
)
from resume.baseline import build_baseline_resume_data, build_role_baseline
from resume.skills import AggregatedSkill, RoleSkillProfile, SkillCategory


def _profile() -> Profile:
    return Profile(
        identity=Identity(
            full_name="Jane Q. Doe",
            email="jane@example.com",
            phone="+1-555-111-2222",
            location="Seattle, WA",
            linkedin_url="https://www.linkedin.com/in/janedoe",
            github_url="https://github.com/janedoe",
            portfolio_url=None,
            address=Address(street="1 Main", city="Seattle", state="WA", zip="98101"),
        ),
        work_authorization=WorkAuthorization(
            status="US Citizen",
            sponsorship_required=False,
            authorized_to_work_us=True,
            needs_visa_sponsorship=False,
        ),
        education=[
            Education(
                degree="M.S.",
                field="CS",
                school="Example U",
                location="Seattle, WA",
                graduation_date="2024-05",
            )
        ],
        experience=[
            Experience(
                title="Software Engineer",
                company="Acme",
                location="Seattle, WA",
                start_date="2022-01",
                end_date="2024-01",
                bullets=[
                    "Built Python APIs with FastAPI.",
                    "Designed SQL data models.",
                    "Deployed Kubernetes services.",
                ],
            )
        ],
        skills=["Python", "SQL", "Kubernetes"],
        preferences=Preferences(
            titles=["Software Engineer", "Product Manager"],
            locations=["Seattle, WA"],
            remote_ok=True,
            relocation_ok=False,
        ),
    )


class FakeClient:
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
        return (
            '[{"name":"Python","category":"tool","importance":5},'
            '{"name":"SQL","category":"hard","importance":4},'
            '{"name":"Kubernetes","category":"tool","importance":4}]'
        )


@pytest.mark.asyncio
async def test_get_jobs_for_role_matches_title(db_ready) -> None:
    async with session_scope() as session:
        await upsert_job(
            session,
            Job(
                source=Source.linkedin,
                external_id="se1",
                title="Senior Software Engineer",
                company="A",
                url="https://example.com/1",
                description_clean="Need Python and SQL experience for backend work.",
                status=Status.discovered,
            ),
        )
        await upsert_job(
            session,
            Job(
                source=Source.linkedin,
                external_id="pm1",
                title="Product Manager",
                company="B",
                url="https://example.com/2",
                description_clean="Roadmapping and stakeholder management.",
                status=Status.discovered,
            ),
        )
        matched = await get_jobs_for_role(session, ["software engineer"], limit=10)

    assert len(matched) == 1
    assert "software" in matched[0].title.lower()


@pytest.mark.asyncio
async def test_build_role_baseline_persists(db_ready, tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("BASELINES_DIR", str(tmp_path / "baselines"))
    from config.settings import get_settings

    get_settings.cache_clear()

    async with session_scope() as session:
        for i in range(5):
            await upsert_job(
                session,
                Job(
                    source=Source.linkedin,
                    external_id=f"se{i}",
                    title="Software Engineer",
                    company=f"Co{i}",
                    url=f"https://example.com/{i}",
                    description_clean=(
                        "Python FastAPI SQL Kubernetes backend engineer role. "
                        "Build APIs and ship reliable services."
                    ),
                    status=Status.discovered,
                ),
            )

    baseline = await build_role_baseline(
        "Software Engineer",
        title_terms=["Software Engineer"],
        profile=_profile(),
        client=FakeClient(),
        limit=5,
    )
    assert isinstance(baseline, RoleBaseline)
    assert baseline.role == "Software Engineer"
    assert baseline.pdf_path
    assert Path_exists(baseline.pdf_path)
    assert len(baseline.skills) > 0
    assert len(baseline.job_ids) == 5

    async with session_scope() as session:
        loaded = await get_role_baseline_by_role(session, "Software Engineer")
    assert loaded is not None
    assert loaded.id == baseline.id


def Path_exists(path: str | None) -> bool:
    from pathlib import Path

    return bool(path) and Path(path).is_file()


def test_build_baseline_resume_data_orders_skills() -> None:
    skill_profile = RoleSkillProfile(
        role="Software Engineer",
        jd_count=3,
        skills=[
            AggregatedSkill(
                name="Python",
                category=SkillCategory.tool,
                prevalence_pct=100,
                avg_importance=5,
                mention_count=3,
            ),
            AggregatedSkill(
                name="SQL",
                category=SkillCategory.hard,
                prevalence_pct=66,
                avg_importance=4,
                mention_count=2,
            ),
        ],
    )
    data = build_baseline_resume_data(_profile(), skill_profile)
    assert data["skills"][0] == "Python"
    assert "SQL" in data["skills"]
    assert data["name"] == "Jane Q. Doe"

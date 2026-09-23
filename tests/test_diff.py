"""Tests for per-JD skill diff and suggestion generation."""

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
    SkillProvenance,
    Source,
    Status,
    SuggestionStatus,
    get_suggestions_for_job,
    session_scope,
    upsert_job,
)
from resume.diff import (
    apply_approved_suggestions_to_resume_data,
    classify_provenance,
    diff_against_baseline,
    generate_suggestions_for_job,
)
from resume.skills import JdSkill, SkillCategory


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
                bullets=["Built Python APIs with FastAPI.", "Designed SQL data models."],
            )
        ],
        skills=["Python", "SQL"],
        preferences=Preferences(
            titles=["Software Engineer"],
            locations=["Seattle, WA"],
            remote_ok=True,
            relocation_ok=False,
        ),
    )


class FakeClient:
    """Return different skills for baseline JDs vs the target posting."""

    def __init__(self) -> None:
        self.calls = 0

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
        self.calls += 1
        # Target posting mentions Kafka/GraphQL; baseline JDs do not.
        if "Kafka" in user or "GraphQL" in user:
            return (
                '[{"name":"Python","category":"tool","importance":5},'
                '{"name":"Kafka","category":"tool","importance":4},'
                '{"name":"GraphQL","category":"tool","importance":3}]'
            )
        return (
            '[{"name":"Python","category":"tool","importance":5},'
            '{"name":"SQL","category":"hard","importance":4},'
            '{"name":"FastAPI","category":"tool","importance":3}]'
        )


def test_classify_provenance_grounded_vs_inferred() -> None:
    profile = _profile()
    assert (
        classify_provenance(
            JdSkill(name="Python", category=SkillCategory.tool, importance=5),
            profile,
        )
        == SkillProvenance.grounded
    )
    assert (
        classify_provenance(
            JdSkill(name="Kafka", category=SkillCategory.tool, importance=4),
            profile,
        )
        == SkillProvenance.inferred
    )


def test_diff_against_baseline_only_missing() -> None:
    baseline = RoleBaseline(
        id=1,
        role="Software Engineer",
        title_terms=["Software Engineer"],
        skills=[{"name": "Python", "prevalence_pct": 100}],
        resume_data={"skills": ["Python", "SQL"]},
        job_ids=[],
    )
    jd_skills = [
        JdSkill(name="Python", category=SkillCategory.tool, importance=5),
        JdSkill(name="Kafka", category=SkillCategory.tool, importance=4),
        JdSkill(name="SQL", category=SkillCategory.hard, importance=4),
    ]
    drafts = diff_against_baseline(baseline, jd_skills, _profile(), job_id=42)
    names = [d["skill"] for d in drafts]
    assert names == ["Kafka"]
    assert drafts[0]["provenance"] == SkillProvenance.inferred


def test_apply_approved_suggestions_to_resume_data() -> None:
    from core.db import SkillPlacement, SkillSuggestion

    data = {"skills": ["Python"], "experience": [{"title": "SE", "bullets": ["Did stuff"]}]}
    sug = SkillSuggestion(
        id=1,
        job_id=1,
        skill="Kafka",
        category="tool",
        placement=SkillPlacement.skills,
        proposed_text="Kafka",
        provenance=SkillProvenance.inferred,
        status=SuggestionStatus.approved,
    )
    out = apply_approved_suggestions_to_resume_data(data, [sug])
    assert "Kafka" in out["skills"]


@pytest.mark.asyncio
async def test_generate_suggestions_for_job(db_ready, tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("BASELINES_DIR", str(tmp_path / "baselines"))
    monkeypatch.setenv("RESUMES_DIR", str(tmp_path / "resumes"))
    from config.settings import get_settings

    get_settings.cache_clear()

    # Seed role JDs (no Kafka) and build baseline before the target posting exists.
    async with session_scope() as session:
        for i in range(4):
            await upsert_job(
                session,
                Job(
                    source=Source.linkedin,
                    external_id=f"se{i}",
                    title="Software Engineer",
                    company=f"Co{i}",
                    url=f"https://example.com/{i}",
                    description_clean="Python SQL backend services FastAPI.",
                    status=Status.discovered,
                ),
            )

    from resume.baseline import build_role_baseline

    await build_role_baseline(
        "Software Engineer",
        title_terms=["Software Engineer"],
        profile=_profile(),
        client=FakeClient(),
        limit=4,
    )

    async with session_scope() as session:
        target = await upsert_job(
            session,
            Job(
                source=Source.linkedin,
                external_id="target",
                title="Software Engineer",
                company="TargetCo",
                url="https://example.com/target",
                description_clean="Need Python, Kafka, and GraphQL experience.",
                status=Status.staged,
            ),
        )
        job_id = target.id
    assert job_id is not None

    suggestions = await generate_suggestions_for_job(
        job_id,
        role="Software Engineer",
        profile=_profile(),
        client=FakeClient(),
    )
    assert all(s.status == SuggestionStatus.pending for s in suggestions)
    # Kafka / GraphQL should be proposed; Python already on baseline/profile
    names = {s.skill.lower() for s in suggestions}
    assert "kafka" in names or "graphql" in names

    async with session_scope() as session:
        loaded = await get_suggestions_for_job(session, job_id)
    assert len(loaded) == len(suggestions)
    report = tmp_path / "resumes" / str(job_id) / "tailoring_report.json"
    assert report.is_file()

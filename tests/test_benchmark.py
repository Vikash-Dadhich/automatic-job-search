"""Tests for peer benchmark comparator."""

from __future__ import annotations

import pytest

from benchmark.engine import build_benchmark, profile_to_peer_data, run_benchmark
from config.profile import (
    Address,
    Education,
    Experience,
    Identity,
    Preferences,
    Profile,
    WorkAuthorization,
)
from core.db import Job, Source, Status, session_scope, upsert_job
from resume.skills import JdSkill, SkillCategory
from scraper.linkedin_people import PeerProfileData


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
                degree="MBA",
                field="Business",
                school="Foster",
                location="Seattle, WA",
                graduation_date="2028-06",
            )
        ],
        experience=[
            Experience(
                title="Software Engineer",
                company="Acme",
                location="Seattle, WA",
                start_date="2022-01",
                end_date="2025-01",
                bullets=["Built Python APIs."],
            )
        ],
        skills=["Python", "SQL", "Kubernetes"],
        preferences=Preferences(
            titles=["Software Engineer"],
            locations=["Seattle, WA"],
            remote_ok=True,
            relocation_ok=False,
        ),
    )


def test_build_benchmark_percentiles() -> None:
    job = Job(
        id=1,
        source=Source.linkedin,
        external_id="b1",
        title="Software Engineer",
        company="Acme",
        url="https://example.com/b1",
        description_clean="Python SQL",
    )
    me = profile_to_peer_data(_profile())
    assert me.seniority in {"junior", "mid", "senior", "staff"}
    # 2022-2025 ≈ 3 years → mid
    assert me.seniority == "mid"
    peers = [
        PeerProfileData(
            url="https://linkedin.com/in/p1",
            years_experience=10,
            skills=["Python"],
            education_level="bachelor",
            seniority="senior",
        ),
        PeerProfileData(
            url="https://linkedin.com/in/p2",
            years_experience=2,
            skills=["Python", "SQL", "Kubernetes", "Kafka"],
            education_level="master",
            seniority="mid",
        ),
    ]
    jd_skills = [
        JdSkill(name="Python", category=SkillCategory.tool, importance=5),
        JdSkill(name="SQL", category=SkillCategory.hard, importance=4),
        JdSkill(name="Kafka", category=SkillCategory.tool, importance=4),
    ]
    report = build_benchmark(job, me, peers, jd_skills)
    assert 0 <= report.overall_score <= 100
    assert report.peer_count == 2
    assert any(d.name == "jd_skill_coverage" for d in report.dimensions)
    assert any("Kafka" in g for g in report.gaps)


@pytest.mark.asyncio
async def test_run_benchmark_persists(db_ready, tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("BENCHMARKS_DIR", str(tmp_path / "benchmarks"))
    from config.settings import get_settings

    get_settings.cache_clear()

    async with session_scope() as session:
        job = await upsert_job(
            session,
            Job(
                source=Source.linkedin,
                external_id="bm1",
                title="Software Engineer",
                company="Acme",
                url="https://example.com/bm1",
                description_clean="Python SQL Kafka",
                status=Status.staged,
            ),
        )
        job_id = job.id
    assert job_id is not None

    peers = [
        PeerProfileData(
            url="https://linkedin.com/in/p1",
            years_experience=8,
            skills=["Python", "SQL"],
            education_level="master",
            seniority="senior",
        )
    ]
    summary = await run_benchmark(
        job_id,
        profile=_profile(),
        peers=peers,
        jd_skills=[
            JdSkill(name="Python", category=SkillCategory.tool, importance=5),
            JdSkill(name="Kafka", category=SkillCategory.tool, importance=4),
        ],
        scrape=False,
    )
    assert summary.report is not None
    assert summary.report_path
    assert Path_exists(summary.report_path)


def Path_exists(path: str | None) -> bool:
    from pathlib import Path

    return bool(path) and Path(path).is_file()

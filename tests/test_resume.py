"""Tests for resume selection, Typst compile, and pikepdf sanitization."""

from __future__ import annotations

import time
from pathlib import Path

import pikepdf
import pytest

from config.profile import (
    Address,
    Education,
    Exclusions,
    Experience,
    Identity,
    Preferences,
    Profile,
    WorkAuthorization,
)
from core.db import Job, Source, Status, session_scope, upsert_job
from resume.compiler import clean_name, compile_pending, compile_resume, sanitize_pdf
from resume.selector import (
    build_resume_data,
    extract_job_terms,
    reorder_skills,
    select_bullets,
)


def _rich_profile() -> Profile:
    """Profile with several verified bullets for selection tests."""
    return Profile(
        identity=Identity(
            full_name="Jane Q. Doe",
            email="jane@example.com",
            phone="+1-555-111-2222",
            location="Seattle, WA",
            linkedin_url="https://www.linkedin.com/in/janedoe",
            github_url="https://github.com/janedoe",
            portfolio_url=None,
            address=Address(
                street="1 Main St",
                city="Seattle",
                state="WA",
                zip="98101",
            ),
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
                field="Computer Science",
                school="Example University",
                location="Seattle, WA",
                graduation_date="2024-05",
                gpa=3.8,
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
                    "Built Python APIs with FastAPI serving 1M requests/day.",
                    "Designed SQL data models and optimized Postgres queries.",
                    "Deployed Kubernetes services with Helm and CI/CD.",
                    "Led stakeholder demos and wrote design docs.",
                    "Mentored two junior engineers on code review.",
                    "Owned on-call rotations for the payments service.",
                ],
            ),
            Experience(
                title="Intern",
                company="Beta Labs",
                location="Remote",
                start_date="2021-06",
                end_date="2021-09",
                bullets=[
                    "Prototyped React dashboards for internal tooling.",
                    "Wrote unit tests covering critical billing paths.",
                ],
            ),
        ],
        skills=["Python", "SQL", "Kubernetes", "FastAPI", "React"],
        preferences=Preferences(
            titles=["Software Engineer"],
            locations=["Remote", "Seattle, WA"],
            remote_ok=True,
            relocation_ok=False,
            dream_companies=[],
        ),
        exclusions=Exclusions(),
    )


def _sample_job(**kwargs) -> Job:
    defaults = {
        "id": 42,
        "source": Source.linkedin,
        "external_id": "resume-job-1",
        "title": "Backend Engineer",
        "company": "GoodCo",
        "location": "Remote",
        "url": "https://example.com/jobs/1",
        "description_clean": (
            "Requirements\n"
            "Strong Python and SQL experience.\n"
            "Kubernetes and cloud services preferred.\n"
            "Responsibilities\n"
            "Build APIs and data pipelines."
        ),
        "status": Status.staged,
    }
    defaults.update(kwargs)
    return Job(**defaults)


def test_clean_name() -> None:
    assert clean_name("Jane Q. Doe") == "Jane_Q_Doe"
    assert clean_name("  Ada  Lovelace  ") == "Ada_Lovelace"
    assert clean_name("") == "Resume"
    assert clean_name("O'Brien") == "OBrien"


def test_extract_job_terms_and_selection() -> None:
    profile = _rich_profile()
    job = _sample_job()
    terms = extract_job_terms(job)
    assert "python" in terms
    assert "sql" in terms
    assert "kubernetes" in terms

    selected = select_bullets(profile, job, min_n=4, max_n=6)
    bullets = [b for exp in selected for b in exp.bullets]
    available = sum(len(e.bullets) for e in profile.experience)
    assert min(4, available) <= len(bullets) <= 6
    # Top matches should prefer Python/SQL/K8s bullets
    joined = " ".join(bullets).lower()
    assert "python" in joined or "sql" in joined

    skills = reorder_skills(profile, terms)
    assert skills[0] in {"Python", "SQL", "Kubernetes", "FastAPI"}
    assert set(skills) == set(profile.skills)


def test_select_bullets_caps_when_sparse() -> None:
    profile = _rich_profile()
    # Tiny JD with no overlapping tech terms
    job = _sample_job(
        title="Office Manager",
        description_clean="Schedule meetings and order supplies.",
    )
    selected = select_bullets(profile, job, min_n=4, max_n=6)
    bullets = [b for exp in selected for b in exp.bullets]
    assert len(bullets) == 4  # padded to min_n from available


def test_build_resume_data_shape() -> None:
    data = build_resume_data(_rich_profile(), _sample_job())
    assert data["name"] == "Jane Q. Doe"
    assert "Python" in data["skills"]
    assert data["experience"]
    assert data["education"][0]["degree"] == "M.S."
    assert data["summary"]


def test_compile_resume_and_sanitize(tmp_path: Path) -> None:
    profile = _rich_profile()
    job = _sample_job(id=7)
    started = time.perf_counter()
    path = compile_resume(profile, job, out_dir=tmp_path)
    elapsed = time.perf_counter() - started

    assert path.exists()
    assert path.name == "Jane_Q_Doe_Resume.pdf"
    assert path.parent.name == "7"
    raw = path.read_bytes()
    assert raw.startswith(b"%PDF")
    assert len(raw) > 500
    assert elapsed < 5.0

    with pikepdf.open(path) as pdf:
        producer = str(pdf.docinfo.get("/Producer", ""))
        creator = str(pdf.docinfo.get("/Creator", ""))
        assert "Microsoft" in producer or "Print To PDF" in producer
        assert "Microsoft Word" in creator or "Word" in creator
        assert "/Author" not in pdf.docinfo


def test_sanitize_pdf_idempotent(tmp_path: Path) -> None:
    profile = _rich_profile()
    path = compile_resume(profile, _sample_job(id=9), out_dir=tmp_path)
    sanitize_pdf(path)
    with pikepdf.open(path) as pdf:
        assert "/Author" not in pdf.docinfo


async def test_compile_pending_skips_existing(
    db_ready: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Point resumes_dir at tmp so DB writes don't touch real storage
    monkeypatch.setenv("RESUMES_DIR", str(tmp_path / "resumes"))
    from config.settings import get_settings

    get_settings.cache_clear()

    async with session_scope() as session:
        await upsert_job(
            session,
            Job(
                source=Source.linkedin,
                external_id="staged-1",
                title="Backend Engineer",
                company="GoodCo",
                location="Remote",
                url="https://example.com/1",
                description_clean="Requirements\nPython and SQL.",
                status=Status.staged,
            ),
        )
        await upsert_job(
            session,
            Job(
                source=Source.linkedin,
                external_id="staged-2",
                title="Data Engineer",
                company="DataCo",
                location="Remote",
                url="https://example.com/2",
                description_clean="Requirements\nSQL and Python pipelines.",
                status=Status.staged,
            ),
        )

    profile = _rich_profile()
    first = await compile_pending(profile=profile, out_dir=tmp_path / "resumes")
    assert first.generated == 2
    assert first.errors == 0
    assert first.skipped == 0

    async with session_scope() as session:
        from core.db import get_job_by_source_id

        j1 = await get_job_by_source_id(session, Source.linkedin, "staged-1")
        j2 = await get_job_by_source_id(session, Source.linkedin, "staged-2")
        assert j1 is not None and j1.resume_path
        assert j2 is not None and j2.resume_path
        assert Path(j1.resume_path).exists()
        assert Path(j2.resume_path).exists()

    second = await compile_pending(profile=profile, out_dir=tmp_path / "resumes")
    assert second.skipped == 2
    assert second.generated == 0

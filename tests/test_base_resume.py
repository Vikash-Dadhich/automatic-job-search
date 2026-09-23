"""Tests for static base resume preparation and on-demand Typst tailoring."""

from __future__ import annotations

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
from config.settings import get_settings
from core.db import Job, Source, Status, get_job_by_id, session_scope, upsert_job
from resume.compiler import (
    _DEFAULT_CREATOR,
    _DEFAULT_PRODUCER,
    compile_for_job,
    compile_resume,
    prepare_base_resume,
    prepare_pending,
)


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
                bullets=["Built Python APIs with FastAPI."],
            )
        ],
        skills=["Python", "SQL"],
        preferences=Preferences(
            titles=["Software Engineer"],
            locations=["Remote"],
            remote_ok=True,
            relocation_ok=False,
            dream_companies=[],
        ),
        exclusions=Exclusions(),
    )


def _sample_job(**kwargs) -> Job:
    defaults = {
        "id": 77,
        "source": Source.workday,
        "external_id": "base-resume-job",
        "title": "Backend Engineer",
        "company": "GoodCo",
        "location": "Remote",
        "url": "https://example.com/jobs/1",
        "description_clean": "Python and SQL required.",
        "status": Status.staged,
    }
    defaults.update(kwargs)
    return Job(**defaults)


def _make_base_pdf(tmp_path: Path, profile: Profile) -> Path:
    """Create a valid PDF via Typst to stand in for the user's base resume."""
    source_job = _sample_job(id=1, external_id="seed-pdf")
    compiled = compile_resume(profile, source_job, out_dir=tmp_path / "seed")
    base = tmp_path / "base_resume.pdf"
    base.write_bytes(compiled.read_bytes())
    # Dirty metadata so sanitize_pdf has something to overwrite
    with pikepdf.open(base, allow_overwriting_input=True) as pdf:
        info = pdf.docinfo
        info["/Creator"] = "SecretTool"
        info["/Author"] = "ShouldBeRemoved"
        pdf.save(base)
    return base


def test_prepare_base_resume_copies_and_sanitizes(tmp_path: Path) -> None:
    profile = _profile()
    base = _make_base_pdf(tmp_path, profile)
    job = _sample_job(id=42)
    out = prepare_base_resume(
        profile,
        job,
        out_dir=tmp_path / "resumes",
        base_resume=base,
    )
    assert out.is_file()
    assert out.name == "Jane_Q_Doe_Resume.pdf"
    assert out != base
    with pikepdf.open(out) as pdf:
        assert str(pdf.docinfo.get("/Creator")) == _DEFAULT_CREATOR
        assert str(pdf.docinfo.get("/Producer")) == _DEFAULT_PRODUCER
        assert "/Author" not in pdf.docinfo


def test_prepare_base_resume_missing_file(tmp_path: Path) -> None:
    profile = _profile()
    with pytest.raises(FileNotFoundError, match="Base resume not found"):
        prepare_base_resume(
            profile,
            _sample_job(),
            out_dir=tmp_path,
            base_resume=tmp_path / "missing.pdf",
        )


async def test_prepare_pending_sets_resume_path(
    db_ready: Path,
    tmp_path: Path,
) -> None:
    profile = _profile()
    base = _make_base_pdf(tmp_path, profile)

    async with session_scope() as session:
        job = await upsert_job(
            session,
            Job(
                source=Source.workday,
                external_id="prep-1",
                title="Engineer",
                company="Co",
                location="Remote",
                url="https://example.com/1",
                description_clean="Python",
                status=Status.staged,
            ),
        )
        job_id = job.id
    assert job_id is not None

    summary = await prepare_pending(
        profile=profile,
        out_dir=tmp_path / "resumes",
        base_resume=base,
    )
    assert summary.generated == 1
    assert summary.errors == 0

    async with session_scope() as session:
        target = await get_job_by_id(session, job_id)
        assert target is not None
        assert target.resume_path
        assert Path(target.resume_path).is_file()

    # Second call skips existing
    summary2 = await prepare_pending(
        profile=profile,
        out_dir=tmp_path / "resumes",
        base_resume=base,
    )
    assert summary2.skipped == 1
    assert summary2.generated == 0

    # Force re-prepares
    summary3 = await prepare_pending(
        profile=profile,
        force=True,
        out_dir=tmp_path / "resumes",
        base_resume=base,
    )
    assert summary3.generated == 1


async def test_prepare_pending_missing_base_no_crash(
    db_ready: Path,
    tmp_path: Path,
) -> None:
    profile = _profile()
    async with session_scope() as session:
        await upsert_job(
            session,
            Job(
                source=Source.workday,
                external_id="prep-missing",
                title="Engineer",
                company="Co",
                location="Remote",
                url="https://example.com/2",
                description_clean="Python",
                status=Status.staged,
            ),
        )

    summary = await prepare_pending(
        profile=profile,
        out_dir=tmp_path / "resumes",
        base_resume=tmp_path / "nope.pdf",
    )
    assert summary.generated == 0
    assert summary.errors == 1
    assert "base resume" in summary.error_details[0].lower()


async def test_compile_for_job_overwrites(
    db_ready: Path,
    tmp_path: Path,
) -> None:
    profile = _profile()
    base = _make_base_pdf(tmp_path, profile)

    async with session_scope() as session:
        job = await upsert_job(
            session,
            Job(
                source=Source.linkedin,
                external_id="tailor-1",
                title="Backend Engineer",
                company="GoodCo",
                location="Remote",
                url="https://example.com/3",
                description_clean="Python and SQL required.",
                status=Status.staged,
            ),
        )
        job_id = job.id
    assert job_id is not None

    await prepare_pending(
        profile=profile,
        out_dir=tmp_path / "resumes",
        base_resume=base,
    )
    tailored = await compile_for_job(
        job_id,
        profile=profile,
        out_dir=tmp_path / "resumes",
    )
    assert tailored.is_file()

    async with session_scope() as session:
        target = await get_job_by_id(session, job_id)
        assert target is not None
        assert target.resume_path == str(tailored)


def test_base_resume_file_property() -> None:
    settings = get_settings()
    assert settings.base_resume_file.name == "base_resume.pdf"
    assert "config" in str(settings.base_resume_file)

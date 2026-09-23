"""Offline tests for apply_pending with FakeApplicator (no browser)."""

from __future__ import annotations

from pathlib import Path

from automation.runner import apply_pending
from automation.workday import ApplyResult, BlockerError
from core.db import Job, Source, Status, get_job_by_id, session_scope, upsert_job


class FakeApplicator:
    def __init__(self, *, mode: str = "ok") -> None:
        self.mode = mode
        self.calls: list[int | None] = []

    async def apply(self, job: Job) -> ApplyResult:
        self.calls.append(job.id)
        if self.mode == "blocker":
            raise BlockerError("cloudflare", screenshot_path="/tmp/blocker.png")
        if self.mode == "error":
            raise RuntimeError("boom")
        return ApplyResult(
            screenshot_path="/tmp/review.png",
            application_answers={
                "items": [{"question": "Email", "answer": "a@b.com", "source": "deterministic"}],
                "count": 1,
            },
            reached_review=True,
        )


async def _seed_job(
    *,
    source: Source = Source.workday,
    status: Status = Status.staged,
    resume_path: str | None = "/tmp/resume.pdf",
    external_id: str = "wd-apply-1",
    url: str | None = None,
) -> Job:
    default_url = (
        "https://www.linkedin.com/jobs/view/123"
        if source == Source.linkedin
        else "https://acme.wd5.myworkdayjobs.com/en-US/External/job/City/Title_R1"
    )
    job = Job(
        source=source,
        external_id=external_id,
        title="Software Engineer",
        company="Acme",
        url=url or default_url,
        tenant="acme" if source == Source.workday else None,
        status=status,
        resume_path=resume_path,
    )
    async with session_scope() as session:
        return await upsert_job(session, job)


async def test_apply_pending_success(db_ready: Path) -> None:
    job = await _seed_job()
    fake = FakeApplicator(mode="ok")
    summary = await apply_pending(applicator=fake, limit=10)

    assert summary.applied == 1
    assert summary.pending_review == 1
    assert summary.manual_review == 0
    assert summary.errors == 0
    assert fake.calls == [job.id]

    async with session_scope() as session:
        assert job.id is not None
        refreshed = await get_job_by_id(session, job.id)
        assert refreshed is not None
        assert refreshed.status == Status.pending_review
        assert refreshed.screenshot_path == "/tmp/review.png"
        assert refreshed.application_answers is not None
        assert refreshed.application_answers["count"] == 1


async def test_apply_pending_blocker(db_ready: Path) -> None:
    job = await _seed_job(external_id="wd-blocker")
    fake = FakeApplicator(mode="blocker")
    summary = await apply_pending(applicator=fake)

    assert summary.manual_review == 1
    assert summary.pending_review == 0
    async with session_scope() as session:
        assert job.id is not None
        refreshed = await get_job_by_id(session, job.id)
        assert refreshed is not None
        assert refreshed.status == Status.manual_review
        assert refreshed.screenshot_path == "/tmp/blocker.png"
        assert refreshed.last_error is not None
        assert "cloudflare" in refreshed.last_error
        assert refreshed.alerted_at is None


async def test_apply_pending_error(db_ready: Path) -> None:
    job = await _seed_job(external_id="wd-err")
    fake = FakeApplicator(mode="error")
    summary = await apply_pending(applicator=fake)

    assert summary.errors == 1
    assert summary.error_details
    async with session_scope() as session:
        assert job.id is not None
        refreshed = await get_job_by_id(session, job.id)
        assert refreshed is not None
        assert refreshed.status == Status.error
        assert refreshed.last_error == "boom"

async def test_apply_skips_non_workday_and_missing_resume(db_ready: Path) -> None:
    await _seed_job(
        source=Source.linkedin,
        external_id="li-1",
        resume_path="/tmp/r.pdf",
    )
    await _seed_job(
        source=Source.workday,
        external_id="wd-no-resume",
        resume_path=None,
    )
    fake = FakeApplicator()
    summary = await apply_pending(applicator=fake)

    assert summary.skipped == 2
    assert summary.applied == 0
    assert fake.calls == []


async def test_apply_linkedin_with_workday_url(db_ready: Path) -> None:
    """LinkedIn-discovered roles that apply on Workday must be eligible."""
    job = Job(
        source=Source.linkedin,
        external_id="li-wd-1",
        title="Product Manager",
        company="Meijer",
        url=(
            "https://meijer.wd5.myworkdayjobs.com/Meijer/job/"
            "Grand-Rapids-MI/Product-Owner_R123"
        ),
        tenant=None,
        status=Status.staged,
        resume_path="/tmp/resume.pdf",
    )
    async with session_scope() as session:
        job = await upsert_job(session, job)

    fake = FakeApplicator(mode="ok")
    summary = await apply_pending(applicator=fake, limit=10)

    assert summary.applied == 1
    assert summary.skipped == 0
    assert fake.calls == [job.id]

    async with session_scope() as session:
        assert job.id is not None
        refreshed = await get_job_by_id(session, job.id)
        assert refreshed is not None
        assert refreshed.status == Status.pending_review
        assert refreshed.tenant == "meijer"


async def test_apply_pending_empty(db_ready: Path) -> None:
    summary = await apply_pending(applicator=FakeApplicator())
    assert summary.applied == 0
    assert summary.skipped == 0

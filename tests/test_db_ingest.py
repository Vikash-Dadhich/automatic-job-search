"""Async tests for Job mapping, upsert idempotency, and ingest noop."""

from __future__ import annotations

from pathlib import Path

from core.db import Source, Status, get_job_by_source_id, session_scope, upsert_job
from scraper.ingest import run_ingestion
from scraper.models import RawPosting, to_job
from scraper.textclean import content_hash


def _posting(**kwargs) -> RawPosting:
    defaults = {
        "source": Source.linkedin,
        "external_id": "job-100",
        "title": "Software Engineer",
        "company": "GoodCo",
        "location": "Remote",
        "url": "https://example.com/jobs/100",
        "description_clean": "Requirements\nPython and SQL experience.",
    }
    defaults.update(kwargs)
    return RawPosting(**defaults)


async def test_to_job_maps_fields_and_hash(db_ready: Path) -> None:
    posting = _posting()
    job = to_job(posting, status=Status.discovered)
    assert job.source == Source.linkedin
    assert job.external_id == "job-100"
    assert job.title == "Software Engineer"
    assert job.status == Status.discovered
    assert job.content_hash == content_hash(posting.description_clean or "")
    assert job.description_clean is not None


async def test_upsert_idempotent_and_status_refresh(db_ready: Path) -> None:
    posting = _posting()
    async with session_scope() as session:
        first = await upsert_job(session, to_job(posting, status=Status.discovered))
        assert first.id is not None
        first_id = first.id

        updated = await upsert_job(
            session,
            to_job(
                _posting(title="Software Engineer II"),
                status=Status.discovered,
            ),
        )
        assert updated.id == first_id
        assert updated.title == "Software Engineer II"

        filtered = await upsert_job(
            session,
            to_job(
                _posting(title="Software Engineer II"),
                status=Status.filtered_out,
                justification=["excluded keyword: test"],
            ),
        )
        assert filtered.id == first_id
        assert filtered.status == Status.filtered_out
        assert filtered.justification == ["excluded keyword: test"]

        again = await get_job_by_source_id(session, Source.linkedin, "job-100")
        assert again is not None
        assert again.status == Status.filtered_out


async def test_run_ingestion_noop(db_ready: Path) -> None:
    summary = await run_ingestion(include_jobspy=False, include_workday=False)
    assert summary.fetched == 0
    assert summary.discovered == 0
    assert summary.filtered_out == 0
    assert summary.upserted == 0
    assert summary.errors == []

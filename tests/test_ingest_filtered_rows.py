"""Hard-filtered rows are saved, but they are not enriched."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from config.profile import load_profile
from core.db import Source, Status, get_job_by_source_id, session_scope
from scraper.ingest import run_ingestion
from scraper.models import RawPosting

_DESCRIPTION = (
    "A summer product internship. You will work with engineering and design "
    "to shape the roadmap, run customer interviews, and present a final project."
)


def _posting(external_id: str, company: str) -> RawPosting:
    return RawPosting(
        source=Source.linkedin,
        external_id=external_id,
        title="Product Manager Intern",
        company=company,
        location="Remote",
        url=f"https://example.com/{external_id}",
        description_clean=_DESCRIPTION,
    )


async def test_filtered_rows_skip_enrichment(
    db_ready: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    profile = load_profile()
    blocked_profile = profile.model_copy(
        update={
            "exclusions": profile.exclusions.model_copy(update={"companies": ["Blockedco"]}),
        }
    )
    postings = [_posting("blocked", "Blockedco"), _posting("open", "Openco")]
    enriched: dict[str, list[str]] = {
        "company": [],
        "eligibility": [],
        "structured": [],
        "role": [],
    }

    async def fetch(*_args: object, **_kwargs: object) -> list[RawPosting]:
        return postings

    async def company(_session: Any, job: Any, **_kwargs: object) -> None:
        enriched["company"].append(job.external_id)

    async def eligibility(job: Any, _profile: Any, **_kwargs: object) -> None:
        enriched["eligibility"].append(job.external_id)

    async def structured(_session: Any, job: Any) -> None:
        enriched["structured"].append(job.external_id)

    async def role(_session: Any, job: Any, _client: Any) -> None:
        enriched["role"].append(job.external_id)

    monkeypatch.setattr("scraper.ingest.fetch_linkedin_indeed", fetch)
    monkeypatch.setattr("scraper.ingest.attach_company_intelligence", company)
    monkeypatch.setattr("scraper.ingest.attach_eligibility", eligibility)
    monkeypatch.setattr("scraper.ingest.attach_structured_jd", structured)
    monkeypatch.setattr("scraper.ingest._apply_role_classification", role)

    summary = await run_ingestion(profile=blocked_profile, include_workday=False)

    assert summary.errors == []
    assert summary.upserted == 2
    assert summary.filtered_out == 1
    for name, ids in enriched.items():
        assert ids == ["open"], name
    async with session_scope() as session:
        blocked = await get_job_by_source_id(session, Source.linkedin, "blocked")
        opened = await get_job_by_source_id(session, Source.linkedin, "open")
    assert blocked is not None
    assert blocked.status == Status.filtered_out
    assert opened is not None
    assert opened.status == Status.discovered

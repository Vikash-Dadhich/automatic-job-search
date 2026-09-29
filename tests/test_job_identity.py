"""One posting, one job. Uncertain matches stay separate."""

from __future__ import annotations

from pathlib import Path

from core.db import (
    CompanyIntelligence,
    Source,
    Status,
    get_job_by_source_id,
    session_scope,
    upsert_job,
)
from core.job_identity import canonicalize_job_url, same_posting_url
from scraper.models import RawPosting, to_job

_DESC = "Own the product roadmap and write requirements for this internship. " * 3


def _posting(
    *,
    source: Source = Source.linkedin,
    external_id: str = "post-1",
    company: str = "Acme",
    title: str = "Product Manager Intern",
    location: str | None = "Seattle, WA",
    url: str = "https://jobs.example.com/postings/99",
    description: str | None = _DESC,
    query: str = "product manager intern",
    family: str = "PRODUCT_MANAGEMENT",
) -> RawPosting:
    return RawPosting(
        source=source,
        external_id=external_id,
        title=title,
        company=company,
        location=location,
        url=url,
        description_clean=description,
        discovery_family=family,
        discovery_bucket="primary",
        discovery_query=query,
    )


def test_url_canonicalization_drops_tracking_and_keeps_posting_ids() -> None:
    linkedin = canonicalize_job_url(
        "https://jobs.example.com/postings/99?utm_source=linkedin&utm_medium=cpc#apply"
    )
    indeed = canonicalize_job_url("https://jobs.example.com/postings/99?utm_source=indeed")
    assert linkedin == indeed
    assert same_posting_url(
        "https://jobs.example.com/postings/99?utm_source=linkedin",
        "https://JOBS.example.com/postings/99/?ref=email",
    )
    first = canonicalize_job_url("https://example.com/jobs?id=123")
    second = canonicalize_job_url("https://example.com/jobs?id=456&utm_source=linkedin")
    assert first != second
    assert canonicalize_job_url("https://example.com/") != canonicalize_job_url(
        "https://example.com/job/1"
    )
    assert same_posting_url("https://example.com/", "https://example.com/?utm_source=x") is False


async def test_same_source_identity_and_cross_source_url(db_ready: Path) -> None:
    del db_ready
    async with session_scope() as session:
        employer = CompanyIntelligence(
            lookup_key="acme-identity-test",
            company_name="Acme",
            canonical_name="Acme",
            sources=[],
        )
        session.add(employer)
        await session.flush()
        first = await upsert_job(session, to_job(_posting(), status=Status.staged))
        first.score = 88
        first.fit_version = "phase6-v2"
        first.eligibility_state = "LIKELY_ELIGIBLE"
        first.role_family = "PRODUCT_MANAGEMENT"
        first.company_intelligence_id = employer.id
        first.vector_score = 0.4
        again = await upsert_job(
            session,
            to_job(
                _posting(query="mba summer associate", family="CONSULTING"),
                status=Status.discovered,
            ),
        )
        other_id = await upsert_job(
            session,
            to_job(_posting(external_id="post-2", url="https://jobs.example.com/postings/100")),
        )
        cross = await upsert_job(
            session,
            to_job(
                _posting(
                    source=Source.indeed,
                    external_id="indeed-99",
                    url="https://jobs.example.com/postings/99?utm_source=indeed",
                    location=None,
                    query="strategy intern",
                    family="STRATEGY_TRANSFORMATION",
                )
            ),
        )
        assert again.id == first.id
        assert again.discovery_family == "PRODUCT_MANAGEMENT"
        assert again.discovery_bucket == "primary"
        assert again.discovery_query == "product manager intern"
        assert again.score == 88
        assert again.fit_version == "phase6-v2"
        assert again.eligibility_state == "LIKELY_ELIGIBLE"
        assert again.role_family == "PRODUCT_MANAGEMENT"
        assert again.company_intelligence_id == employer.id
        assert again.vector_score == 0.4
        assert again.source == Source.linkedin
        assert again.external_id == "post-1"
        assert other_id.id != first.id
        assert cross.id == first.id
        linkedin = await get_job_by_source_id(session, Source.linkedin, "post-1")
        indeed = await get_job_by_source_id(session, Source.indeed, "indeed-99")
        assert linkedin is not None and linkedin.id == first.id
        assert indeed is None


async def test_weak_similarity_does_not_merge(db_ready: Path) -> None:
    del db_ready
    async with session_scope() as session:
        seattle = await upsert_job(session, to_job(_posting(external_id="sea")))
        nyc = await upsert_job(
            session,
            to_job(
                _posting(
                    source=Source.indeed,
                    external_id="nyc",
                    location="New York, NY",
                    url="https://jobs.example.com/postings/nyc",
                )
            ),
        )
        ambiguous = await upsert_job(
            session,
            to_job(
                _posting(
                    source=Source.indeed,
                    external_id="amb",
                    location=None,
                    url="https://other.example.com/req/amb",
                    description="A different internship description about finance modeling. " * 3,
                )
            ),
        )
        different_text = await upsert_job(
            session,
            to_job(
                _posting(
                    source=Source.workday,
                    external_id="wd",
                    location="Seattle, WA",
                    url="https://jobs.example.com/postings/other-text",
                    description="Support a separate requisition for a hardware internship. " * 3,
                )
            ),
        )
    assert len({seattle.id, nyc.id, ambiguous.id, different_text.id}) == 4
    async with session_scope() as session:
        google = await upsert_job(
            session,
            to_job(_posting(external_id="brand-a", company="Google", url="https://jobs.example.com/shared")),
        )
        other = await upsert_job(
            session,
            to_job(
                _posting(
                    source=Source.indeed,
                    external_id="brand-b",
                    company="Unknown Startup",
                    url="https://jobs.example.com/shared?utm_source=indeed",
                )
            ),
        )
    assert google.id != other.id


async def test_same_place_and_text_can_merge_without_using_fit(db_ready: Path) -> None:
    del db_ready
    async with session_scope() as session:
        first = await upsert_job(
            session,
            to_job(
                _posting(
                    external_id="field-1",
                    url="https://boards.example.com/listing",
                )
            ),
        )
        first.score = 10
        first.role_family = "OTHER"
        first.vector_score = 0.99
        second = await upsert_job(
            session,
            to_job(
                _posting(
                    source=Source.indeed,
                    external_id="field-2",
                    url="https://boards.example.com/",
                    company="Acme, Inc.",
                    title="product manager intern",
                )
            ),
        )
    assert second.id == first.id
    assert second.score == 10
    assert second.external_id == "field-1"


async def test_material_description_change_still_clears_fit(db_ready: Path) -> None:
    del db_ready
    async with session_scope() as session:
        saved = await upsert_job(session, to_job(_posting(), status=Status.staged))
        saved.score = 70
        saved.fit_version = "phase6-v2"
        changed = await upsert_job(
            session,
            to_job(
                _posting(
                    description=_DESC + " The employer added a new on-call requirement.",
                ),
                status=Status.discovered,
            ),
        )
    assert changed.id == saved.id
    assert changed.score is None
    assert changed.fit_version is None

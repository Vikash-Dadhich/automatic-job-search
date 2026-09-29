"""Phase 8 company facts. They do not change fit, weight, tier, status, or discovery."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import httpx

from core.db import (
    Job,
    Source,
    Status,
    Tier,
    get_recently_applied_companies,
    session_scope,
    upsert_job,
)
from scorer.company_intelligence import (
    INTELLIGENCE_VERSION,
    CompanyLookupResult,
    CompanySourceDocument,
    HttpCompanyIntelProvider,
    attach_company_intelligence,
    canonical_company_name,
    extract_company_facts,
    normalize_company_name,
    resolve_company,
)
from scorer.engine import compute_tier, is_dream_company
from scorer.role_weights import get_role_family_weight
from scraper.discovery import load_discovery
from scraper.models import RawPosting, to_job

ACME_TEXT = "Acme is a publicly traded software company headquartered in Seattle."
FULL_TEXT = (
    "Acme is a publicly traded software company headquartered in Seattle. "
    "Approximately 5,000 employees. Founded in 2008. Subsidiary of Northwind. "
    "Acme describes itself as providing inventory software."
)
RETRIEVED = datetime(2026, 9, 29, 16, 0, tzinfo=UTC)


class FakeProvider:
    def __init__(self, text: str = ACME_TEXT, *, error: str | None = None) -> None:
        self.text = text
        self.error = error
        self.calls = 0
        self.claimed: dict[str, object] | None = None
        self.raise_exc: Exception | None = None

    async def lookup(
        self,
        company_name: str,
        source_url: str,
        source_type: str = "official_website",
    ) -> CompanyLookupResult:
        del company_name
        self.calls += 1
        if self.raise_exc is not None:
            raise self.raise_exc
        if self.error:
            return CompanyLookupResult(error=self.error)
        return CompanyLookupResult(
            document=CompanySourceDocument(
                source_type=source_type,
                url=source_url,
                text=self.text,
                retrieved_at=RETRIEVED,
            ),
            claimed=self.claimed,
        )


def test_normalization_is_deterministic() -> None:
    assert normalize_company_name("  Acme,   Inc. ") == normalize_company_name("Acme Inc")
    assert normalize_company_name("ACME INC") == "acme"
    assert canonical_company_name("Acme, Inc.") == "Acme"


def test_legal_suffixes_do_not_collapse_distinct_names() -> None:
    assert normalize_company_name("Acme, Inc.") == "acme"
    assert normalize_company_name("Acme Inc") == "acme"
    assert normalize_company_name("  ACME, LLC ") == "acme"
    assert normalize_company_name("Acme LLC") == "acme"
    assert normalize_company_name("Mercury") == "mercury"
    assert normalize_company_name("Mercury Systems") == "mercury systems"
    assert normalize_company_name("Mercury Insurance") == "mercury insurance"
    assert normalize_company_name("Mercury") != normalize_company_name("Mercury Systems")
    assert normalize_company_name("Mercury Systems") != normalize_company_name(
        "Mercury Insurance"
    )
    assert normalize_company_name("AT&T") == "at&t"
    assert normalize_company_name("Johnson & Johnson") == "johnson & johnson"
    assert normalize_company_name("A.B. Corp") == "a.b."


def test_extractor_keeps_unstated_facts_null() -> None:
    facts = extract_company_facts(ACME_TEXT)
    assert facts["public_private"] == "public"
    assert facts["industry"] == "software"
    assert facts["headquarters"] == "Seattle"
    assert facts["employee_range"] is None
    assert facts["founded_year"] is None
    assert facts["parent_company"] is None
    assert facts["company_type"] is None


def test_prestige_language_is_not_a_fact() -> None:
    facts = extract_company_facts(
        "Acme is a prestigious top-tier employer with a great culture."
    )
    assert all(value is None for value in facts.values())


def _posting(external_id: str, company: str) -> RawPosting:
    return RawPosting(
        source=Source.linkedin,
        external_id=external_id,
        title="Product Manager Intern",
        company=company,
        location="Seattle, WA",
        url=f"https://example.com/jobs/{external_id}",
        description_clean="Requirements\nOwn a product roadmap for an internship. " * 3,
        discovery_family="CONSULTING",
        discovery_bucket="STRATEGY_CONSULTING",
        discovery_query="management consultant intern",
    )


def _job(
    external_id: str,
    company: str,
    *,
    score: int,
    role_family: str,
    source: Source = Source.linkedin,
) -> Job:
    job = to_job(_posting(external_id, company), status=Status.staged)
    job.source = source
    job.score = score
    job.tier = Tier.one
    job.role_family = role_family
    job.role_family_weight = get_role_family_weight(role_family)
    job.vector_score = 0.42
    job.fit_version = "phase6-v1"
    job.fit_content_hash = "abc"
    return job


async def test_source_grounded_partial_record(db_ready: Path) -> None:
    provider = FakeProvider()
    async with session_scope() as session:
        record = await resolve_company(
            session,
            "Acme, Inc.",
            source_url="https://acme.example/about",
            source_type="official_website",
            provider=provider,
        )
    assert record.public_private == "public"
    assert record.industry == "software"
    assert record.headquarters == "Seattle"
    assert record.employee_range is None
    assert record.founded_year is None
    assert record.parent_company is None
    assert record.business_description is None
    assert record.status == "partial"
    assert record.confidence == "medium"
    assert record.intelligence_version == INTELLIGENCE_VERSION
    assert record.retrieved_at is not None
    assert record.website == "https://acme.example/about"
    assert record.sources == [
        {
            "source_type": "official_website",
            "url": "https://acme.example/about",
            "retrieved_at": RETRIEVED.isoformat(),
        }
    ]
    assert "score" not in type(record).model_fields
    assert "visa_eligible" not in type(record).model_fields


async def test_complete_record_and_ignored_claims(db_ready: Path) -> None:
    provider = FakeProvider(FULL_TEXT)
    provider.claimed = {"employee_range": "900000 employees", "industry": "banking"}
    async with session_scope() as session:
        record = await resolve_company(
            session,
            "Acme Inc",
            source_url="https://acme.example/about",
            provider=provider,
        )
    assert record.status == "complete"
    assert record.confidence == "high"
    assert record.founded_year == 2008
    assert record.parent_company == "Northwind"
    assert record.company_type == "subsidiary"
    assert record.employee_range is not None
    assert "5,000" in record.employee_range
    assert "900000" not in record.employee_range
    assert record.industry == "software"


async def test_unknown_without_a_source_stays_null(db_ready: Path) -> None:
    provider = FakeProvider()
    async with session_scope() as session:
        record = await resolve_company(session, "Acme", provider=provider)
    assert provider.calls == 0
    assert record.status == "unresolved"
    assert record.confidence == "low"
    assert record.website is None
    assert record.industry is None
    assert record.public_private is None
    assert record.headquarters is None
    assert record.sources == []
    assert record.intelligence_version == INTELLIGENCE_VERSION


async def test_ambiguous_names_stay_separate(db_ready: Path) -> None:
    async with session_scope() as session:
        mercury = await resolve_company(session, "Mercury")
        systems = await resolve_company(session, "Mercury Systems")
        insurance = await resolve_company(session, "Mercury Insurance")
    assert len({mercury.id, systems.id, insurance.id}) == 3
    assert mercury.lookup_key != systems.lookup_key != insurance.lookup_key


async def test_same_company_is_reused_without_merging_jobs(db_ready: Path) -> None:
    provider = FakeProvider()
    async with session_scope() as session:
        first = await upsert_job(
            session,
            _job("job-1", "Acme, Inc.", score=90, role_family="PRODUCT_MANAGEMENT"),
        )
        second = await upsert_job(
            session,
            _job(
                "job-2",
                "Acme Inc",
                score=60,
                role_family="CONSULTING",
                source=Source.indeed,
            ),
        )
        await attach_company_intelligence(
            session,
            first,
            source_url="https://acme.example/about",
            provider=provider,
        )
        await attach_company_intelligence(
            session,
            second,
            source_url="https://acme.example/about",
            provider=provider,
        )
    assert provider.calls == 1
    assert first.company_intelligence_id == second.company_intelligence_id
    assert first.id != second.id
    assert first.external_id == "job-1"
    assert second.external_id == "job-2"
    assert first.source == Source.linkedin
    assert second.source == Source.indeed
    assert first.score == 90
    assert second.score == 60
    assert first.role_family_weight == 40
    assert second.role_family_weight == 40
    assert get_role_family_weight("PRODUCT_MANAGEMENT") == 40
    assert get_role_family_weight("CONSULTING") == 40


async def test_explicit_refresh_calls_the_provider_again(db_ready: Path) -> None:
    provider = FakeProvider()
    async with session_scope() as session:
        job = await upsert_job(
            session,
            _job("refresh-1", "Acme", score=90, role_family="PRODUCT_MANAGEMENT"),
        )
        await attach_company_intelligence(
            session,
            job,
            source_url="https://acme.example/about",
            provider=provider,
        )
        await attach_company_intelligence(
            session,
            job,
            source_url="https://acme.example/about",
            provider=provider,
            refresh=True,
        )
    assert provider.calls == 2
    assert job.score == 90
    assert job.fit_version == "phase6-v1"
    assert job.fit_content_hash == "abc"
    assert job.role_family_weight == 40
    assert job.tier == Tier.one
    assert job.status == Status.staged


async def test_provider_failures_do_not_change_the_job(db_ready: Path) -> None:
    timeout = FakeProvider()
    timeout.raise_exc = TimeoutError("slow")
    malformed = FakeProvider(error="malformed")
    async with session_scope() as session:
        job = await upsert_job(
            session,
            _job("fail-1", "Acme", score=90, role_family="STRATEGY_TRANSFORMATION"),
        )
        failed = await attach_company_intelligence(
            session,
            job,
            source_url="https://acme.example/about",
            provider=timeout,
        )
        assert failed.status == "failed"
        assert failed.industry is None
        again = await attach_company_intelligence(
            session,
            job,
            source_url="https://acme.example/about",
            provider=malformed,
            refresh=True,
        )
    assert again.status == "failed"
    assert job.score == 90
    assert job.role_family_weight == 15
    assert job.tier == Tier.one
    assert job.status == Status.staged
    assert job.discovery_family == "CONSULTING"
    assert job.discovery_query == "management consultant intern"
    assert job.vector_score == 0.42


async def test_company_facts_do_not_change_scoring_signals(db_ready: Path, profile) -> None:
    provider = FakeProvider(FULL_TEXT)
    async with session_scope() as session:
        job = await upsert_job(
            session,
            _job("signals", "Acme", score=75, role_family="CONSULTING"),
        )
        dream_before = is_dream_company("Acme", profile)
        tier_before = compute_tier(75, "Acme", profile)
        await attach_company_intelligence(
            session,
            job,
            source_url="https://acme.example/about",
            provider=provider,
        )
        dream_after = is_dream_company("Acme", profile)
        tier_after = compute_tier(75, "Acme", profile)
    assert job.score == 75
    assert job.role_family_weight == 40
    assert job.tier == Tier.one
    assert job.status == Status.staged
    assert dream_before == dream_after
    assert tier_before == tier_after == Tier.two
    families = {family.id: family.weight for family in load_discovery().families}
    assert str(families["PRODUCT_MANAGEMENT"]) == "0.40"


async def test_cooldown_set_is_unchanged(db_ready: Path) -> None:
    async with session_scope() as session:
        session.add(
            Job(
                source=Source.linkedin,
                external_id="cool-done",
                title="Product Manager Intern",
                company="CoolCo",
                location="Remote",
                url="https://example.com/cool-done",
                description_clean="Already applied.",
                status=Status.submitted,
                decided_at=datetime.now(UTC),
            )
        )
        await session.flush()
        before = await get_recently_applied_companies(session)
        await resolve_company(session, "CoolCo")
        after = await get_recently_applied_companies(session)
    assert before == after == {"CoolCo"}


async def test_http_provider_handles_timeout_and_malformed_pages() -> None:
    def timeout(request: httpx.Request) -> httpx.Response:
        del request
        raise httpx.ReadTimeout("slow")

    timeout_client = httpx.AsyncClient(transport=httpx.MockTransport(timeout))
    result = await HttpCompanyIntelProvider(timeout_client).lookup(
        "Acme",
        "https://acme.example/about",
    )
    await timeout_client.aclose()
    assert result.error == "timeout"
    assert result.document is None

    def empty(request: httpx.Request) -> httpx.Response:
        del request
        return httpx.Response(200, text="   ")

    empty_client = httpx.AsyncClient(transport=httpx.MockTransport(empty))
    malformed = await HttpCompanyIntelProvider(empty_client).lookup(
        "Acme",
        "https://acme.example/about",
    )
    await empty_client.aclose()
    assert malformed.error == "malformed"

    page = (
        "<html><body><p>"
        "Acme is a privately held software company headquartered in Austin."
        "</p></body></html>"
    )

    def ok(request: httpx.Request) -> httpx.Response:
        del request
        return httpx.Response(200, text=page)

    ok_client = httpx.AsyncClient(transport=httpx.MockTransport(ok))
    fetched = await HttpCompanyIntelProvider(ok_client).lookup(
        "Acme",
        "https://acme.example/about",
        "official_website",
    )
    await ok_client.aclose()
    assert fetched.document is not None
    assert fetched.document.source_type == "official_website"
    assert fetched.document.url == "https://acme.example/about"
    facts = extract_company_facts(fetched.document.text)
    assert facts["public_private"] == "private"
    assert facts["headquarters"] == "Austin"
    assert facts["employee_range"] is None


async def test_http_provider_keeps_the_caller_source_type() -> None:
    page = "<html><body><p>Acme is a publicly traded software company.</p></body></html>"

    def ok(request: httpx.Request) -> httpx.Response:
        del request
        return httpx.Response(200, text=page)

    for source_type, url in (
        ("official_website", "https://acme.example/about"),
        ("sec", "https://www.sec.gov/Archives/edgar/data/1/acme.htm"),
        ("regulatory", "https://www.sec.gov/cgi-bin/browse-edgar"),
        ("careers", "https://careers.acme.example/about"),
    ):
        client = httpx.AsyncClient(transport=httpx.MockTransport(ok))
        result = await HttpCompanyIntelProvider(client).lookup("Acme", url, source_type)
        await client.aclose()
        assert result.document is not None
        assert result.document.source_type == source_type
        assert result.document.url == url


async def test_persisted_source_type_matches_the_caller(db_ready: Path) -> None:
    provider = FakeProvider()
    async with session_scope() as session:
        record = await resolve_company(
            session,
            "Acme",
            source_url="https://www.sec.gov/Archives/edgar/data/1/acme.htm",
            source_type="sec",
            provider=provider,
        )
    assert record.sources[0]["source_type"] == "sec"
    assert record.sources[0]["url"] == "https://www.sec.gov/Archives/edgar/data/1/acme.htm"
    assert record.website is None

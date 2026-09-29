"""Marketing, technology strategy, MBA summer associate, and first discovery provenance."""

from __future__ import annotations

from pathlib import Path

from config.targets import load_targets
from core.db import Source, Status, Tier, get_job_by_source_id, session_scope, upsert_job
from scorer.eligibility import LIKELY_ELIGIBLE, evaluate_eligibility
from scorer.role_classify import classify_role
from scorer.role_weights import get_role_family_weight
from scraper.discovery import build_discovery_plan, load_discovery
from scraper.filters import evaluate, has_internship_signal
from scraper.models import RawPosting, to_job

_PAD = " The team meets weekly to review the work and the plan. " * 3


def _jd(text: str) -> str:
    body = f"{text}{_PAD}"
    assert len(body) >= 80
    return body


async def _family(title: str, description: str) -> tuple[str, str | None]:
    result = await classify_role(
        title=title,
        description=_jd(description),
        content_hash="abc",
        discovery_family="OTHER",
        discovery_query="unrelated query",
    )
    return result.role_family, result.role_subfamily


async def test_marketing_is_separate_from_product_marketing_and_other() -> None:
    assert await _family(
        "2027 MBA Marketing Summer Associate",
        "Own marketing strategy, brand planning, consumer insights, and campaign development.",
    ) == ("MARKETING", "MARKETING_GENERAL")
    assert await _family(
        "Brand Management Intern",
        "Lead brand management and brand planning for the consumer portfolio.",
    ) == ("MARKETING", "MARKETING_GENERAL")
    assert await _family(
        "Marketing Strategy Intern",
        "Build the marketing strategy and the annual marketing planning cycle.",
    ) == ("MARKETING", "MARKETING_GENERAL")
    assert await _family(
        "2027 MBA Product Marketing Summer Associate",
        "Own positioning, messaging, competitive intelligence, and sales enablement.",
    ) == ("PRODUCT_MARKETING", "PRODUCT_MARKETING")
    assert await _family(
        "Sales Associate",
        "Own a sales quota and close revenue for assigned accounts.",
    ) == ("OTHER", None)
    assert await _family(
        "Software Engineer Intern",
        "Write production software and review pull requests with the platform team.",
    ) == ("OTHER", None)


async def test_technology_strategy_is_not_technology_consulting() -> None:
    assert await _family(
        "Technology Strategy MBA Summer Associate",
        "Own enterprise technology strategy, the digital roadmap, and the technology portfolio.",
    ) == ("STRATEGY_TRANSFORMATION", "TECHNOLOGY_STRATEGY")
    assert await _family(
        "Digital Strategy Intern",
        "Set digital strategy and the technology operating model for the enterprise.",
    ) == ("STRATEGY_TRANSFORMATION", "TECHNOLOGY_STRATEGY")
    assert await _family(
        "IT Strategy Intern",
        "Lead IT strategy and technology portfolio choices for the company.",
    ) == ("STRATEGY_TRANSFORMATION", "TECHNOLOGY_STRATEGY")
    assert await _family(
        "Technology Consulting Summer Associate",
        "Deliver client engagements and technology consulting recommendations for clients.",
    ) == ("CONSULTING", "TECHNOLOGY_CONSULTING")
    assert await _family(
        "Technology Consulting Intern",
        "Client-facing technology consulting and advisory work for external clients.",
    ) == ("CONSULTING", "TECHNOLOGY_CONSULTING")
    assert await _family(
        "Corporate Strategy Summer Associate",
        "Support internal corporate strategy and strategic planning for the company.",
    ) == ("STRATEGY_TRANSFORMATION", "CORPORATE_STRATEGY")
    assert await _family(
        "Summer Associate",
        "Investment banking internship covering valuation, pitch books, and transaction execution.",
    ) == ("OTHER", None)
    ambiguous = await classify_role(
        title="Technology Intern",
        description=_jd("Help the technology team with assorted internal projects and notes."),
        content_hash="abc",
    )
    assert ambiguous.role_family == "UNKNOWN"


def test_discovery_plan_includes_controlled_mba_vocabulary() -> None:
    load_discovery.cache_clear()
    config = load_discovery()
    phrases = {
        phrase.casefold()
        for family in config.families
        for bucket in family.buckets
        for phrase in (*bucket.queries, *bucket.title_variants)
    }
    required = {
        "mba summer associate",
        "summer associate mba",
        "mba summer internship",
        "mba marketing summer associate",
        "marketing summer associate",
        "marketing strategy intern",
        "brand management intern",
        "technology strategy intern",
        "it strategy intern",
        "digital strategy intern",
        "mba technology strategy intern",
        "technology strategy summer associate",
        "mba strategy summer associate",
        "summer associate, strategy",
        "mba product summer associate",
        "summer associate, product management",
        "product manager intern",
        "strategy intern",
        "consulting intern",
    }
    assert required <= phrases
    assert "associate" not in phrases
    assert "senior associate" not in phrases
    plan = build_discovery_plan(load_targets())
    executed = {search.query.casefold() for search in plan.searches}
    assert "mba summer associate" in executed
    assert "associate" not in executed
    load_discovery.cache_clear()


def test_mba_summer_associate_is_an_internship_signal(profile, monkeypatch) -> None:
    yes = [
        "2027 MBA Summer Associate",
        "MBA Marketing Summer Associate",
        "MBA Strategy Summer Associate",
        "Summer Associate, Corporate Strategy",
        "Summer Associate, Product Management",
        "Product Management Intern",
        "Marketing Intern",
        "Strategy Intern",
    ]
    for title in yes:
        assert has_internship_signal(title), title
    strategy = "Summer Associate, Strategy"
    jd = "This MBA summer internship is a 11-week internship for MBA students."
    assert has_internship_signal(strategy, description=jd)
    for title in (
        "Associate",
        "Senior Associate",
        "Client Associate",
        "Sales Associate",
        "Operations Associate",
        "Summer Associate",
    ):
        assert not has_internship_signal(title), title
    monkeypatch.setenv("INTERNSHIP_ONLY", "true")
    from config.settings import get_settings

    get_settings.cache_clear()
    kept = evaluate(
        RawPosting(
            source=Source.linkedin,
            external_id="mba-sa",
            title="2027 MBA Summer Associate",
            company="Acme",
            location="Remote",
            url="https://example.com/mba-sa",
            description_clean=_jd("Brand planning and marketing strategy for the summer program."),
        ),
        profile,
    )
    assert kept.passed is True
    blocked = evaluate(
        RawPosting(
            source=Source.linkedin,
            external_id="assoc",
            title="Senior Associate",
            company="Acme",
            location="Remote",
            url="https://example.com/assoc",
            description_clean=_jd("Support the team with research and weekly updates."),
        ),
        profile,
    )
    assert blocked.passed is False
    get_settings.cache_clear()


async def test_first_discovery_provenance_is_immutable(db_ready: Path, profile) -> None:
    del db_ready
    description = _jd("Own the product roadmap and product prioritization for the internship.")
    first = to_job(
        RawPosting(
            source=Source.linkedin,
            external_id="job-x",
            title="Product Manager Intern",
            company="Acme",
            location="Seattle, WA",
            url="https://example.com/job-x",
            description_clean=description,
            discovery_family="PRODUCT_MANAGEMENT",
            discovery_bucket="primary",
            discovery_query="product manager",
        ),
        status=Status.staged,
    )
    first.score = 90
    first.tier = Tier.two
    first.vector_score = 0.33
    async with session_scope() as session:
        saved = await upsert_job(session, first)
        saved.eligibility_state = LIKELY_ELIGIBLE
        later = to_job(
            RawPosting(
                source=Source.linkedin,
                external_id="job-x",
                title="Product Manager Intern",
                company="Acme",
                location="Seattle, WA",
                url="https://example.com/job-x",
                description_clean=description,
                discovery_family="CONSULTING",
                discovery_bucket="broad",
                discovery_query="strategy summer associate",
            )
        )
        updated = await upsert_job(session, later)
        assert updated.id == saved.id
        assert updated.discovery_family == "PRODUCT_MANAGEMENT"
        assert updated.discovery_bucket == "primary"
        assert updated.discovery_query == "product manager"
        assert updated.external_id == "job-x"
        assert updated.score == 90
        assert updated.tier == Tier.two
        assert updated.status == Status.staged
        assert updated.eligibility_state == LIKELY_ELIGIBLE
        assert updated.vector_score == 0.33

        blank = to_job(
            RawPosting(
                source=Source.linkedin,
                external_id="job-blank",
                title="Strategy Intern",
                company="Acme",
                location="Remote",
                url="https://example.com/job-blank",
                description_clean=description,
            )
        )
        empty = await upsert_job(session, blank)
        assert empty.discovery_query is None
        filled = to_job(
            RawPosting(
                source=Source.linkedin,
                external_id="job-blank",
                title="Strategy Intern",
                company="Acme",
                location="Remote",
                url="https://example.com/job-blank",
                description_clean=description,
                discovery_family="STRATEGY_TRANSFORMATION",
                discovery_bucket="CORPORATE_STRATEGY",
                discovery_query="strategy intern",
            )
        )
        populated = await upsert_job(session, filled)
        assert populated.id == empty.id
        assert populated.discovery_family == "STRATEGY_TRANSFORMATION"
        assert populated.discovery_query == "strategy intern"

        other_source = to_job(
            RawPosting(
                source=Source.indeed,
                external_id="job-x",
                title="Product Manager Intern",
                company="Acme",
                location="Seattle, WA",
                url="https://example.com/indeed",
                description_clean=description,
                discovery_family="CONSULTING",
                discovery_bucket="broad",
                discovery_query="consulting intern",
            )
        )
        separate = await upsert_job(session, other_source)
        original = await get_job_by_source_id(session, Source.linkedin, "job-x")
    assert separate.id != updated.id
    assert separate.source == Source.indeed
    assert separate.discovery_family == "CONSULTING"
    assert original is not None
    assert original.discovery_query == "product manager"
    decision = await evaluate_eligibility(original, profile)
    assert original.score == 90
    assert decision.state != ""
    assert get_role_family_weight("MARKETING") == 5
    assert get_role_family_weight("STRATEGY_TRANSFORMATION") == 15
    assert get_role_family_weight("PRODUCT_MANAGEMENT") == 40
    assert get_role_family_weight("CONSULTING") == 40
    assert get_role_family_weight("UNKNOWN") == 5

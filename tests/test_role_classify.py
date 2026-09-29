"""Role classification from the posting. No candidate profile and no live model."""

from __future__ import annotations

from pathlib import Path

import pytest

from core.db import Source, get_job_by_source_id, session_scope, upsert_job
from scorer.role_classify import (
    ROLE_CLASSIFIER_VERSION,
    classification_is_current,
    classify_role,
)
from scraper.models import RawPosting, to_job

_PAD = " The team meets weekly to review the work. " * 3


def _jd(text: str) -> str:
    body = f"{text}{_PAD}"
    assert len(body) >= 80
    return body


class _FakeClient:
    def __init__(self, payload: str | None = None, *, explode: bool = False) -> None:
        self.payload = payload or ""
        self.explode = explode
        self.calls = 0

    async def complete(self, **_kwargs: object) -> str:
        self.calls += 1
        if self.explode:
            raise RuntimeError("model down")
        return self.payload


@pytest.mark.parametrize(
    ("title", "description", "discovery", "family", "subfamily"),
    [
        (
            "Product Manager Intern",
            "You will own the product roadmap and lead product prioritization.",
            "OTHER",
            "PRODUCT_MANAGEMENT",
            "PM_CORE",
        ),
        (
            "Technical Product Manager Intern",
            "Own the platform roadmap and define the API product with engineering.",
            "OTHER",
            "PRODUCT_MANAGEMENT",
            "TECHNICAL_PRODUCT",
        ),
        (
            "Product Strategy Intern",
            "Set product strategy and the product vision for the portfolio.",
            "OTHER",
            "PRODUCT_MANAGEMENT",
            "PRODUCT_STRATEGY",
        ),
        (
            "Product Operations Intern",
            "Run product operations for launch readiness across the product.",
            "OTHER",
            "PRODUCT_MANAGEMENT",
            "PRODUCT_OPERATIONS",
        ),
        (
            "Product Intern",
            "Own product positioning, messaging, and go-to-market launches.",
            "PRODUCT_MANAGEMENT",
            "PRODUCT_MARKETING",
            "PRODUCT_MARKETING",
        ),
        (
            "Consulting Intern",
            "Join a case team for client-facing management consulting engagements.",
            "OTHER",
            "CONSULTING",
            "MANAGEMENT_CONSULTING",
        ),
        (
            "Strategy Consulting Intern",
            "This strategy consulting internship delivers client strategy projects.",
            "OTHER",
            "CONSULTING",
            "STRATEGY_CONSULTING",
        ),
        (
            "Technology Consulting Intern",
            "Technology consulting for client digital systems and delivery.",
            "OTHER",
            "CONSULTING",
            "TECHNOLOGY_CONSULTING",
        ),
        (
            "Transformation Consulting Intern",
            "Lead transformation consulting workstreams for clients this summer.",
            "OTHER",
            "CONSULTING",
            "TRANSFORMATION_CONSULTING",
        ),
        (
            "Consulting Intern",
            "Join the internal corporate strategy team to set enterprise strategy.",
            "CONSULTING",
            "STRATEGY_TRANSFORMATION",
            "CORPORATE_STRATEGY",
        ),
        (
            "Strategy Intern",
            "Develop corporate strategy and enterprise strategy for the company.",
            "CONSULTING",
            "STRATEGY_TRANSFORMATION",
            "CORPORATE_STRATEGY",
        ),
        (
            "Strategy Intern",
            "This strategy and operations internship partners with business leaders.",
            "OTHER",
            "STRATEGY_TRANSFORMATION",
            "STRATEGY_OPERATIONS",
        ),
        (
            "Strategy Intern",
            "Lead strategic initiatives and the annual strategic planning cycle.",
            "OTHER",
            "STRATEGY_TRANSFORMATION",
            "STRATEGIC_INITIATIVES",
        ),
        (
            "Strategy Intern",
            "Drive business transformation across the company's operating units.",
            "OTHER",
            "STRATEGY_TRANSFORMATION",
            "BUSINESS_TRANSFORMATION",
        ),
        (
            "Strategy Intern",
            "Own go-to-market strategy for entering two new geographic markets.",
            "OTHER",
            "STRATEGY_TRANSFORMATION",
            "GTM_STRATEGY",
        ),
        (
            "Corporate Development Intern",
            "Corporate development internship evaluating acquisition targets.",
            "OTHER",
            "STRATEGY_TRANSFORMATION",
            "CORPORATE_DEVELOPMENT",
        ),
        (
            "Corporate Development Intern",
            "Investment banking internship in a coverage group preparing pitch books.",
            "STRATEGY_TRANSFORMATION",
            "OTHER",
            None,
        ),
        (
            "Product Marketing Intern",
            "Own product marketing, positioning, and messaging for a launch.",
            "PRODUCT_MANAGEMENT",
            "PRODUCT_MARKETING",
            "PRODUCT_MARKETING",
        ),
        (
            "Program Manager Intern",
            "Program manager responsible for program management across teams.",
            "OTHER",
            "PROGRAM_PROJECT_OPERATIONS",
            "PROGRAM_MANAGEMENT",
        ),
        (
            "Project Manager Intern",
            "Project manager leading project management of a defined project plan.",
            "OTHER",
            "PROGRAM_PROJECT_OPERATIONS",
            "PROJECT_MANAGEMENT",
        ),
        (
            "Business Operations Intern",
            "Business operations internship improving business operations processes.",
            "STRATEGY_TRANSFORMATION",
            "PROGRAM_PROJECT_OPERATIONS",
            "BUSINESS_OPERATIONS",
        ),
        (
            "Software Engineer Intern",
            "Write production software and review code with the engineering team.",
            "PRODUCT_MANAGEMENT",
            "OTHER",
            None,
        ),
        (
            "Investing Intern",
            "Private equity internship researching portfolio company investments.",
            "STRATEGY_TRANSFORMATION",
            "OTHER",
            None,
        ),
    ],
)
async def test_role_families_follow_the_job(
    title: str,
    description: str,
    discovery: str,
    family: str,
    subfamily: str | None,
) -> None:
    result = await classify_role(
        title=title,
        description=_jd(description),
        content_hash="hash",
        discovery_family=discovery,
        discovery_query=title,
    )
    assert result.role_family == family
    assert result.role_subfamily == subfamily
    assert result.role_confidence in {"high", "medium", "low"}
    assert result.role_classifier_version == ROLE_CLASSIFIER_VERSION
    blob = " ".join(result.role_evidence).lower()
    assert "candidate" not in blob
    assert "fit" not in blob
    assert result.used_llm is False


async def test_short_or_ambiguous_text_is_unknown_without_a_model() -> None:
    client = _FakeClient(explode=True)
    short = await classify_role(
        title="Intern",
        description="Intern.",
        content_hash="s",
        client=client,
    )
    assert short.role_family == "UNKNOWN"
    vague = await classify_role(
        title="Intern",
        description=_jd("Help the team and attend meetings during the summer internship."),
        content_hash="v",
        client=None,
    )
    assert vague.role_family == "UNKNOWN"
    assert client.calls == 0


async def test_invalid_model_output_falls_back_to_unknown() -> None:
    vague = _jd("Help the team and attend meetings during the summer internship.")
    broken = _FakeClient("this is not json")
    invalid = _FakeClient(
        '{"primary_family":"BANANA","subfamily":"NOPE","confidence":"high","evidence":["x"]}'
    )
    down = _FakeClient(explode=True)
    for client in (broken, invalid, down):
        result = await classify_role(
            title="Intern",
            description=vague,
            content_hash="x",
            client=client,
        )
        assert result.role_family == "UNKNOWN"
        assert client.calls == 1


async def test_invalid_confidence_is_unknown() -> None:
    client = _FakeClient(
        '{"primary_family":"CONSULTING","subfamily":"BUSINESS_CONSULTING",'
        '"confidence":"extremely_sure","evidence":["JD describes business consulting."]}'
    )
    result = await classify_role(
        title="Intern",
        description=_jd("Help the team and attend meetings during the summer internship."),
        content_hash="bad-confidence",
        client=client,
    )
    assert result.role_family == "UNKNOWN"
    assert result.role_subfamily is None
    assert result.role_confidence == "low"
    assert result.role_classifier_version == ROLE_CLASSIFIER_VERSION
    assert result.role_content_hash == "bad-confidence"
    assert client.calls == 1


async def test_valid_model_output_is_accepted_when_rules_do_not_decide() -> None:
    client = _FakeClient(
        '{"primary_family":"CONSULTING","subfamily":"BUSINESS_CONSULTING",'
        '"confidence":"medium","evidence":["JD describes business consulting for clients."]}'
    )
    result = await classify_role(
        title="Intern",
        description=_jd("Help the team and attend meetings during the summer internship."),
        content_hash="llm",
        client=client,
    )
    assert result.role_family == "CONSULTING"
    assert result.role_subfamily == "BUSINESS_CONSULTING"
    assert result.used_llm is True
    assert client.calls == 1


async def test_classification_persists_and_does_not_filter(db_ready: Path) -> None:
    del db_ready
    posting = RawPosting(
        source=Source.linkedin,
        external_id="role-1",
        title="Software Engineer Intern",
        company="GoodCo",
        url="https://example.com/role",
        description_clean=_jd(
            "Write production software and review code with the engineering team."
        ),
        discovery_family="PRODUCT_MANAGEMENT",
        discovery_bucket="PM_CORE",
        discovery_query="Product Intern",
    )
    labeled = await classify_role(
        title=posting.title,
        description=posting.description_clean or "",
        content_hash="role-hash",
        discovery_family=posting.discovery_family,
        discovery_query=posting.discovery_query,
    )
    job = to_job(posting)
    job.content_hash = "role-hash"
    job.role_family = labeled.role_family
    job.role_subfamily = labeled.role_subfamily
    job.role_confidence = labeled.role_confidence
    job.role_evidence = labeled.role_evidence
    job.role_classifier_version = labeled.role_classifier_version
    job.role_content_hash = "role-hash"
    async with session_scope() as session:
        await upsert_job(session, job)
        saved = await get_job_by_source_id(session, Source.linkedin, "role-1")
    assert saved is not None
    assert saved.status.value == "discovered"
    assert saved.role_family == "OTHER"
    assert saved.discovery_family == "PRODUCT_MANAGEMENT"
    assert saved.discovery_query == "Product Intern"
    assert saved.role_classifier_version == ROLE_CLASSIFIER_VERSION


async def test_unchanged_jd_keeps_classification_and_a_change_replaces_it(db_ready: Path) -> None:
    del db_ready
    description = _jd("You will own the product roadmap and lead product prioritization.")
    posting = RawPosting(
        source=Source.indeed,
        external_id="role-2",
        title="Product Manager Intern",
        company="GoodCo",
        url="https://example.com/role2",
        description_clean=description,
    )
    first = to_job(posting)
    first.role_family = "PRODUCT_MANAGEMENT"
    first.role_subfamily = "PM_CORE"
    first.role_confidence = "high"
    first.role_evidence = ["cached"]
    first.role_classifier_version = ROLE_CLASSIFIER_VERSION
    first.role_content_hash = first.content_hash
    async with session_scope() as session:
        await upsert_job(session, first)
        again = to_job(posting)
        again.role_family = "OTHER"
        again.role_evidence = ["fresh"]
        again.role_classifier_version = ROLE_CLASSIFIER_VERSION
        again.role_content_hash = again.content_hash
        await upsert_job(session, again)
        kept = await get_job_by_source_id(session, Source.indeed, "role-2")
        assert kept is not None
        assert kept.role_evidence == ["cached"]
        assert classification_is_current(
            role_family=kept.role_family,
            role_content_hash=kept.role_content_hash,
            role_classifier_version=kept.role_classifier_version,
            content_hash=kept.content_hash,
        )
        rewritten = to_job(
            RawPosting(
                source=Source.indeed,
                external_id="role-2",
                title="Product Marketing Intern",
                company="GoodCo",
                url="https://example.com/role2",
                description_clean=_jd(
                    "Own product positioning, messaging, and go-to-market launches."
                ),
            )
        )
        labeled = await classify_role(
            title=rewritten.title,
            description=rewritten.description_clean or "",
            content_hash=rewritten.content_hash,
        )
        rewritten.role_family = labeled.role_family
        rewritten.role_subfamily = labeled.role_subfamily
        rewritten.role_confidence = labeled.role_confidence
        rewritten.role_evidence = labeled.role_evidence
        rewritten.role_classifier_version = labeled.role_classifier_version
        rewritten.role_content_hash = rewritten.content_hash
        await upsert_job(session, rewritten)
        changed = await get_job_by_source_id(session, Source.indeed, "role-2")
        assert changed is not None
        assert changed.role_family == "PRODUCT_MARKETING"
        assert changed.role_evidence != ["cached"]


def test_classifier_version_bump_invalidates_phase5_v1() -> None:
    assert ROLE_CLASSIFIER_VERSION == "phase5-v2"
    assert not classification_is_current(
        role_family="OTHER",
        role_content_hash="abc",
        role_classifier_version="phase5-v1",
        content_hash="abc",
    )
    assert classification_is_current(
        role_family="MARKETING",
        role_content_hash="abc",
        role_classifier_version=ROLE_CLASSIFIER_VERSION,
        content_hash="abc",
    )


async def test_stale_classifier_version_is_replaced_on_reprocess(db_ready: Path) -> None:
    del db_ready
    from scraper.ingest import _apply_role_classification

    description = _jd(
        "Own marketing strategy, brand planning, and campaign development for the summer."
    )
    posting = RawPosting(
        source=Source.linkedin,
        external_id="role-stale",
        title="2027 MBA Marketing Summer Associate",
        company="GoodCo",
        url="https://example.com/role-stale",
        description_clean=description,
    )
    stored = to_job(posting)
    stored.role_family = "OTHER"
    stored.role_subfamily = None
    stored.role_confidence = "low"
    stored.role_evidence = ["old taxonomy"]
    stored.role_classifier_version = "phase5-v1"
    stored.role_content_hash = stored.content_hash
    async with session_scope() as session:
        await upsert_job(session, stored)
        incoming = to_job(posting)
        await _apply_role_classification(session, incoming, None)
        saved = await upsert_job(session, incoming)
    assert saved.role_family == "MARKETING"
    assert saved.role_subfamily == "MARKETING_GENERAL"
    assert saved.role_classifier_version == "phase5-v2"
    assert saved.role_content_hash == saved.content_hash

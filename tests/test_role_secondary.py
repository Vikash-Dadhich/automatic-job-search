"""Primary and secondary role families. Downstream decisions stay on the primary family."""

from __future__ import annotations

import pytest

from core.db import (
    _JOB_COLUMN_DDL,
    Source,
    get_job_by_source_id,
    session_scope,
    upsert_job,
)
from scorer.role_classify import ROLE_CLASSIFIER_VERSION, classification_is_current, classify_role
from scraper.models import RawPosting, to_job
from scraper.structured_jd import extract_structured_jd

_PAD = " The team meets weekly to review the work. " * 3


def _jd(text: str) -> str:
    body = f"{text}{_PAD}"
    assert len(body) >= 80
    return body


async def test_pure_roles_have_no_secondary_family() -> None:
    cases = [
        (
            "Product Owner Intern",
            "Own the product roadmap and lead product prioritization.",
            "PRODUCT_MANAGEMENT",
        ),
        (
            "Management Consulting Intern",
            "Join a case team for client-facing management consulting engagements.",
            "CONSULTING",
        ),
        (
            "Corporate Strategy Intern",
            "Develop corporate strategy and enterprise strategy for the company.",
            "STRATEGY_TRANSFORMATION",
        ),
        (
            "Product Marketing Intern",
            "Own product marketing, positioning, and messaging for a launch.",
            "PRODUCT_MARKETING",
        ),
    ]
    for title, description, family in cases:
        result = await classify_role(
            title=title,
            description=_jd(description),
            content_hash=family,
        )
        assert result.role_family == family
        assert result.role_secondary_family is None
        assert result.role_secondary_confidence is None
        assert result.role_secondary_evidence == []


async def test_hybrid_roles_keep_a_second_family() -> None:
    pm_strategy = await classify_role(
        title="Product Owner Intern",
        description=_jd(
            "Own the product roadmap and product requirements. "
            "Also develop corporate strategy and business strategy for the unit."
        ),
        content_hash="pm-strategy",
    )
    consulting = await classify_role(
        title="Management Consulting Intern",
        description=_jd(
            "Join a case team for client-facing management consulting engagements. "
            "Also develop corporate strategy and business strategy for the client."
        ),
        content_hash="consulting-strategy",
    )
    marketing = await classify_role(
        title="Product Marketing Intern",
        description=_jd(
            "Own product marketing, positioning, and messaging for a launch. "
            "Also own marketing strategy, brand planning, and campaign development."
        ),
        content_hash="pmm-marketing",
    )
    transformation = await classify_role(
        title="Business Transformation Intern",
        description=_jd(
            "Drive business transformation and the transformation strategy. "
            "Own program management and the program manager plan for the rollout."
        ),
        content_hash="transform-program",
    )
    technology = await classify_role(
        title="Technology Strategy Intern",
        description=_jd(
            "Develop technology strategy and the technology operating model. "
            "Also own the product roadmap and write the product requirements."
        ),
        content_hash="pm-tech-strategy",
    )
    assert pm_strategy.role_family == "PRODUCT_MANAGEMENT"
    assert pm_strategy.role_secondary_family == "STRATEGY_TRANSFORMATION"
    assert consulting.role_family == "CONSULTING"
    assert consulting.role_secondary_family == "STRATEGY_TRANSFORMATION"
    assert marketing.role_family == "PRODUCT_MARKETING"
    assert marketing.role_secondary_family == "MARKETING"
    assert transformation.role_family == "STRATEGY_TRANSFORMATION"
    assert transformation.role_secondary_family == "PROGRAM_PROJECT_OPERATIONS"
    assert technology.role_family == "STRATEGY_TRANSFORMATION"
    assert technology.role_subfamily == "TECHNOLOGY_STRATEGY"
    assert technology.role_secondary_family == "PRODUCT_MANAGEMENT"
    for result in (pm_strategy, consulting, marketing, transformation, technology):
        assert result.role_secondary_confidence in {"high", "medium", "low"}
        assert result.role_secondary_evidence
        assert "fit" not in " ".join(result.role_secondary_evidence).lower()


async def test_interaction_is_not_a_second_family() -> None:
    consulting = await classify_role(
        title="Management Consulting Intern",
        description=_jd(
            "Join a case team for client-facing management consulting engagements. "
            "Collaborate with product managers on the product roadmap."
        ),
        content_hash="consult-interact",
        discovery_family="PRODUCT_MANAGEMENT",
        discovery_query="product manager",
    )
    product = await classify_role(
        title="Product Owner Intern",
        description=_jd(
            "Own the product roadmap and lead product prioritization. "
            "Work closely with marketing during the launch."
        ),
        content_hash="pm-interact",
    )
    assert consulting.role_family == "CONSULTING"
    assert consulting.role_secondary_family is None
    assert product.role_family == "PRODUCT_MANAGEMENT"
    assert product.role_secondary_family is None


async def test_one_phrase_needs_structured_confirmation() -> None:
    description = _jd(
        "Own the product roadmap and product requirements. "
        "The intern also develops corporate strategy with business leaders."
    )
    alone = await classify_role(
        title="Product Owner Intern",
        description=description,
        content_hash="one-phrase",
    )
    structured = extract_structured_jd(
        "Responsibilities\n- Develop corporate strategy\n\n" + description,
        jd_status="present",
    )
    confirmed = await classify_role(
        title="Product Owner Intern",
        description=description,
        content_hash="one-phrase",
        structured=structured,
    )
    assert alone.role_family == "PRODUCT_MANAGEMENT"
    assert alone.role_secondary_family is None
    assert confirmed.role_family == "PRODUCT_MANAGEMENT"
    assert confirmed.role_secondary_family == "STRATEGY_TRANSFORMATION"
    assert confirmed.role_secondary_confidence == "low"


async def test_truncated_posting_has_no_secondary_family() -> None:
    result = await classify_role(
        title="Product Owner Intern",
        description=_jd(
            "Own the product roadmap and product requirements. "
            "Also develop corporate strategy and business strategy for the unit."
        ),
        content_hash="truncated-hybrid",
        truncated=True,
    )
    assert result.role_family == "PRODUCT_MANAGEMENT"
    assert result.role_secondary_family is None
    assert result.role_confidence in {"high", "medium", "low"}


async def test_short_text_stays_unknown() -> None:
    result = await classify_role(
        title="Technology Strategy MBA Intern",
        description="Technology strategy.",
        content_hash="short",
    )
    assert result.role_family == "UNKNOWN"
    assert result.role_secondary_family is None


def test_secondary_columns_exist_for_sqlite_and_postgres() -> None:
    expected = {
        "role_secondary_family": "VARCHAR(64)",
        "role_secondary_subfamily": "VARCHAR(64)",
        "role_secondary_confidence": "VARCHAR(16)",
        "role_secondary_evidence": "JSON",
    }
    assert expected.items() <= _JOB_COLUMN_DDL["sqlite"].items()
    assert expected.items() <= _JOB_COLUMN_DDL["postgresql"].items()


async def test_secondary_fields_persist_and_clear_when_the_jd_changes(db_ready: object) -> None:
    del db_ready
    description = _jd(
        "Own the product roadmap and product requirements. "
        "Also develop corporate strategy and business strategy for the unit."
    )
    posting = RawPosting(
        source=Source.linkedin,
        external_id="secondary-1",
        title="Product Owner Intern",
        company="Acme",
        url="https://example.com/secondary-1",
        description_clean=description,
    )
    labeled = await classify_role(
        title=posting.title,
        description=description,
        content_hash="secondary-hash",
    )
    job = to_job(posting)
    job.content_hash = "secondary-hash"
    job.role_family = labeled.role_family
    job.role_subfamily = labeled.role_subfamily
    job.role_confidence = labeled.role_confidence
    job.role_evidence = labeled.role_evidence
    job.role_classifier_version = labeled.role_classifier_version
    job.role_content_hash = "secondary-hash"
    job.role_secondary_family = labeled.role_secondary_family
    job.role_secondary_subfamily = labeled.role_secondary_subfamily
    job.role_secondary_confidence = labeled.role_secondary_confidence
    job.role_secondary_evidence = labeled.role_secondary_evidence
    async with session_scope() as session:
        await upsert_job(session, job)
        saved = await get_job_by_source_id(session, Source.linkedin, "secondary-1")
        assert saved is not None
        assert saved.role_family == "PRODUCT_MANAGEMENT"
        assert saved.role_secondary_family == "STRATEGY_TRANSFORMATION"
        changed = to_job(
            RawPosting(
                source=Source.linkedin,
                external_id="secondary-1",
                title="Product Owner Intern",
                company="Acme",
                url="https://example.com/secondary-1",
                description_clean=_jd("Own the product roadmap and lead product prioritization."),
            )
        )
        cleared = await upsert_job(session, changed)
        assert cleared.role_secondary_family is None
        assert cleared.role_family is None


async def test_cache_recomputes_only_when_hash_or_version_changes(
    db_ready: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    from scraper.ingest import _apply_role_classification

    calls = {"n": 0}
    original = classify_role

    async def counted(**kwargs: object) -> object:
        calls["n"] += 1
        return await original(**kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr("scorer.role_classify.classify_role", counted)
    description = _jd(
        "Own the product roadmap and product requirements. "
        "Also develop corporate strategy and business strategy for the unit."
    )
    posting = RawPosting(
        source=Source.indeed,
        external_id="secondary-cache",
        title="Product Owner Intern",
        company="Acme",
        url="https://example.com/secondary-cache",
        description_clean=description,
    )
    async with session_scope() as session:
        saved = await upsert_job(session, to_job(posting))
        await _apply_role_classification(session, saved, None)
        assert calls["n"] == 1
        assert saved.role_secondary_family == "STRATEGY_TRANSFORMATION"
        await _apply_role_classification(session, saved, None)
        assert calls["n"] == 1
        assert classification_is_current(
            role_family=saved.role_family,
            role_content_hash=saved.role_content_hash,
            role_classifier_version=saved.role_classifier_version,
            content_hash=saved.content_hash,
        )
        saved.role_classifier_version = "phase5-v2"
        session.add(saved)
        await _apply_role_classification(session, saved, None)
        assert calls["n"] == 2
        assert saved.role_classifier_version == ROLE_CLASSIFIER_VERSION
        saved.description_clean = _jd("Own the product roadmap and lead product prioritization.")
        saved.content_hash = "changed-hash"
        saved.role_content_hash = "secondary-old"
        saved.role_secondary_family = "MARKETING"
        session.add(saved)
        await _apply_role_classification(session, saved, None)
        assert calls["n"] == 3
        assert saved.role_family == "PRODUCT_MANAGEMENT"
        assert saved.role_secondary_family is None
        assert saved.role_content_hash == "changed-hash"

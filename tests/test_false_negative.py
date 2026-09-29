"""Missing or weak evidence must not become a hard rejection."""

from __future__ import annotations

import json

from config.profile import Profile
from core.db import Job, Source, Status
from scorer.eligibility import CLEARLY_INELIGIBLE, UNKNOWN, evaluate_eligibility
from scorer.fit import DIMENSIONS, parse_fit
from scraper.filters import evaluate, evaluate_job, max_acceptable_years
from scraper.models import RawPosting


def _posting(**kwargs: object) -> RawPosting:
    defaults: dict[str, object] = {
        "source": Source.linkedin,
        "external_id": "fn-1",
        "title": "Product Manager Intern",
        "company": "GoodCo",
        "location": "Remote",
        "url": "https://example.com/fn",
        "description_clean": "Own the product roadmap for a summer internship.",
    }
    defaults.update(kwargs)
    return RawPosting(**defaults)  # type: ignore[arg-type]


def test_preferred_clearance_is_not_a_hard_rejection(profile: Profile) -> None:
    preferred = evaluate(
        _posting(description_clean="Ability to obtain a security clearance is preferred."),
        profile,
    )
    assert preferred.passed is True
    required = evaluate(
        _posting(
            external_id="fn-clearance",
            description_clean="This role requires an active TS/SCI clearance.",
        ),
        profile,
    )
    assert required.passed is False
    assert required.reason is not None
    assert "clearance" in required.reason.lower()


def test_explicit_internship_title_survives_seniority_words(profile: Profile) -> None:
    result = evaluate(
        _posting(title="Summer VP Internship", description_clean="A summer internship program."),
        profile,
    )
    assert result.passed is True
    blocked = evaluate(
        _posting(
            title="VP of Product",
            external_id="fn-vp",
            description_clean="Lead the product org.",
        ),
        profile,
    )
    assert blocked.passed is False


def test_missing_or_weak_evidence_does_not_filter(profile: Profile) -> None:
    ceiling = max_acceptable_years(profile)
    missing_jd = evaluate(
        _posting(description_clean=None, title="Marketing Intern"),
        profile,
    )
    assert missing_jd.passed is True
    short = evaluate(
        _posting(description_clean="Intern.", external_id="fn-short"),
        profile,
    )
    assert short.passed is True
    no_years = evaluate(
        _posting(description_clean="Join the product internship team.", external_id="fn-noyoe"),
        profile,
    )
    assert no_years.passed is True
    preferred = evaluate(
        _posting(
            external_id="fn-pref",
            description_clean=f"{ceiling + 5}+ years of experience preferred.",
        ),
        profile,
    )
    assert preferred.passed is True
    required = evaluate(
        _posting(
            external_id="fn-req",
            description_clean=f"Requires {ceiling + 5}+ years of experience.",
        ),
        profile,
    )
    assert required.passed is False


def test_role_uncertainty_does_not_filter(profile: Profile) -> None:
    for family, confidence in (("UNKNOWN", "low"), ("OTHER", "low"), ("PRODUCT_MANAGEMENT", "low")):
        job = Job(
            source=Source.linkedin,
            external_id=f"fn-{family}",
            title="Product Manager Intern",
            company="GoodCo",
            location="Remote",
            url="https://example.com/role",
            description_clean="Own the product roadmap for a summer internship.",
            status=Status.discovered,
            role_family=family,
            role_confidence=confidence,
            discovery_family="CONSULTING",
            discovery_query="strategy intern",
        )
        assert evaluate_job(job, profile).passed is True


async def test_unknown_eligibility_is_not_a_rejection(profile: Profile) -> None:
    job = Job(
        source=Source.linkedin,
        external_id="fn-elig",
        title="Product Manager Intern",
        company="GoodCo",
        location="Remote",
        url="https://example.com/elig",
        description_clean="Join the product internship team. " * 4,
        status=Status.discovered,
        role_family="UNKNOWN",
    )
    missing = await evaluate_eligibility(job, profile)
    assert missing.state != CLEARLY_INELIGIBLE
    ambiguous = await evaluate_eligibility(
        Job(
            source=Source.linkedin,
            external_id="fn-amb",
            title="Product Manager Intern",
            company="GoodCo",
            location="Remote",
            url="https://example.com/amb",
            description_clean="Applicants must be authorized to work in the U.S. " * 3,
            status=Status.discovered,
        ),
        profile,
    )
    assert ambiguous.state == UNKNOWN
    hostile = await evaluate_eligibility(
        Job(
            source=Source.linkedin,
            external_id="fn-no",
            title="Product Manager Intern",
            company="GoodCo",
            location="Remote",
            url="https://example.com/no",
            description_clean="This internship will not sponsor visas.",
            status=Status.discovered,
        ),
        profile,
    )
    assert hostile.state == CLEARLY_INELIGIBLE


def test_unknown_fit_judgment_stays_unknown(profile: Profile) -> None:
    dimensions = {
        name: {"judgment": "unknown", "note": "not stated"} for name in DIMENSIONS
    }
    payload = {
        "fit_score": 70,
        "confidence": "medium",
        "strengths": ["The description asks for roadmap ownership."],
        "gaps": [],
        "evidence": ["The description asks for roadmap ownership."],
        "dimensions": dimensions,
    }
    job = Job(
        source=Source.linkedin,
        external_id="fn-fit",
        title="Product Manager Intern",
        company="GoodCo",
        location="Remote",
        url="https://example.com/fit",
        description_clean="Own roadmap ownership for the internship.",
        content_hash="fn-fit",
        status=Status.discovered,
    )
    decision = parse_fit(json.dumps(payload), job, profile)
    assert decision is not None
    assert decision.score == 70
    assert all(item["judgment"] == "unknown" for item in decision.dimensions.values())

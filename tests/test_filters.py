"""Tests for the negative pre-filter."""

from __future__ import annotations

from config.profile import Profile
from core.db import Source
from scraper.filters import evaluate
from scraper.models import RawPosting


def _posting(**kwargs) -> RawPosting:
    defaults = {
        "source": Source.linkedin,
        "external_id": "x",
        "title": "Software Engineer",
        "company": "GoodCo",
        "location": "Remote",
        "url": "https://example.com/job",
        "description_clean": "Build Python services.",
    }
    defaults.update(kwargs)
    return RawPosting(**defaults)


def test_exclude_staffing_company(profile: Profile) -> None:
    result = evaluate(_posting(company="Revature", external_id="1"), profile)
    assert result.passed is False
    assert result.reason is not None
    assert "company" in result.reason.lower()


def test_exclude_clearance_keyword(profile: Profile) -> None:
    result = evaluate(
        _posting(
            external_id="2",
            company="DefenseCo",
            description_clean="Must have active TS/SCI clearance to start.",
        ),
        profile,
    )
    assert result.passed is False
    assert result.reason is not None


def test_exclude_off_target_location(profile: Profile) -> None:
    # Force relocation_ok=False so off-target on-site locations are rejected
    local_profile = profile.model_copy(
        update={
            "preferences": profile.preferences.model_copy(update={"relocation_ok": False})
        }
    )
    result = evaluate(
        _posting(
            external_id="3",
            source=Source.indeed,
            location="Berlin, Germany",
            description_clean="Python backend role.",
        ),
        local_profile,
    )
    assert result.passed is False
    assert result.reason is not None
    assert "location" in result.reason.lower()


def test_pass_remote_role(profile: Profile) -> None:
    result = evaluate(_posting(external_id="4"), profile)
    assert result.passed is True
    assert result.reason is None


def test_clearance_regex_pattern(profile: Profile) -> None:
    result = evaluate(
        _posting(
            external_id="5",
            company="GovTech",
            description_clean="This role requires a security clearance.",
        ),
        profile,
    )
    assert result.passed is False


def test_exclude_seniority_title(profile: Profile) -> None:
    result = evaluate(
        _posting(external_id="6", title="AVP - Product Manager", company="BankCo"),
        profile,
    )
    assert result.passed is False
    assert result.reason is not None
    assert "seniority" in result.reason.lower()


def test_exclude_high_yoe_requirement(profile: Profile) -> None:
    result = evaluate(
        _posting(
            external_id="7",
            title="Product Manager",
            description_clean="Requires 10+ years of experience in product.",
        ),
        profile,
    )
    assert result.passed is False
    assert result.reason is not None
    assert "years" in result.reason.lower()


def test_exclude_sponsorship_hostile_when_needed(profile: Profile) -> None:
    assert profile.work_authorization.sponsorship_required or (
        profile.work_authorization.needs_visa_sponsorship
    )
    result = evaluate(
        _posting(
            external_id="8",
            title="Product Manager",
            description_clean="No visa sponsorship. US citizens only.",
        ),
        profile,
    )
    assert result.passed is False
    assert result.reason is not None
    assert "sponsorship" in result.reason.lower()


def test_pass_mid_level_pm(profile: Profile) -> None:
    result = evaluate(
        _posting(
            external_id="9",
            title="Product Manager",
            company="GoodCo",
            location="Seattle, WA",
            description_clean="3-5 years of experience preferred. Sponsorship available.",
        ),
        profile,
    )
    assert result.passed is True

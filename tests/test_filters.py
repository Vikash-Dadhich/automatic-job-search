"""Tests for the negative pre-filter."""

from __future__ import annotations

import pytest

from config.profile import Profile
from core.db import Source
from scraper.filters import evaluate, sponsorship_signal
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


def test_yoe_counts_only_a_mandatory_minimum(profile: Profile) -> None:
    from scraper.filters import max_acceptable_years

    ceiling = max_acceptable_years(profile)
    cases = [
        ("3+ years of experience required. 8+ years of experience preferred.", True),
        ("10+ years of experience required. 12+ years of experience preferred.", False),
        ("10+ years of experience preferred.", True),
        ("10+ years desired.", True),
        ("10+ years of experience desired.", True),
        ("5+ years of experience required.", True),
        ("10+ years of experience in product.", True),
        ("3-5 years of experience required.", True),
        (
            f"{ceiling + 1}-{ceiling + 3} years of experience required.",
            False,
        ),
    ]
    for description, should_pass in cases:
        result = evaluate(
            _posting(external_id=description[:12], description_clean=description),
            profile,
        )
        assert result.passed is should_pass, description


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


def test_internship_only_rejects_fulltime(
    profile: Profile, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("INTERNSHIP_ONLY", "true")
    from config.settings import get_settings

    get_settings.cache_clear()
    result = evaluate(_posting(title="Product Manager", external_id="intern-1"), profile)
    assert result.passed is False
    assert "intern" in (result.reason or "").lower()
    get_settings.cache_clear()


def test_internship_only_passes_intern_title(
    profile: Profile, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("INTERNSHIP_ONLY", "true")
    from config.settings import get_settings

    get_settings.cache_clear()
    result = evaluate(
        _posting(title="Product Manager Intern", external_id="intern-2"), profile
    )
    assert result.passed is True
    get_settings.cache_clear()


def test_internship_only_off_by_default(profile: Profile) -> None:
    result = evaluate(_posting(title="Product Manager", external_id="intern-3"), profile)
    assert result.passed is True


def test_internship_only_rejects_international_substring(
    profile: Profile, monkeypatch: pytest.MonkeyPatch
) -> None:
    """'international' must not satisfy the intern word-boundary gate."""
    monkeypatch.setenv("INTERNSHIP_ONLY", "true")
    from config.settings import get_settings

    get_settings.cache_clear()
    result = evaluate(
        _posting(
            title="Senior Product Manager, Growth - International",
            external_id="intern-intl",
        ),
        profile,
    )
    assert result.passed is False
    assert "internship signal" in (result.reason or "")
    get_settings.cache_clear()


# ── Sponsorship signal ──────────────────────────────────────────────────────

def test_sponsorship_signal_hostile_no_sponsorship() -> None:
    assert sponsorship_signal("We do not offer visa sponsorship.") == "hostile"
    assert sponsorship_signal("This role requires US citizenship.") == "hostile"
    assert sponsorship_signal("Will not sponsor work visas.") == "hostile"


def test_sponsorship_signal_hostile_citizenship_required() -> None:
    assert sponsorship_signal("US citizens only.") == "hostile"
    assert sponsorship_signal("Citizenship required for this position.") == "hostile"


def test_sponsorship_signal_friendly_explicit() -> None:
    assert sponsorship_signal("Visa sponsorship is available for this role.") == "friendly"
    assert sponsorship_signal("We offer visa sponsorship for qualified candidates.") == "friendly"
    assert sponsorship_signal("We will sponsor H-1B and other work visas.") == "friendly"


def test_sponsorship_signal_friendly_opt_cpt() -> None:
    assert sponsorship_signal("OPT and CPT students are welcome to apply.") == "friendly"
    assert sponsorship_signal("F-1 visa students eligible.") == "friendly"
    assert sponsorship_signal("OPT friendly internship program.") == "friendly"


def test_sponsorship_signal_unknown_no_mention() -> None:
    jd = "We are looking for a motivated intern to join our product team."
    assert sponsorship_signal(jd) == "unknown"


def test_sponsorship_signal_hostile_beats_friendly() -> None:
    # Negated sentence must never be classified as friendly
    assert sponsorship_signal(
        "We do not offer visa sponsorship. OPT students may apply but we cannot sponsor."
    ) == "hostile"
    assert sponsorship_signal(
        "OPT students may apply but we cannot sponsor."
    ) == "hostile"


def test_sponsorship_signal_sponsor_events_is_not_friendly() -> None:
    assert sponsorship_signal("We sponsor employee events throughout the year.") == "unknown"

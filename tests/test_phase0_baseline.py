"""Phase 0 locks: profile facts, experience span, internship gate, sponsorship."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Any

import pytest

from config.profile import (
    Address,
    Education,
    Experience,
    Identity,
    Preferences,
    Profile,
    WorkAuthorization,
)
from config.settings import Settings, get_settings
from core.db import Source
from scraper.filters import evaluate, max_acceptable_years, sponsorship_signal
from scraper.models import RawPosting

_FROZEN = date(2026, 9, 29)


def _posting(**kwargs: Any) -> RawPosting:
    defaults: dict[str, Any] = {
        "source": Source.linkedin,
        "external_id": "phase0",
        "title": "Product Manager Intern",
        "company": "GoodCo",
        "location": "Remote",
        "url": "https://example.com/job",
        "description_clean": "Join the product team for the summer.",
    }
    defaults.update(kwargs)
    return RawPosting(**defaults)


def _profile_with_spans(spans: list[tuple[str, str]]) -> Profile:
    return Profile(
        identity=Identity(
            full_name="Test Candidate",
            email="test@example.com",
            phone="000",
            location="Seattle, WA",
            linkedin_url="https://www.linkedin.com/in/example/",
            github_url="https://github.com/example",
            address=Address(
                street="1 Main St",
                city="Seattle",
                state="WA",
                zip="98105",
            ),
        ),
        work_authorization=WorkAuthorization(
            status="F-1",
            sponsorship_required=True,
            authorized_to_work_us=False,
            needs_visa_sponsorship=True,
        ),
        education=[
            Education(
                degree="MBA",
                field="Business Administration",
                school="Foster School of Business, University of Washington",
                location="Seattle, WA",
                graduation_date="2028-06",
            )
        ],
        experience=[
            Experience(
                title=f"Role {index}",
                company=f"Co {index}",
                location="Seattle, WA",
                start_date=start,
                end_date=end,
                bullets=["Did the work."],
            )
            for index, (start, end) in enumerate(spans, start=1)
        ],
        skills=["Python"],
        preferences=Preferences(
            titles=["Product Manager Intern"],
            locations=["Seattle, WA", "Remote"],
            remote_ok=True,
            relocation_ok=True,
        ),
    )


def _enable_internship_only(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("INTERNSHIP_ONLY", "true")
    get_settings.cache_clear()


def test_profile_facts_match_phase0_brief(profile: Profile) -> None:
    assert profile.identity.full_name == "Vikash Dadhich"
    assert profile.identity.location == "Seattle, WA"
    mba, undergrad = profile.education
    assert mba.degree == "MBA"
    assert mba.school == "Foster School of Business, University of Washington"
    assert mba.graduation_date == "2028-06"
    assert undergrad.degree == "B.Tech"
    assert undergrad.field == "Metallurgical and Materials Engineering"
    assert "NITK" in undergrad.school
    assert undergrad.graduation_date == "2021-05"
    assert undergrad.gpa == 7.68

    roles = [
        (item.company, item.title, item.start_date, item.end_date) for item in profile.experience
    ]
    assert roles == [
        (
            "Saarthi Manosetu Wellness",
            "Co-founder and Technical Product Lead",
            "2025-04",
            "present",
        ),
        ("Standard Chartered GBS", "Manager – Development", "2025-09", "2026-08"),
        ("Standard Chartered GBS", "Senior Software Developer", "2024-04", "2025-09"),
        ("Standard Chartered GBS", "Software Developer", "2021-07", "2024-04"),
    ]
    assert all("Foster" not in item.company for item in profile.experience)

    auth = profile.work_authorization
    assert "CPT" in auth.status
    assert "sponsorship" in auth.status.lower()
    assert auth.sponsorship_required is True
    assert auth.needs_visa_sponsorship is True
    assert auth.authorized_to_work_us is False

    assert profile.preferences.remote_ok is True
    assert profile.preferences.relocation_ok is True
    assert profile.preferences.locations == ["Seattle, WA", "Remote"]
    assert profile.preferences.dream_companies == []
    assert "Product Strategy" in profile.skills
    assert "Java" in profile.skills
    lowered = [skill.lower() for skill in profile.skills]
    assert not any("java 17" in skill or "java 21" in skill for skill in lowered)


def test_experience_span_is_about_five_years_and_not_summed(profile: Profile) -> None:
    years = profile.total_years_experience(today=_FROZEN)
    assert years == 5.2
    summed_days = 0
    for item in profile.experience:
        start = date(int(item.start_date[:4]), int(item.start_date[5:7]), 1)
        if item.end_date == "present":
            end = _FROZEN
        else:
            end = date(int(item.end_date[:4]), int(item.end_date[5:7]), 1)
        summed_days += (end - start).days
    summed = round(summed_days / 365.25, 1)
    assert summed == 6.6
    assert years < summed


def test_overlapping_roles_use_the_outer_span() -> None:
    profile = _profile_with_spans([("2020-01", "2024-01"), ("2022-01", "2023-06")])
    years = profile.total_years_experience(today=date(2030, 1, 1))
    expected = round((date(2024, 1, 1) - date(2020, 1, 1)).days / 365.25, 1)
    assert years == expected == 4.0


def test_open_ended_role_ends_at_the_given_day() -> None:
    profile = _profile_with_spans([("2021-07", "present")])
    earlier = profile.total_years_experience(today=date(2026, 9, 29))
    later = profile.total_years_experience(today=date(2026, 10, 29))
    assert later > earlier


def test_yoe_ceiling_is_rounded_span_plus_three(
    profile: Profile, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("YEARS_EXPERIENCE_SLACK", "3")
    monkeypatch.delenv("MAX_REQUIRED_YEARS_EXPERIENCE", raising=False)
    get_settings.cache_clear()

    class _FrozenDate(date):
        @classmethod
        def today(cls) -> date:
            return _FROZEN

    monkeypatch.setattr("config.profile.date", _FrozenDate)
    assert profile.total_years_experience() == 5.2
    assert max_acceptable_years(profile) == 8
    get_settings.cache_clear()


def test_internship_only_code_default_is_false(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("INTERNSHIP_ONLY", raising=False)
    settings = Settings(_env_file=None)  # type: ignore[call-arg]
    assert settings.internship_only is False


@pytest.mark.parametrize(
    "title",
    [
        "Product Manager Intern",
        "MBA Product Manager Intern",
        "Strategy Intern",
        "Management Consultant Intern",
        "Summer 2027 MBA Product Manager",
        "International Product Manager Intern",
    ],
)
def test_internship_only_keeps_internship_titles(
    profile: Profile, monkeypatch: pytest.MonkeyPatch, title: str
) -> None:
    _enable_internship_only(monkeypatch)
    result = evaluate(_posting(title=title, external_id=title), profile)
    assert result.passed is True
    get_settings.cache_clear()


@pytest.mark.parametrize(
    "title",
    [
        "Product Manager",
        "Senior Product Manager",
        "Director of Product",
        "Product Management Director",
        "Software Engineer",
        "Senior Product Manager, Growth - International",
    ],
)
def test_internship_only_drops_non_internship_titles(
    profile: Profile, monkeypatch: pytest.MonkeyPatch, title: str
) -> None:
    _enable_internship_only(monkeypatch)
    result = evaluate(_posting(title=title, external_id=title), profile)
    assert result.passed is False
    get_settings.cache_clear()


@pytest.mark.parametrize(
    ("text", "signal"),
    [
        ("No visa sponsorship available", "hostile"),
        ("Applicants must be U.S. citizens", "hostile"),
        ("Must be authorized to work in the U.S. without sponsorship", "unknown"),
        ("Must have permanent work authorization", "unknown"),
        ("Visa sponsorship available", "friendly"),
        ("Sponsorship may be available", "unknown"),
        ("Open to candidates requiring sponsorship", "unknown"),
        ("Join the product team for the summer.", "unknown"),
    ],
)
def test_sponsorship_signal_current_behavior(text: str, signal: str) -> None:
    assert sponsorship_signal(text) == signal


def test_unknown_sponsorship_stays_eligible(profile: Profile) -> None:
    result = evaluate(
        _posting(description_clean="Join the product team for the summer."),
        profile,
    )
    assert result.passed is True


def test_hostile_sponsorship_is_rejected(profile: Profile) -> None:
    result = evaluate(
        _posting(description_clean="No visa sponsorship available for this internship."),
        profile,
    )
    assert result.passed is False
    assert result.reason is not None
    assert "sponsorship" in result.reason.lower()


def test_friendly_sponsorship_stays_eligible(profile: Profile) -> None:
    result = evaluate(
        _posting(description_clean="Visa sponsorship available for qualified interns."),
        profile,
    )
    assert result.passed is True


def test_production_workflow_flags() -> None:
    text = Path(".github/workflows/pipeline.yml").read_text(encoding="utf-8")
    assert 'INTERNSHIP_ONLY: "true"' in text
    assert 'ENABLE_APPLY: "false"' in text
    assert 'ENABLE_BENCHMARK: "false"' in text
    assert 'ENABLE_LINKEDIN_SCRAPE: "false"' in text
    assert 'ENABLE_REVIEWS: "true"' in text
    assert 'ENABLE_PREP_PACK: "true"' in text
    assert 'PREP_PACK_BRIEF: "true"' in text
    assert 'PREP_PACK_LIMIT: "20"' in text
    assert 'ENABLE_SUGGESTIONS: "false"' in text
    assert "LLM_PROVIDER: openai" in text
    assert "OPENAI_SCORER_MODEL: gpt-5-mini" in text
    assert "OPENAI_WRITER_MODEL: gpt-5-mini" in text
    assert 'TIER_ONE_DRAFTS_ENABLED: "false"' in text
    for cap in (
        "SEARCH_CAPACITY",
        "INGEST_POSTING_CAP",
        "EMBED_MAX_INPUTS",
        "ROLE_CLASSIFY_MAX_CALLS",
        "SCORE_BUDGET",
        "OPENAI_MAX_REQUESTS",
    ):
        match = re.search(rf'^\s+{cap}: "(\d+)"$', text, re.MULTILINE)
        assert match is not None, f"{cap} must be set in production"
        assert int(match.group(1)) > 0, cap
    assert "VECTOR_GATE" not in text
    assert "TIMEZONE: America/Los_Angeles" in text

"""Phase 9 eligibility. Unknown sponsorship is not a rejection, and fit is untouched."""

from __future__ import annotations

from pathlib import Path

import pytest

from config.profile import Profile
from core.db import (
    _JOB_COLUMN_DDL,
    Job,
    Source,
    Status,
    get_job_by_source_id,
    session_scope,
    upsert_job,
)
from scorer.eligibility import (
    CLEARLY_INELIGIBLE,
    CONFIRMED_ELIGIBLE,
    ELIGIBILITY_VERSION,
    LIKELY_ELIGIBLE,
    UNKNOWN,
    assign_eligibility,
    attach_eligibility,
    eligibility_column_types,
    eligibility_is_current,
    evaluate_eligibility,
    profile_eligibility_hash,
)
from scraper.filters import evaluate, has_internship_signal, sponsorship_signal
from scraper.ingest import run_ingestion
from scraper.models import RawPosting, to_job

INTERN = "Product Manager Intern"


def _job(
    description: str,
    *,
    title: str = INTERN,
    external_id: str = "elig-1",
    company: str = "Acme",
    location: str = "Seattle, WA",
) -> Job:
    job = to_job(
        RawPosting(
            source=Source.linkedin,
            external_id=external_id,
            title=title,
            company=company,
            location=location,
            url=f"https://example.com/{external_id}",
            description_clean=description,
        ),
        status=Status.discovered,
    )
    return job


class _Model:
    def __init__(self, payload: str | None = None, *, error: Exception | None = None) -> None:
        self.payload = payload
        self.error = error
        self.calls = 0

    async def complete(self, **kwargs: object) -> str:
        del kwargs
        self.calls += 1
        if self.error is not None:
            raise self.error
        return self.payload or ""


def test_sponsorship_and_false_friends(profile: Profile) -> None:
    friendly = "Visa sponsorship is available. CPT accepted. F-1 students welcome."
    assert sponsorship_signal(friendly) == "friendly"


async def test_explicit_sponsorship_paths(profile: Profile) -> None:
    available = await evaluate_eligibility(
        _job("Visa sponsorship available for this internship."),
        profile,
    )
    assert available.state == CONFIRMED_ELIGIBLE
    assert available.dimensions["VISA_SPONSORSHIP"].state == CONFIRMED_ELIGIBLE

    opted = await evaluate_eligibility(_job("OPT/CPT accepted for this internship."), profile)
    assert opted.dimensions["VISA_SPONSORSHIP"].state == CONFIRMED_ELIGIBLE

    f1 = await evaluate_eligibility(_job("F-1 students welcome to apply."), profile)
    assert f1.state == CONFIRMED_ELIGIBLE

    hostile = await evaluate_eligibility(
        _job("This internship does not offer visa sponsorship."),
        profile,
    )
    assert hostile.state == CLEARLY_INELIGIBLE

    silent = await evaluate_eligibility(_job("Join the product internship team."), profile)
    assert silent.state == LIKELY_ELIGIBLE
    assert silent.state != CLEARLY_INELIGIBLE


async def test_hostile_language_wins_and_false_friends_do_not(profile: Profile) -> None:
    mixed = await evaluate_eligibility(
        _job(
            "We support sponsorship for eligible employees. "
            "This specific internship does not offer visa sponsorship."
        ),
        profile,
    )
    assert mixed.state == CLEARLY_INELIGIBLE

    citizens = await evaluate_eligibility(
        _job(
            "We are an equal opportunity employer and sponsor visas where applicable. "
            "Applicants must be U.S. citizens for this internship."
        ),
        profile,
    )
    assert citizens.state == CLEARLY_INELIGIBLE
    assert citizens.dimensions["CITIZENSHIP"].state == CLEARLY_INELIGIBLE

    events = await evaluate_eligibility(
        _job("We sponsor employee events throughout the year."),
        profile,
    )
    assert events.state != CLEARLY_INELIGIBLE
    assert events.dimensions["VISA_SPONSORSHIP"].state == UNKNOWN

    welcome = await evaluate_eligibility(
        _job("International candidates welcome."),
        profile,
    )
    assert welcome.dimensions["VISA_SPONSORSHIP"].state == UNKNOWN
    assert welcome.state != CLEARLY_INELIGIBLE


async def test_citizenship_clearance_and_eeo(profile: Profile) -> None:
    only = await evaluate_eligibility(_job("U.S. citizens only."), profile)
    assert only.state == CLEARLY_INELIGIBLE
    required = await evaluate_eligibility(_job("U.S. citizenship required."), profile)
    assert required.state == CLEARLY_INELIGIBLE
    eeo = await evaluate_eligibility(
        _job("We are an equal opportunity employer."),
        profile,
    )
    assert eeo.dimensions["CITIZENSHIP"].state != CLEARLY_INELIGIBLE
    assert eeo.state != CLEARLY_INELIGIBLE

    ts = await evaluate_eligibility(
        _job("Active TS/SCI clearance required."),
        profile,
    )
    assert ts.state == CLEARLY_INELIGIBLE
    preferred = await evaluate_eligibility(
        _job("Ability to obtain a clearance preferred."),
        profile,
    )
    assert preferred.state != CLEARLY_INELIGIBLE
    assert preferred.dimensions["SECURITY_CLEARANCE"].state != CLEARLY_INELIGIBLE


async def test_education_graduation_and_experience(profile: Profile) -> None:
    mba = await evaluate_eligibility(
        _job("MBA required. Currently enrolled in an MBA program."),
        profile,
    )
    assert mba.dimensions["EDUCATION"].state == CONFIRMED_ELIGIBLE
    assert mba.state != CLEARLY_INELIGIBLE

    preferred = await evaluate_eligibility(_job("MBA preferred."), profile)
    assert preferred.dimensions["EDUCATION"].state != CLEARLY_INELIGIBLE
    assert preferred.state != CLEARLY_INELIGIBLE

    bachelor = await evaluate_eligibility(
        _job("Must be currently pursuing a bachelor's degree."),
        profile,
    )
    assert bachelor.state == CLEARLY_INELIGIBLE

    year = await evaluate_eligibility(_job("Must be graduating in 2028."), profile)
    assert year.dimensions["GRADUATION_TIMING"].state == CONFIRMED_ELIGIBLE

    window = await evaluate_eligibility(
        _job("Must graduate between December 2026 and August 2027."),
        profile,
    )
    assert window.state == CLEARLY_INELIGIBLE

    soft_grad = await evaluate_eligibility(_job("Graduating students preferred."), profile)
    assert soft_grad.dimensions["GRADUATION_TIMING"].state != CLEARLY_INELIGIBLE
    assert soft_grad.state != CLEARLY_INELIGIBLE

    none = await evaluate_eligibility(_job("Join the internship team this summer."), profile)
    assert none.dimensions["GRADUATION_TIMING"].state == UNKNOWN
    assert none.state != CLEARLY_INELIGIBLE

    reachable = await evaluate_eligibility(
        _job("Must have 2 years of professional experience."),
        profile,
    )
    assert reachable.dimensions["EXPERIENCE_REQUIREMENT"].state == CONFIRMED_ELIGIBLE

    unreachable = await evaluate_eligibility(
        _job("Must have 15 years of professional experience."),
        profile,
    )
    assert unreachable.state == CLEARLY_INELIGIBLE

    preferred_years = await evaluate_eligibility(
        _job("2+ years of experience preferred."),
        profile,
    )
    assert preferred_years.dimensions["EXPERIENCE_REQUIREMENT"].state != CLEARLY_INELIGIBLE
    assert preferred_years.state != CLEARLY_INELIGIBLE


def test_internship_signal_matches_the_existing_gate(
    profile: Profile,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert has_internship_signal("Product Manager Intern")
    assert has_internship_signal("Summer 2027 Product Manager")
    monkeypatch.setenv("INTERNSHIP_ONLY", "true")
    from config.settings import get_settings

    get_settings.cache_clear()
    kept = evaluate(
        RawPosting(
            source=Source.linkedin,
            external_id="keep",
            title="Product Manager Intern",
            company="Acme",
            location="Remote",
            url="https://example.com/keep",
            description_clean="A summer internship.",
        ),
        profile,
    )
    assert kept.passed is True
    get_settings.cache_clear()


async def test_location_is_not_a_seattle_gate(profile: Profile) -> None:
    austin = await evaluate_eligibility(
        _job("Relocation required for this U.S. internship.", location="Austin, TX"),
        profile,
    )
    assert austin.state != CLEARLY_INELIGIBLE
    remote = await evaluate_eligibility(
        _job("This internship is remote.", location="Remote"),
        profile,
    )
    assert remote.state != CLEARLY_INELIGIBLE
    chicago = await evaluate_eligibility(
        _job("On-site internship.", location="Chicago, IL"),
        profile,
    )
    assert chicago.dimensions["LOCATION"].state != CLEARLY_INELIGIBLE


async def test_unknown_authorization_and_dates(profile: Profile) -> None:
    ambiguous = await evaluate_eligibility(
        _job("Applicants must be authorized to work in the U.S."),
        profile,
    )
    assert ambiguous.state == UNKNOWN
    missing = await evaluate_eligibility(_job("Build product features with the team."), profile)
    assert missing.state in {UNKNOWN, LIKELY_ELIGIBLE}
    assert missing.state != CLEARLY_INELIGIBLE
    dated = await evaluate_eligibility(
        _job("Internship dates are May 2027 – August 2027."),
        profile,
    )
    assert dated.dimensions["INTERNSHIP_DATES"].state == UNKNOWN
    assert dated.state == UNKNOWN


async def test_signals_do_not_change_eligibility(profile: Profile) -> None:
    text = "Join the product internship team."
    base = await evaluate_eligibility(_job(text, external_id="base"), profile)
    other = _job(text, external_id="other", company="Other Co")
    other.discovery_family = "CONSULTING"
    other.discovery_bucket = "STRATEGY_CONSULTING"
    other.discovery_query = "management consultant intern"
    other.score = 12
    other.role_family_weight = 5
    other.vector_score = 0.99
    other.company_intelligence_id = 99
    moved = await evaluate_eligibility(other, profile)
    assert moved.state == base.state
    assert moved.profile_hash == base.profile_hash
    dreamed = profile.model_copy(
        update={
            "preferences": profile.preferences.model_copy(
                update={"dream_companies": ["Acme"]}
            )
        }
    )
    again = await evaluate_eligibility(_job(text, external_id="dream"), dreamed)
    assert again.state == base.state
    assert profile_eligibility_hash(dreamed) == profile_eligibility_hash(profile)


async def test_cache_identity(profile: Profile) -> None:
    job = _job("Applicants must be authorized to work in the U.S.", external_id="cache")
    model = _Model('{"state": "CONFIRMED_ELIGIBLE"}')
    first = await evaluate_eligibility(job, profile, client=model)
    assert first.state == UNKNOWN
    assert model.calls == 1
    assign_eligibility(job, first)
    second = await evaluate_eligibility(job, profile, client=model)
    assert second.state == UNKNOWN
    assert model.calls == 1

    job.content_hash = "different-hash"
    await evaluate_eligibility(job, profile, client=model)
    assert model.calls == 2

    assign_eligibility(job, first)
    job.eligibility_content_hash = job.content_hash
    changed = profile.model_copy(
        update={
            "work_authorization": profile.work_authorization.model_copy(
                update={"status": "changed authorization text"}
            )
        }
    )
    assert not eligibility_is_current(job, changed)
    await evaluate_eligibility(job, changed, client=model)
    assert model.calls == 3

    assign_eligibility(job, await evaluate_eligibility(job, profile, client=model))
    job.eligibility_version = "phase9-v0"
    assert not eligibility_is_current(job, profile)


async def test_malformed_model_stays_unknown(profile: Profile) -> None:
    job = _job("Applicants must be authorized to work in the U.S.")
    broken = _Model("not-json")
    decision = await evaluate_eligibility(job, profile, client=broken)
    assert decision.state == UNKNOWN
    raised = _Model(error=RuntimeError("down"))
    failed = await evaluate_eligibility(job, profile, client=raised)
    assert failed.state == UNKNOWN
    assert job.score is None


async def test_sqlite_persistence_and_upsert(db_ready: Path, profile: Profile) -> None:
    original = _job("Join the product internship team.", external_id="persist")
    original.score = 90
    original.role_family = "PRODUCT_MANAGEMENT"
    async with session_scope() as session:
        saved = await upsert_job(session, original)
        await attach_eligibility(saved, profile)
        assert saved.score == 90
        assert saved.role_family_weight == 40
        assert saved.eligibility_state == LIKELY_ELIGIBLE
        assert saved.eligibility_version == ELIGIBILITY_VERSION
        assert saved.eligibility_content_hash == saved.content_hash
        reloaded = await get_job_by_source_id(session, Source.linkedin, "persist")
        assert reloaded is not None
        assert reloaded.eligibility_state == LIKELY_ELIGIBLE

        same = _job("Join the product internship team.", external_id="persist")
        kept = await upsert_job(session, same)
        assert kept.eligibility_state == LIKELY_ELIGIBLE

        changed = _job("A rewritten internship description. " * 5, external_id="persist")
        cleared = await upsert_job(session, changed)
        assert cleared.eligibility_state is None
        assert cleared.eligibility_version is None
        assert cleared.score == 90


def test_postgres_eligibility_columns() -> None:
    expected = eligibility_column_types()
    assert expected.items() <= _JOB_COLUMN_DDL["postgresql"].items()
    assert expected.items() <= _JOB_COLUMN_DDL["sqlite"].items()


async def test_provider_failure_does_not_break_ingestion(
    db_ready: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def boom(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("eligibility down")

    async def one_posting(*_args: object, **_kwargs: object) -> list[RawPosting]:
        return [
            RawPosting(
                source=Source.linkedin,
                external_id="ingest-elig",
                title="Product Manager Intern",
                company="Acme",
                location="Remote",
                url="https://example.com/ingest-elig",
                description_clean="A summer product internship.",
            )
        ]

    monkeypatch.setattr("scraper.ingest.fetch_linkedin_indeed", one_posting)
    monkeypatch.setattr("scraper.ingest.attach_eligibility", boom)
    summary = await run_ingestion(include_workday=False)
    assert summary.errors == []
    assert summary.upserted == 1

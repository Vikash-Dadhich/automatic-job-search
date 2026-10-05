"""Structured JD readings. Deterministic, and independent of fit or eligibility."""

from __future__ import annotations

import pytest
from sqlalchemy import Table
from sqlalchemy.dialects import postgresql, sqlite
from sqlalchemy.schema import CreateTable
from sqlmodel import SQLModel

from core.db import Job, Source, Status, StructuredJobDescription, session_scope, upsert_job
from scraper.models import RawPosting
from scraper.structured_jd import (
    STRUCTURED_JD_VERSION,
    attach_structured_jd,
    extract_structured_jd,
    get_structured_jd,
    structured_jd_is_current,
)
from scraper.textclean import content_hash

GOOD = """
Join the Seattle, WA product organization for a 10-week summer 2026 MBA internship.

Responsibilities
- Own the roadmap
- Collaborate with cross-functional partners
- Present the plan to stakeholders
- Lead a team through people management

Required qualifications
- Bachelor's degree required
- 3+ years of product management experience
- SQL required

Preferred qualifications
- MBA preferred
- 2 years preferred in management consulting

The role is hybrid. Visa sponsorship is available. The work is in financial services.
"""

PM = (
    "Responsibilities\n- Own a product area\n\nRequired qualifications\n"
    "- Product management experience with stakeholders and a product roadmap\n"
)
CONSULTING = (
    "Responsibilities\n- Support a consulting engagement\n\nRequired qualifications\n"
    "- Management consulting experience with a client team over several months\n"
)
STRATEGY = (
    "Responsibilities\n- Prepare the annual plan\n\nRequired qualifications\n"
    "- Corporate strategy experience and comfort with ambiguous problems\n"
)
PRODUCT_MARKETING = (
    "Responsibilities\n- Shape the launch story\n\nRequired qualifications\n"
    "- Product marketing experience for a technical product and its buyers\n"
)
PROGRAM = (
    "Responsibilities\n- Keep delivery on track\n\nRequired qualifications\n"
    "- Program management experience across business operations partners\n"
)
TECH = (
    "Responsibilities\n- Build the model\n\nRequired qualifications\n"
    "- Software development and machine learning experience on production data\n"
)
PLAIN = (
    "The team meets each week to review notes and share updates with the group. "
    "This posting has no degree, visa, years, or specialty wording in it at all."
)


def _areas(text: str) -> set[str]:
    document = extract_structured_jd(text, jd_status="present")
    return {item.category for item in document.functional.areas}


def test_good_mba_internship_populates_several_fields() -> None:
    document = extract_structured_jd(GOOD, jd_status="present")
    assert document.version == STRUCTURED_JD_VERSION
    assert document.availability == "available"
    assert document.responsibilities.state == "explicit"
    assert {item.category for item in document.responsibilities.items} >= {
        "ownership",
        "collaboration",
        "stakeholder",
        "leadership",
    }
    required = " ".join(item.text for item in document.qualifications.required).lower()
    preferred = " ".join(item.text for item in document.qualifications.preferred).lower()
    assert "bachelor" in required
    assert "mba" not in required
    assert "mba" in preferred
    assert "bachelor" not in preferred
    assert document.experience.minimum_years == 3
    assert document.experience.preferred_years == 2
    assert document.education.bachelors == "required"
    assert document.education.mba == "preferred"
    assert document.program.mba_internship is True
    assert document.program.summer_internship is True
    assert document.program.duration == "10-week"
    assert document.program.timing is not None
    assert "Seattle, WA" in document.work_model.places
    assert document.work_model.hybrid is True
    assert document.authorization.sponsorship == "available"
    assert "financial_services" in {item.category for item in document.domain.domains}
    assert "product_management" in _areas(GOOD)
    assert all(len(item.snippet) <= 160 for item in document.responsibilities.items)


def test_required_and_preferred_stay_separate() -> None:
    document = extract_structured_jd(GOOD, jd_status="present")
    assert any(item.category == "technical" for item in document.qualifications.required)
    assert any("mba" in item.text.lower() for item in document.qualifications.preferred)
    assert not any("mba" in item.text.lower() for item in document.qualifications.required)


def test_mba_required_preferred_and_absent() -> None:
    required = extract_structured_jd(
        "Required qualifications\n- MBA required for this full-time corporate role\n" + PLAIN,
        jd_status="present",
    )
    preferred = extract_structured_jd(
        "Preferred qualifications\n- MBA preferred for this full-time corporate role\n" + PLAIN,
        jd_status="present",
    )
    absent = extract_structured_jd(PLAIN, jd_status="present")
    internship = extract_structured_jd(
        "This MBA internship lasts 10 weeks in Seattle, WA. " + PLAIN,
        jd_status="present",
    )
    assert required.education.mba == "required"
    assert preferred.education.mba == "preferred"
    assert absent.education.mba == "not_mentioned"
    assert internship.education.mba == "not_mentioned"
    assert internship.program.mba_internship is True


def test_experience_shapes() -> None:
    plus = extract_structured_jd("Required qualifications\n- 3+ years of experience\n" + PLAIN)
    band = extract_structured_jd("We want 5-7 years of experience in the field. " + PLAIN)
    preferred = extract_structured_jd("2 years preferred. " + PLAIN)
    none = extract_structured_jd(PLAIN, jd_status="present")
    assert plus.experience.minimum_years == 3
    assert plus.experience.years_basis == "required"
    assert band.experience.minimum_years == 5
    assert band.experience.maximum_years == 7
    assert preferred.experience.preferred_years == 2
    assert preferred.experience.minimum_years is None
    assert preferred.experience.years_basis == "preferred"
    assert none.experience.state == "not_mentioned"
    assert none.experience.minimum_years is None


def test_sponsorship_and_authorization() -> None:
    available = extract_structured_jd("Visa sponsorship is available. " + PLAIN)
    unavailable = extract_structured_jd("We do not sponsor visas. " + PLAIN)
    absent = extract_structured_jd(PLAIN, jd_status="present")
    citizen = extract_structured_jd("Must be a US citizen. " + PLAIN)
    clearance = extract_structured_jd("Must have an active security clearance. " + PLAIN)
    neither = extract_structured_jd(PLAIN, jd_status="present")
    assert available.authorization.sponsorship == "available"
    assert unavailable.authorization.sponsorship == "unavailable"
    assert absent.authorization.sponsorship == "not_mentioned"
    assert citizen.authorization.citizenship_required == "explicit"
    assert clearance.authorization.security_clearance == "required"
    assert neither.authorization.citizenship_required == "not_mentioned"
    assert neither.authorization.security_clearance == "not_mentioned"


def test_functional_signals_are_phrase_evidence() -> None:
    assert "product_management" in _areas(PM)
    assert "consulting" in _areas(CONSULTING)
    assert "strategy" in _areas(STRATEGY)
    assert "product_marketing" in _areas(PRODUCT_MARKETING)
    assert "marketing" not in _areas(PRODUCT_MARKETING)
    assert "program_operations" in _areas(PROGRAM)
    assert {"software_technology", "ai_ml"} <= _areas(TECH)
    assert _areas(PLAIN) == set()


def test_missing_evidence_stays_unknown_or_not_mentioned() -> None:
    usable = extract_structured_jd(PLAIN, jd_status="present")
    assert usable.education.mba == "not_mentioned"
    assert usable.experience.state == "not_mentioned"
    assert usable.functional.state == "not_mentioned"
    assert usable.authorization.sponsorship == "not_mentioned"
    assert usable.program.internship is None
    missing = extract_structured_jd("", jd_status="missing")
    short = extract_structured_jd("Too short to trust.", jd_status="suspicious")
    assert missing.availability == "unavailable"
    assert short.availability == "unavailable"
    assert missing.education.mba == "unknown"
    assert short.experience.years_basis == "unknown"
    assert missing.responsibilities.items == []


def test_tables_compile_for_sqlite_and_postgres() -> None:
    for dialect in (sqlite.dialect(), postgresql.dialect()):
        table = SQLModel.metadata.tables["structured_job_descriptions"]
        assert isinstance(table, Table)
        sql = str(CreateTable(table).compile(dialect=dialect))
        assert "structured_job_descriptions" in sql


def test_version_must_match_the_current_extractor() -> None:
    row = StructuredJobDescription(
        job_id=1,
        content_hash="abc",
        version="phase19-v0",
        availability="available",
        document={"version": "phase19-v0"},
    )
    assert structured_jd_is_current(row, "abc") is False
    row.version = STRUCTURED_JD_VERSION
    assert structured_jd_is_current(row, "abc") is False
    row.document = {
        "version": STRUCTURED_JD_VERSION,
        "application_deadline": {"version": "deadline-v1", "state": "NOT_FOUND"},
    }
    assert structured_jd_is_current(row, "different") is False
    assert structured_jd_is_current(row, "abc") is True


def _job(text: str, external_id: str = "jd-1") -> Job:
    return Job(
        source=Source.linkedin,
        external_id=external_id,
        title="Intern",
        company="Acme",
        url=f"https://jobs.example.com/{external_id}",
        description_clean=text,
        content_hash=content_hash(text),
        jd_status="present",
        status=Status.discovered,
    )


async def test_same_text_is_not_recomputed_and_a_change_is(
    db_ready: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    calls = {"n": 0}
    original = extract_structured_jd

    def counted(text: str, **kwargs: object):
        calls["n"] += 1
        return original(text, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr("scraper.structured_jd.extract_structured_jd", counted)
    async with session_scope() as session:
        saved = await upsert_job(session, _job(GOOD))
        assert saved.id is not None
        first = await attach_structured_jd(session, saved)
        assert first is not None
        assert calls["n"] == 1
        again = await attach_structured_jd(session, saved)
        assert again is not None
        assert calls["n"] == 1
        assert again.content_hash == saved.content_hash
        loaded = await get_structured_jd(session, saved.id)
        assert loaded is not None
        assert loaded.document["education"]["mba"] == "preferred"
        saved.description_clean = PLAIN
        saved.content_hash = content_hash(PLAIN)
        session.add(saved)
        await attach_structured_jd(session, saved)
        assert calls["n"] == 2
        updated = await get_structured_jd(session, saved.id)
        assert updated is not None
        assert updated.document["education"]["mba"] == "not_mentioned"
        assert updated.version == STRUCTURED_JD_VERSION


async def test_changed_upsert_drops_the_old_reading(db_ready: object) -> None:
    del db_ready
    async with session_scope() as session:
        saved = await upsert_job(session, _job(GOOD, "jd-drop"))
        assert saved.id is not None
        await attach_structured_jd(session, saved)
        assert await get_structured_jd(session, saved.id) is not None
        incoming = _job(PLAIN, "jd-drop")
        replaced = await upsert_job(session, incoming)
        assert replaced.id == saved.id
        assert replaced.id is not None
        assert await get_structured_jd(session, replaced.id) is None


async def test_structured_jd_failure_does_not_stop_ingestion(
    db_ready: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    from scraper.ingest import run_ingestion

    async def boom(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("structured jd down")

    async def one_posting(*_args: object, **_kwargs: object) -> list[RawPosting]:
        return [
            RawPosting(
                source=Source.linkedin,
                external_id="ingest-sjd",
                title="Product Manager Intern",
                company="Acme",
                location="Remote",
                url="https://example.com/ingest-sjd",
                description_clean=GOOD,
            )
        ]

    monkeypatch.setattr("scraper.ingest.fetch_linkedin_indeed", one_posting)
    monkeypatch.setattr("scraper.ingest.attach_structured_jd", boom)
    summary = await run_ingestion(include_workday=False)
    assert summary.errors == []
    assert summary.upserted == 1

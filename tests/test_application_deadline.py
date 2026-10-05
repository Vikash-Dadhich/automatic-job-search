"""Conservative application-deadline extraction. Not a ranking input."""

from __future__ import annotations

import pytest

from core.db import Job, Source, Status, session_scope, upsert_job
from scorer.priority import _structured_view
from scraper.application_deadline import DEADLINE_EXTRACTION_VERSION, extract_application_deadline
from scraper.structured_jd import StructuredJdDocument, attach_structured_jd, extract_structured_jd
from scraper.textclean import content_hash

_FILLER = (
    " The team reviews weekly notes and shares updates with the group about the work."
)


def _pad(body: str) -> str:
    text = body.strip()
    while len(text) < 80:
        text += _FILLER
    return text


def _read(body: str, *, jd_status: str | None = "present"):
    return extract_application_deadline(_pad(body), jd_status=jd_status)


def test_observed_explicit_deadlines() -> None:
    cases = (
        ("Deadline to Apply: 10/16/26", "2026-10-16", "deadline_to_apply"),
        ("Application Deadline: October 30, 2026", "2026-10-30", "application_deadline"),
        (
            "application window for this opening will close on: 09/20/2026",
            "2026-09-20",
            "application_window_close",
        ),
        ("Recruiting for this role ends on 9/30/2026", "2026-09-30", "recruiting_ends"),
        ("posted until 09/25/2026", "2026-09-25", "posted_until"),
        ("Job Posting Expiration Date: 10/30/2026", "2026-10-30", "posting_expiration"),
        ("must be submitted by 12/19/2026", "2026-12-19", "must_be_submitted_by"),
        ("Close Date: 10/04/2026", "2026-10-04", "close_date"),
        ("Apply by January 10, 2027", "2027-01-10", "apply_by"),
    )
    for body, expected, rule in cases:
        reading = _read(body)
        assert reading.state == "CONFIRMED", body
        assert reading.deadline_date == expected
        assert reading.rule == rule
        assert reading.version == DEADLINE_EXTRACTION_VERSION
        assert reading.evidence


def test_month_name_and_numeric_dates() -> None:
    named = _read("Closing Date: October 12, 2026")
    numeric = _read("Applications close: 24 Oct 2026")
    assert named.deadline_date == "2026-10-12"
    assert numeric.deadline_date == "2026-10-24"
    assert named.state == numeric.state == "CONFIRMED"


def test_missing_year_stays_ambiguous_without_a_date() -> None:
    reading = _read("Applications will close on 18th October")
    assert reading.state == "AMBIGUOUS"
    assert reading.deadline_date is None
    assert reading.evidence
    assert "18th October" in (reading.evidence or "")


def test_markdown_split_year_is_kept() -> None:
    reading = _read("The application deadline is **September 28** **th** **, 2026**")
    assert reading.state == "CONFIRMED"
    assert reading.deadline_date == "2026-09-28"


def test_invalid_calendar_date_is_ambiguous() -> None:
    reading = _read("Application Deadline: February 31, 2026")
    assert reading.state == "AMBIGUOUS"
    assert reading.deadline_date is None
    assert reading.evidence


def test_date_far_from_the_phrase_is_ambiguous() -> None:
    body = "The application deadline is listed in the portal. " + ("note " * 40)
    body += "The office calendar shows October 30, 2026."
    reading = extract_application_deadline(body, jd_status="present")
    assert reading.state == "AMBIGUOUS"
    assert reading.deadline_date is None


def test_posting_and_revision_dates_are_not_deadlines() -> None:
    posting = _read("Job Posting Date: 9/17/2026")
    revised = _read("Last revised: 07/27/2026")
    live = _read("Date live: 09/09/2026")
    assert posting.state == revised.state == live.state == "NOT_FOUND"
    assert posting.deadline_date is revised.deadline_date is live.deadline_date is None


def test_internship_and_graduation_dates_are_not_deadlines() -> None:
    start = _read("Start Date: August 2nd, 2027")
    season = _read("Employment Dates: May or June 2027 to August 2027")
    graduation = _read("Anticipated graduation date between December 2027 and June 2028")
    assert start.state == season.state == graduation.state == "NOT_FOUND"


def test_interview_deadline_is_not_an_application_deadline() -> None:
    reading = _read(
        "Video interview submissions are due no later than October 16th 2026"
    )
    assert reading.state == "NOT_FOUND"
    assert reading.deadline_date is None


def test_meet_deadlines_is_not_an_application_deadline() -> None:
    reading = _read("Self-motivated to meet project deadlines and keep the details straight.")
    assert reading.state == "NOT_FOUND"


def test_phrase_without_a_date_is_ambiguous() -> None:
    reading = _read("Applications must be submitted prior to the closing date.")
    assert reading.state == "AMBIGUOUS"
    assert reading.deadline_date is None
    assert reading.rule == "closing_date"


def test_empty_and_unusable_descriptions() -> None:
    empty = extract_application_deadline("", jd_status="present")
    missing = extract_application_deadline(_pad("Apply by October 1, 2026"), jd_status="missing")
    suspicious = extract_application_deadline("Apply by October 1, 2026", jd_status="suspicious")
    short = extract_application_deadline("Apply by October 1, 2026")
    assert empty.state == missing.state == suspicious.state == short.state == "UNUSABLE"
    assert empty.deadline_date is None


def test_structured_document_stores_the_deadline_and_ignores_priority() -> None:
    document = extract_structured_jd(
        _pad("Deadline to Apply: 10/16/26"),
        jd_status="present",
    )
    assert document.application_deadline.state == "CONFIRMED"
    assert document.application_deadline.deadline_date == "2026-10-16"
    view = _structured_view(document)
    assert view is not None
    assert "application_deadline" not in view


def test_older_document_without_the_field_still_loads() -> None:
    document = extract_structured_jd(
        _pad("The team meets each week to review notes and share updates with the group."),
        jd_status="present",
    )
    raw = document.model_dump()
    raw.pop("application_deadline")
    loaded = StructuredJdDocument.model_validate(raw)
    assert loaded.application_deadline.state == "NOT_FOUND"
    assert loaded.application_deadline.deadline_date is None
    assert loaded.education.state == document.education.state


def test_deadline_failure_does_not_drop_the_rest_of_the_reading(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def boom(*_args: object, **_kwargs: object):
        raise RuntimeError("deadline parser down")

    monkeypatch.setattr("scraper.structured_jd.extract_application_deadline", boom)
    document = extract_structured_jd(
        _pad("Required qualifications\n- Bachelor's degree required\n"),
        jd_status="present",
    )
    assert document.application_deadline.state == "UNUSABLE"
    assert document.application_deadline.rule == "extract_failed"
    assert document.education.bachelors == "required"
    assert document.availability == "available"


async def test_deadline_persists_on_the_structured_row(db_ready: object) -> None:
    del db_ready
    text = _pad("Application Deadline: October 30, 2026")
    async with session_scope() as session:
        saved = await upsert_job(
            session,
            Job(
                source=Source.indeed,
                external_id="deadline-1",
                title="Intern",
                company="Novonesis",
                url="https://jobs.example.com/deadline-1",
                description_clean=text,
                content_hash=content_hash(text),
                jd_status="present",
                status=Status.discovered,
            ),
        )
        assert saved.id is not None
        row = await attach_structured_jd(session, saved)
        assert row is not None
        stored = row.document["application_deadline"]
        assert stored["state"] == "CONFIRMED"
        assert stored["deadline_date"] == "2026-10-30"
        assert stored["version"] == DEADLINE_EXTRACTION_VERSION
        assert stored["rule"] == "application_deadline"
        assert "October 30, 2026" in stored["evidence"]

"""Tests for Workday recency helpers (no network)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from config.targets import WorkdayTenant
from scraper.workday_rest import (
    _as_text,
    _company_name,
    _is_recent_posted_on,
    _parse_start_date,
    _within_hours,
)


def test_is_recent_posted_on_variants() -> None:
    assert _is_recent_posted_on("Posted Today") is True
    assert _is_recent_posted_on("Posted 2 Hours Ago") is True
    assert _is_recent_posted_on("Posted Yesterday", max_hours=24) is True
    assert _is_recent_posted_on("Posted 3 Days Ago", max_hours=24) is False
    assert _is_recent_posted_on("Posted 30+ Days Ago") is False
    assert _is_recent_posted_on(None) is True


def test_parse_start_date() -> None:
    dt = _parse_start_date("2026-09-01")
    assert dt is not None
    assert dt.year == 2026 and dt.month == 9 and dt.day == 1
    assert dt.tzinfo is not None
    assert _parse_start_date(None) is None
    assert _parse_start_date("not-a-date") is None


def test_within_hours() -> None:
    now = datetime.now(UTC)
    assert _within_hours(now - timedelta(hours=12), max_hours=24) is True
    assert _within_hours(now - timedelta(hours=48), max_hours=24) is False
    assert _within_hours(None, max_hours=24) is True


def test_as_text_coercion() -> None:
    assert _as_text(None) is None
    assert _as_text("  Seattle, WA  ") == "Seattle, WA"
    assert _as_text({"descriptor": "Austin, TX"}) == "Austin, TX"
    assert _as_text({"name": "Remote"}) == "Remote"


def test_company_name_ignores_location_field() -> None:
    tenant = WorkdayTenant(
        name="Acme Corp",
        url="https://acme.wd1.myworkdayjobs.com/External",
    )
    # jobRequisitionLocation must NOT be used as company
    name = _company_name(
        tenant,
        {"jobRequisitionLocation": {"descriptor": "Seattle, WA"}},
    )
    assert name == "Acme Corp"

    name2 = _company_name(
        tenant,
        {"hiringOrganization": {"descriptor": "Acme Labs"}},
    )
    assert name2 == "Acme Labs"

"""Greenhouse, Lever and Ashby board readers. Mocked HTTP, no network."""

from __future__ import annotations

import html
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import httpx
import pytest
from pydantic import ValidationError
from tenacity import wait_none

from config.profile import load_profile
from config.settings import get_settings
from config.targets import AtsBoard, Targets, load_targets
from core.db import Source, Status, get_job_by_source_id, session_scope
from scraper import ats_boards
from scraper.ats_boards import (
    BoardRun,
    board_url,
    fetch_all_boards,
    keep_posting,
    parse_board,
)
from scraper.ingest import run_ingestion
from scraper.models import RawPosting

_NOW = datetime(2026, 10, 25, tzinfo=UTC)

_GREENHOUSE = {
    "jobs": [
        {
            "id": 101,
            "title": "Product Manager Intern, Summer 2027",
            "absolute_url": "https://boards.greenhouse.io/acme/jobs/101",
            "location": {"name": "Seattle, WA"},
            "first_published": "2026-10-24T12:00:00-04:00",
            "content": html.escape("<p>Own a roadmap with engineering and design.</p>"),
        },
        {
            "id": 102,
            "title": "Senior Software Engineer",
            "absolute_url": "https://boards.greenhouse.io/acme/jobs/102",
            "location": {"name": "Remote"},
            "updated_at": "2026-10-20T00:00:00Z",
            "content": "",
        },
    ]
}

_LEVER = [
    {
        "id": "abc-1",
        "text": "Strategy Intern (MBA)",
        "hostedUrl": "https://jobs.lever.co/acme/abc-1",
        "categories": {"location": "New York, NY"},
        "createdAt": 1_761_350_400_000,
        "description": "<p>Support the strategy team.</p>",
        "lists": [{"text": "You will", "content": "<li>Run analyses</li>"}],
        "additional": "<p>Equal opportunity employer.</p>",
    },
    {"id": "abc-2", "text": "Recruiter", "hostedUrl": "https://jobs.lever.co/acme/abc-2"},
]

_ASHBY = {
    "jobs": [
        {
            "id": "x1",
            "title": "Business Operations Intern",
            "jobUrl": "https://jobs.ashbyhq.com/acme/x1",
            "isRemote": True,
            "publishedAt": "2026-10-23T09:00:00.000+00:00",
            "descriptionHtml": "<p>Help run operations.</p>",
        },
        {
            "id": "x2",
            "title": "Hidden Intern",
            "jobUrl": "https://jobs.ashbyhq.com/acme/x2",
            "isListed": False,
        },
    ]
}


def _board(provider: str, token: str = "acme") -> AtsBoard:
    return AtsBoard(name="Acme", provider=provider, token=token)


def test_board_urls() -> None:
    assert board_url(_board("greenhouse")).endswith("/boards/acme/jobs?content=true")
    assert board_url(_board("lever")) == "https://api.lever.co/v0/postings/acme?mode=json"
    assert board_url(_board("ashby")).endswith("/job-board/acme")


def test_greenhouse_parse_unescapes_the_description() -> None:
    rows = parse_board(_board("greenhouse"), _GREENHOUSE)
    assert [row.external_id for row in rows] == ["acme:101", "acme:102"]
    first = rows[0]
    assert first.source == Source.greenhouse
    assert first.company == "Acme"
    assert first.location == "Seattle, WA"
    assert first.description_html == "<p>Own a roadmap with engineering and design.</p>"
    assert first.posted_at is not None and first.posted_at.tzinfo is not None
    assert first.tenant == "acme"


def test_lever_parse_joins_description_lists_and_epoch_time() -> None:
    rows = parse_board(_board("lever"), _LEVER)
    assert len(rows) == 2
    assert rows[0].source == Source.lever
    assert rows[0].location == "New York, NY"
    assert "Run analyses" in (rows[0].description_html or "")
    assert rows[0].posted_at == datetime.fromtimestamp(1_761_350_400, tz=UTC)


def test_ashby_parse_skips_unlisted_and_marks_remote() -> None:
    rows = parse_board(_board("ashby"), _ASHBY)
    assert [row.external_id for row in rows] == ["acme:x1"]
    assert rows[0].location == "Remote"
    assert rows[0].source == Source.ashby


@pytest.mark.parametrize("provider", ["greenhouse", "lever", "ashby"])
def test_unexpected_payload_shapes_give_no_rows(provider: str) -> None:
    for junk in (None, 7, "text", [], {}, {"jobs": "no"}, {"jobs": [1, None]}):
        assert parse_board(_board(provider), junk) == []


def _posting(title: str, posted: datetime | None) -> RawPosting:
    return RawPosting(
        source=Source.greenhouse,
        external_id=title,
        title=title,
        company="Acme",
        url="https://example.com/x",
        posted_at=posted,
    )


def test_keep_posting_needs_an_internship_signal_and_respects_age() -> None:
    fresh = _NOW - timedelta(hours=5)
    old = _NOW - timedelta(days=10)
    assert keep_posting(_posting("Product Manager Intern", fresh), max_age_hours=None)
    assert not keep_posting(_posting("International Product Manager", fresh), max_age_hours=None)
    assert not keep_posting(_posting("Senior Product Manager", fresh), max_age_hours=None)
    assert keep_posting(_posting("Product Manager Intern", old), max_age_hours=None)
    assert not keep_posting(_posting("Product Manager Intern", old), max_age_hours=48, now=_NOW)
    assert keep_posting(_posting("Product Manager Intern", None), max_age_hours=48, now=_NOW)


def test_board_config_is_validated() -> None:
    with pytest.raises(ValidationError):
        AtsBoard(name="X", provider="workable", token="x")
    with pytest.raises(ValidationError):
        AtsBoard(name="X", provider="lever", token="a/b")


def test_shipped_boards_are_valid_and_unique() -> None:
    boards = load_targets().ats_boards
    assert len(boards) >= 20
    keys = [(b.provider, b.token) for b in boards]
    assert len(keys) == len(set(keys))


def test_boards_are_off_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ENABLE_ATS_BOARDS", raising=False)
    get_settings.cache_clear()
    assert get_settings().enable_ats_boards is False
    assert get_settings().ats_max_age_hours is None


def _client(handler: Any) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


async def test_fetch_all_boards_isolates_failures(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ats_boards._get.retry, "wait", wait_none())

    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        if "greenhouse" in url and "/boards/good/" in url:
            return httpx.Response(200, json=_GREENHOUSE)
        if "greenhouse" in url and "/boards/gone/" in url:
            return httpx.Response(404)
        if "lever" in url:
            return httpx.Response(503)
        return httpx.Response(200, text="<html>not json</html>")

    boards = [
        AtsBoard(name="Good", provider="greenhouse", token="good"),
        AtsBoard(name="Gone", provider="greenhouse", token="gone"),
        AtsBoard(name="Busy", provider="lever", token="busy"),
        AtsBoard(name="Odd", provider="ashby", token="odd"),
    ]
    async with _client(handler) as client:
        run = await fetch_all_boards(boards, client=client)
    assert isinstance(run, BoardRun)
    assert [p.external_id for p in run.postings] == ["good:101"]
    assert run.seen == 2
    assert run.kept == 1
    assert run.not_found == ["Gone"]
    assert sorted(run.failed) == ["Busy", "Odd"]


async def test_ingestion_saves_board_postings(
    db_ready: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    del db_ready
    profile = load_profile()
    posting = parse_board(_board("greenhouse"), _GREENHOUSE)[0]
    run = BoardRun(postings=[posting], not_found=["Gone"], failed=["Busy"], seen=2, kept=1)

    async def fake_fetch(*_args: object, **_kwargs: object) -> BoardRun:
        return run

    async def no_enrich(*_args: object, **_kwargs: object) -> None:
        return None

    monkeypatch.setattr("scraper.ingest.fetch_all_boards", fake_fetch)
    monkeypatch.setattr("scraper.ingest.attach_company_intelligence", no_enrich)
    monkeypatch.setattr("scraper.ingest.attach_eligibility", no_enrich)
    monkeypatch.setattr("scraper.ingest.attach_structured_jd", no_enrich)
    monkeypatch.setattr("scraper.ingest._apply_role_classification", no_enrich)

    targets = Targets.model_validate(
        {
            "search": {"terms": ["x"]},
            "ats_boards": [{"name": "Acme", "provider": "greenhouse", "token": "acme"}],
        }
    )
    summary = await run_ingestion(
        targets=targets,
        profile=profile,
        include_jobspy=False,
        include_workday=False,
        include_boards=True,
    )
    assert summary.upserted == 1
    assert summary.by_source == {"boards": 1}
    assert summary.boards_not_found == ["Gone"]
    assert any("Busy" in error for error in summary.errors)
    async with session_scope() as session:
        saved = await get_job_by_source_id(session, Source.greenhouse, "acme:101")
    assert saved is not None
    assert saved.status in {Status.discovered, Status.filtered_out}
    assert saved.company == "Acme"


async def test_ingestion_skips_boards_when_off(
    db_ready: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    del db_ready
    called = False

    async def fake_fetch(*_args: object, **_kwargs: object) -> BoardRun:
        nonlocal called
        called = True
        return BoardRun()

    monkeypatch.setattr("scraper.ingest.fetch_all_boards", fake_fetch)
    monkeypatch.delenv("ENABLE_ATS_BOARDS", raising=False)
    get_settings.cache_clear()
    targets = Targets.model_validate(
        {
            "search": {"terms": ["x"]},
            "ats_boards": [{"name": "Acme", "provider": "greenhouse", "token": "acme"}],
        }
    )
    await run_ingestion(
        targets=targets, profile=load_profile(), include_jobspy=False, include_workday=False
    )
    assert called is False

"""Simplify Summer 2027 list parsing, board discovery, and catch-up mode. Offline."""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest

from config.profile import load_profile
from config.settings import get_settings
from config.targets import AtsBoard, Targets
from scraper.ats_boards import BoardRun, check_boards
from scraper.ingest import run_ingestion
from scraper.simplify_list import (
    board_from_url,
    discover_boards,
    fetch_simplify_rows,
    parse_simplify_readme,
)

_README = """
# Summer 2027 Internships

## 💻 Software Engineering Internship Roles

<table>
<thead><tr><th>Company</th><th>Role</th><th>Location</th>
<th>Application</th><th>Age</th></tr></thead>
<tbody>
<tr><td><strong><a href="https://simplify.jobs/c/Epic">Epic Games</a></strong></td>
<td>Tools Programmer Intern</td><td>Cary, NC</td>
<td><a href="https://boards.greenhouse.io/epic/jobs/1"><img alt="Apply"></a></td><td>1d</td></tr>
</tbody></table>

## 📱 Product Management Internship Roles

<table>
<thead><tr><th>Company</th><th>Role</th><th>Location</th>
<th>Application</th><th>Age</th></tr></thead>
<tbody>
<tr>
<td><strong><a href="https://simplify.jobs/c/Acme">🔥 Acme</a></strong></td>
<td>Product Manager Intern 🎓</td>
<td>Seattle, WA<br>Remote in USA</td>
<td><div align="center">
<a href="https://job-boards.greenhouse.io/acme/jobs/55?gh_src=x"><img alt="Apply"></a>
<a href="https://simplify.jobs/p/abc"><img alt="Simplify"></a></div></td><td>2d</td>
</tr>
<tr>
<td>↳</td><td>Associate PM Intern 🛂</td><td>New York, NY</td>
<td><a href="https://jobs.lever.co/acme-labs/uuid-1">Apply</a></td><td>3d</td>
</tr>
<tr>
<td><a href="https://simplify.jobs/c/Beta">Beta Corp</a></td>
<td>Product Intern 🔒</td><td>Austin, TX</td>
<td><a href="https://jobs.ashbyhq.com/beta/uuid-2">Apply</a></td><td>9d</td>
</tr>
<tr>
<td><a href="https://simplify.jobs/c/Gamma">Gamma</a></td>
<td>Product Strategy Intern 🇺🇸</td><td>Remote</td>
<td><a href="https://gamma.wd5.myworkdayjobs.com/en-US/Careers/job/x">Apply</a></td><td>4d</td>
</tr>
<tr><td>Broken</td></tr>
</tbody></table>
"""


def test_parse_reads_only_the_product_section_by_default() -> None:
    rows = parse_simplify_readme(_README)
    assert [(r.company, r.role) for r in rows] == [
        ("Acme", "Product Manager Intern"),
        ("Acme", "Associate PM Intern"),
        ("Beta Corp", "Product Intern"),
        ("Gamma", "Product Strategy Intern"),
    ]
    first, second, third, fourth = rows
    assert first.location == "Seattle, WA; Remote in USA"
    assert first.url.startswith("https://job-boards.greenhouse.io/acme/jobs/55")
    assert second.no_sponsorship and not second.closed
    assert third.closed
    assert fourth.citizens_only


def test_parse_can_read_every_section() -> None:
    rows = parse_simplify_readme(_README, only_product=False)
    assert rows[0].company == "Epic Games"
    assert len(rows) == 5


def test_unknown_markup_gives_no_rows() -> None:
    assert parse_simplify_readme("") == []
    assert parse_simplify_readme("## Product Management\nno table here") == []


@pytest.mark.parametrize(
    ("url", "provider", "token"),
    [
        ("https://boards.greenhouse.io/acme/jobs/1", "greenhouse", "acme"),
        ("https://job-boards.greenhouse.io/acme/jobs/1?x=1", "greenhouse", "acme"),
        ("https://jobs.lever.co/acme-labs/abc", "lever", "acme-labs"),
        ("https://jobs.ashbyhq.com/beta/abc", "ashby", "beta"),
    ],
)
def test_board_from_url(url: str, provider: str, token: str) -> None:
    board = board_from_url(url, "Co")
    assert board is not None
    assert (board.provider, board.token) == (provider, token)


@pytest.mark.parametrize(
    "url",
    ["https://gamma.wd5.myworkdayjobs.com/en-US/Careers/job/x", "https://example.com/careers", "x"],
)
def test_board_from_url_ignores_other_sites(url: str) -> None:
    assert board_from_url(url, "Co") is None


def test_discover_skips_closed_known_and_duplicate_boards() -> None:
    rows = parse_simplify_readme(_README)
    found = discover_boards(rows, known={("greenhouse", "acme")})
    assert [(b.provider, b.token) for b in found] == [("lever", "acme-labs")]
    found_all = discover_boards(rows, known=set())
    assert [(b.provider, b.token) for b in found_all] == [
        ("greenhouse", "acme"),
        ("lever", "acme-labs"),
    ]
    assert len(discover_boards(rows, known=set(), limit=1)) == 1


async def test_fetch_rows_handles_http_failure() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(404)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        assert await fetch_simplify_rows(client) == []

    def ok(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=_README)

    async with httpx.AsyncClient(transport=httpx.MockTransport(ok)) as client:
        assert len(await fetch_simplify_rows(client)) == 4


async def test_ingestion_adds_discovered_boards(
    db_ready: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    del db_ready
    seen: dict[str, object] = {}

    async def fake_fetch(boards: list[AtsBoard], **kwargs: object) -> BoardRun:
        seen["boards"] = [(b.provider, b.token) for b in boards]
        seen["age"] = kwargs.get("max_age_hours")
        return BoardRun()

    async def fake_rows() -> list[object]:
        return parse_simplify_readme(_README)

    monkeypatch.setattr("scraper.ingest.fetch_all_boards", fake_fetch)
    monkeypatch.setattr("scraper.ingest.fetch_simplify_rows", fake_rows)
    monkeypatch.setenv("SIMPLIFY_DISCOVERY", "true")
    monkeypatch.setenv("ENABLE_ATS_BOARDS", "true")
    monkeypatch.delenv("ATS_MAX_AGE_HOURS", raising=False)
    get_settings.cache_clear()
    targets = Targets.model_validate(
        {
            "search": {"terms": ["x"]},
            "ats_boards": [{"name": "Acme", "provider": "greenhouse", "token": "acme"}],
        }
    )
    summary = await run_ingestion(
        targets=targets, profile=load_profile(), include_jobspy=False, include_workday=False
    )
    assert seen["boards"] == [("greenhouse", "acme"), ("lever", "acme-labs")]
    assert seen["age"] == 36
    assert summary.boards_discovered == 1
    assert summary.mode == "daily"


async def test_catchup_mode_looks_back_a_month_without_a_board_age_limit(
    db_ready: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    del db_ready
    seen: dict[str, object] = {}

    async def fake_fetch(boards: list[AtsBoard], **kwargs: object) -> BoardRun:
        seen["age"] = kwargs.get("max_age_hours", "missing")
        return BoardRun()

    monkeypatch.setattr("scraper.ingest.fetch_all_boards", fake_fetch)
    monkeypatch.setenv("INGEST_MODE", "catchup")
    monkeypatch.setenv("ENABLE_ATS_BOARDS", "true")
    monkeypatch.delenv("ATS_MAX_AGE_HOURS", raising=False)
    monkeypatch.delenv("SIMPLIFY_DISCOVERY", raising=False)
    get_settings.cache_clear()
    targets = Targets.model_validate(
        {
            "search": {"terms": ["x"], "hours_old": 36},
            "ats_boards": [{"name": "Acme", "provider": "greenhouse", "token": "acme"}],
        }
    )
    summary = await run_ingestion(
        targets=targets, profile=load_profile(), include_jobspy=False, include_workday=False
    )
    assert seen["age"] is None
    assert summary.hours_old == 720
    assert summary.mode == "catchup"


async def test_check_boards_reports_each_board(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_board(
        _client: object, board: AtsBoard, **_kwargs: object
    ) -> tuple[list[object], int, str]:
        return ([], 0, "not_found") if board.token == "gone" else ([], 9, "ok")

    monkeypatch.setattr("scraper.ats_boards.fetch_board", fake_board)
    boards = [
        AtsBoard(name="Gone", provider="lever", token="gone"),
        AtsBoard(name="Here", provider="ashby", token="here"),
    ]
    results = await check_boards(boards)
    assert [(r["name"], r["status"], r["open_roles"]) for r in results] == [
        ("Gone", "not_found", 0),
        ("Here", "ok", 9),
    ]

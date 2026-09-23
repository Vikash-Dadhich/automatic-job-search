"""Offline tests for LinkedIn profile HTML parse and peer discovery."""

from __future__ import annotations

from pathlib import Path

import pytest

from scraper.linkedin_people import (
    discover_peers,
    parse_profile,
    parse_profile_html,
    parse_profile_json,
)

FIXTURE = Path(__file__).parent / "fixtures" / "linkedin_profile.html"


def test_parse_profile_html_fixture() -> None:
    html = FIXTURE.read_text(encoding="utf-8")
    raw = parse_profile_html(html, "https://www.linkedin.com/in/janedoe")
    assert raw.headline == "Jane Doe"
    assert "Python" in raw.skills_text or "Python" in raw.full_text
    assert "Experience" in raw.full_text or raw.experience_text


def test_parse_profile_json() -> None:
    data = parse_profile_json(
        '{"full_name":"Jane","current_title":"SE","years_experience":3,'
        '"companies":["Acme"],"education_level":"master","skills":["Python"],'
        '"seniority":"mid","headline":"SE"}',
        "https://www.linkedin.com/in/janedoe",
    )
    assert data.full_name == "Jane"
    assert data.years_experience == 3
    assert data.skills == ["Python"]


@pytest.mark.asyncio
async def test_parse_profile_heuristic_without_client() -> None:
    html = FIXTURE.read_text(encoding="utf-8")
    raw = parse_profile_html(html, "https://www.linkedin.com/in/janedoe")
    peer = await parse_profile(raw, client=None)
    assert peer.url.endswith("janedoe")
    assert peer.skills or peer.headline


def test_discover_peers_semi_auto(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_LINKEDIN_SCRAPE", "true")
    from config.settings import get_settings

    get_settings.cache_clear()
    urls = discover_peers(
        urls=[
            "https://www.linkedin.com/in/a",
            "https://www.linkedin.com/in/b",
            "https://www.linkedin.com/in/a",
        ]
    )
    assert urls == [
        "https://www.linkedin.com/in/a",
        "https://www.linkedin.com/in/b",
    ]


def test_scrape_requires_flag(monkeypatch) -> None:
    monkeypatch.setenv("ENABLE_LINKEDIN_SCRAPE", "false")
    from config.settings import get_settings

    get_settings.cache_clear()

    from scraper.linkedin_people import scrape_profile

    with pytest.raises(RuntimeError, match="disabled"):
        import asyncio

        asyncio.run(scrape_profile("https://www.linkedin.com/in/x"))

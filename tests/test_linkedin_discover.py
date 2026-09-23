"""Tests for LinkedIn people-search URL building and profile URL extraction."""

from __future__ import annotations

from scraper.linkedin_people import build_people_search_url, extract_profile_urls


def test_build_people_search_url_encodes_keywords() -> None:
    url = build_people_search_url(
        title="Product Manager",
        location="Seattle, WA",
    )
    assert "linkedin.com/search/results/people/" in url
    assert "Product" in url or "Product%20Manager" in url or "Product+Manager" in url
    assert "Seattle" in url


def test_extract_profile_urls_dedupes_and_caps() -> None:
    html = """
    <a href="https://www.linkedin.com/in/alice-pm/">Alice</a>
    <a href="https://www.linkedin.com/in/alice-pm/?miniProfileUrn=x">Alice again</a>
    <a href="https://www.linkedin.com/in/bob-smith">Bob</a>
    <a href="https://linkedin.com/in/carol">Carol</a>
    <a href="https://www.linkedin.com/company/visa">not a person</a>
    """
    urls = extract_profile_urls(html, max_peers=2)
    assert len(urls) == 2
    assert all("/in/" in u for u in urls)
    assert urls[0].endswith("alice-pm")


def test_extract_profile_urls_empty() -> None:
    assert extract_profile_urls("<html></html>", max_peers=5) == []

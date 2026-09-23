"""Tests for HTML → text cleaning and section extraction."""

from __future__ import annotations

from scraper.textclean import content_hash, extract_sections, html_to_text

SAMPLE_HTML = """
<html><body>
<nav>Ignore nav</nav>
<script>bad()</script>
<style>.x{}</style>
<h2>Responsibilities</h2>
<p>Build APIs in Python and ship features.</p>
<h2>Requirements</h2>
<p>3+ years Python. Strong SQL skills required.</p>
<h2>Qualifications</h2>
<ul><li>BS in Computer Science</li></ul>
<footer>copyright 2026</footer>
</body></html>
"""


def test_html_to_text_strips_boilerplate() -> None:
    text = html_to_text(SAMPLE_HTML)
    assert "bad()" not in text
    assert "Ignore nav" not in text
    assert "copyright" not in text
    assert "Build APIs" in text
    assert "3+ years Python" in text


def test_extract_sections_keeps_known_headers() -> None:
    text = html_to_text(SAMPLE_HTML)
    sections = extract_sections(text)
    assert "Responsibilities" in sections
    assert "Requirements" in sections
    assert "Qualifications" in sections
    assert "Build APIs" in sections


def test_extract_sections_fallback_without_headers() -> None:
    plain = "Just a plain job description with no section headers at all."
    assert extract_sections(plain) == plain


def test_content_hash_stable() -> None:
    a = content_hash("Hello World")
    b = content_hash("Hello World")
    c = content_hash("hello world")  # normalized to lower
    assert a == b
    assert a == c
    assert a != content_hash("different")

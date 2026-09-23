"""Tests for the shared matching / truncation helpers."""

from __future__ import annotations

from core.textmatch import (
    company_matches,
    contains_phrase,
    is_remote_location,
    location_matches,
    truncate_middle,
)


def test_company_matches_ignores_legal_suffixes() -> None:
    assert company_matches("Google", "Google LLC")
    assert company_matches("Barclays Bank", "Barclays")
    assert company_matches("Acme Inc.", "acme")


def test_company_matches_rejects_lookalikes() -> None:
    """The substring blocklist used to drop MetLife whenever Meta was excluded."""
    assert not company_matches("MetLife", "Meta")
    assert not company_matches("Microsoft", "Micro")
    assert not company_matches("", "Meta")


def test_contains_phrase_is_word_bounded() -> None:
    assert contains_phrase("I would delve into this", "delve")
    assert not contains_phrase("delverton systems", "delve")
    assert contains_phrase("We are thrilled to apply models", "thrilled to apply")


def test_is_remote_location_word_bounded() -> None:
    assert is_remote_location("Remote - US")
    assert is_remote_location("Work From Home")
    assert not is_remote_location("Remoteville, IN")


def test_location_matches_respects_state() -> None:
    assert location_matches("Portland, OR", "Portland, OR")
    assert not location_matches("Portland, OR", "Portland, ME")
    # Without a state on either side, city agreement is enough.
    assert location_matches("Seattle, WA", "Seattle")
    assert location_matches("Remote - US", "remote")
    assert not location_matches("Austin, TX", "Seattle, WA")


def test_truncate_middle_keeps_both_ends() -> None:
    text = "START" + ("x" * 5000) + "END"
    out = truncate_middle(text, 500)
    assert out.startswith("START")
    assert out.endswith("END")
    assert len(out) <= 500


def test_truncate_middle_noop_when_short() -> None:
    assert truncate_middle("short text", 500) == "short text"

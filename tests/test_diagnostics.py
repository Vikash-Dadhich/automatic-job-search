"""Secret-free profile and config identity."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from config.diagnostics import (
    effective_baseline,
    effective_config_hash,
    profile_hash,
    write_effective_baseline,
)
from config.settings import get_settings


def test_profile_hash_is_stable() -> None:
    first = profile_hash()
    second = profile_hash()
    assert first == second
    assert len(first) == 64
    int(first, 16)


def test_config_hash_changes_when_internship_only_changes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("INTERNSHIP_ONLY", "false")
    get_settings.cache_clear()
    off = effective_config_hash()
    monkeypatch.setenv("INTERNSHIP_ONLY", "true")
    get_settings.cache_clear()
    on = effective_config_hash()
    assert off != on
    get_settings.cache_clear()


def test_baseline_file_has_no_secrets(tmp_path: Path) -> None:
    path = write_effective_baseline(tmp_path / "effective_config.json")
    text = path.read_text(encoding="utf-8")
    payload = json.loads(text)
    assert payload["profile_hash"] == profile_hash()
    assert payload["effective_config_hash"] == effective_config_hash()
    assert "internship_only" in payload
    assert "scorer_model" in payload
    lowered = text.lower()
    for needle in ("sk-", "api_key", "password", "postgresql://", "bot_token", "@"):
        assert needle not in lowered
    assert "secret" not in payload


def test_effective_baseline_matches_public_fields() -> None:
    baseline = effective_baseline()
    assert set(baseline) >= {
        "profile_hash",
        "effective_config_hash",
        "internship_only",
        "scorer_model",
        "writer_model",
        "embedding_model",
        "embedding_threshold",
        "tier_one_min_score",
        "tier_two_min_score",
        "max_jd_chars",
        "vector_gate_enabled",
        "score_budget",
        "prep_pack_brief",
        "prep_pack_limit",
        "enable_apply",
        "enable_reviews",
    }

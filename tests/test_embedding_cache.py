"""Cached profile vectors: only real, unit-length vectors are trusted."""

from __future__ import annotations

import subprocess

from scorer.embeddings import load_profile_embedding, save_profile_embedding

_MODEL = "text-embedding-3-small"


def _unit(width: int) -> list[float]:
    value = width**-0.5
    return [value] * width


def test_unit_length_vector_round_trips() -> None:
    save_profile_embedding("abc", _unit(8), model=_MODEL, dimensions=8)
    assert load_profile_embedding("abc", model=_MODEL, dimensions=8) is not None


def test_all_ones_fixture_vector_is_ignored() -> None:
    save_profile_embedding("fixture", [1.0] * 768, model=_MODEL, dimensions=768)
    assert load_profile_embedding("fixture", model=_MODEL, dimensions=768) is None


def test_zero_vector_is_ignored() -> None:
    save_profile_embedding("zero", [0.0] * 8, model=_MODEL, dimensions=8)
    assert load_profile_embedding("zero", model=_MODEL, dimensions=8) is None


def test_no_cached_vector_is_tracked_in_git() -> None:
    tracked = subprocess.run(
        ["git", "ls-files", "storage/embeddings"],
        capture_output=True,
        text=True,
        check=False,
    ).stdout.split()
    assert tracked == []

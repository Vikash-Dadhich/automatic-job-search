"""Tests for human delay / typing bound helpers."""

from __future__ import annotations

import pytest

from automation.telemetry import (
    action_delay_bounds,
    human_delay,
    typing_delay_bounds,
)
from config.settings import get_settings


def test_delay_bounds_from_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ACTION_DELAY_MS_MIN", "100")
    monkeypatch.setenv("ACTION_DELAY_MS_MAX", "200")
    monkeypatch.setenv("TYPING_DELAY_MS_MIN", "10")
    monkeypatch.setenv("TYPING_DELAY_MS_MAX", "40")
    get_settings.cache_clear()

    assert action_delay_bounds() == (100, 200)
    assert typing_delay_bounds() == (10, 40)

    get_settings.cache_clear()


def test_delay_bounds_swap_when_inverted(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ACTION_DELAY_MS_MIN", "300")
    monkeypatch.setenv("ACTION_DELAY_MS_MAX", "50")
    get_settings.cache_clear()
    lo, hi = action_delay_bounds()
    assert lo == 300
    assert hi == 300
    get_settings.cache_clear()


async def test_human_delay_respects_explicit_bounds() -> None:
    slept = await human_delay(min_ms=0, max_ms=0)
    assert slept == 0.0


async def test_human_delay_jitter_in_range(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ACTION_DELAY_MS_MIN", "5")
    monkeypatch.setenv("ACTION_DELAY_MS_MAX", "15")
    get_settings.cache_clear()
    slept = await human_delay()
    assert 0.005 <= slept <= 0.015
    get_settings.cache_clear()

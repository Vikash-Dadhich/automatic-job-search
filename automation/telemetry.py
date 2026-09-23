"""Human-like delay and typing helpers for browser automation."""

from __future__ import annotations

import asyncio
import random
from typing import TYPE_CHECKING

from config.settings import get_settings

if TYPE_CHECKING:
    from playwright.async_api import Locator


def action_delay_bounds() -> tuple[int, int]:
    """Return (min_ms, max_ms) for between-action pauses."""
    settings = get_settings()
    lo = max(0, settings.action_delay_ms_min)
    hi = max(lo, settings.action_delay_ms_max)
    return lo, hi


def typing_delay_bounds() -> tuple[int, int]:
    """Return (min_ms, max_ms) for per-keystroke typing delay."""
    settings = get_settings()
    lo = max(0, settings.typing_delay_ms_min)
    hi = max(lo, settings.typing_delay_ms_max)
    return lo, hi


async def human_delay(
    *,
    min_ms: int | None = None,
    max_ms: int | None = None,
) -> float:
    """Sleep a jittered duration; return the seconds slept."""
    if min_ms is None or max_ms is None:
        lo, hi = action_delay_bounds()
        min_ms = lo if min_ms is None else min_ms
        max_ms = hi if max_ms is None else max_ms
    lo = max(0, min_ms)
    hi = max(lo, max_ms)
    delay_ms = random.randint(lo, hi) if hi > lo else lo
    seconds = delay_ms / 1000.0
    if seconds > 0:
        await asyncio.sleep(seconds)
    return seconds


async def type_like_human(locator: Locator, text: str) -> None:
    """Clear and type text with per-keystroke jitter (accessibility-friendly)."""
    lo, hi = typing_delay_bounds()
    delay_ms = random.randint(lo, hi) if hi > lo else lo
    await locator.click()
    await locator.fill("")
    if text:
        await locator.type(text, delay=delay_ms)

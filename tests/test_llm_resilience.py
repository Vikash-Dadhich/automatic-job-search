"""Tests for transient-error classification and the retry/fallback wrapper."""

from __future__ import annotations

import pytest

from scorer.clients import (
    LLMBillingError,
    LLMError,
    TruncatedCompletionError,
    call_with_resilience,
    is_permanent_account_error,
    is_transient,
    suggested_delay,
)

# Real messages captured from the Gemini API during live runs.
_RATE_LIMIT_429 = (
    "429 RESOURCE_EXHAUSTED. {'error': {'code': 429, 'message': 'You exceeded your "
    "current quota, please check your plan and billing details.'}}"
)
_DEPLETED_429 = (
    "429 RESOURCE_EXHAUSTED. {'error': {'code': 429, 'message': 'Your prepayment "
    "credits are depleted. Please go to AI Studio to manage your project and billing.'}}"
)


def test_is_transient_covers_rate_limit_and_overload() -> None:
    assert is_transient(RuntimeError("429 RESOURCE_EXHAUSTED"))
    assert is_transient(RuntimeError("503 UNAVAILABLE: model is overloaded"))
    assert is_transient(RuntimeError("500 INTERNAL"))
    assert is_transient(ConnectionError("reset"))


def test_is_transient_excludes_permanent_errors() -> None:
    assert not is_transient(ValueError("400 INVALID_ARGUMENT: bad thinking level"))
    assert not is_transient(TruncatedCompletionError("no output"))


def test_rate_limit_and_depleted_credits_are_distinguished() -> None:
    """Both are 429; only the per-minute rate limit is worth retrying."""
    assert is_transient(RuntimeError(_RATE_LIMIT_429))
    assert not is_permanent_account_error(RuntimeError(_RATE_LIMIT_429))
    assert is_permanent_account_error(RuntimeError(_DEPLETED_429))
    assert not is_transient(RuntimeError(_DEPLETED_429))


@pytest.mark.asyncio
async def test_depleted_credits_fail_fast_without_fallback() -> None:
    """Burning the whole fallback chain on a dead account wastes ~2 minutes."""
    attempts: list[str] = []

    async def broke(model: str) -> str:
        attempts.append(model)
        raise RuntimeError(_DEPLETED_429)

    with pytest.raises(LLMBillingError):
        await call_with_resilience(
            broke, models=["m1", "m2", "m3"], max_attempts=4, max_wait=0, label="test"
        )
    assert attempts == ["m1"], "must not retry or fail over on a billing error"


def test_suggested_delay_reads_server_hint() -> None:
    exc = RuntimeError("429 RESOURCE_EXHAUSTED {'retryDelay': '38s'}")
    assert suggested_delay(exc) == 38.0
    assert suggested_delay(RuntimeError("boom")) is None


@pytest.mark.asyncio
async def test_call_with_resilience_retries_then_succeeds() -> None:
    attempts: list[str] = []

    async def flaky(model: str) -> str:
        attempts.append(model)
        if len(attempts) < 3:
            raise RuntimeError("503 UNAVAILABLE")
        return "ok"

    result = await call_with_resilience(
        flaky, models=["m1"], max_attempts=4, max_wait=0, label="test"
    )
    assert result == "ok"
    assert len(attempts) == 3


@pytest.mark.asyncio
async def test_call_with_resilience_falls_through_to_next_model() -> None:
    async def only_second_works(model: str) -> str:
        if model == "m1":
            raise RuntimeError("503 UNAVAILABLE")
        return f"ok:{model}"

    result = await call_with_resilience(
        only_second_works, models=["m1", "m2"], max_attempts=2, max_wait=0, label="test"
    )
    assert result == "ok:m2"


@pytest.mark.asyncio
async def test_call_with_resilience_reraises_permanent_error() -> None:
    async def bad_request(model: str) -> str:
        raise ValueError("400 INVALID_ARGUMENT")

    with pytest.raises(ValueError, match="400"):
        await call_with_resilience(
            bad_request, models=["m1", "m2"], max_attempts=3, max_wait=0, label="test"
        )


@pytest.mark.asyncio
async def test_call_with_resilience_raises_llm_error_when_all_fail() -> None:
    async def always_down(model: str) -> str:
        raise RuntimeError("503 UNAVAILABLE")

    with pytest.raises(LLMError, match="all models failed"):
        await call_with_resilience(
            always_down, models=["m1", "m2"], max_attempts=2, max_wait=0, label="test"
        )

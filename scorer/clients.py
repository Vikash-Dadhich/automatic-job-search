"""LLM client layer: provider clients, transient-error retries, model fallback.

Resilience rules learned from live Gemini traffic:
- 503 UNAVAILABLE is common on newly released models and must be retried.
- Thinking tokens count against max_output_tokens, so a truncated reply comes
  back as finish_reason=MAX_TOKENS with unusable text instead of an error.
- 429 responses carry a server-side retryDelay that beats blind backoff.
"""

from __future__ import annotations

import asyncio
import random
import re
from dataclasses import dataclass
from typing import Any, Protocol

import structlog

from config.settings import get_settings

log = structlog.get_logger(__name__)


@dataclass
class TokenUsage:
    """Accumulated provider usage for one client instance (one scoring run)."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    cached_tokens: int = 0
    total_calls: int = 0

    def __iadd__(self, other: TokenUsage) -> TokenUsage:
        self.prompt_tokens += other.prompt_tokens
        self.completion_tokens += other.completion_tokens
        self.cached_tokens += other.cached_tokens
        self.total_calls += other.total_calls
        return self


def _as_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0

_RETRY_DELAY_RE = re.compile(r"retryDelay['\"]?\s*:\s*['\"]?(\d+(?:\.\d+)?)s", re.IGNORECASE)
_TRANSIENT_MARKERS = (
    "RESOURCE_EXHAUSTED",
    "UNAVAILABLE",
    "INTERNAL",
    "DEADLINE_EXCEEDED",
    "overloaded",
    "high demand",
)
_TRANSIENT_STATUS = frozenset({408, 429, 500, 502, 503, 504})
# Billing exhaustion also arrives as 429, but no amount of backoff fixes it.
# Matched before the transient check so a dead account fails in seconds.
_PERMANENT_MARKERS = (
    "credits are depleted",
    "credits depleted",
    "billing account",
    "API key not valid",
    "PERMISSION_DENIED",
    "API_KEY_INVALID",
)
# Raised when the model spends its whole budget on thinking and emits no answer.
TRUNCATED_MARKER = "MAX_TOKENS"


class LLMError(RuntimeError):
    """Raised when a completion cannot be obtained from any candidate model."""


class LLMBillingError(LLMError):
    """Account has no credit / invalid key — retrying and failing over is pointless."""


class TruncatedCompletionError(LLMError):
    """Model hit max_output_tokens before producing a usable answer."""


class LLMClient(Protocol):
    """Minimal async LLM interface (mockable for offline tests)."""

    async def complete(
        self,
        *,
        model: str,
        system_blocks: list[dict[str, Any]],
        user: str,
        max_tokens: int,
        temperature: float,
        json_mode: bool = False,
        json_schema: dict[str, Any] | None = None,
        thinking_level: str | None = None,
    ) -> str: ...


def _status_code(exc: BaseException) -> int | None:
    for attr in ("code", "status_code"):
        value = getattr(exc, attr, None)
        if isinstance(value, int):
            return value
    match = re.search(r"\b(4\d{2}|5\d{2})\b", str(exc))
    return int(match.group(1)) if match else None


def is_permanent_account_error(exc: BaseException) -> bool:
    """Depleted credits / bad key: surfaces as 429 or 403 but will never recover."""
    text = str(exc).lower()
    return any(marker.lower() in text for marker in _PERMANENT_MARKERS)


def is_transient(exc: BaseException) -> bool:
    """True for rate limits, overload, and server-side hiccups worth retrying."""
    if isinstance(exc, TruncatedCompletionError):
        return False
    if is_permanent_account_error(exc):
        return False
    if isinstance(exc, (asyncio.TimeoutError, ConnectionError)):
        return True
    status = _status_code(exc)
    if status is not None and status in _TRANSIENT_STATUS:
        return True
    text = str(exc)
    return any(marker in text for marker in _TRANSIENT_MARKERS)


def suggested_delay(exc: BaseException) -> float | None:
    """Server-provided retryDelay, when the API supplies one."""
    match = _RETRY_DELAY_RE.search(str(exc))
    return float(match.group(1)) if match else None


def _backoff_delay(attempt: int, exc: BaseException, max_wait: float) -> float:
    hinted = suggested_delay(exc)
    base = hinted if hinted is not None else min(2.0 * (2**attempt), max_wait)
    # Jitter avoids synchronized retries across concurrent scoring workers.
    return max(0.0, min(base, max_wait)) + random.uniform(0, 0.5)


async def call_with_resilience(
    attempt_fn: Any,
    *,
    models: list[str],
    max_attempts: int,
    max_wait: float,
    label: str,
) -> str:
    """Run attempt_fn(model) across candidate models, retrying transient errors.

    Each model gets `max_attempts` tries; persistent transient failure falls
    through to the next model so one overloaded endpoint cannot stall a run.
    """
    last_exc: BaseException | None = None
    for model_index, model in enumerate(models):
        for attempt in range(max_attempts):
            try:
                return await attempt_fn(model)
            except Exception as exc:
                last_exc = exc
                if is_permanent_account_error(exc):
                    raise LLMBillingError(
                        f"{label}: account cannot serve requests ({exc})"
                    ) from exc
                if not is_transient(exc):
                    raise
                final_attempt = attempt == max_attempts - 1
                if final_attempt:
                    log.warning(
                        "llm_model_exhausted",
                        label=label,
                        model=model,
                        attempts=max_attempts,
                        error=str(exc)[:200],
                        next_model=(
                            models[model_index + 1] if model_index + 1 < len(models) else None
                        ),
                    )
                    break
                delay = _backoff_delay(attempt, exc, max_wait)
                log.info(
                    "llm_transient_retry",
                    label=label,
                    model=model,
                    attempt=attempt + 1,
                    sleep_s=round(delay, 1),
                    error=str(exc)[:160],
                )
                await asyncio.sleep(delay)
    raise LLMError(
        f"{label}: all models failed ({', '.join(models)}); last error: {last_exc}"
    ) from last_exc


class AnthropicClient:
    """Anthropic Messages API client with prompt-caching system blocks."""

    def __init__(self, api_key: str | None = None, *, client: Any | None = None) -> None:
        self._usage = TokenUsage()
        if client is not None:
            self._client = client
            return
        settings = get_settings()
        key = (api_key if api_key is not None else settings.anthropic_api_key) or ""
        if not key.strip():
            raise ValueError("ANTHROPIC_API_KEY is empty. Set it in .env before live scoring.")
        import anthropic

        self._client = anthropic.AsyncAnthropic(api_key=key.strip())

    async def complete(
        self,
        *,
        model: str,
        system_blocks: list[dict[str, Any]],
        user: str,
        max_tokens: int,
        temperature: float,
        json_mode: bool = False,
        json_schema: dict[str, Any] | None = None,
        thinking_level: str | None = None,
    ) -> str:
        # Anthropic gets its JSON contract from the prompt; these are Gemini-only knobs.
        del json_mode, json_schema, thinking_level
        settings = get_settings()

        async def _attempt(candidate: str) -> str:
            # Anthropic SDK overloads don't accept our list[dict] system blocks cleanly
            response = await self._client.messages.create(  # type: ignore[reportCallIssue]
                model=candidate,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_blocks,
                messages=[{"role": "user", "content": user}],
            )
            self._record_anthropic_usage(response)
            parts: list[str] = []
            for block in response.content:
                text = getattr(block, "text", None)
                if text:
                    parts.append(text)
            return "".join(parts).strip()

        return await call_with_resilience(
            _attempt,
            models=[model],
            max_attempts=settings.llm_max_attempts,
            max_wait=settings.llm_retry_max_wait_s,
            label="anthropic",
        )

    @property
    def usage(self) -> TokenUsage:
        return self._usage

    def _record_anthropic_usage(self, response: Any) -> None:
        usage = getattr(response, "usage", None)
        if usage is None:
            return
        self._usage.prompt_tokens += _as_int(getattr(usage, "input_tokens", 0))
        self._usage.completion_tokens += _as_int(getattr(usage, "output_tokens", 0))
        self._usage.cached_tokens += _as_int(getattr(usage, "cache_read_input_tokens", 0))
        self._usage.total_calls += 1


class OpenAIClient:
    """OpenAI Chat Completions client. JSON scoring uses json_object mode."""

    def __init__(self, api_key: str | None = None, *, client: Any | None = None) -> None:
        self._usage = TokenUsage()
        if client is not None:
            self._client = client
            return
        settings = get_settings()
        key = (api_key if api_key is not None else settings.openai_api_key) or ""
        if not key.strip():
            raise ValueError("OPENAI_API_KEY is empty. Set it in .env before live scoring.")
        from openai import AsyncOpenAI

        self._client = AsyncOpenAI(api_key=key.strip())

    async def complete(
        self,
        *,
        model: str,
        system_blocks: list[dict[str, Any]],
        user: str,
        max_tokens: int,
        temperature: float,
        json_mode: bool = False,
        json_schema: dict[str, Any] | None = None,
        thinking_level: str | None = None,
    ) -> str:
        del json_schema, thinking_level
        settings = get_settings()
        system = system_blocks_to_text(system_blocks)

        async def _attempt(candidate: str) -> str:
            kwargs: dict[str, Any] = {
                "model": candidate,
                "max_completion_tokens": max_tokens,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            }
            # gpt-5 and o-series reject a custom temperature.
            if not candidate.startswith(("gpt-5", "o1", "o3", "o4")):
                kwargs["temperature"] = temperature
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
            if candidate.startswith(("gpt-5", "o1", "o3", "o4")):
                kwargs["reasoning_effort"] = "minimal"
            response = await self._client.chat.completions.create(**kwargs)
            self._record_openai_usage(response)
            choice = response.choices[0]
            text = (getattr(choice.message, "content", None) or "").strip()
            if text:
                return text
            # Reasoning models can spend the whole budget and return no text.
            kwargs["max_completion_tokens"] = min(max_tokens * 3, 8192)
            response = await self._client.chat.completions.create(**kwargs)
            self._record_openai_usage(response)
            choice = response.choices[0]
            text = (getattr(choice.message, "content", None) or "").strip()
            if not text:
                raise TruncatedCompletionError(f"empty response from {candidate}")
            return text

        return await call_with_resilience(
            _attempt,
            models=[model],
            max_attempts=settings.llm_max_attempts,
            max_wait=settings.llm_retry_max_wait_s,
            label="openai",
        )

    @property
    def usage(self) -> TokenUsage:
        return self._usage

    def _record_openai_usage(self, response: Any) -> None:
        usage = getattr(response, "usage", None)
        if usage is None:
            return
        self._usage.prompt_tokens += _as_int(getattr(usage, "prompt_tokens", 0))
        self._usage.completion_tokens += _as_int(getattr(usage, "completion_tokens", 0))
        details = getattr(usage, "prompt_tokens_details", None)
        self._usage.cached_tokens += _as_int(getattr(details, "cached_tokens", 0))
        self._usage.total_calls += 1


def system_blocks_to_text(system_blocks: list[dict[str, Any]]) -> str:
    """Join protocol system_blocks into a single instruction string (Gemini)."""
    parts: list[str] = []
    for block in system_blocks:
        text = block.get("text") if isinstance(block, dict) else None
        if isinstance(text, str) and text.strip():
            parts.append(text.strip())
    return "\n\n".join(parts)


class GeminiClient:
    """Google Gemini client via google-genai (maps system_blocks → system_instruction)."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        client: Any | None = None,
    ) -> None:
        # Levels rejected by a model are remembered so we stop re-sending them.
        self._unsupported_levels: set[tuple[str, str]] = set()
        self._usage = TokenUsage()
        if client is not None:
            self._client = client
            return
        settings = get_settings()
        key = (api_key if api_key is not None else settings.gemini_api_key) or ""
        if not key.strip():
            raise ValueError("GEMINI_API_KEY is empty. Set it in .env before live scoring.")
        from google import genai

        self._client = genai.Client(api_key=key.strip())

    def _build_config(
        self,
        types_mod: Any,
        *,
        model: str,
        system_instruction: str | None,
        max_tokens: int,
        temperature: float,
        json_mode: bool,
        json_schema: dict[str, Any] | None,
        thinking_level: str | None,
    ) -> Any:
        kwargs: dict[str, Any] = {
            "system_instruction": system_instruction,
            "max_output_tokens": max_tokens,
            "temperature": temperature,
        }
        if json_mode:
            kwargs["response_mime_type"] = "application/json"
            if json_schema:
                kwargs["response_schema"] = json_schema
        level = (thinking_level or "").strip().lower()
        if level and (model, level) not in self._unsupported_levels:
            try:
                kwargs["thinking_config"] = types_mod.ThinkingConfig(thinking_level=level)
            except Exception:
                log.warning("gemini_thinking_config_unsupported", level=level, model=model)
        return types_mod.GenerateContentConfig(**kwargs)

    async def complete(
        self,
        *,
        model: str,
        system_blocks: list[dict[str, Any]],
        user: str,
        max_tokens: int,
        temperature: float,
        json_mode: bool = False,
        json_schema: dict[str, Any] | None = None,
        thinking_level: str | None = None,
    ) -> str:
        from google.genai import types

        settings = get_settings()
        system_instruction = system_blocks_to_text(system_blocks) or None

        async def _attempt(candidate: str) -> str:
            budget = max_tokens
            level = thinking_level
            # One escalation: thinking consumed the budget before any answer text.
            for escalation in range(2):
                config = self._build_config(
                    types,
                    model=candidate,
                    system_instruction=system_instruction,
                    max_tokens=budget,
                    temperature=temperature,
                    json_mode=json_mode,
                    json_schema=json_schema,
                    thinking_level=level,
                )
                try:
                    response = await self._client.aio.models.generate_content(
                        model=candidate,
                        contents=user,
                        config=config,
                    )
                    self._record_gemini_usage(response)
                except Exception as exc:
                    # An unsupported thinking level is permanent for this model: drop and retry.
                    if level and "thinking level" in str(exc).lower():
                        self._unsupported_levels.add((candidate, level.strip().lower()))
                        log.warning(
                            "gemini_thinking_level_rejected", model=candidate, level=level
                        )
                        level = None
                        continue
                    raise

                text = (getattr(response, "text", None) or "").strip()
                if text:
                    return text

                if _finish_reason(response) == TRUNCATED_MARKER and escalation == 0:
                    budget = min(budget * 3, 8192)
                    level = _lower_thinking(level)
                    log.warning(
                        "gemini_truncated_retry",
                        model=candidate,
                        new_max_tokens=budget,
                        thinking_level=level,
                    )
                    continue
                raise TruncatedCompletionError(
                    f"empty response from {candidate} "
                    f"(finish_reason={_finish_reason(response)})"
                )
            raise TruncatedCompletionError(f"no usable output from {candidate}")

        models = [model, *settings.fallback_models_for(model)]
        return await call_with_resilience(
            _attempt,
            models=models,
            max_attempts=settings.llm_max_attempts,
            max_wait=settings.llm_retry_max_wait_s,
            label="gemini",
        )

    @property
    def usage(self) -> TokenUsage:
        return self._usage

    def _record_gemini_usage(self, response: Any) -> None:
        meta = getattr(response, "usage_metadata", None)
        if meta is None:
            return
        self._usage.prompt_tokens += _as_int(getattr(meta, "prompt_token_count", 0))
        self._usage.completion_tokens += _as_int(getattr(meta, "candidates_token_count", 0))
        self._usage.cached_tokens += _as_int(getattr(meta, "cached_content_token_count", 0))
        self._usage.total_calls += 1


def _finish_reason(response: Any) -> str | None:
    candidates = getattr(response, "candidates", None) or []
    if not candidates:
        return None
    reason = getattr(candidates[0], "finish_reason", None)
    if reason is None:
        return None
    return getattr(reason, "name", None) or str(reason).rsplit(".", 1)[-1]


def _lower_thinking(level: str | None) -> str | None:
    """Step thinking down so a retry spends its budget on the answer, not reasoning."""
    ladder = {"high": "low", "medium": "low", "low": "low"}
    if not level:
        return None
    return ladder.get(level.strip().lower(), level)


def build_llm_client() -> LLMClient:
    """Scoring and writing always go through OpenAI."""
    return OpenAIClient()

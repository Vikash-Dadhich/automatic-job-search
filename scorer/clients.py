"""LLM client layer: provider clients, transient-error retries, model fallback.

Resilience rules learned from live Gemini traffic:
- 503 UNAVAILABLE is common on newly released models and must be retried.
- Thinking tokens count against max_output_tokens, so a truncated reply comes
  back as finish_reason=MAX_TOKENS with unusable text instead of an error.
- 429 responses carry a server-side retryDelay that beats blind backoff.
"""

from __future__ import annotations

import asyncio
import contextvars
import random
import re
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Protocol

import structlog

from config.settings import get_settings

log = structlog.get_logger(__name__)

# Prices fetched 2026-10-14 from the OpenAI model pages. USD per 1,000,000 tokens.
# Cached input is a subset of prompt tokens, not an extra charge on top of them.
# Reasoning tokens are reported separately and are not added to completion tokens.
_RATE_SOURCE = (
    "https://platform.openai.com/docs/models/gpt-5-mini ; "
    "https://platform.openai.com/docs/models/text-embedding-3-small"
)
_RATE_EFFECTIVE = "2026-10-14"
_RATE_UNITS = "USD per 1000000 tokens"
_OPERATIONS = ("fit", "embedding", "role", "other")
_openai_operation: contextvars.ContextVar[str] = contextvars.ContextVar(
    "openai_operation",
    default="other",
)


def push_openai_operation(name: str) -> contextvars.Token[str]:
    """Label OpenAI calls made until ``pop_openai_operation``."""
    return _openai_operation.set(name if name in _OPERATIONS else "other")


def pop_openai_operation(token: contextvars.Token[str]) -> None:
    _openai_operation.reset(token)


@dataclass(frozen=True, slots=True)
class _ModelRate:
    """Token prices for one model. ``None`` means that category does not apply."""

    kind: str
    input_per_million: Decimal
    cached_input_per_million: Decimal | None = None
    output_per_million: Decimal | None = None


# gpt-5-mini-2025-08-07 is the default snapshot listed on the gpt-5-mini page.
_MODEL_RATES: dict[str, _ModelRate] = {
    "gpt-5-mini": _ModelRate("chat", Decimal("0.25"), Decimal("0.025"), Decimal("2")),
    "gpt-5-mini-2025-08-07": _ModelRate(
        "chat", Decimal("0.25"), Decimal("0.025"), Decimal("2")
    ),
    "text-embedding-3-small": _ModelRate("embedding", Decimal("0.02")),
}


@dataclass
class TokenUsage:
    """Accumulated provider usage for one client instance (one scoring run).

    Token fields stay ``None`` until a response actually reports them. Zero
    means the API sent zero. Counters are this process's own observations.
    """

    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    cached_tokens: int | None = None
    reasoning_tokens: int | None = None
    request_attempts: int = 0
    successful_responses: int = 0
    empty_response_retries: int = 0
    api_exceptions: int = 0
    transient_retries: int = 0
    total_calls: int = 0
    models: dict[str, int] = field(default_factory=dict)

    def __iadd__(self, other: TokenUsage) -> TokenUsage:
        self.prompt_tokens = _add_measured(self.prompt_tokens, other.prompt_tokens)
        self.completion_tokens = _add_measured(self.completion_tokens, other.completion_tokens)
        self.cached_tokens = _add_measured(self.cached_tokens, other.cached_tokens)
        self.reasoning_tokens = _add_measured(self.reasoning_tokens, other.reasoning_tokens)
        self.request_attempts += other.request_attempts
        self.successful_responses += other.successful_responses
        self.empty_response_retries += other.empty_response_retries
        self.api_exceptions += other.api_exceptions
        self.transient_retries += other.transient_retries
        self.total_calls += other.total_calls
        for model, count in other.models.items():
            self.models[model] = self.models.get(model, 0) + count
        return self

    def log_fields(self) -> dict[str, Any]:
        """Numbers and model ids only. No prompts or job text."""
        return {
            "models": dict(self.models),
            "request_attempts": self.request_attempts,
            "successful_responses": self.successful_responses,
            "empty_response_retries": self.empty_response_retries,
            "api_exceptions": self.api_exceptions,
            "transient_retries": self.transient_retries,
            "prompt_tokens": self.prompt_tokens,
            "cached_tokens": self.cached_tokens,
            "completion_tokens": self.completion_tokens,
            "reasoning_tokens": self.reasoning_tokens,
        }


def _measured_int(value: Any) -> int | None:
    """None stays missing. Zero stays zero. Non-numeric values stay missing."""
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _add_measured(current: int | None, value: int | None) -> int | None:
    if value is None:
        return current
    if current is None:
        return value
    return current + value

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


class OpenAIRequestBlocked(LLMError):
    """Refused before a network call. No attempt slot was taken."""


class OpenAIBudgetExceeded(OpenAIRequestBlocked):
    """The configured OpenAI attempt limit is already reserved."""


class OpenAIBillingHalted(OpenAIRequestBlocked):
    """A billing error halted later OpenAI requests. In-flight calls still finish."""


@dataclass(slots=True)
class _Attempt:
    operation: str
    model: str
    success: bool
    empty_followup: bool
    transient_retry: bool
    api_exception: bool
    usage_present: bool
    response_id: str | None
    prompt_tokens: int | None
    cached_tokens: int | None
    completion_tokens: int | None
    reasoning_tokens: int | None


class OpenAIRequestLedger:
    """Process-wide reservation count for OpenAI HTTP attempts.

    ``reserve`` runs before a request is started. The slot is kept when the
    call fails or returns empty, because the provider may already have billed
    it. ``halt`` stops later reservations after a billing error. A worker that
    already reserved its slot still runs; this ledger cannot cancel or unbill it.
    """

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self.reserved = 0
        self.halted = False
        self.role_calls = 0
        self.embed_inputs = 0
        self.embed_capped = False
        self._attempts: list[_Attempt] = []

    async def reserve(self) -> None:
        """Take one attempt slot, or refuse before any network call."""
        async with self._lock:
            limit = get_settings().openai_max_requests
            if self.halted:
                log.warning(
                    "openai_request_blocked",
                    reason="billing",
                    reserved=self.reserved,
                    limit=limit,
                )
                raise OpenAIBillingHalted(
                    "OpenAI billing halt is set; no further request will start"
                )
            if limit is not None and self.reserved >= limit:
                log.warning(
                    "openai_request_blocked",
                    reason="budget",
                    reserved=self.reserved,
                    limit=limit,
                )
                raise OpenAIBudgetExceeded(
                    f"OpenAI request attempt limit reached ({self.reserved}/{limit})"
                )
            self.reserved += 1

    async def halt(self) -> None:
        """Stop reservations that have not started. In-flight attempts continue."""
        async with self._lock:
            self.halted = True

    async def reserve_role_call(self) -> bool:
        """Take one role-classification model attempt.

        ``None`` allows the call and does not count it. Deterministic labels
        and cache hits must not call this. A refusal happens before any network
        request. The OpenAI attempt slot is reserved later, inside the client.
        """
        async with self._lock:
            limit = get_settings().role_classify_max_calls
            if limit is None:
                return True
            if self.role_calls >= limit:
                return False
            self.role_calls += 1
            return True

    async def reserve_embed_inputs(self, count: int) -> int:
        """How many of ``count`` inputs may be sent.

        ``None`` returns ``count`` and does not track it. A shortfall sets
        ``embed_capped``. The returned inputs stay reserved even if the HTTP
        call later fails.
        """
        if count <= 0:
            return 0
        async with self._lock:
            limit = get_settings().embed_max_inputs
            if limit is None:
                return count
            room = limit - self.embed_inputs
            if room <= 0:
                self.embed_capped = True
                return 0
            allowed = min(count, room)
            self.embed_inputs += allowed
            if allowed < count:
                self.embed_capped = True
            return allowed

    async def record_attempt(
        self,
        *,
        operation: str,
        model: str,
        success: bool,
        empty_followup: bool = False,
        transient_retry: bool = False,
        api_exception: bool = False,
        usage_present: bool = False,
        response_id: str | None = None,
        prompt_tokens: int | None = None,
        cached_tokens: int | None = None,
        completion_tokens: int | None = None,
        reasoning_tokens: int | None = None,
    ) -> None:
        """Record one HTTP attempt. A refusal before the call is not an attempt."""
        label = operation if operation in _OPERATIONS else "other"
        model_id = model.strip() if isinstance(model, str) else ""
        if not model_id or len(model_id) > 80 or any(ch.isspace() for ch in model_id):
            model_id = "unknown"
        async with self._lock:
            self._attempts.append(
                _Attempt(
                    operation=label,
                    model=model_id,
                    success=success,
                    empty_followup=empty_followup,
                    transient_retry=transient_retry,
                    api_exception=api_exception,
                    usage_present=usage_present,
                    response_id=_safe_response_id(response_id),
                    prompt_tokens=prompt_tokens,
                    cached_tokens=cached_tokens,
                    completion_tokens=completion_tokens,
                    reasoning_tokens=reasoning_tokens,
                )
            )

    async def summary_fields(self) -> dict[str, Any]:
        """Numbers, model ids, and response ids. No prompts or job text."""
        async with self._lock:
            attempts = list(self._attempts)
            reserved = self.reserved
        return _run_usage_fields(attempts, reserved)


def is_openai_safety_error(exc: BaseException) -> bool:
    """Billing halt or request-budget refusal. Ordinary failures are not included."""
    return isinstance(exc, (LLMBillingError, OpenAIBillingHalted, OpenAIBudgetExceeded))


_openai_request_ledger = OpenAIRequestLedger()


def get_openai_request_ledger() -> OpenAIRequestLedger:
    """The process-wide OpenAI attempt ledger."""
    return _openai_request_ledger


def reset_openai_request_ledger() -> None:
    """Replace the ledger. Tests use this so a halt cannot leak across cases."""
    global _openai_request_ledger
    _openai_request_ledger = OpenAIRequestLedger()


def _safe_response_id(value: object) -> str | None:
    """Keep a provider id. Drop anything that could carry a key or a prompt."""
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text or len(text) > 128 or any(ch.isspace() for ch in text):
        return None
    lowered = text.lower()
    if "sk-" in lowered or "bearer" in lowered or "api_key" in lowered:
        return None
    return text


def _chat_usage(
    response: Any,
) -> tuple[bool, str | None, int | None, int | None, int | None, int | None]:
    """Chat usage. Cached tokens stay out of the prompt total."""
    response_id = _safe_response_id(getattr(response, "id", None))
    usage = getattr(response, "usage", None)
    if usage is None:
        return False, response_id, None, None, None, None
    prompt = _measured_int(getattr(usage, "prompt_tokens", None))
    if prompt is None:
        prompt = _measured_int(getattr(usage, "input_tokens", None))
    completion = _measured_int(getattr(usage, "completion_tokens", None))
    if completion is None:
        completion = _measured_int(getattr(usage, "output_tokens", None))
    prompt_details = getattr(usage, "prompt_tokens_details", None)
    if prompt_details is None:
        prompt_details = getattr(usage, "input_tokens_details", None)
    completion_details = getattr(usage, "completion_tokens_details", None)
    if completion_details is None:
        completion_details = getattr(usage, "output_tokens_details", None)
    cached = _measured_int(getattr(prompt_details, "cached_tokens", None))
    reasoning = _measured_int(getattr(completion_details, "reasoning_tokens", None))
    return True, response_id, prompt, cached, completion, reasoning


def _embedding_usage(response: Any) -> tuple[bool, str | None, int | None]:
    """Embedding usage from this SDK: prompt_tokens and total_tokens.

    ``total_tokens`` is not added to ``prompt_tokens``. This response type has no id.
    """
    reported = getattr(response, "model", None)
    model = reported.strip() if isinstance(reported, str) else ""
    usage = getattr(response, "usage", None)
    if usage is None:
        return False, model or None, None
    return True, model or None, _measured_int(getattr(usage, "prompt_tokens", None))


def _blank_bucket() -> dict[str, Any]:
    return {
        "request_attempts": 0,
        "successful_responses": 0,
        "empty_response_retries": 0,
        "transient_retries": 0,
        "api_exceptions": 0,
        "missing_usage": 0,
        "responses_without_id": 0,
        "prompt_tokens": None,
        "cached_tokens": None,
        "completion_tokens": None,
        "reasoning_tokens": None,
        "response_ids": [],
    }


def _add_token(bucket: dict[str, Any], key: str, value: int | None, *, present: bool) -> None:
    if not present or value is None:
        return
    current = bucket[key]
    bucket[key] = value if current is None else current + value


def _usd(tokens: int, per_million: Decimal) -> Decimal:
    return (Decimal(tokens) * per_million) / Decimal(1_000_000)


def _estimate_model(model: str, bucket: dict[str, Any], *, complete: bool) -> str | None:
    """Return a USD string, or None when the rate or the token split is unknown."""
    rate = _MODEL_RATES.get(model)
    if rate is None or not complete or bucket["missing_usage"]:
        return None
    prompt = bucket["prompt_tokens"]
    if not isinstance(prompt, int):
        return None
    if rate.kind == "embedding":
        amount = _usd(prompt, rate.input_per_million)
        return format(amount, "f")
    cached = bucket["cached_tokens"]
    completion = bucket["completion_tokens"]
    if (
        not isinstance(cached, int)
        or not isinstance(completion, int)
        or rate.cached_input_per_million is None
        or rate.output_per_million is None
        or cached > prompt
    ):
        return None
    amount = (
        _usd(prompt - cached, rate.input_per_million)
        + _usd(cached, rate.cached_input_per_million)
        + _usd(completion, rate.output_per_million)
    )
    return format(amount, "f")


def _run_usage_fields(attempts: list[_Attempt], reserved: int) -> dict[str, Any]:
    operations = {name: _blank_bucket() for name in _OPERATIONS}
    models: dict[str, dict[str, Any]] = {}
    model_complete: dict[str, bool] = {}
    for attempt in attempts:
        bucket = operations[attempt.operation]
        model_bucket = models.get(attempt.model)
        if model_bucket is None:
            model_bucket = _blank_bucket()
            models[attempt.model] = model_bucket
            model_complete[attempt.model] = True
        for target in (bucket, model_bucket):
            target["request_attempts"] += 1
            if attempt.success:
                target["successful_responses"] += 1
            if attempt.empty_followup:
                target["empty_response_retries"] += 1
            if attempt.transient_retry:
                target["transient_retries"] += 1
            if attempt.api_exception:
                target["api_exceptions"] += 1
            if not attempt.usage_present:
                target["missing_usage"] += 1
            _add_token(
                target,
                "prompt_tokens",
                attempt.prompt_tokens,
                present=attempt.usage_present,
            )
            _add_token(
                target,
                "cached_tokens",
                attempt.cached_tokens,
                present=attempt.usage_present,
            )
            _add_token(
                target,
                "completion_tokens",
                attempt.completion_tokens,
                present=attempt.usage_present,
            )
            _add_token(
                target,
                "reasoning_tokens",
                attempt.reasoning_tokens,
                present=attempt.usage_present,
            )
            if attempt.response_id is None:
                target["responses_without_id"] += 1
            elif attempt.response_id not in target["response_ids"]:
                target["response_ids"].append(attempt.response_id)
        rate = _MODEL_RATES.get(attempt.model)
        embedding_priced = (
            rate is not None
            and rate.kind == "embedding"
            and attempt.usage_present
            and attempt.prompt_tokens is not None
        )
        priced = rate is not None and (
            embedding_priced
            or (
                rate is not None
                and rate.kind == "chat"
                and attempt.usage_present
                and attempt.prompt_tokens is not None
                and attempt.cached_tokens is not None
                and attempt.completion_tokens is not None
                and attempt.cached_tokens <= attempt.prompt_tokens
            )
        )
        if not priced:
            model_complete[attempt.model] = False
    model_fields: dict[str, Any] = {}
    estimates: list[Decimal] = []
    run_complete = True
    for model, bucket in models.items():
        estimate = _estimate_model(model, bucket, complete=model_complete[model])
        if estimate is None:
            run_complete = False
        else:
            estimates.append(Decimal(estimate))
        model_fields[model] = {
            **bucket,
            "estimated_usd": estimate,
            "cost_complete": estimate is not None,
        }
    if not attempts:
        total: str | None = None
        run_complete = True
    elif run_complete:
        total = format(sum(estimates, Decimal(0)), "f")
    else:
        total = None
    return {
        "cost_basis": "estimate",
        "cost_complete": run_complete,
        "estimated_usd": total,
        "rate_source": _RATE_SOURCE,
        "rate_effective": _RATE_EFFECTIVE,
        "rate_units": _RATE_UNITS,
        "reserved_attempts": reserved,
        "operations": operations,
        "models": model_fields,
    }


async def remember_openai_attempt(**kwargs: Any) -> None:
    """Record an attempt. A bookkeeping failure must not hide the API result."""
    try:
        await get_openai_request_ledger().record_attempt(**kwargs)
    except Exception as exc:
        log.warning("openai_usage_record_failed", error=str(exc)[:200])


async def emit_openai_run_usage() -> None:
    """Log one process summary. A logging failure must not replace the caller's error.

    ``estimated_usd`` is not an invoice and not a spending cap. An empty process
    reports zero attempts and leaves token and cost fields unknown.
    """
    try:
        fields = await get_openai_request_ledger().summary_fields()
        log.info("openai_run_usage", **fields)
    except Exception as exc:
        try:
            log.warning("openai_run_usage_failed", error=str(exc)[:200])
        except Exception:
            return


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
    usage: TokenUsage | None = None,
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
            except OpenAIRequestBlocked:
                raise
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
                if usage is not None:
                    usage.transient_retries += 1
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
        self._usage.prompt_tokens = _add_measured(
            self._usage.prompt_tokens, _measured_int(getattr(usage, "input_tokens", None))
        )
        self._usage.completion_tokens = _add_measured(
            self._usage.completion_tokens, _measured_int(getattr(usage, "output_tokens", None))
        )
        self._usage.cached_tokens = _add_measured(
            self._usage.cached_tokens,
            _measured_int(getattr(usage, "cache_read_input_tokens", None)),
        )
        self._usage.total_calls += 1
        self._usage.successful_responses += 1


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

        attempt_number = 0

        async def _attempt(candidate: str) -> str:
            nonlocal attempt_number
            attempt_number += 1
            is_retry = attempt_number > 1
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

            async def _create(*, empty_followup: bool = False) -> Any:
                await get_openai_request_ledger().reserve()
                if empty_followup:
                    self._usage.empty_response_retries += 1
                self._usage.request_attempts += 1
                self._usage.models[candidate] = self._usage.models.get(candidate, 0) + 1
                try:
                    response = await self._client.chat.completions.create(**kwargs)
                except Exception as exc:
                    self._usage.api_exceptions += 1
                    await remember_openai_attempt(
                        operation=_openai_operation.get(),
                        model=candidate,
                        success=False,
                        empty_followup=empty_followup,
                        transient_retry=is_retry and not empty_followup,
                        api_exception=True,
                    )
                    if is_permanent_account_error(exc):
                        await get_openai_request_ledger().halt()
                    raise
                present, response_id, prompt, cached, completion, reasoning = _chat_usage(
                    response
                )
                reported = getattr(response, "model", None)
                model_id = reported if isinstance(reported, str) and reported.strip() else candidate
                await remember_openai_attempt(
                    operation=_openai_operation.get(),
                    model=model_id,
                    success=True,
                    empty_followup=empty_followup,
                    transient_retry=is_retry and not empty_followup,
                    usage_present=present,
                    response_id=response_id,
                    prompt_tokens=prompt,
                    cached_tokens=cached,
                    completion_tokens=completion,
                    reasoning_tokens=reasoning,
                )
                self._record_openai_usage(response)
                return response

            response = await _create()
            choice = response.choices[0]
            text = (getattr(choice.message, "content", None) or "").strip()
            if text:
                return text
            # Count the follow-up only after its slot is reserved inside _create.
            kwargs["max_completion_tokens"] = min(max_tokens * 3, 8192)
            response = await _create(empty_followup=True)
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
            usage=self._usage,
        )

    @property
    def usage(self) -> TokenUsage:
        return self._usage

    def _record_openai_usage(self, response: Any) -> None:
        self._usage.successful_responses += 1
        self._usage.total_calls += 1
        usage = getattr(response, "usage", None)
        if usage is None:
            return
        prompt = _measured_int(getattr(usage, "prompt_tokens", None))
        if prompt is None:
            prompt = _measured_int(getattr(usage, "input_tokens", None))
        completion = _measured_int(getattr(usage, "completion_tokens", None))
        if completion is None:
            completion = _measured_int(getattr(usage, "output_tokens", None))
        prompt_details = getattr(usage, "prompt_tokens_details", None)
        if prompt_details is None:
            prompt_details = getattr(usage, "input_tokens_details", None)
        completion_details = getattr(usage, "completion_tokens_details", None)
        if completion_details is None:
            completion_details = getattr(usage, "output_tokens_details", None)
        self._usage.prompt_tokens = _add_measured(self._usage.prompt_tokens, prompt)
        self._usage.completion_tokens = _add_measured(self._usage.completion_tokens, completion)
        self._usage.cached_tokens = _add_measured(
            self._usage.cached_tokens,
            _measured_int(getattr(prompt_details, "cached_tokens", None)),
        )
        self._usage.reasoning_tokens = _add_measured(
            self._usage.reasoning_tokens,
            _measured_int(getattr(completion_details, "reasoning_tokens", None)),
        )


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
        self._usage.prompt_tokens = _add_measured(
            self._usage.prompt_tokens,
            _measured_int(getattr(meta, "prompt_token_count", None)),
        )
        self._usage.completion_tokens = _add_measured(
            self._usage.completion_tokens,
            _measured_int(getattr(meta, "candidates_token_count", None)),
        )
        self._usage.cached_tokens = _add_measured(
            self._usage.cached_tokens,
            _measured_int(getattr(meta, "cached_content_token_count", None)),
        )
        self._usage.total_calls += 1
        self._usage.successful_responses += 1


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

"""Unified OpenAI usage summary. The HTTP client is a fake; no network."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

import pytest

from config.settings import get_settings
from core.db import Job, Source, Status
from scorer.clients import (
    LLMBillingError,
    OpenAIClient,
    emit_openai_run_usage,
    get_openai_request_ledger,
    pop_openai_operation,
    push_openai_operation,
)
from scorer.embeddings import OpenAIEmbedder
from scorer.fit import evaluate_fit
from scorer.role_classify import classify_role

_SECRET = "sk-test-secret-value"
_ROLE = (
    '{"primary_family":"CONSULTING","subfamily":"BUSINESS_CONSULTING",'
    '"confidence":"medium","evidence":["JD describes business consulting for clients."]}'
)
_AMBIGUOUS = (
    "Help the team and attend meetings during the summer internship."
    " The team meets weekly to review the work. " * 3
)


def _env(monkeypatch: pytest.MonkeyPatch, **values: str | None) -> None:
    for key, value in values.items():
        if value is None:
            monkeypatch.delenv(key, raising=False)
        else:
            monkeypatch.setenv(key, value)
    get_settings.cache_clear()


@dataclass
class _Msg:
    content: str


@dataclass
class _Choice:
    message: _Msg


@dataclass
class _PromptDetails:
    cached_tokens: int | None = None


@dataclass
class _CompletionDetails:
    reasoning_tokens: int | None = None


@dataclass
class _ChatUsage:
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    prompt_tokens_details: _PromptDetails | None = None
    completion_tokens_details: _CompletionDetails | None = None


@dataclass
class _ChatResponse:
    choices: list[_Choice]
    usage: _ChatUsage | None = None
    id: str | None = None
    model: str | None = None


class _RateLimit(Exception):
    status_code = 429


class _Completions:
    def __init__(self, script: list[Any]) -> None:
        self.script = list(script)
        self.calls = 0

    async def create(self, **_kwargs: Any) -> _ChatResponse:
        self.calls += 1
        step = self.script.pop(0)
        if isinstance(step, Exception):
            raise step
        return step


class _Chat:
    def __init__(self, completions: _Completions) -> None:
        self.completions = completions


class _ChatHolder:
    def __init__(self, script: list[Any]) -> None:
        self.chat = _Chat(_Completions(script))


def _ok(
    content: str,
    *,
    prompt: int | None = 10,
    completion: int | None = 2,
    cached: int | None = 0,
    reasoning: int | None = None,
    model: str = "gpt-5-mini-2025-08-07",
    response_id: str | None = "chatcmpl-test",
    usage: _ChatUsage | None | object = ...,
) -> _ChatResponse:
    if usage is ...:
        details = None if cached is None else _PromptDetails(cached_tokens=cached)
        completion_details = (
            None if reasoning is None else _CompletionDetails(reasoning_tokens=reasoning)
        )
        parsed: _ChatUsage | None = _ChatUsage(
            prompt_tokens=prompt,
            completion_tokens=completion,
            prompt_tokens_details=details,
            completion_tokens_details=completion_details,
        )
    else:
        parsed = usage  # type: ignore[assignment]
    return _ChatResponse(
        choices=[_Choice(message=_Msg(content=content))],
        usage=parsed,
        id=response_id,
        model=model,
    )


async def _complete(client: OpenAIClient, *, model: str = "gpt-5-mini", user: str = "Job") -> str:
    return await client.complete(
        model=model,
        system_blocks=[{"text": "Score."}],
        user=user,
        max_tokens=128,
        temperature=0.0,
        json_mode=True,
    )


def _operations(summary: dict[str, Any], name: str) -> dict[str, Any]:
    operations = summary["operations"]
    assert isinstance(operations, dict)
    bucket = operations[name]
    assert isinstance(bucket, dict)
    return bucket


async def test_concurrent_records_keep_the_token_sum() -> None:
    ledger = get_openai_request_ledger()

    async def one(index: int) -> None:
        await ledger.record_attempt(
            operation="fit" if index % 2 == 0 else "role",
            model="gpt-5-mini",
            success=True,
            usage_present=True,
            prompt_tokens=1,
            cached_tokens=0,
            completion_tokens=1,
            response_id=f"chatcmpl-{index}",
        )

    await asyncio.gather(*[one(index) for index in range(20)])
    summary = await ledger.summary_fields()
    assert summary["reserved_attempts"] == 0
    fit = _operations(summary, "fit")
    role = _operations(summary, "role")
    assert fit["request_attempts"] + role["request_attempts"] == 20
    assert fit["prompt_tokens"] + role["prompt_tokens"] == 20
    model = summary["models"]["gpt-5-mini"]
    assert model["prompt_tokens"] == 20
    assert model["cached_tokens"] == 0
    assert len(model["response_ids"]) == 20


async def test_fit_role_and_embedding_usage_are_separate(
    profile: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del monkeypatch
    described = f"Python SQL data analysis for this team. {_SECRET}"
    job = Job(
        source=Source.linkedin,
        external_id="usage-fit",
        title="Engineer",
        company="GoodCo",
        location="Remote",
        url="https://example.com/usage-fit",
        description_clean=described,
        status=Status.discovered,
        content_hash="usage-fit",
    )
    fit_client = OpenAIClient(client=_ChatHolder([_ok('{"s": 40, "r": ["Python"]}')]))
    await evaluate_fit(
        job,
        profile,  # type: ignore[arg-type]
        fit_client,
        model="gpt-5-mini",
        max_tokens=128,
    )
    role_client = OpenAIClient(
        client=_ChatHolder([_ok(_ROLE, response_id="chatcmpl-role", prompt=4, completion=3)])
    )
    classified = await classify_role(
        title="Intern",
        description=_AMBIGUOUS,
        content_hash="usage-role",
        client=role_client,
    )
    assert classified.used_llm is True

    @dataclass
    class _Item:
        index: int
        embedding: list[float]

    @dataclass
    class _EmbedUsage:
        prompt_tokens: int
        total_tokens: int

    @dataclass
    class _EmbedResponse:
        data: list[_Item]
        model: str
        usage: _EmbedUsage

    class _Embeddings:
        def __init__(self) -> None:
            self.inputs: list[list[str]] = []

        async def create(self, **kwargs: Any) -> _EmbedResponse:
            raw = kwargs["input"]
            texts = list(raw)
            self.inputs.append(texts)
            return _EmbedResponse(
                data=[_Item(index=0, embedding=[0.1, 0.2])],
                model="text-embedding-3-small",
                usage=_EmbedUsage(prompt_tokens=5, total_tokens=9),
            )

    class _Holder:
        def __init__(self) -> None:
            self.embeddings = _Embeddings()

    await OpenAIEmbedder(client=_Holder()).embed(["one description"])
    summary = await get_openai_request_ledger().summary_fields()
    assert _operations(summary, "fit")["request_attempts"] == 1
    assert _operations(summary, "role")["request_attempts"] == 1
    assert _operations(summary, "embedding")["request_attempts"] == 1
    assert _operations(summary, "embedding")["prompt_tokens"] == 5
    assert _operations(summary, "fit")["response_ids"] == ["chatcmpl-test"]
    assert _operations(summary, "embedding")["responses_without_id"] == 1
    assert summary["models"]["gpt-5-mini-2025-08-07"]["request_attempts"] == 2
    assert summary["models"]["text-embedding-3-small"]["prompt_tokens"] == 5
    events: list[dict[str, Any]] = []

    def _record(*_args: object, **kwargs: Any) -> None:
        events.append(kwargs)

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr("scorer.clients.log.info", _record)
    await emit_openai_run_usage()
    monkeypatch.undo()
    rendered = repr(events)
    assert _SECRET not in rendered
    assert "one description" not in rendered
    assert described not in rendered


async def test_empty_followup_and_transient_retry_are_attempts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _no_sleep(*_args: object, **_kwargs: object) -> None:
        return None

    monkeypatch.setattr("scorer.clients.asyncio.sleep", _no_sleep)
    monkeypatch.setattr("scorer.clients.random.uniform", lambda *_args: 0.0)
    token = push_openai_operation("fit")
    try:
        empty = OpenAIClient(
            client=_ChatHolder(
                [
                    _ok("", prompt=3, completion=1, cached=0, response_id="chatcmpl-empty"),
                    _ok('{"s":1}', prompt=4, completion=2, cached=1, response_id="chatcmpl-next"),
                ]
            )
        )
        assert await _complete(empty) == '{"s":1}'
    finally:
        pop_openai_operation(token)
    summary = await get_openai_request_ledger().summary_fields()
    fit = _operations(summary, "fit")
    assert fit["request_attempts"] == 2
    assert fit["empty_response_retries"] == 1
    assert fit["successful_responses"] == 2
    assert fit["prompt_tokens"] == 7
    assert fit["cached_tokens"] == 1

    from scorer.clients import reset_openai_request_ledger

    reset_openai_request_ledger()
    token = push_openai_operation("fit")
    try:
        retried = OpenAIClient(
            client=_ChatHolder(
                [
                    _RateLimit("429 RESOURCE_EXHAUSTED"),
                    _ok('{"s":2}', prompt=8, completion=2, cached=0, response_id="chatcmpl-retry"),
                ]
            )
        )
        assert await _complete(retried) == '{"s":2}'
    finally:
        pop_openai_operation(token)
    summary = await get_openai_request_ledger().summary_fields()
    fit = _operations(summary, "fit")
    assert fit["request_attempts"] == 2
    assert fit["transient_retries"] == 1
    assert fit["api_exceptions"] == 1
    assert fit["successful_responses"] == 1
    assert fit["missing_usage"] == 1
    assert fit["prompt_tokens"] == 8
    assert summary["estimated_usd"] is None
    assert summary["cost_complete"] is False


async def test_missing_usage_stays_unknown_and_cached_tokens_are_not_added(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del monkeypatch
    token = push_openai_operation("fit")
    try:
        client = OpenAIClient(
            client=_ChatHolder(
                [
                    _ok(
                        '{"s":1}',
                        prompt=100,
                        completion=0,
                        cached=40,
                        reasoning=7,
                        response_id="chatcmpl-cached",
                    )
                ]
            )
        )
        await _complete(client)
        bare = OpenAIClient(client=_ChatHolder([_ok('{"s":2}', usage=None, response_id=None)]))
        await _complete(bare)
    finally:
        pop_openai_operation(token)
    summary = await get_openai_request_ledger().summary_fields()
    fit = _operations(summary, "fit")
    assert fit["prompt_tokens"] == 100
    assert fit["cached_tokens"] == 40
    assert fit["reasoning_tokens"] == 7
    assert fit["completion_tokens"] == 0
    assert fit["missing_usage"] == 1
    assert summary["estimated_usd"] is None


async def test_billing_and_budget_exhaustion_do_not_invent_usage(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _env(monkeypatch, OPENAI_MAX_REQUESTS=None)
    token = push_openai_operation("fit")
    try:
        billed = OpenAIClient(client=_ChatHolder([RuntimeError("credits are depleted")]))
        with pytest.raises(LLMBillingError):
            await _complete(billed)
        from scorer.clients import OpenAIBillingHalted

        with pytest.raises(OpenAIBillingHalted):
            await _complete(OpenAIClient(client=_ChatHolder([_ok('{"s":1}')])))
    finally:
        pop_openai_operation(token)
    summary = await get_openai_request_ledger().summary_fields()
    assert _operations(summary, "fit")["request_attempts"] == 1
    assert _operations(summary, "fit")["api_exceptions"] == 1
    assert _operations(summary, "fit")["prompt_tokens"] is None
    assert summary["reserved_attempts"] == 1

    from scorer.clients import reset_openai_request_ledger

    reset_openai_request_ledger()
    _env(monkeypatch, OPENAI_MAX_REQUESTS="1")
    token = push_openai_operation("fit")
    try:
        limited = OpenAIClient(
            client=_ChatHolder([_ok('{"s":1}', prompt=6, completion=1, cached=0)])
        )
        await _complete(limited)
        from scorer.clients import OpenAIBudgetExceeded

        with pytest.raises(OpenAIBudgetExceeded):
            await _complete(limited)
    finally:
        pop_openai_operation(token)
    summary = await get_openai_request_ledger().summary_fields()
    assert summary["reserved_attempts"] == 1
    assert _operations(summary, "fit")["request_attempts"] == 1
    assert _operations(summary, "fit")["prompt_tokens"] == 6


async def test_unknown_model_has_a_null_estimate() -> None:
    token = push_openai_operation("other")
    try:
        client = OpenAIClient(
            client=_ChatHolder(
                [
                    _ok(
                        '{"s":1}',
                        model="not-a-priced-model",
                        prompt=10,
                        completion=2,
                        cached=0,
                    )
                ]
            )
        )
        await _complete(client, model="not-a-priced-model")
    finally:
        pop_openai_operation(token)
    summary = await get_openai_request_ledger().summary_fields()
    assert summary["models"]["not-a-priced-model"]["estimated_usd"] is None
    assert summary["estimated_usd"] is None
    assert summary["cost_basis"] == "estimate"
    assert summary["cost_complete"] is False


async def test_known_rates_estimate_without_double_counting_cached_or_embedding_totals() -> None:
    token = push_openai_operation("fit")
    try:
        client = OpenAIClient(
            client=_ChatHolder(
                [_ok('{"s":1}', prompt=100, completion=4, cached=40, reasoning=3)]
            )
        )
        await _complete(client)
    finally:
        pop_openai_operation(token)

    @dataclass
    class _Item:
        index: int
        embedding: list[float]

    @dataclass
    class _Usage:
        prompt_tokens: int
        total_tokens: int

    @dataclass
    class _Response:
        data: list[_Item]
        model: str
        usage: _Usage

    class _Embeddings:
        async def create(self, **_kwargs: Any) -> _Response:
            return _Response(
                data=[_Item(0, [0.1])],
                model="text-embedding-3-small",
                usage=_Usage(prompt_tokens=50, total_tokens=80),
            )

    class _Holder:
        def __init__(self) -> None:
            self.embeddings = _Embeddings()

    await OpenAIEmbedder(client=_Holder()).embed(["text"])
    summary = await get_openai_request_ledger().summary_fields()
    chat = summary["models"]["gpt-5-mini-2025-08-07"]
    embedded = summary["models"]["text-embedding-3-small"]
    assert chat["prompt_tokens"] == 100
    assert chat["cached_tokens"] == 40
    assert chat["completion_tokens"] == 4
    assert chat["reasoning_tokens"] == 3
    assert embedded["prompt_tokens"] == 50
    chat_usd = (
        Decimal(60) * Decimal("0.25")
        + Decimal(40) * Decimal("0.025")
        + Decimal(4) * Decimal("2")
    ) / Decimal(1000000)
    embed_usd = (Decimal(50) * Decimal("0.02")) / Decimal(1000000)
    assert chat["estimated_usd"] == format(chat_usd, "f")
    assert embedded["estimated_usd"] == format(embed_usd, "f")
    assert summary["estimated_usd"] == format(chat_usd + embed_usd, "f")
    assert summary["cost_basis"] == "estimate"
    assert summary["cost_complete"] is True


async def test_empty_process_does_not_invent_tokens_or_cost() -> None:
    events: list[dict[str, Any]] = []

    def _record(event: str, **kwargs: Any) -> None:
        events.append({"event": event, **kwargs})

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr("scorer.clients.log.info", _record)
    await emit_openai_run_usage()
    monkeypatch.undo()
    assert len(events) == 1
    summary = events[0]
    assert summary["event"] == "openai_run_usage"
    assert summary["reserved_attempts"] == 0
    assert summary["estimated_usd"] is None
    assert summary["cost_complete"] is True
    assert _operations(summary, "fit")["request_attempts"] == 0
    assert _operations(summary, "fit")["prompt_tokens"] is None
    assert summary["models"] == {}


async def test_failed_pipeline_stage_still_emits_the_run_summary(
    db_ready: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    events: list[str] = []
    original = __import__("scorer.clients", fromlist=["log"]).log.info

    def _record(event: str, **kwargs: Any) -> None:
        events.append(event)
        if event == "openai_run_usage":
            rendered = repr(kwargs)
            assert _SECRET not in rendered
            assert kwargs["reserved_attempts"] == 0
            assert kwargs["estimated_usd"] is None

    monkeypatch.setattr("scorer.clients.log.info", _record)

    async def ingest(**_kwargs: object) -> object:
        from scraper.ingest import IngestSummary

        return IngestSummary()

    async def fail(**_kwargs: object) -> object:
        raise RuntimeError(f"stage failed {_SECRET}")

    monkeypatch.setattr("orchestrator.pipeline._run_ingestion", ingest)
    monkeypatch.setattr("orchestrator.pipeline._score_pending", fail)
    from orchestrator.pipeline import run_pipeline

    summary = await run_pipeline(
        enable_apply=False,
        enable_reviews=False,
        enable_prep_pack=False,
        enable_suggestions=False,
        enable_benchmark=False,
    )
    assert summary.ok is False
    assert events.count("openai_run_usage") == 1
    del original

"""Process-wide OpenAI attempt gate. The HTTP client is a fake; no network."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

import pytest

from config.settings import get_settings
from scorer.clients import (
    LLMBillingError,
    OpenAIBillingHalted,
    OpenAIBudgetExceeded,
    OpenAIClient,
    get_openai_request_ledger,
    reset_openai_request_ledger,
)
from scorer.embeddings import OpenAIEmbedder
from scorer.role_classify import classify_role

_SECRET = "sk-test-secret-value"
_ROLE_JSON = (
    '{"primary_family":"CONSULTING","subfamily":"BUSINESS_CONSULTING",'
    '"confidence":"medium","evidence":["JD describes business consulting for clients."]}'
)
_AMBIGUOUS_JD = (
    "Help the team and attend meetings during the summer internship."
    + " The team meets weekly to review the work. " * 3
)


@dataclass
class _Msg:
    content: str


@dataclass
class _Choice:
    message: _Msg


@dataclass
class _Usage:
    prompt_tokens: int = 1
    completion_tokens: int = 1


@dataclass
class _ChatResponse:
    choices: list[_Choice]
    usage: _Usage | None = None


class _RateLimit(Exception):
    status_code = 429


def _ok(content: str) -> _ChatResponse:
    return _ChatResponse(choices=[_Choice(message=_Msg(content=content))], usage=_Usage())


class _Completions:
    def __init__(self, script: list[Any] | None = None) -> None:
        self.script = list(script or [])
        self.calls = 0

    async def create(self, **kwargs: Any) -> _ChatResponse:
        del kwargs
        self.calls += 1
        if self.script:
            step = self.script.pop(0)
            if isinstance(step, Exception):
                raise step
            return step
        return _ok('{"s":80}')


class _Chat:
    def __init__(self, completions: Any) -> None:
        self.completions = completions


class _ChatClient:
    def __init__(self, script: list[Any] | None = None) -> None:
        self.chat = _Chat(_Completions(script))


def _limit(monkeypatch: pytest.MonkeyPatch, value: str | None) -> None:
    if value is None:
        monkeypatch.delenv("OPENAI_MAX_REQUESTS", raising=False)
    else:
        monkeypatch.setenv("OPENAI_MAX_REQUESTS", value)
    get_settings.cache_clear()


def _silence_retry_sleep(monkeypatch: pytest.MonkeyPatch, module: str) -> None:
    async def _no_sleep(*_args: object, **_kwargs: object) -> None:
        return None

    monkeypatch.setattr(f"{module}.asyncio.sleep", _no_sleep)
    if module == "scorer.clients":
        monkeypatch.setattr(f"{module}.random.uniform", lambda *_args: 0.0)


async def _complete(client: OpenAIClient, *, user: str = "Job") -> str:
    return await client.complete(
        model="gpt-5-mini",
        system_blocks=[{"text": "Score."}],
        user=user,
        max_tokens=128,
        temperature=0.0,
        json_mode=True,
    )


@pytest.mark.parametrize("limit", [1, 4])
async def test_limit_allows_exactly_n_network_attempts(
    monkeypatch: pytest.MonkeyPatch, limit: int
) -> None:
    _limit(monkeypatch, str(limit))
    fake = _ChatClient()
    client = OpenAIClient(client=fake)
    for _ in range(limit):
        assert await _complete(client) == '{"s":80}'
    with pytest.raises(OpenAIBudgetExceeded):
        await _complete(client)
    assert fake.chat.completions.calls == limit
    assert get_openai_request_ledger().reserved == limit


async def test_concurrent_tasks_cannot_bypass_the_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _limit(monkeypatch, "3")
    fake = _ChatClient()
    client = OpenAIClient(client=fake)

    async def _one() -> str:
        await asyncio.sleep(0)
        return await _complete(client)

    results = await asyncio.gather(*[_one() for _ in range(20)], return_exceptions=True)
    successes = [item for item in results if item == '{"s":80}']
    blocked = [item for item in results if isinstance(item, OpenAIBudgetExceeded)]
    assert fake.chat.completions.calls == 3
    assert len(successes) == 3
    assert len(blocked) == 17
    assert get_openai_request_ledger().reserved == 3


async def test_empty_response_retry_consumes_a_request_slot(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _limit(monkeypatch, "2")
    fake = _ChatClient([_ok(""), _ok('{"s":70}')])
    client = OpenAIClient(client=fake)
    assert await _complete(client) == '{"s":70}'
    assert fake.chat.completions.calls == 2
    assert client.usage.empty_response_retries == 1
    assert get_openai_request_ledger().reserved == 2

    _limit(monkeypatch, "1")
    reset_openai_request_ledger()
    blocked = _ChatClient([_ok(""), _ok('{"s":70}')])
    blocked_client = OpenAIClient(client=blocked)
    with pytest.raises(OpenAIBudgetExceeded):
        await _complete(blocked_client)
    assert blocked.chat.completions.calls == 1
    assert blocked_client.usage.empty_response_retries == 0
    assert blocked_client.usage.request_attempts == 1
    assert get_openai_request_ledger().reserved == 1
    refused = await get_openai_request_ledger().summary_fields()
    assert refused["operations"]["other"]["request_attempts"] == 1
    assert refused["operations"]["other"]["empty_response_retries"] == 0


async def test_transient_retry_consumes_a_request_slot(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _silence_retry_sleep(monkeypatch, "scorer.clients")
    _limit(monkeypatch, "2")
    fake = _ChatClient([_RateLimit("429 RESOURCE_EXHAUSTED"), _ok('{"s":70}')])
    client = OpenAIClient(client=fake)
    assert await _complete(client) == '{"s":70}'
    assert fake.chat.completions.calls == 2
    assert client.usage.transient_retries == 1
    assert get_openai_request_ledger().reserved == 2

    _limit(monkeypatch, "1")
    reset_openai_request_ledger()
    blocked = _ChatClient([_RateLimit("429 RESOURCE_EXHAUSTED"), _ok('{"s":70}')])
    blocked_client = OpenAIClient(client=blocked)
    with pytest.raises(OpenAIBudgetExceeded):
        await _complete(blocked_client)
    assert blocked.chat.completions.calls == 1
    assert get_openai_request_ledger().reserved == 1


async def test_failed_attempt_is_not_refunded(monkeypatch: pytest.MonkeyPatch) -> None:
    _limit(monkeypatch, "1")
    fake = _ChatClient([ValueError("nope")])
    client = OpenAIClient(client=fake)
    with pytest.raises(ValueError, match="nope"):
        await _complete(client)
    assert fake.chat.completions.calls == 1
    assert get_openai_request_ledger().reserved == 1
    with pytest.raises(OpenAIBudgetExceeded):
        await _complete(client)
    assert fake.chat.completions.calls == 1


@dataclass
class _EmbedItem:
    index: int
    embedding: list[float]


@dataclass
class _EmbedResponse:
    data: list[_EmbedItem]


def _embed_ok() -> _EmbedResponse:
    return _EmbedResponse(data=[_EmbedItem(index=0, embedding=[0.25, 0.5])])


class _Embeddings:
    def __init__(self, script: list[Any]) -> None:
        self.script = list(script)
        self.calls = 0

    async def create(self, **kwargs: Any) -> _EmbedResponse:
        del kwargs
        self.calls += 1
        step = self.script.pop(0)
        if isinstance(step, Exception):
            raise step
        return step


class _EmbedClient:
    def __init__(self, script: list[Any]) -> None:
        self.embeddings = _Embeddings(script)


async def test_embedding_retry_consumes_a_request_slot(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _silence_retry_sleep(monkeypatch, "scorer.embeddings")
    _limit(monkeypatch, "2")
    fake = _EmbedClient([RuntimeError("503 UNAVAILABLE"), _embed_ok()])
    embedder = OpenAIEmbedder(client=fake)
    vectors = await embedder.embed(["a job description"])
    assert vectors == [[0.25, 0.5]]
    assert fake.embeddings.calls == 2
    assert get_openai_request_ledger().reserved == 2

    _limit(monkeypatch, "1")
    reset_openai_request_ledger()
    blocked = _EmbedClient([RuntimeError("503 UNAVAILABLE"), _embed_ok()])
    with pytest.raises(OpenAIBudgetExceeded):
        await OpenAIEmbedder(client=blocked).embed(["a job description"])
    assert blocked.embeddings.calls == 1
    assert get_openai_request_ledger().reserved == 1


async def test_role_classification_uses_the_shared_ledger(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _limit(monkeypatch, "1")
    fake = _ChatClient([_ok(_ROLE_JSON)])
    client = OpenAIClient(client=fake)
    classified = await classify_role(
        title="Intern",
        description=_AMBIGUOUS_JD,
        content_hash="gate",
        client=client,
    )
    assert classified.used_llm is True
    assert fake.chat.completions.calls == 1
    assert get_openai_request_ledger().reserved == 1

    follow = _ChatClient()
    with pytest.raises(OpenAIBudgetExceeded):
        await _complete(OpenAIClient(client=follow))
    assert follow.chat.completions.calls == 0

    embed = _EmbedClient([_embed_ok()])
    with pytest.raises(OpenAIBudgetExceeded):
        await OpenAIEmbedder(client=embed).embed(["another description"])
    assert embed.embeddings.calls == 0
    assert get_openai_request_ledger().reserved == 1


async def test_billing_error_blocks_later_reservations_but_not_inflight(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _limit(monkeypatch, None)
    warnings: list[dict[str, Any]] = []

    def _record(*_args: object, **kwargs: Any) -> None:
        warnings.append(kwargs)

    monkeypatch.setattr("scorer.clients.log.warning", _record)
    completions = _InFlightCompletions()
    fake = _ChatClient()
    fake.chat.completions = completions
    client = OpenAIClient(client=fake)

    first = asyncio.create_task(_complete(client, user=f"prompt {_SECRET}"))
    await completions.first_started.wait()
    second = asyncio.create_task(_complete(client, user=f"prompt {_SECRET}"))
    while completions.calls < 2:
        await asyncio.sleep(0)
    completions.release_first.set()
    with pytest.raises(LLMBillingError):
        await first
    assert await second == '{"s":80}'
    assert completions.calls == 2
    with pytest.raises(OpenAIBillingHalted):
        await _complete(client, user=f"prompt {_SECRET}")
    assert completions.calls == 2
    assert get_openai_request_ledger().halted is True
    rendered = repr(warnings)
    assert _SECRET not in rendered
    assert any(item.get("reason") == "billing" for item in warnings)


class _InFlightCompletions:
    def __init__(self) -> None:
        self.calls = 0
        self.first_started = asyncio.Event()
        self.release_first = asyncio.Event()

    async def create(self, **kwargs: Any) -> _ChatResponse:
        del kwargs
        self.calls += 1
        if self.calls == 1:
            self.first_started.set()
            await self.release_first.wait()
            raise RuntimeError(f"credits are depleted {_SECRET}")
        return _ok('{"s":80}')


async def test_unset_limit_does_not_cap_attempts(monkeypatch: pytest.MonkeyPatch) -> None:
    _limit(monkeypatch, None)
    assert get_settings().openai_max_requests is None
    fake = _ChatClient()
    client = OpenAIClient(client=fake)
    for _ in range(5):
        await _complete(client)
    assert fake.chat.completions.calls == 5
    assert get_openai_request_ledger().reserved == 5

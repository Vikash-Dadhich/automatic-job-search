"""OpenAI usage counters. The HTTP client is a fake; no network."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

import pytest

from scorer.clients import OpenAIClient, TokenUsage


@dataclass
class _Msg:
    content: str | None = None
    refusal: str | None = None


@dataclass
class _Choice:
    message: _Msg
    finish_reason: str | None = None


@dataclass
class _PromptDetails:
    cached_tokens: int | None = None


@dataclass
class _CompletionDetails:
    reasoning_tokens: int | None = None


@dataclass
class _Usage:
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    prompt_tokens_details: _PromptDetails | None = None
    completion_tokens_details: _CompletionDetails | None = None


@dataclass
class _Response:
    choices: list[_Choice]
    usage: _Usage | None = None
    id: str | None = None


class _RateLimit(Exception):
    status_code = 429


class _Completions:
    def __init__(self, script: list[Any]) -> None:
        self.script = list(script)
        self.calls: list[dict[str, Any]] = []

    async def create(self, **kwargs: Any) -> _Response:
        self.calls.append(kwargs)
        step = self.script.pop(0)
        if isinstance(step, Exception):
            raise step
        return step


class _Chat:
    def __init__(self, script: list[Any]) -> None:
        self.completions = _Completions(script)


class _Fake:
    def __init__(self, script: list[Any]) -> None:
        self.chat = _Chat(script)


def _ok(content: str, *, prompt: int | None = 10, completion: int | None = 2) -> _Response:
    return _Response(
        choices=[_Choice(message=_Msg(content=content))],
        usage=_Usage(prompt_tokens=prompt, completion_tokens=completion),
    )


async def _complete(client: OpenAIClient) -> str:
    return await client.complete(
        model="gpt-5-mini",
        system_blocks=[{"text": "Score."}],
        user="Job",
        max_tokens=128,
        temperature=0.0,
        json_mode=True,
    )


async def test_successful_response_records_tokens_and_one_attempt() -> None:
    client = OpenAIClient(client=_Fake([_ok('{"s":80}')]))
    text = await _complete(client)
    assert text == '{"s":80}'
    usage = client.usage
    assert usage.request_attempts == 1
    assert usage.successful_responses == 1
    assert usage.empty_response_retries == 0
    assert usage.api_exceptions == 0
    assert usage.transient_retries == 0
    assert usage.prompt_tokens == 10
    assert usage.completion_tokens == 2
    assert usage.cached_tokens is None
    assert usage.reasoning_tokens is None
    assert usage.models == {"gpt-5-mini": 1}


async def test_empty_response_retries_and_counts_both_requests() -> None:
    first = _ok("", prompt=11, completion=0)
    second = _ok('{"s":70}', prompt=15, completion=4)
    fake = _Fake([first, second])
    client = OpenAIClient(client=fake)
    text = await _complete(client)
    assert text == '{"s":70}'
    usage = client.usage
    assert usage.request_attempts == 2
    assert usage.successful_responses == 2
    assert usage.empty_response_retries == 1
    assert usage.api_exceptions == 0
    assert usage.prompt_tokens == 26
    assert usage.completion_tokens == 4
    assert usage.models == {"gpt-5-mini": 2}
    assert fake.chat.completions.calls[1]["max_completion_tokens"] == 384


async def test_failed_request_counts_an_attempt_not_a_success() -> None:
    client = OpenAIClient(client=_Fake([RuntimeError("boom")]))
    with pytest.raises(RuntimeError, match="boom"):
        await _complete(client)
    usage = client.usage
    assert usage.request_attempts == 1
    assert usage.successful_responses == 0
    assert usage.api_exceptions == 1
    assert usage.transient_retries == 0
    assert usage.prompt_tokens is None
    assert usage.total_calls == 0


async def test_absent_usage_metadata_stays_missing() -> None:
    blank = _Response(choices=[_Choice(message=_Msg(content='{"s":1}'))], usage=None)
    client = OpenAIClient(client=_Fake([blank]))
    await _complete(client)
    usage = client.usage
    assert usage.successful_responses == 1
    assert usage.prompt_tokens is None
    assert usage.completion_tokens is None
    assert usage.cached_tokens is None
    assert usage.reasoning_tokens is None


async def test_cached_and_reasoning_tokens_keep_an_explicit_zero() -> None:
    response = _Response(
        choices=[_Choice(message=_Msg(content='{"s":1}'))],
        usage=_Usage(
            prompt_tokens=40,
            completion_tokens=8,
            prompt_tokens_details=_PromptDetails(cached_tokens=0),
            completion_tokens_details=_CompletionDetails(reasoning_tokens=5),
        ),
    )
    client = OpenAIClient(client=_Fake([response]))
    await _complete(client)
    assert client.usage.cached_tokens == 0
    assert client.usage.reasoning_tokens == 5
    assert client.usage.prompt_tokens == 40


async def test_usage_aggregates_across_jobs_including_concurrent_calls() -> None:
    client = OpenAIClient(
        client=_Fake(
            [
                _ok('{"s":1}', prompt=20, completion=1),
                _ok('{"s":2}', prompt=30, completion=2),
                _ok('{"s":3}', prompt=40, completion=3),
            ]
        )
    )
    await asyncio.gather(_complete(client), _complete(client))
    await _complete(client)
    usage = client.usage
    assert usage.request_attempts == 3
    assert usage.successful_responses == 3
    assert usage.prompt_tokens == 90
    assert usage.completion_tokens == 6
    assert usage.models == {"gpt-5-mini": 3}


async def test_transient_retry_counts_the_failed_attempt_and_the_retry() -> None:
    client = OpenAIClient(
        client=_Fake([_RateLimit("slow"), _ok('{"s":9}', prompt=7, completion=1)])
    )
    text = await _complete(client)
    assert text == '{"s":9}'
    usage = client.usage
    assert usage.request_attempts == 2
    assert usage.successful_responses == 1
    assert usage.api_exceptions == 1
    assert usage.transient_retries == 1
    assert usage.empty_response_retries == 0
    assert usage.prompt_tokens == 7


def test_scoring_summary_emits_one_usage_line(monkeypatch: pytest.MonkeyPatch) -> None:
    from scorer.engine import ScoreSummary, _attach_usage_summary

    events: list[tuple[str, dict[str, Any]]] = []

    class _Log:
        def info(self, event: str, **kwargs: Any) -> None:
            events.append((event, kwargs))

    monkeypatch.setattr("scorer.engine.log", _Log())
    usage = TokenUsage(request_attempts=2, successful_responses=2, prompt_tokens=9)
    client = type("Client", (), {"usage": usage})()
    summary = ScoreSummary()
    _attach_usage_summary(summary, client)
    assert events == [("openai_usage_summary", usage.log_fields())]
    assert summary.token_usage is usage
    assert "Job" not in str(events)


async def test_usage_summary_survives_an_unexpected_score_pending_error(
    db_ready: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    from sqlmodel import select

    from core.db import Job, session_scope
    from scorer.engine import score_pending

    events: list[str] = []

    class _Log:
        def info(self, event: str, **kwargs: Any) -> None:
            events.append(event)

        def warning(self, event: str, **kwargs: Any) -> None:
            events.append(event)

    monkeypatch.setattr("scorer.engine.log", _Log())
    boom = RuntimeError("db read failed")

    async def fail(*_args: object, **_kwargs: object) -> list[object]:
        raise boom

    monkeypatch.setattr("scorer.engine.get_jobs_by_status", fail)
    client = OpenAIClient(client=_Fake([]))
    with pytest.raises(RuntimeError) as caught:
        await score_pending(client=client)
    assert caught.value is boom
    assert events.count("openai_usage_summary") == 1
    async with session_scope() as session:
        rows = (await session.exec(select(Job))).all()
    assert rows == []

    class _FailingLog:
        def info(self, event: str, **kwargs: Any) -> None:
            if event == "openai_usage_summary":
                raise RuntimeError("log failed")

        def warning(self, event: str, **kwargs: Any) -> None:
            events.append(event)

    monkeypatch.setattr("scorer.engine.log", _FailingLog())
    with pytest.raises(RuntimeError) as masked:
        await score_pending(client=client)
    assert masked.value is boom
    assert "openai_usage_summary_failed" in events


def _chat_attempts(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, object]]:
    events: list[dict[str, object]] = []

    def _record(event: str, **kwargs: object) -> None:
        if event == "openai_chat_attempt":
            events.append(kwargs)

    monkeypatch.setattr("scorer.clients.log.info", _record)
    return events


async def test_empty_length_attempt_is_distinct_from_the_followup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events = _chat_attempts(monkeypatch)
    job_text = "SECRET_JD product manager internship description"
    prompt_text = "SECRET_PROMPT score this candidate"
    model_text = '{"fit_score": 40}'
    first = _Response(
        id="chatcmpl-empty1",
        choices=[_Choice(message=_Msg(content="   "), finish_reason="length")],
        usage=_Usage(
            prompt_tokens=20,
            completion_tokens=1024,
            completion_tokens_details=_CompletionDetails(reasoning_tokens=1024),
        ),
    )
    second = _Response(
        id="chatcmpl-follow1",
        choices=[_Choice(message=_Msg(content=model_text), finish_reason="stop")],
        usage=_Usage(
            prompt_tokens=21,
            completion_tokens=40,
            completion_tokens_details=_CompletionDetails(reasoning_tokens=0),
        ),
    )
    fake = _Fake([first, second])
    client = OpenAIClient(client=fake)
    text = await client.complete(
        model="gpt-5-mini",
        system_blocks=[{"text": prompt_text}],
        user=job_text,
        max_tokens=1024,
        temperature=0.0,
        json_mode=True,
    )
    assert text == model_text
    assert [call["max_completion_tokens"] for call in fake.chat.completions.calls] == [1024, 3072]
    assert events == [
        {
            "attempt": "initial",
            "empty": True,
            "max_completion_tokens": 1024,
            "finish_reason": "length",
            "refusal": False,
            "prompt_tokens": 20,
            "completion_tokens": 1024,
            "reasoning_tokens": 1024,
            "response_id": "chatcmpl-empty1",
        },
        {
            "attempt": "followup",
            "empty": False,
            "max_completion_tokens": 3072,
            "finish_reason": "stop",
            "refusal": False,
            "prompt_tokens": 21,
            "completion_tokens": 40,
            "reasoning_tokens": 0,
            "response_id": "chatcmpl-follow1",
        },
    ]
    rendered = repr(events)
    assert job_text not in rendered
    assert prompt_text not in rendered
    assert model_text not in rendered
    usage = client.usage
    assert usage.request_attempts == 2
    assert usage.successful_responses == 2
    assert usage.empty_response_retries == 1
    assert usage.transient_retries == 0
    assert usage.prompt_tokens == 41
    assert usage.completion_tokens == 1064
    assert usage.reasoning_tokens == 1024


async def test_chat_attempt_log_keeps_missing_finish_reason_and_usage(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events = _chat_attempts(monkeypatch)
    client = OpenAIClient(
        client=_Fake([_Response(choices=[_Choice(message=_Msg(content='{"s":1}'))], usage=None)])
    )
    assert await _complete(client) == '{"s":1}'
    assert events == [
        {
            "attempt": "initial",
            "empty": False,
            "max_completion_tokens": 128,
            "finish_reason": None,
            "refusal": False,
            "prompt_tokens": None,
            "completion_tokens": None,
            "reasoning_tokens": None,
        }
    ]
    assert "response_id" not in events[0]
    assert client.usage.request_attempts == 1
    assert client.usage.empty_response_retries == 0
    assert client.usage.prompt_tokens is None
    assert client.usage.reasoning_tokens is None


async def test_chat_attempt_log_marks_a_refusal_without_its_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events = _chat_attempts(monkeypatch)
    refusal_text = "SECRET_REFUSAL cannot answer this posting"
    model_text = "SECRET_MODEL_JSON"
    job_text = "SECRET_JD role requirements"
    prompt_text = "SECRET_PROMPT instructions"
    client = OpenAIClient(
        client=_Fake(
            [
                _Response(
                    id="chatcmpl-refused",
                    choices=[
                        _Choice(
                            message=_Msg(content=model_text, refusal=refusal_text),
                            finish_reason="SECRET_FINISH wrote the answer",
                        )
                    ],
                    usage=_Usage(prompt_tokens=4, completion_tokens=2),
                )
            ]
        )
    )
    text = await client.complete(
        model="gpt-5-mini",
        system_blocks=[{"text": prompt_text}],
        user=job_text,
        max_tokens=128,
        temperature=0.0,
        json_mode=True,
    )
    assert text == model_text
    assert events == [
        {
            "attempt": "initial",
            "empty": False,
            "max_completion_tokens": 128,
            "finish_reason": "other",
            "refusal": True,
            "prompt_tokens": 4,
            "completion_tokens": 2,
            "reasoning_tokens": None,
            "response_id": "chatcmpl-refused",
        }
    ]
    rendered = repr(events)
    assert refusal_text not in rendered
    assert model_text not in rendered
    assert job_text not in rendered
    assert prompt_text not in rendered
    assert "SECRET_FINISH" not in rendered
    assert client.usage.empty_response_retries == 0
    assert client.usage.request_attempts == 1


def test_log_fields_do_not_replace_missing_tokens_with_zero() -> None:
    usage = TokenUsage(request_attempts=1, successful_responses=1)
    fields = usage.log_fields()
    assert fields["prompt_tokens"] is None
    assert fields["cached_tokens"] is None
    assert fields["reasoning_tokens"] is None
    assert fields["request_attempts"] == 1
    assert "text" not in fields

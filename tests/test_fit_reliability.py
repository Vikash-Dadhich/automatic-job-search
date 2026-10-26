"""Fit reliability: strict schema, rubric labels, grounding, retry cap."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from config.profile import Profile
from core.db import Status, get_job_by_id, session_scope, upsert_job
from scorer.clients import OpenAIClient
from scorer.engine import Scorer
from scorer.fit import (
    _CONFIDENCE,
    _JUDGMENTS,
    DIMENSIONS,
    FIT_JSON_SCHEMA,
    FIT_RUBRIC,
    _ground,
    evaluate_fit,
)
from tests.test_fit import _Client, _job, _payload


def test_schema_matches_the_validation_sets() -> None:
    schema = FIT_JSON_SCHEMA["schema"]
    assert FIT_JSON_SCHEMA["strict"] is True
    assert schema["additionalProperties"] is False
    dims = schema["properties"]["dimensions"]
    assert dims["required"] == list(DIMENSIONS)
    assert set(dims["properties"]) == set(DIMENSIONS)
    for item in dims["properties"].values():
        assert set(item["properties"]["judgment"]["enum"]) == _JUDGMENTS
        assert item["required"] == ["judgment", "note"]
    assert set(schema["properties"]["confidence"]["enum"]) == _CONFIDENCE
    assert set(schema["required"]) == set(schema["properties"])


def test_rubric_defines_every_label_for_requirements_risk() -> None:
    section = FIT_RUBRIC.split("REQUIREMENTS_RISK the", 1)[1].split("Never write", 1)[0]
    for label in _JUDGMENTS:
        assert label in section


async def test_fit_call_sends_the_strict_schema(profile: Profile) -> None:
    sent: dict[str, Any] = {}

    class _Spy(_Client):
        async def complete(self, **kwargs: object) -> str:
            sent.update(kwargs)
            return await super().complete(**kwargs)

    decision = await evaluate_fit(
        _job(), profile, _Spy(_payload(70)), model="gpt-5-mini", max_tokens=128  # type: ignore[arg-type]
    )
    assert decision.available is True
    assert sent["json_schema"] is FIT_JSON_SCHEMA


def test_grounding_accepts_inflections_and_still_drops_invented_facts() -> None:
    corpus = "Team leader for the platform migration. Manage roadmap with engineering partners."
    kept = _ground(
        [
            "Leadership of the platform migration maps to the roadmap work.",
            "Management of engineering partners.",
            "Strong xylophone certification.",
            "Hands-on kubernetes administration.",
        ],
        corpus,
    )
    assert kept == [
        "Leadership of the platform migration maps to the roadmap work.",
        "Management of engineering partners.",
    ]


async def test_unusable_answers_stop_after_the_cap(
    db_ready: Path, profile: Profile, monkeypatch: pytest.MonkeyPatch
) -> None:
    del db_ready
    monkeypatch.setenv("FIT_MAX_ATTEMPTS", "3")
    from config.settings import get_settings

    get_settings.cache_clear()
    async with session_scope() as session:
        saved = await upsert_job(session, _job())
        job_id = saved.id
    client = _Client("not json")
    kinds: list[tuple[int, int]] = []
    for _ in range(4):
        summary = await Scorer(client=client, profile=profile).score_pending(  # type: ignore[arg-type]
            client=client,  # type: ignore[arg-type]
            profile=profile,
            generate_outreach=False,
            concurrency=1,
        )
        kinds.append((summary.skipped, summary.errors))
    assert job_id is not None
    async with session_scope() as session:
        row = await get_job_by_id(session, job_id)
    assert row is not None
    assert client.calls == 3
    assert kinds == [(1, 0), (1, 0), (0, 1), (0, 0)]
    assert row.status == Status.error
    assert row.fit_attempts == 3
    assert row.score is None
    assert "unusable after 3 attempts" in (row.last_error or "")


async def test_good_answer_clears_the_attempt_count(
    db_ready: Path, profile: Profile
) -> None:
    del db_ready
    async with session_scope() as session:
        saved = await upsert_job(session, _job())
        saved.fit_attempts = 2
        session.add(saved)
        job_id = saved.id
    client = _Client(_payload(70))
    await Scorer(client=client, profile=profile).score_pending(  # type: ignore[arg-type]
        client=client,  # type: ignore[arg-type]
        profile=profile,
        generate_outreach=False,
        concurrency=1,
    )
    assert job_id is not None
    async with session_scope() as session:
        row = await get_job_by_id(session, job_id)
    assert row is not None
    assert row.score == 70
    assert row.fit_attempts is None


async def test_openai_client_sends_json_schema_response_format() -> None:
    seen: list[dict[str, Any]] = []

    class _Msg:
        content = "{}"

    class _Choice:
        message = _Msg()

    class _Usage:
        prompt_tokens = 1
        completion_tokens = 1

    class _Resp:
        choices = [_Choice()]
        usage = _Usage()

    class _Completions:
        async def create(self, **kwargs: Any) -> _Resp:
            seen.append(kwargs)
            return _Resp()

    class _Chat:
        completions = _Completions()

    class _Fake:
        chat = _Chat()

    client = OpenAIClient(client=_Fake())  # type: ignore[arg-type]
    await client.complete(
        model="gpt-5-mini",
        system_blocks=[{"text": "x"}],
        user="y",
        max_tokens=128,
        temperature=0.0,
        json_mode=True,
        json_schema=FIT_JSON_SCHEMA,
    )
    assert seen[0]["response_format"] == {"type": "json_schema", "json_schema": FIT_JSON_SCHEMA}

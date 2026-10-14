"""Workload caps and scoring safety stops. No network and no production database."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

import pytest
from pydantic import ValidationError
from sqlmodel import select

from config.settings import Settings, get_settings
from config.targets import SearchConfig, Targets, load_targets
from core.db import Job, Source, Status, session_scope, upsert_job
from orchestrator.monitoring import list_pipeline_runs
from orchestrator.pipeline import run_pipeline
from scorer.clients import (
    LLMBillingError,
    OpenAIClient,
    get_openai_request_ledger,
    reset_openai_request_ledger,
)
from scorer.embeddings import OpenAIEmbedder
from scorer.engine import ScoringSafetyHalt, score_pending
from scorer.role_classify import ROLE_CLASSIFIER_VERSION, classify_role
from scraper.discovery import build_discovery_plan
from scraper.ingest import run_ingestion
from scraper.models import RawPosting

_FIT = '{"s": 40, "r": ["Python"]}'
_DESC = "Requirements\nPython SQL data analysis for this role and team."
_AMBIGUOUS = (
    "Help the team and attend meetings during the summer internship."
    " The team meets weekly to review the work. " * 3
)
_CLEAR_PM = (
    "You will own the product roadmap and lead product prioritization. " * 2
)


def _env(monkeypatch: pytest.MonkeyPatch, **values: str | None) -> None:
    for key, value in values.items():
        if value is None:
            monkeypatch.delenv(key, raising=False)
        else:
            monkeypatch.setenv(key, value)
    get_settings.cache_clear()


async def _seed_jobs(count: int) -> None:
    async with session_scope() as session:
        for index in range(count):
            await upsert_job(
                session,
                Job(
                    source=Source.linkedin,
                    external_id=f"cap-{index}",
                    title="Engineer",
                    company=f"Co{index}",
                    location="Remote",
                    url=f"https://example.com/cap-{index}",
                    description_clean=_DESC,
                    status=Status.discovered,
                    content_hash=f"cap-hash-{index}",
                ),
            )


async def _rows() -> list[Job]:
    async with session_scope() as session:
        return list((await session.exec(select(Job))).all())


_ROLE = (
    '{"primary_family":"CONSULTING","subfamily":"BUSINESS_CONSULTING",'
    '"confidence":"medium","evidence":["JD describes business consulting for clients."]}'
)


class _FitClient:
    def __init__(self, payload: str = _FIT) -> None:
        self.payload = payload
        self.calls = 0
        self.models: list[str] = []

    async def complete(self, **kwargs: Any) -> str:
        self.calls += 1
        model = kwargs.get("model")
        if isinstance(model, str):
            self.models.append(model)
        return self.payload


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
    usage: _Usage


def _chat_ok() -> _ChatResponse:
    return _ChatResponse(choices=[_Choice(message=_Msg(content=_FIT))], usage=_Usage())


class _Completions:
    def __init__(self) -> None:
        self.calls = 0

    async def create(self, **_kwargs: Any) -> _ChatResponse:
        self.calls += 1
        return _chat_ok()


class _Chat:
    def __init__(self, completions: Any) -> None:
        self.completions = completions


class _ChatHolder:
    def __init__(self, completions: Any) -> None:
        self.chat = _Chat(completions)


def _posting(external_id: str) -> RawPosting:
    return RawPosting(
        source=Source.linkedin,
        external_id=external_id,
        title="Engineer",
        company=f"Co {external_id}",
        location="Remote",
        url=f"https://example.com/{external_id}",
        description_clean=_DESC,
    )


def test_capacity_of_one_is_one_planned_query() -> None:
    plan = build_discovery_plan(load_targets(), capacity=1)
    assert len(plan.searches) == 1


def test_negative_workload_limits_are_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(
            search_capacity=-1,
            ingest_posting_cap=-1,
            role_classify_max_calls=-1,
            embed_max_inputs=-1,
            openai_max_requests=-1,
        )


async def test_pipeline_passes_search_capacity(
    db_ready: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    seen: list[int | None] = []

    async def ingest(**kwargs: object) -> object:
        value = kwargs.get("search_capacity")
        seen.append(value if value is None or isinstance(value, int) else None)
        from scraper.ingest import IngestSummary

        return IngestSummary()

    monkeypatch.setattr("orchestrator.pipeline._run_ingestion", ingest)
    _env(monkeypatch, SEARCH_CAPACITY="1")
    await run_pipeline(
        enable_apply=False,
        enable_reviews=False,
        enable_prep_pack=False,
        enable_suggestions=False,
        enable_benchmark=False,
    )
    _env(monkeypatch, SEARCH_CAPACITY=None)
    await run_pipeline(
        enable_apply=False,
        enable_reviews=False,
        enable_prep_pack=False,
        enable_suggestions=False,
        enable_benchmark=False,
    )
    assert seen == [1, None]


async def test_posting_cap_does_not_persist_or_classify_the_next_row(
    db_ready: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    classified: list[str] = []

    async def spy_classify(**kwargs: object) -> object:
        title = kwargs.get("title")
        classified.append(title if isinstance(title, str) else "")
        from scorer.role_classify import _unknown

        return _unknown("hash", "test")

    async def fetch(*_args: object, on_batch: Any = None, **_kwargs: object) -> list[object]:
        assert on_batch is not None
        await on_batch([_posting("one"), _posting("two")])
        return []

    monkeypatch.setattr("scraper.ingest.fetch_linkedin_indeed", fetch)
    monkeypatch.setattr("scorer.role_classify.classify_role", spy_classify)
    _env(monkeypatch, INGEST_POSTING_CAP="1")
    summary = await run_ingestion(
        targets=Targets(search=SearchConfig(terms=["Intern"], sites=["linkedin"])),
        include_workday=False,
        search_capacity=1,
    )
    assert summary.upserted == 1
    assert len(classified) == 1
    rows = await _rows()
    assert len(rows) == 1


async def test_posting_cap_is_safe_when_batches_arrive_together(
    db_ready: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    classified: list[str] = []

    async def spy_classify(**kwargs: object) -> object:
        title = kwargs.get("title")
        classified.append(title if isinstance(title, str) else "")
        from scorer.role_classify import _unknown

        return _unknown("hash", "test")

    async def fetch(*_args: object, on_batch: Any = None, **_kwargs: object) -> list[object]:
        assert on_batch is not None
        await asyncio.gather(on_batch([_posting("a")]), on_batch([_posting("b")]))
        return []

    monkeypatch.setattr("scraper.ingest.fetch_linkedin_indeed", fetch)
    monkeypatch.setattr("scorer.role_classify.classify_role", spy_classify)
    _env(monkeypatch, INGEST_POSTING_CAP="1")
    summary = await run_ingestion(
        targets=Targets(search=SearchConfig(terms=["Intern"], sites=["linkedin"])),
        include_workday=False,
        search_capacity=1,
    )
    assert summary.upserted == 1
    assert len(classified) == 1
    assert len(await _rows()) == 1


async def test_role_call_cap_skips_deterministic_labels_and_blocks_zero(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _env(monkeypatch, ROLE_CLASSIFY_MAX_CALLS="1")
    client = _FitClient(_ROLE)
    decided = await classify_role(
        title="Product Manager Intern",
        description=_CLEAR_PM,
        content_hash="clear",
        client=client,
    )
    assert decided.used_llm is False
    assert client.calls == 0
    assert get_openai_request_ledger().role_calls == 0

    first = await classify_role(
        title="Intern",
        description=_AMBIGUOUS,
        content_hash="llm-1",
        client=client,
    )
    assert first.used_llm is True
    assert client.calls == 1
    assert client.models == [get_settings().openai_scorer_model]
    assert "role-classifier" not in client.models
    assert get_openai_request_ledger().role_calls == 1

    second = await classify_role(
        title="Intern",
        description=_AMBIGUOUS,
        content_hash="llm-2",
        client=client,
    )
    assert second.used_llm is False
    assert client.calls == 1
    assert get_openai_request_ledger().role_calls == 1

    reset_openai_request_ledger()
    _env(monkeypatch, ROLE_CLASSIFY_MAX_CALLS="0")
    blocked = _FitClient(_ROLE)
    refused = await classify_role(
        title="Intern",
        description=_AMBIGUOUS,
        content_hash="none",
        client=blocked,
    )
    assert refused.used_llm is False
    assert blocked.calls == 0
    assert get_openai_request_ledger().role_calls == 0


async def test_stored_role_label_does_not_consume_a_call_slot(
    db_ready: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    _env(monkeypatch, ROLE_CLASSIFY_MAX_CALLS="0")
    async with session_scope() as session:
        saved = await upsert_job(
            session,
            Job(
                source=Source.linkedin,
                external_id="cached-role",
                title="Engineer",
                company="CacheCo",
                location="Remote",
                url="https://example.com/cached-role",
                description_clean=_DESC,
                status=Status.discovered,
                content_hash="cached-hash",
                role_family="PRODUCT_MANAGEMENT",
                role_classifier_version=ROLE_CLASSIFIER_VERSION,
                role_content_hash="cached-hash",
            ),
        )
        assert saved.id is not None

    class _Explode:
        async def complete(self, **_kwargs: object) -> str:
            raise AssertionError("cached role label must not call the model")

    from scraper.ingest import _apply_role_classification

    async with session_scope() as session:
        job = (await _rows())[0]
        await _apply_role_classification(session, job, _Explode())  # type: ignore[arg-type]
    assert get_openai_request_ledger().role_calls == 0


@dataclass
class _EmbedItem:
    index: int
    embedding: list[float]


@dataclass
class _EmbedResponse:
    data: list[_EmbedItem]


class _Embeddings:
    def __init__(self) -> None:
        self.inputs: list[list[str]] = []

    async def create(self, **kwargs: Any) -> _EmbedResponse:
        raw = kwargs.get("input")
        texts = [str(item) for item in raw] if isinstance(raw, list) else []
        self.inputs.append(texts)
        items = [
            _EmbedItem(index=index, embedding=[0.2, 0.4])
            for index, _item in enumerate(texts)
        ]
        return _EmbedResponse(data=items)


class _EmbedHolder:
    def __init__(self, embeddings: _Embeddings) -> None:
        self.embeddings = embeddings


async def test_embed_cap_limits_cumulative_inputs_across_batches(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _env(monkeypatch, EMBED_MAX_INPUTS="2", VECTOR_BATCH_SIZE="1")
    fake = _Embeddings()
    embedder = OpenAIEmbedder(client=_EmbedHolder(fake))
    first = await embedder.embed(["a", "b", "c", "d"])
    assert [len(batch) for batch in fake.inputs] == [1, 1]
    assert sum(len(batch) for batch in fake.inputs) == 2
    assert len(first) == 2
    second = await embedder.embed(["e"])
    assert second == []
    assert sum(len(batch) for batch in fake.inputs) == 2


class _ShortEmbedder:
    """Returns one vector per call until two inputs have been accepted."""

    def __init__(self) -> None:
        self.sent = 0

    async def embed(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        width = get_settings().vector_dimensions
        for _text in texts:
            if self.sent >= 2:
                break
            self.sent += 1
            vectors.append([1.0] * width)
        return vectors


async def test_short_embed_result_does_not_fail_open_into_fit(
    db_ready: object,
    profile: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    _env(monkeypatch, VECTOR_GATE_ENABLED="true", SCORE_BUDGET=None)
    await _seed_jobs(3)
    client = _FitClient()
    summary = await score_pending(
        client=client,  # type: ignore[arg-type]
        profile=profile,  # type: ignore[arg-type]
        embedder=_ShortEmbedder(),  # type: ignore[arg-type]
    )
    assert summary.scored < 3
    assert summary.skipped >= 1
    assert client.calls == summary.scored
    discovered = [row for row in await _rows() if row.status == Status.discovered]
    assert len(discovered) == 3 - summary.scored


async def test_score_budget_admits_jobs_not_requests(
    db_ready: object,
    profile: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    _env(monkeypatch, SCORE_BUDGET="1", VECTOR_GATE_ENABLED="false")
    await _seed_jobs(3)
    client = _FitClient()
    summary = await score_pending(
        client=client,  # type: ignore[arg-type]
        profile=profile,  # type: ignore[arg-type]
    )
    assert client.calls == 1
    assert summary.scored == 1
    discovered = [row for row in await _rows() if row.status == Status.discovered]
    assert len(discovered) == 2


async def test_vector_gate_billing_does_not_start_fit_scoring(
    db_ready: object,
    profile: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    _env(monkeypatch, VECTOR_GATE_ENABLED="true")
    await _seed_jobs(1)

    class _BillingEmbedder:
        async def embed(self, texts: list[str]) -> list[list[float]]:
            del texts
            raise LLMBillingError("credits are depleted")

    client = _FitClient()
    with pytest.raises(ScoringSafetyHalt, match="scoring_safety_halt:"):
        await score_pending(
            client=client,  # type: ignore[arg-type]
            profile=profile,  # type: ignore[arg-type]
            embedder=_BillingEmbedder(),  # type: ignore[arg-type]
        )
    assert client.calls == 0
    rows = await _rows()
    assert rows[0].status == Status.discovered


async def test_request_budget_stops_jobs_that_have_not_started(
    db_ready: object,
    profile: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    _env(
        monkeypatch,
        OPENAI_MAX_REQUESTS="1",
        SCORE_BUDGET="3",
        VECTOR_GATE_ENABLED="false",
        TIER_ONE_DRAFTS_ENABLED="false",
    )
    await _seed_jobs(3)
    completions = _Completions()
    client = OpenAIClient(client=_ChatHolder(completions))
    with pytest.raises(ScoringSafetyHalt, match="scoring_safety_halt: OpenAIBudgetExceeded"):
        await score_pending(client=client, profile=profile, concurrency=1)  # type: ignore[arg-type]
    assert completions.calls == 1
    rows = await _rows()
    assert sum(row.status == Status.discovered for row in rows) == 2
    assert all(row.status != Status.error for row in rows)


class _InFlightCompletions:
    def __init__(self) -> None:
        self.calls = 0
        self.first_started = asyncio.Event()
        self.second_started = asyncio.Event()
        self.release_first = asyncio.Event()
        self.release_second = asyncio.Event()

    async def create(self, **_kwargs: Any) -> _ChatResponse:
        self.calls += 1
        if self.calls == 1:
            self.first_started.set()
            await self.release_first.wait()
            raise RuntimeError("credits are depleted")
        if self.calls == 2:
            self.second_started.set()
            await self.release_second.wait()
            return _chat_ok()
        raise AssertionError("a third request started")


async def test_inflight_score_persists_and_later_jobs_do_not_start(
    db_ready: object,
    profile: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    _env(
        monkeypatch,
        OPENAI_MAX_REQUESTS=None,
        VECTOR_GATE_ENABLED="false",
        TIER_ONE_DRAFTS_ENABLED="false",
    )
    await _seed_jobs(3)
    completions = _InFlightCompletions()
    client = OpenAIClient(client=_ChatHolder(completions))
    task = asyncio.create_task(
        score_pending(client=client, profile=profile, concurrency=2)  # type: ignore[arg-type]
    )
    await completions.first_started.wait()
    await completions.second_started.wait()
    completions.release_first.set()
    while not get_openai_request_ledger().halted:
        await asyncio.sleep(0)
    completions.release_second.set()
    with pytest.raises(ScoringSafetyHalt, match="scoring_safety_halt: LLMBillingError"):
        await task
    assert completions.calls == 2
    rows = await _rows()
    assert sum(row.status == Status.discovered for row in rows) == 2
    assert all(row.status != Status.error for row in rows)
    assert sum(row.score is not None for row in rows) == 1


async def test_ordinary_embed_failure_still_fail_opens(
    db_ready: object,
    profile: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    _env(monkeypatch, VECTOR_GATE_ENABLED="true", SCORE_BUDGET="1")
    await _seed_jobs(1)

    class _Down:
        async def embed(self, texts: list[str]) -> list[list[float]]:
            del texts
            raise RuntimeError("embed down")

    client = _FitClient()
    summary = await score_pending(
        client=client,  # type: ignore[arg-type]
        profile=profile,  # type: ignore[arg-type]
        embedder=_Down(),  # type: ignore[arg-type]
    )
    assert client.calls == 1
    assert summary.scored == 1


async def test_safety_halt_marks_the_pipeline_failed(
    db_ready: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready

    async def ingest(**_kwargs: object) -> object:
        from scraper.ingest import IngestSummary

        return IngestSummary()

    async def halt(**_kwargs: object) -> object:
        raise ScoringSafetyHalt("OpenAIBudgetExceeded")

    monkeypatch.setattr("orchestrator.pipeline._run_ingestion", ingest)
    monkeypatch.setattr("orchestrator.pipeline._score_pending", halt)
    summary = await run_pipeline(
        enable_apply=False,
        enable_reviews=False,
        enable_prep_pack=False,
        enable_suggestions=False,
        enable_benchmark=False,
    )
    assert summary.ok is False
    assert summary.stage_errors["scoring"].startswith("scoring_safety_halt:")
    runs = await list_pipeline_runs()
    assert runs[0].status == "failed"


async def test_unset_limits_do_not_cap_work(monkeypatch: pytest.MonkeyPatch) -> None:
    _env(
        monkeypatch,
        SEARCH_CAPACITY=None,
        INGEST_POSTING_CAP=None,
        ROLE_CLASSIFY_MAX_CALLS=None,
        EMBED_MAX_INPUTS=None,
        SCORE_BUDGET=None,
        OPENAI_MAX_REQUESTS=None,
    )
    settings = get_settings()
    assert settings.search_capacity is None
    assert settings.ingest_posting_cap is None
    assert settings.role_classify_max_calls is None
    assert settings.embed_max_inputs is None
    assert settings.score_budget is None
    assert settings.openai_max_requests is None
    fake = _Embeddings()
    embedder = OpenAIEmbedder(client=_EmbedHolder(fake))
    vectors = await embedder.embed(["a", "b", "c"])
    assert len(vectors) == 3
    assert sum(len(batch) for batch in fake.inputs) == 3

"""Offline tests for orchestrator.pipeline (monkeypatched stages)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

import orchestrator.pipeline as pipeline_mod
from core.db import Status
from orchestrator.pipeline import run_pipeline


@dataclass
class _FakeSummary:
    name: str
    n: int = 1


async def test_pipeline_order_and_aggregation(
    db_ready: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    order: list[str] = []

    async def fake_ingestion(**_kwargs: object) -> _FakeSummary:
        order.append("ingestion")
        return _FakeSummary("ingestion")

    async def fake_score() -> _FakeSummary:
        order.append("scoring")
        return _FakeSummary("scoring")

    async def fake_shortlist() -> dict[str, int]:
        order.append("shortlist")
        return {"selected": 0, "considered": 0, "already_pending": 0}

    async def fake_resume() -> _FakeSummary:
        order.append("resume")
        return _FakeSummary("resume")

    async def fake_suggest_gen(*_args: object, **_kwargs: object) -> dict[str, int]:
        order.append("suggest_generate")
        return {"generated": 0, "skipped": 0}

    async def fake_suggest_send() -> _FakeSummary:
        order.append("suggest_send")
        return _FakeSummary("suggest_send")

    async def fake_prep(*_args: object, **_kwargs: object) -> _FakeSummary:
        order.append("prep")
        return _FakeSummary("prep")

    async def fake_portfolio(*_args: object, **_kwargs: object) -> dict[str, list[int]]:
        order.append("portfolio")
        return {"allocated_ids": []}

    async def fake_apply(*_args: object, **_kwargs: object) -> _FakeSummary:
        order.append("apply")
        return _FakeSummary("apply")

    async def fake_reviews() -> _FakeSummary:
        order.append("reviews")
        return _FakeSummary("reviews")

    async def fake_outcomes() -> _FakeSummary:
        order.append("outcome_prompts")
        return _FakeSummary("outcome_prompts")

    async def fake_alerts() -> _FakeSummary:
        order.append("alerts")
        return _FakeSummary("alerts")

    async def fake_benchmark(*_args: object, **_kwargs: object) -> dict[str, int]:
        order.append("benchmark")
        return {"benchmarked": 0, "skipped": 0}

    monkeypatch.setattr(pipeline_mod, "_run_ingestion", fake_ingestion)
    monkeypatch.setattr(pipeline_mod, "_score_pending", fake_score)
    monkeypatch.setattr(pipeline_mod, "_shortlist_stage", fake_shortlist)
    monkeypatch.setattr(pipeline_mod, "_prepare_shortlisted_resumes", fake_resume)
    monkeypatch.setattr(pipeline_mod, "_generate_suggestions_stage", fake_suggest_gen)
    monkeypatch.setattr(pipeline_mod, "_send_pending_suggestions", fake_suggest_send)
    monkeypatch.setattr(pipeline_mod, "_benchmark_tier_one_stage", fake_benchmark)
    monkeypatch.setattr(pipeline_mod, "_send_prep_pack", fake_prep)
    monkeypatch.setattr(pipeline_mod, "_portfolio_stage", fake_portfolio)
    monkeypatch.setattr(pipeline_mod, "_apply_pending", fake_apply)
    monkeypatch.setattr(pipeline_mod, "_send_pending_reviews", fake_reviews)
    monkeypatch.setattr(pipeline_mod, "_send_outcome_prompts", fake_outcomes)
    monkeypatch.setattr(pipeline_mod, "_send_pending_alerts", fake_alerts)

    summary = await run_pipeline(
        enable_apply=True,
        enable_reviews=True,
        enable_prep_pack=True,
        enable_suggestions=True,
        enable_benchmark=True,
    )
    assert order == [
        "ingestion",
        "scoring",
        "shortlist",
        "resume",
        "suggest_generate",
        "suggest_send",
        "benchmark",
        "prep",
        "portfolio",
        "apply",
        "reviews",
        "outcome_prompts",
        "alerts",
    ]
    assert set(summary.stages) == {
        "ingestion",
        "scoring",
        "shortlist",
        "resume",
        "suggest_generate",
        "suggest_send",
        "benchmark",
        "prep",
        "portfolio",
        "apply",
        "reviews",
        "outcome_prompts",
        "alerts",
    }
    assert summary.stage_errors == {}
    assert summary.skipped == []
    assert summary.ok
    assert summary.duration_ms >= 0


async def test_pipeline_skips_apply_and_reviews(
    db_ready: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    order: list[str] = []

    async def track(name: str) -> _FakeSummary:
        order.append(name)
        return _FakeSummary(name)

    monkeypatch.setattr(pipeline_mod, "_run_ingestion", lambda **_k: track("ingestion"))
    monkeypatch.setattr(pipeline_mod, "_score_pending", lambda: track("scoring"))
    monkeypatch.setattr(pipeline_mod, "_shortlist_stage", lambda: track("shortlist"))
    monkeypatch.setattr(pipeline_mod, "_prepare_shortlisted_resumes", lambda: track("resume"))

    async def boom() -> Any:
        raise AssertionError("should not run")

    monkeypatch.setattr(pipeline_mod, "_generate_suggestions_stage", boom)
    monkeypatch.setattr(pipeline_mod, "_send_pending_suggestions", boom)
    monkeypatch.setattr(pipeline_mod, "_send_prep_pack", boom)
    monkeypatch.setattr(pipeline_mod, "_apply_pending", boom)
    monkeypatch.setattr(pipeline_mod, "_send_pending_reviews", boom)
    monkeypatch.setattr(pipeline_mod, "_send_pending_alerts", boom)

    summary = await run_pipeline(
        enable_apply=False,
        enable_reviews=False,
        enable_suggestions=False,
        enable_benchmark=False,
    )
    assert order == ["ingestion", "scoring", "shortlist", "resume"]
    assert summary.skipped == [
        "suggest_generate",
        "suggest_send",
        "benchmark",
        "prep",
        "portfolio",
        "apply",
        "reviews",
        "outcome_prompts",
        "alerts",
    ]
    assert "portfolio" not in summary.stages
    assert "apply" not in summary.stages
    assert "prep" not in summary.stages
    assert "reviews" not in summary.stages
    assert "alerts" not in summary.stages
    assert "suggest_generate" not in summary.stages


async def test_pipeline_stage_isolation(
    db_ready: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    order: list[str] = []

    async def ok(name: str) -> _FakeSummary:
        order.append(name)
        return _FakeSummary(name)

    async def fail_score() -> _FakeSummary:
        order.append("scoring")
        raise RuntimeError("score boom")

    monkeypatch.setattr(pipeline_mod, "_run_ingestion", lambda **_k: ok("ingestion"))
    monkeypatch.setattr(pipeline_mod, "_score_pending", fail_score)
    monkeypatch.setattr(pipeline_mod, "_shortlist_stage", lambda: ok("shortlist"))
    monkeypatch.setattr(pipeline_mod, "_prepare_shortlisted_resumes", lambda: ok("resume"))
    monkeypatch.setattr(
        pipeline_mod, "_generate_suggestions_stage", lambda *_a, **_k: ok("suggest_generate")
    )
    monkeypatch.setattr(
        pipeline_mod, "_send_pending_suggestions", lambda *_a, **_k: ok("suggest_send")
    )
    monkeypatch.setattr(
        pipeline_mod, "_benchmark_tier_one_stage", lambda *_a, **_k: ok("benchmark")
    )
    monkeypatch.setattr(
        pipeline_mod, "_send_prep_pack", lambda *_a, **_k: ok("prep")
    )
    monkeypatch.setattr(pipeline_mod, "_portfolio_stage", lambda *_a, **_k: ok("portfolio"))
    monkeypatch.setattr(pipeline_mod, "_apply_pending", lambda *_a, **_k: ok("apply"))
    monkeypatch.setattr(pipeline_mod, "_send_pending_reviews", lambda: ok("reviews"))
    monkeypatch.setattr(
        pipeline_mod, "_send_outcome_prompts", lambda: ok("outcome_prompts")
    )
    monkeypatch.setattr(pipeline_mod, "_send_pending_alerts", lambda: ok("alerts"))

    summary = await run_pipeline(
        enable_apply=True,
        enable_reviews=True,
        enable_prep_pack=True,
        enable_suggestions=True,
        enable_benchmark=True,
    )
    assert order == [
        "ingestion",
        "scoring",
        "shortlist",
        "resume",
        "suggest_generate",
        "suggest_send",
        "benchmark",
        "prep",
        "portfolio",
        "apply",
        "reviews",
        "outcome_prompts",
        "alerts",
    ]
    assert "scoring" in summary.stage_errors
    assert "score boom" in summary.stage_errors["scoring"]
    assert "resume" in summary.stages
    assert not summary.ok


async def test_scoring_safety_halt_skips_outbound_stages_when_reviews_are_on(
    db_ready: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Production leaves reviews on. A scoring halt must not reach Telegram."""
    del db_ready
    outbound: list[str] = []

    async def ingest(**_kwargs: object) -> _FakeSummary:
        return _FakeSummary("ingestion")

    async def halt(**_kwargs: object) -> _FakeSummary:
        from scorer.engine import ScoringSafetyHalt

        raise ScoringSafetyHalt("OpenAIBudgetExceeded")

    async def local(name: str) -> _FakeSummary:
        return _FakeSummary(name)

    def outbound_stage(name: str):
        async def _run(*_args: object, **_kwargs: object) -> _FakeSummary:
            outbound.append(name)
            raise AssertionError(name)

        return _run

    monkeypatch.setattr(pipeline_mod, "_run_ingestion", ingest)
    monkeypatch.setattr(pipeline_mod, "_score_pending", halt)
    monkeypatch.setattr(pipeline_mod, "_shortlist_stage", lambda: local("shortlist"))
    monkeypatch.setattr(pipeline_mod, "_prepare_shortlisted_resumes", lambda: local("resume"))
    monkeypatch.setattr(
        pipeline_mod,
        "_generate_suggestions_stage",
        outbound_stage("suggest_generate"),
    )
    monkeypatch.setattr(pipeline_mod, "_send_pending_suggestions", outbound_stage("suggest_send"))
    monkeypatch.setattr(pipeline_mod, "_benchmark_tier_one_stage", outbound_stage("benchmark"))
    monkeypatch.setattr(pipeline_mod, "_send_prep_pack", outbound_stage("prep"))
    monkeypatch.setattr(pipeline_mod, "_portfolio_stage", outbound_stage("portfolio"))
    monkeypatch.setattr(pipeline_mod, "_apply_pending", outbound_stage("apply"))
    monkeypatch.setattr(pipeline_mod, "_send_pending_reviews", outbound_stage("reviews"))
    monkeypatch.setattr(pipeline_mod, "_send_outcome_prompts", outbound_stage("outcome_prompts"))
    monkeypatch.setattr(pipeline_mod, "_send_pending_alerts", outbound_stage("alerts"))
    events: list[str] = []

    def _record(event: str, **_kwargs: object) -> None:
        events.append(event)

    monkeypatch.setattr("scorer.clients.log.info", _record)

    summary = await run_pipeline(
        enable_apply=True,
        enable_reviews=True,
        enable_prep_pack=True,
        enable_suggestions=True,
        enable_benchmark=True,
    )
    assert outbound == []
    assert summary.stage_errors["scoring"].startswith("scoring_safety_halt:")
    assert "shortlist" in summary.stages
    assert "resume" in summary.stages
    for name in (
        "suggest_generate",
        "suggest_send",
        "benchmark",
        "prep",
        "portfolio",
        "apply",
        "reviews",
        "outcome_prompts",
        "alerts",
    ):
        assert name in summary.skipped
        assert name not in summary.stages
    assert not summary.ok
    assert "openai_run_usage" in events
    from orchestrator.monitoring import list_pipeline_runs

    runs = await list_pipeline_runs()
    assert runs[0].status == "failed"


async def test_pipeline_resume_uses_the_review_queue(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, object] = {}

    async def fake_prepare(**kwargs: object) -> _FakeSummary:
        seen.update(kwargs)
        return _FakeSummary("resume")

    monkeypatch.setattr(pipeline_mod, "_prepare_resumes", fake_prepare)
    await pipeline_mod._prepare_shortlisted_resumes()
    assert seen["status"] == Status.pending_review

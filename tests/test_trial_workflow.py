"""Static checks for the isolated trial workflow. No network and no dispatch."""

from __future__ import annotations

import sqlite3
import subprocess
from pathlib import Path

import pytest

from config.settings import get_settings
from core.db import init_db, normalize_database_url, reset_engine
from scorer.clients import get_openai_request_ledger
from scorer.embeddings import get_openai_request_ledger as embed_ledger
from scorer.engine import ScoringSafetyHalt

_ROOT = Path(__file__).resolve().parents[1]
_TRIAL = _ROOT / ".github" / "workflows" / "trial.yml"
_PRODUCTION = _ROOT / ".github" / "workflows" / "pipeline.yml"


def _trial_text() -> str:
    return _TRIAL.read_text(encoding="utf-8")


def test_trial_workflow_is_manual_and_isolated() -> None:
    text = _trial_text()
    assert "workflow_dispatch:" in text
    assert "schedule:" not in text
    assert "push:" not in text
    assert "pull_request:" not in text
    assert "group: pipeline-trial" in text
    assert "cancel-in-progress: false" in text
    assert "timeout-minutes: 30" in text
    assert "contents: read" in text
    assert "ref: ${{ github.sha }}" in text
    assert "trial_sha=" in text
    assert "trial_ref=" in text
    assert 'DATABASE_URL: sqlite+aiosqlite:///storage/trial.db' in text
    assert "secrets.DATABASE_URL" not in text
    assert "TELEGRAM_BOT_TOKEN" not in text
    assert "TELEGRAM_CHAT_ID" not in text
    assert "printenv" not in text
    assert "OPENAI_API_KEY" in text
    assert "secrets.OPENAI_API_KEY" in text
    for flag in (
        'INTERNSHIP_ONLY: "true"',
        'ENABLE_APPLY: "false"',
        'ENABLE_BENCHMARK: "false"',
        'ENABLE_LINKEDIN_SCRAPE: "false"',
        'ENABLE_REVIEWS: "false"',
        'ENABLE_PREP_PACK: "false"',
        'ENABLE_SUGGESTIONS: "false"',
        'TIER_ONE_DRAFTS_ENABLED: "false"',
        'SEARCH_CAPACITY: "1"',
        'INGEST_POSTING_CAP: "8"',
        'ROLE_CLASSIFY_MAX_CALLS: "0"',
        'EMBED_MAX_INPUTS: "8"',
        'SCORE_BUDGET: "3"',
        'SCORER_CONCURRENCY: "1"',
        'LLM_MAX_ATTEMPTS: "1"',
        'OPENAI_MAX_REQUESTS: "12"',
    ):
        assert flag in text
    assert "hard spend limit" in text
    assert "spend alert only" in text.lower() or "A spend alert only" in text


def test_production_workflow_file_is_unchanged() -> None:
    committed = subprocess.check_output(
        ["git", "show", "HEAD:.github/workflows/pipeline.yml"],
        cwd=_ROOT,
        text=True,
    )
    assert _PRODUCTION.read_text(encoding="utf-8") == committed
    assert "secrets.DATABASE_URL" in committed
    assert "pipeline-trial" not in committed


def test_trial_env_matches_the_settings_parser(monkeypatch: pytest.MonkeyPatch) -> None:
    values = {
        "SEARCH_CAPACITY": "1",
        "INGEST_POSTING_CAP": "8",
        "ROLE_CLASSIFY_MAX_CALLS": "0",
        "EMBED_MAX_INPUTS": "8",
        "SCORE_BUDGET": "3",
        "SCORER_CONCURRENCY": "1",
        "LLM_MAX_ATTEMPTS": "1",
        "OPENAI_MAX_REQUESTS": "12",
        "INTERNSHIP_ONLY": "true",
        "ENABLE_APPLY": "false",
        "ENABLE_BENCHMARK": "false",
        "ENABLE_LINKEDIN_SCRAPE": "false",
        "ENABLE_REVIEWS": "false",
        "ENABLE_PREP_PACK": "false",
        "ENABLE_SUGGESTIONS": "false",
        "TIER_ONE_DRAFTS_ENABLED": "false",
        "DATABASE_URL": "sqlite+aiosqlite:///storage/trial.db",
    }
    for key, value in values.items():
        assert f"{key}:" in _trial_text()
        monkeypatch.setenv(key, value)
    get_settings.cache_clear()
    settings = get_settings()
    assert settings.search_capacity == 1
    assert settings.ingest_posting_cap == 8
    assert settings.role_classify_max_calls == 0
    assert settings.embed_max_inputs == 8
    assert settings.score_budget == 3
    assert settings.scorer_concurrency == 1
    assert settings.llm_max_attempts == 1
    assert settings.openai_max_requests == 12
    assert settings.internship_only is True
    assert settings.enable_apply is False
    assert settings.enable_benchmark is False
    assert settings.enable_linkedin_scrape is False
    assert settings.enable_reviews is False
    assert settings.enable_prep_pack is False
    assert settings.enable_suggestions is False
    assert settings.tier_one_drafts_enabled is False
    url = normalize_database_url(settings.database_url)
    assert url.startswith("sqlite+aiosqlite:///")
    assert "postgres" not in url
    assert get_openai_request_ledger() is embed_ledger()


async def test_trial_sqlite_url_creates_the_schema(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    db_path = tmp_path / "trial.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    get_settings.cache_clear()
    await reset_engine()
    await init_db()
    await reset_engine()
    connection = sqlite3.connect(db_path)
    try:
        tables = {
            row[0]
            for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }
        columns = {
            row[1] for row in connection.execute("PRAGMA table_info(jobs)")
        }
    finally:
        connection.close()
    assert "jobs" in tables
    assert "pipeline_runs" in tables
    assert "pipeline_stage_runs" in tables
    assert {"source", "status", "score"} <= columns


async def test_safety_halt_does_not_send_or_apply(
    db_ready: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    for key, value in {
        "ENABLE_REVIEWS": "false",
        "ENABLE_PREP_PACK": "false",
        "ENABLE_APPLY": "false",
        "ENABLE_SUGGESTIONS": "false",
        "ENABLE_BENCHMARK": "false",
        "ENABLE_LINKEDIN_SCRAPE": "false",
        "TIER_ONE_DRAFTS_ENABLED": "false",
    }.items():
        monkeypatch.setenv(key, value)
    get_settings.cache_clear()

    async def ingest(**_kwargs: object) -> object:
        from scraper.ingest import IngestSummary

        return IngestSummary()

    async def halt(**_kwargs: object) -> object:
        raise ScoringSafetyHalt("OpenAIBudgetExceeded")

    async def forbidden(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("trial side effect")

    import orchestrator.pipeline as pipeline_mod

    monkeypatch.setattr(pipeline_mod, "_run_ingestion", ingest)
    monkeypatch.setattr(pipeline_mod, "_score_pending", halt)
    for name in (
        "_send_prep_pack",
        "_send_pending_reviews",
        "_send_outcome_prompts",
        "_send_pending_alerts",
        "_send_pending_suggestions",
        "_apply_pending",
        "_benchmark_tier_one_stage",
    ):
        monkeypatch.setattr(pipeline_mod, name, forbidden)

    summary = await pipeline_mod.run_pipeline()
    assert summary.ok is False
    assert summary.stage_errors["scoring"].startswith("scoring_safety_halt:")
    from orchestrator.monitoring import list_pipeline_runs

    runs = await list_pipeline_runs()
    assert runs[0].status == "failed"
    assert "reviews" in summary.skipped
    assert "apply" in summary.skipped
    assert "prep" in summary.skipped

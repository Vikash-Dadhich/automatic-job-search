"""Operational history and health. No network and no scheduler."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import Table
from sqlalchemy.dialects import postgresql, sqlite
from sqlalchemy.schema import CreateTable
from sqlmodel import SQLModel, func, select

import orchestrator.pipeline as pipeline_mod
from config.settings import get_settings
from core.db import (
    Application,
    Job,
    Source,
    Status,
    reset_engine,
    session_scope,
)
from main import main
from orchestrator.health import format_health_report, get_health_report
from orchestrator.monitoring import (
    MONITORING_VERSION,
    close_pipeline_run,
    close_stage_run,
    interrupt_stale_runs,
    list_pipeline_runs,
    list_stage_runs,
    load_monitoring_config,
    open_pipeline_run,
    open_stage_run,
    stage_counters,
    validate_operational_config,
)
from orchestrator.pipeline import run_pipeline

NOW = datetime(2026, 10, 2, 15, 0, tzinfo=UTC)


def _job(external_id: str, **kwargs: object) -> Job:
    data: dict[str, object] = {
        "source": Source.linkedin,
        "external_id": external_id,
        "title": "Intern",
        "company": "Acme",
        "url": f"https://jobs.example.com/{external_id}",
        "status": Status.discovered,
        "description_clean": "SECRET_JD_BODY",
    }
    data.update(kwargs)
    return Job(**data)  # type: ignore[arg-type]


def test_monitoring_config_is_versioned() -> None:
    loaded = load_monitoring_config()
    assert loaded["version"] == MONITORING_VERSION
    assert loaded["monitoring"]["stale_run_minutes"] == 180
    assert validate_operational_config() == []


def test_counters_keep_known_integers_only() -> None:
    assert stage_counters(
        {"selected": 2, "selected_ids": [1, 2], "note": "secret", "fetched": True}
    ) == {"selected": 2}


def test_operational_tables_compile_for_sqlite_and_postgres() -> None:
    for dialect in (sqlite.dialect(), postgresql.dialect()):
        for name in ("pipeline_runs", "pipeline_stage_runs"):
            table = SQLModel.metadata.tables[name]
            assert isinstance(table, Table)
            sql = str(CreateTable(table).compile(dialect=dialect))
            assert name in sql


async def test_successful_run_records_duration(db_ready: object) -> None:
    del db_ready
    run_id = await open_pipeline_run(now=NOW, run_key="ok")
    assert run_id is not None
    await close_pipeline_run(
        run_id,
        status="succeeded",
        now=NOW + timedelta(seconds=2),
        error_count=0,
        skipped_count=1,
    )
    runs = await list_pipeline_runs()
    assert runs[0].status == "succeeded"
    assert runs[0].duration_ms == 2000
    assert runs[0].monitoring_version == MONITORING_VERSION


async def test_stage_rows_keep_status_error_and_counters(db_ready: object) -> None:
    del db_ready
    run_id = await open_pipeline_run(now=NOW, run_key="stages")
    assert run_id is not None
    ok_id = await open_stage_run(run_id, "scoring", now=NOW)
    assert ok_id is not None
    await close_stage_run(
        ok_id,
        status="succeeded",
        now=NOW + timedelta(milliseconds=40),
        counters={"scored": 3, "filtered_out": 1},
    )
    bad_id = await open_stage_run(run_id, "resume", now=NOW)
    assert bad_id is not None
    await close_stage_run(bad_id, status="failed", now=NOW, error="compile failed\nline")
    from orchestrator.monitoring import record_skipped_stage

    await record_skipped_stage(run_id, "apply", now=NOW)
    rows = await list_stage_runs(run_id)
    by_stage = {row.stage: row for row in rows}
    assert by_stage["scoring"].status == "succeeded"
    assert by_stage["scoring"].duration_ms == 40
    assert by_stage["scoring"].counters == {"scored": 3, "filtered_out": 1}
    assert by_stage["resume"].status == "failed"
    assert by_stage["resume"].error == "compile failed line"
    assert by_stage["apply"].status == "skipped"


async def test_pipeline_partial_when_a_stage_fails(
    db_ready: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready

    async def ok(name: str) -> dict[str, int]:
        return {"fetched": 2} if name == "ingestion" else {"scored": 1}

    async def fail() -> dict[str, int]:
        raise RuntimeError("score boom")

    monkeypatch.setattr(pipeline_mod, "_run_ingestion", lambda **_k: ok("ingestion"))
    monkeypatch.setattr(pipeline_mod, "_score_pending", fail)
    monkeypatch.setattr(pipeline_mod, "_shortlist_stage", lambda: ok("other"))
    monkeypatch.setattr(pipeline_mod, "_prepare_shortlisted_resumes", lambda: ok("other"))
    summary = await run_pipeline(
        enable_apply=False,
        enable_reviews=False,
        enable_prep_pack=False,
        enable_suggestions=False,
        enable_benchmark=False,
    )
    assert "scoring" in summary.stage_errors
    assert summary.stages["ingestion"]["fetched"] == 2
    runs = await list_pipeline_runs()
    assert runs[0].status == "partial"
    stages = await list_stage_runs(runs[0].id or 0)
    failed = [row for row in stages if row.stage == "scoring"]
    skipped = [row for row in stages if row.stage == "apply"]
    assert failed[0].status == "failed"
    assert "score boom" in (failed[0].error or "")
    assert skipped[0].status == "skipped"
    assert stages[0].counters.get("fetched") == 2


async def test_pipeline_failure_outside_a_stage_is_failed(
    db_ready: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready

    async def ok(**_kwargs: object) -> dict[str, int]:
        return {}

    monkeypatch.setattr(pipeline_mod, "_run_ingestion", ok)
    monkeypatch.setattr(pipeline_mod, "_score_pending", ok)
    monkeypatch.setattr(pipeline_mod, "_shortlist_stage", ok)
    monkeypatch.setattr(pipeline_mod, "_prepare_shortlisted_resumes", ok)

    async def boom(summary: object, name: str) -> None:
        del summary, name
        raise RuntimeError("pipeline escaped")

    monkeypatch.setattr(pipeline_mod, "_note_skipped", boom)
    with pytest.raises(RuntimeError, match="pipeline escaped"):
        await run_pipeline(
            enable_apply=False,
            enable_reviews=False,
            enable_prep_pack=False,
            enable_suggestions=False,
            enable_benchmark=False,
        )
    runs = await list_pipeline_runs()
    assert runs[0].status == "failed"


async def test_pre_stage_setup_failure_marks_the_run_failed(
    db_ready: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready

    def boom(_settings: object) -> dict[str, object]:
        raise RuntimeError("baseline setup escaped")

    monkeypatch.setattr(pipeline_mod, "effective_baseline", boom)
    with pytest.raises(RuntimeError, match="baseline setup escaped"):
        await run_pipeline(
            enable_apply=False,
            enable_reviews=False,
            enable_prep_pack=False,
            enable_suggestions=False,
            enable_benchmark=False,
        )
    runs = await list_pipeline_runs()
    assert len(runs) == 1
    assert runs[0].status == "failed"
    assert runs[0].finished_at is not None
    assert runs[0].duration_ms is not None


async def test_telemetry_failure_does_not_stop_the_pipeline(
    db_ready: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready

    async def ok(**_kwargs: object) -> dict[str, int]:
        return {"scored": 1}

    async def explode(*_args: object, **_kwargs: object) -> int:
        raise RuntimeError("telemetry down")

    monkeypatch.setattr(pipeline_mod, "_run_ingestion", ok)
    monkeypatch.setattr(pipeline_mod, "_score_pending", ok)
    monkeypatch.setattr(pipeline_mod, "_shortlist_stage", ok)
    monkeypatch.setattr(pipeline_mod, "_prepare_shortlisted_resumes", ok)
    monkeypatch.setattr("orchestrator.monitoring.open_pipeline_run", explode)
    monkeypatch.setattr("orchestrator.monitoring.open_stage_run", explode)
    summary = await run_pipeline(
        enable_apply=False,
        enable_reviews=False,
        enable_prep_pack=False,
        enable_suggestions=False,
        enable_benchmark=False,
    )
    assert summary.stage_errors == {}
    assert "scoring" in summary.stages


async def test_fresh_sqlite_opens_a_run_without_a_missing_table_warning(
    tmp_path: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from pathlib import Path

    root = tmp_path if isinstance(tmp_path, Path) else Path(str(tmp_path))
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{root / 'fresh.db'}")
    get_settings.cache_clear()
    await reset_engine()
    warnings: list[tuple[str, dict[str, object]]] = []

    def _warn(event: str, **kwargs: object) -> None:
        warnings.append((event, kwargs))

    monkeypatch.setattr(pipeline_mod.log, "warning", _warn)
    run_id = await pipeline_mod._safe_open_run()
    assert run_id is not None
    assert not any("pipeline_runs" in str(item) for item in warnings)
    runs = await list_pipeline_runs()
    assert runs[0].id == run_id
    assert runs[0].status == "running"
    await reset_engine()


async def test_fresh_sqlite_health_check_does_not_warn_about_a_missing_table(
    tmp_path: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from pathlib import Path

    root = tmp_path if isinstance(tmp_path, Path) else Path(str(tmp_path))
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{root / 'health.db'}")
    get_settings.cache_clear()
    await reset_engine()
    warnings: list[tuple[str, dict[str, object]]] = []

    def _warn(event: str, **kwargs: object) -> None:
        warnings.append((event, kwargs))

    monkeypatch.setattr("orchestrator.health.log.warning", _warn)
    try:
        report = await get_health_report()
    finally:
        await reset_engine()
        get_settings.cache_clear()
    assert report["database_ok"] is True
    assert report["status"] == "healthy"
    assert report["latest_run"] is None
    assert not any("pipeline_runs" in str(item) for item in warnings)
    assert not any(event == "monitoring_stale_check_failed" for event, _ in warnings)


async def test_fresh_running_run_is_not_stale(db_ready: object) -> None:
    del db_ready
    await open_pipeline_run(now=NOW, run_key="fresh")
    changed = await interrupt_stale_runs(now=NOW, stale_minutes=180)
    assert changed == 0
    assert (await list_pipeline_runs())[0].status == "running"


async def test_old_running_run_becomes_interrupted(db_ready: object) -> None:
    del db_ready
    await open_pipeline_run(now=NOW - timedelta(minutes=181), run_key="old")
    changed = await interrupt_stale_runs(now=NOW, stale_minutes=180)
    assert changed == 1
    assert (await list_pipeline_runs())[0].status == "interrupted"


async def test_stale_threshold_is_configurable(db_ready: object) -> None:
    del db_ready
    await open_pipeline_run(now=NOW - timedelta(minutes=11), run_key="edge")
    assert await interrupt_stale_runs(now=NOW, stale_minutes=30) == 0
    assert await interrupt_stale_runs(now=NOW, stale_minutes=10) == 1


async def test_health_is_healthy_with_no_runs(db_ready: object) -> None:
    del db_ready
    report = await get_health_report(now=NOW)
    assert report["status"] == "healthy"
    assert report["database_ok"] is True
    assert report["latest_run"] is None


async def test_health_is_degraded_after_a_partial_run(db_ready: object) -> None:
    del db_ready
    run_id = await open_pipeline_run(now=NOW, run_key="partial")
    assert run_id is not None
    await close_pipeline_run(run_id, status="partial", now=NOW, error_count=1)
    report = await get_health_report(now=NOW)
    assert report["status"] == "degraded"
    latest = report["latest_completed_run"]
    assert isinstance(latest, dict)
    assert latest["status"] == "partial"


async def test_health_is_unhealthy_after_repeated_failures(db_ready: object) -> None:
    del db_ready
    for index in range(3):
        run_id = await open_pipeline_run(now=NOW, run_key=f"fail-{index}")
        assert run_id is not None
        await close_pipeline_run(run_id, status="failed", now=NOW, error_count=1)
    report = await get_health_report(now=NOW)
    assert report["status"] == "unhealthy"


async def test_health_reports_database_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    async def down() -> bool:
        return False

    monkeypatch.setattr("orchestrator.health.database_reachable", down)
    report = await get_health_report(now=NOW)
    assert report["status"] == "unhealthy"
    assert report["database_ok"] is False


async def test_health_reports_invalid_configuration(
    db_ready: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    monkeypatch.setenv("TIMEZONE", "Not/AZone")
    get_settings.cache_clear()
    report = await get_health_report(now=NOW)
    assert report["status"] == "unhealthy"
    assert report["config_errors"]


async def test_health_marks_a_stale_run(db_ready: object) -> None:
    del db_ready
    await open_pipeline_run(now=NOW - timedelta(hours=5), run_key="stuck")
    report = await get_health_report(now=NOW)
    assert report["status"] == "unhealthy"
    assert report["interrupted_recent"] == 1
    latest = report["latest_run"]
    assert isinstance(latest, dict)
    assert latest["status"] == "interrupted"


async def test_backlog_and_stale_jobs(db_ready: object) -> None:
    del db_ready
    old = NOW - timedelta(days=30)
    statuses = [
        Status.discovered,
        Status.staged,
        Status.pending_review,
        Status.manual_review,
        Status.submitted,
        Status.error,
        Status.filtered_out,
        Status.ignored,
    ]
    async with session_scope() as session:
        for status in statuses:
            job = _job(status.value, status=status, updated_at=old)
            session.add(job)
    report = await get_health_report(now=NOW)
    backlog = report["backlog"]
    assert isinstance(backlog, dict)
    for status in statuses:
        assert backlog[status.value] == 1
    stale = report["stale"]
    assert isinstance(stale, dict)
    assert stale["pending_review"] == 1
    assert stale["manual_review"] == 1
    assert stale["staged"] == 1
    assert stale["error"] == 1
    assert report["status"] == "degraded"
    text = format_health_report(report)
    assert "SECRET_JD_BODY" not in text


def test_health_command_prints_no_secrets(
    tmp_db: object,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del tmp_db
    monkeypatch.setenv("OPENAI_API_KEY", "sk-secret-value")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:telegram-secret")
    get_settings.cache_clear()

    def scheduler_must_not_start() -> None:
        raise AssertionError("scheduler started")

    monkeypatch.setattr("orchestrator.service.run_service", scheduler_must_not_start)
    try:
        assert main(["health"]) == 0
    finally:
        asyncio.run(reset_engine())
    printed = capsys.readouterr().out
    assert "status: healthy" in printed
    assert "sk-secret-value" not in printed
    assert "telegram-secret" not in printed


async def test_a_new_run_does_not_duplicate_applications(db_ready: object) -> None:
    del db_ready
    async with session_scope() as session:
        job = _job("only")
        session.add(job)
        await session.flush()
        assert job.id is not None
        session.add(
            Application(
                job_id=job.id,
                state="submitted",
                method="manual",
                started_at=NOW,
                submitted_at=NOW,
                last_status_at=NOW,
            )
        )
    await open_pipeline_run(now=NOW, run_key="first")
    await open_pipeline_run(now=NOW, run_key="second")
    async with session_scope() as session:
        apps = await session.exec(select(func.count()).select_from(Application))
        jobs = await session.exec(select(Job).where(Job.external_id == "only"))
        assert int(apps.one()) == 1
        assert jobs.one().status == Status.discovered
    assert len(await list_pipeline_runs()) == 2

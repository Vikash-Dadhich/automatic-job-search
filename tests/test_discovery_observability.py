"""Durable discovery evidence. Offline only."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import text

from config.targets import WorkdayTenant
from core.db import (
    PipelineStageRun,
    Source,
    get_engine,
    session_scope,
)
from orchestrator.monitoring import (
    close_stage_run,
    list_stage_runs,
    open_pipeline_run,
    open_stage_run,
)
from orchestrator.pipeline import PipelineSummary, _safe_close_stage
from scraper.coverage import (
    SearchStatus,
    build_coverage_report,
    discovery_evidence,
    observe_search,
)
from scraper.discovery import DiscoveryPlan, FamilyAllocation, PlannedSearch
from scraper.ingest import IngestSummary, _dedupe
from scraper.linkedin_jobspy import _dataframe_to_postings, possible_result_cap
from scraper.models import RawPosting
from scraper.redact import redact_error
from scraper.workday_rest import fetch_workday


class _Frame:
    def __init__(self, rows: list[dict[str, str]]) -> None:
        self._rows = rows
        self.empty = not rows

    def to_dict(self, orient: str) -> list[dict[str, str]]:
        assert orient == "records"
        return self._rows


def _plan() -> DiscoveryPlan:
    search = PlannedSearch(family_id="PRODUCT_MANAGEMENT", bucket_id="PM", query="MBA Intern")
    family = FamilyAllocation(
        family_id="PRODUCT_MANAGEMENT",
        weight=Decimal("1.00"),
        available=1,
        ideal=Decimal("1"),
        assigned=1,
        spillover=0,
    )
    return DiscoveryPlan(
        capacity_requested=1,
        capacity_usable=1,
        capacity_assigned=1,
        families=(family,),
        bucket_assigned={},
        searches=(search,),
        jobspy_sites=("linkedin", "indeed"),
        workday_enabled=False,
    )


def test_redact_error_removes_representative_secrets() -> None:
    raw = (
        "bearer sk-live-secret\n"
        "api_key=abc123 token: xyz password=hunter2 "
        "postgresql://user:pass@ep.example/neondb "
        "https://board.example/jobs?token=sekret&ok=1"
    )
    cleaned = redact_error(raw)
    assert "sk-live-secret" not in cleaned
    assert "abc123" not in cleaned
    assert "xyz" not in cleaned
    assert "hunter2" not in cleaned
    assert "user:pass" not in cleaned
    assert "sekret" not in cleaned
    assert "\n" not in cleaned
    assert len(cleaned) <= 200


def test_redact_error_covers_unlabeled_sk_and_basic_authorization() -> None:
    raw = (
        "lookup failed sk-live-secretvalue "
        "Authorization: Basic dXNlcjpwYXNz leftover context"
    )
    cleaned = redact_error(raw)
    assert "sk-live-secretvalue" not in cleaned
    assert "dXNlcjpwYXNz" not in cleaned
    assert "Authorization: Basic [redacted]" in cleaned
    assert "lookup failed" in cleaned
    assert "leftover context" in cleaned


def test_empty_query_is_not_a_failure() -> None:
    row = observe_search(family_id="F", bucket_id="B", query="MBA Intern", source="linkedin")
    assert row.status is SearchStatus.empty
    failed = observe_search(
        family_id="F",
        bucket_id="B",
        query="MBA Intern",
        source="indeed",
        failed=True,
        error="token=sekret timeout",
    )
    assert failed.status is SearchStatus.failed
    assert failed.error is not None
    assert "sekret" not in failed.error


def test_placeholder_skip_is_not_empty() -> None:
    row = observe_search(
        family_id="",
        bucket_id="",
        query="(placeholder)",
        source="workday",
        detail="Acme",
        skipped=True,
    )
    assert row.status is SearchStatus.not_executed


def test_partial_source_failure_keeps_the_other_observation() -> None:
    plan = _plan()
    observations = [
        observe_search(
            family_id="PRODUCT_MANAGEMENT",
            bucket_id="PM",
            query="MBA Intern",
            source="linkedin",
            hits=("linkedin:li-1",),
        ),
        observe_search(
            family_id="PRODUCT_MANAGEMENT",
            bucket_id="PM",
            query="MBA Intern",
            source="indeed",
            failed=True,
            error="timeout",
        ),
    ]
    report = build_coverage_report(plan, observations)
    by_source = {row.source: row.status for row in report.queries}
    assert by_source["linkedin"] is SearchStatus.results
    assert by_source["indeed"] is SearchStatus.failed


def test_jobspy_location_counts_and_cap_warning(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "scraper.linkedin_jobspy._location_matches",
        lambda location, _profile: location != "Austin, TX",
    )
    rows = [
        {
            "site": "linkedin",
            "title": "MBA Intern",
            "company": "Acme",
            "job_url": "https://www.linkedin.com/jobs/view/1",
            "location": "Seattle, WA",
            "id": "li-1",
        },
        {
            "site": "linkedin",
            "title": "MBA Intern",
            "company": "Acme",
            "job_url": "https://www.linkedin.com/jobs/view/2",
            "location": "Austin, TX",
            "id": "li-2",
        },
    ]
    kept, stats = _dataframe_to_postings(_Frame(rows), profile=None, search=None)
    assert stats["linkedin"]["fetched"] == 2
    assert stats["linkedin"]["location_dropped"] == 1
    assert len(kept) == 1
    assert possible_result_cap(2, 2) is True
    assert possible_result_cap(1, 2) is False


def test_within_run_duplicates_are_counted_separately() -> None:
    posting = RawPosting(
        source=Source.linkedin,
        external_id="li-1",
        title="MBA Intern",
        company="Acme",
        url="https://www.linkedin.com/jobs/view/1",
    )
    kept, removed = _dedupe([posting, posting])
    assert len(kept) == 1
    assert removed == 1


def test_evidence_documents_the_persistence_limit() -> None:
    observation = observe_search(
        family_id="PRODUCT_MANAGEMENT",
        bucket_id="PM",
        query="MBA Intern",
        source="linkedin",
        hits=("linkedin:li-1",),
        fetched_count=2,
        location_dropped=1,
        possible_cap=True,
    )
    report = build_coverage_report(_plan(), [observation])
    payload = discovery_evidence(
        report,
        hours_old=36,
        within_run_duplicates=1,
        hard_filtered_out=0,
        persisted=1,
    )
    assert payload["persistence_note"] == "upsert_job does not distinguish insert from update"
    query = payload["queries"][0]
    assert query["hits"] == ["linkedin:li-1"]
    assert query["fetched_count"] == 2
    assert query["location_dropped"] == 1
    assert query["retained_count"] == 1
    assert query["possible_cap_hit"] is True
    assert "f_TPR" in payload["recency_semantics"]["linkedin"]
    assert "missing date is kept" in payload["recency_semantics"]["workday"]


async def test_workday_counts_recency_drops(monkeypatch: pytest.MonkeyPatch) -> None:
    tenant = WorkdayTenant(name="Acme", url="https://acme.wd1.myworkdayjobs.com/External")

    async def listing(*_args: object, **_kwargs: object) -> dict[str, object]:
        return {
            "total": 2,
            "jobPostings": [
                {"title": "Keep", "externalPath": "/job/Keep_R1", "postedOn": "Posted Today"},
                {
                    "title": "Drop",
                    "externalPath": "/job/Drop_R2",
                    "postedOn": "Posted 3 Days Ago",
                },
            ],
        }

    async def detail(*_args: object, **_kwargs: object) -> dict[str, object]:
        return {
            "title": "Keep",
            "jobReqId": "R1",
            "startDate": datetime.now(UTC).isoformat(),
            "jobDescription": "short",
        }

    monkeypatch.setattr("scraper.workday_rest._fetch_listing_page", listing)
    monkeypatch.setattr("scraper.workday_rest._fetch_detail", detail)
    notes: list = []
    postings = await fetch_workday(
        tenant,
        search_terms=["MBA Intern"],
        hours_old=36,
        observations=notes,
    )
    assert len(postings) == 1
    assert notes[0].fetched_count == 2
    assert notes[0].recency_dropped == 1
    assert notes[0].status is SearchStatus.results


async def test_placeholder_tenant_is_not_an_empty_search() -> None:
    tenant = WorkdayTenant(
        name="PLACEHOLDER Co",
        url="https://placeholder.wd1.myworkdayjobs.com/External",
    )
    notes: list = []
    postings = await fetch_workday(tenant, search_terms=["MBA Intern"], observations=notes)
    assert postings == []
    assert notes[0].status is SearchStatus.not_executed


async def test_two_runs_keep_separate_evidence(db_ready: object) -> None:
    del db_ready
    first = await open_pipeline_run(run_key="run-a")
    second = await open_pipeline_run(run_key="run-b")
    assert first is not None and second is not None
    stage_a = await open_stage_run(first, "ingestion")
    stage_b = await open_stage_run(second, "ingestion")
    assert stage_a is not None and stage_b is not None
    await close_stage_run(stage_a, status="succeeded", evidence={"marker": "a", "queries": []})
    await close_stage_run(stage_b, status="succeeded", evidence={"marker": "b", "queries": []})
    saved_a = await list_stage_runs(first)
    saved_b = await list_stage_runs(second)
    assert saved_a[0].evidence is not None and saved_a[0].evidence["marker"] == "a"
    assert saved_a[0].evidence["run_id"] == first
    assert saved_a[0].evidence["run_key"] == "run-a"
    assert saved_b[0].evidence is not None and saved_b[0].evidence["marker"] == "b"
    assert saved_b[0].evidence["run_key"] == "run-b"


async def test_fresh_database_has_nullable_evidence(db_ready: object) -> None:
    del db_ready
    engine = get_engine()
    async with engine.begin() as conn:
        rows = (await conn.execute(text("PRAGMA table_info(pipeline_stage_runs)"))).fetchall()
    names = {str(row[1]) for row in rows}
    assert "evidence" in names
    async with session_scope() as session:
        run_id = await open_pipeline_run(run_key="legacy-shape")
        assert run_id is not None
        stage_id = await open_stage_run(run_id, "scoring")
        assert stage_id is not None
        await close_stage_run(stage_id, status="succeeded")
        row = await session.get(PipelineStageRun, stage_id)
        assert row is not None
        assert row.evidence is None


async def test_existing_stage_table_gains_evidence_column(tmp_db: object) -> None:
    del tmp_db
    from core.db import _ensure_pipeline_stage_columns

    engine = get_engine()
    async with engine.begin() as conn:
        await conn.execute(
            text(
                "CREATE TABLE pipeline_stage_runs ("
                "id INTEGER PRIMARY KEY, pipeline_run_id INTEGER, stage VARCHAR, "
                "status VARCHAR, started_at DATETIME, counters JSON)"
            )
        )
        await _ensure_pipeline_stage_columns(conn)
        rows = (await conn.execute(text("PRAGMA table_info(pipeline_stage_runs)"))).fetchall()
    assert "evidence" in {str(row[1]) for row in rows}


async def test_evidence_failure_does_not_hide_the_ingest_result(
    monkeypatch: pytest.MonkeyPatch,
    db_ready: object,
) -> None:
    del db_ready

    def boom(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise RuntimeError("api_key=supersecret")

    monkeypatch.setattr("scraper.coverage.discovery_evidence", boom)
    run_id = await open_pipeline_run(run_key="evidence-down")
    assert run_id is not None
    stage_id = await open_stage_run(run_id, "ingestion")
    observation = observe_search(
        family_id="PRODUCT_MANAGEMENT",
        bucket_id="PM",
        query="MBA Intern",
        source="linkedin",
        hits=("linkedin:li-9",),
    )
    ingest = IngestSummary(fetched=1, upserted=1, hours_old=36)
    ingest.coverage = build_coverage_report(_plan(), [observation])
    summary = PipelineSummary()
    summary.stages["ingestion"] = ingest
    summary.stage_errors["ingestion"] = "board timeout"
    await _safe_close_stage(stage_id, status="failed", result=ingest, error="board timeout")
    assert summary.stage_errors["ingestion"] == "board timeout"
    assert summary.stages["ingestion"].upserted == 1
    saved = await list_stage_runs(run_id)
    blob = str(saved[0].evidence) + str(saved[0].error)
    assert "supersecret" not in blob


def test_stale_start_date_counts_as_recency_drop() -> None:
    from scraper.workday_rest import _within_hours

    old = datetime.now(UTC) - timedelta(hours=48)
    assert _within_hours(old, max_hours=36) is False
    assert _within_hours(None, max_hours=36) is True

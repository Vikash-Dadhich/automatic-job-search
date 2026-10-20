"""Bounded JobSpy queries and incremental ingest commits. No live boards."""

from __future__ import annotations

import asyncio
import inspect
import os
import sys
from pathlib import Path

import pytest
from sqlmodel import select

from config.targets import SearchConfig, Targets
from core.db import Job, Source, get_job_by_source_id, session_scope
from scraper.coverage import SearchStatus
from scraper.discovery import DiscoveryPlan, PlannedSearch
from scraper.jobspy_process import LineWorker, QueryTimeoutError
from scraper.linkedin_jobspy import fetch_linkedin_indeed
from scraper.models import RawPosting

_DESC = "Product Manager Intern\n\nRequirements\nCurrent MBA student for a summer internship."
_SLEEPER = """
import json, os, sys, time
pid_path = sys.argv[1]
for line in sys.stdin:
    req = json.loads(line)
    if req.get("term") == "HANG":
        with open(pid_path, "w", encoding="utf-8") as handle:
            handle.write(str(os.getpid()))
        time.sleep(60)
    record = {
        "site": "linkedin",
        "id": "li-next",
        "title": "Product Manager Intern",
        "company": "Acme",
        "job_url": "https://www.linkedin.com/jobs/view/li-next",
        "description": "Product Manager Intern. Requirements. Current MBA student.",
    }
    sys.stdout.write(json.dumps({"ok": True, "records": [record]}) + "\\n")
    sys.stdout.flush()
"""


def _record(external_id: str, *, title: str = "Product Manager Intern") -> dict[str, str]:
    return {
        "site": "linkedin",
        "id": external_id,
        "title": title,
        "company": "Acme",
        "job_url": f"https://www.linkedin.com/jobs/view/{external_id}",
        "description": _DESC,
    }


def _plan(*queries: str) -> DiscoveryPlan:
    return DiscoveryPlan(
        capacity_requested=len(queries),
        capacity_usable=len(queries),
        capacity_assigned=len(queries),
        families=(),
        bucket_assigned={},
        searches=tuple(PlannedSearch("FAMILY", "BUCKET", query) for query in queries),
        jobspy_sites=("linkedin",),
        workday_enabled=False,
    )


def _targets() -> Targets:
    return Targets(search=SearchConfig(terms=["HANG", "NEXT"], sites=["linkedin"]))


def _workday_posting() -> RawPosting:
    return RawPosting(
        source=Source.workday,
        external_id="wd-kept",
        title="Product Manager Intern",
        company="Workday Co",
        location="Seattle, WA",
        url="https://example.wd1.myworkdayjobs.com/en-US/External/job/Seattle/Intern_R1",
        description_clean=_DESC,
        tenant="example",
    )


def test_installed_jobspy_does_not_apply_request_timeout() -> None:
    """The hard bound is our process kill. JobSpy's field is unused."""
    import jobspy
    from jobspy import scrape_jobs

    assert "request_timeout" not in inspect.signature(scrape_jobs).parameters
    assert "request_timeout" not in inspect.getsource(scrape_jobs)
    root = Path(jobspy.__file__).resolve().parent
    linkedin = (root / "linkedin" / "__init__.py").read_text(encoding="utf-8")
    indeed = (root / "indeed" / "__init__.py").read_text(encoding="utf-8")
    google = (root / "google" / "__init__.py").read_text(encoding="utf-8")
    zip_recruiter = (root / "ziprecruiter" / "__init__.py").read_text(encoding="utf-8")
    assert "timeout=10" in linkedin
    assert "timeout=5" in linkedin
    assert "timeout=10" in indeed
    assert "timeout" not in google
    assert "timeout" not in zip_recruiter


async def test_hanging_process_is_killed_and_the_next_query_runs(tmp_path: Path) -> None:
    pid_path = tmp_path / "hang.pid"
    notes: list = []
    saved: list[RawPosting] = []

    async def _keep(batch: list[RawPosting]) -> None:
        saved.extend(batch)

    postings = await fetch_linkedin_indeed(
        _targets(),
        profile=None,
        plan=_plan("HANG", "NEXT"),
        observations=notes,
        on_batch=_keep,
        timeout=0.5,
        command=[sys.executable, "-c", _SLEEPER, str(pid_path)],
    )
    assert postings == []
    assert [item.external_id for item in saved] == ["li-next"]
    hang = [note for note in notes if note.query == "HANG"]
    assert hang
    assert all(note.status is SearchStatus.failed for note in hang)
    assert all(note.status is not SearchStatus.empty for note in hang)
    assert "worker process was stopped" in (hang[0].error or "")
    pid = int(pid_path.read_text(encoding="utf-8"))
    with pytest.raises(ProcessLookupError):
        os.kill(pid, 0)


async def test_cancel_kills_the_query_process(tmp_path: Path) -> None:
    pid_path = tmp_path / "cancel.pid"
    worker = LineWorker([sys.executable, "-c", _SLEEPER, str(pid_path)])
    task = asyncio.create_task(worker.request({"term": "HANG"}, timeout=30))
    for _ in range(50):
        if pid_path.exists():
            break
        await asyncio.sleep(0.05)
    assert pid_path.exists()
    pid = int(pid_path.read_text(encoding="utf-8"))
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    with pytest.raises(ProcessLookupError):
        os.kill(pid, 0)
    await worker.close()


async def test_query_exception_is_failed_and_the_next_query_is_stored(db_ready: Path) -> None:
    del db_ready
    from scraper.ingest import run_ingestion

    calls = {"n": 0}

    async def executor(
        _search: object,
        _term: str,
        _sites: list[str],
        _timeout: float,
    ) -> list[dict[str, str]]:
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("api_key=supersecret")
        return [_record("li-second")]

    summary = await run_ingestion(
        include_workday=False,
        search_capacity=2,
        jobspy_executor=executor,
    )
    assert summary.partial is True
    assert summary.queries_failed == 1
    assert summary.upserted == 1
    assert calls["n"] == 2
    assert summary.coverage is not None
    failed = [row for row in summary.coverage.queries if row.status is SearchStatus.failed]
    assert failed
    assert all(row.status is not SearchStatus.empty for row in failed)
    assert all("supersecret" not in (row.error or "") for row in failed)
    async with session_scope() as session:
        stored = await get_job_by_source_id(session, Source.linkedin, "li-second")
        assert stored is not None
        assert stored.discovery_query


async def test_timeout_error_is_not_an_empty_result(db_ready: Path) -> None:
    del db_ready
    from scraper.ingest import run_ingestion

    async def executor(
        _search: object,
        _term: str,
        _sites: list[str],
        _timeout: float,
    ) -> list[dict[str, str]]:
        raise QueryTimeoutError(0.5)

    summary = await run_ingestion(
        include_workday=False,
        search_capacity=1,
        jobspy_executor=executor,
    )
    assert summary.upserted == 0
    assert summary.partial is True
    assert summary.coverage is not None
    rows = [row for row in summary.coverage.queries if row.source == "linkedin"]
    assert rows
    assert all(row.status is SearchStatus.failed for row in rows)
    assert "worker process was stopped" in (rows[0].error or "")


async def test_early_query_is_committed_before_the_later_query_finishes(db_ready: Path) -> None:
    del db_ready
    from scraper.ingest import run_ingestion

    seen: list[str] = []

    async def executor(
        _search: object,
        term: str,
        _sites: list[str],
        _timeout: float,
    ) -> list[dict[str, str]]:
        seen.append(term)
        if len(seen) == 1:
            return [_record("li-early")]
        async with session_scope() as session:
            stored = await get_job_by_source_id(session, Source.linkedin, "li-early")
            assert stored is not None
        seen.append("visible")
        return [_record("li-later")]

    summary = await run_ingestion(
        include_workday=False,
        search_capacity=2,
        jobspy_executor=executor,
    )
    assert "visible" in seen
    assert summary.upserted == 2


async def test_workday_is_saved_when_jobspy_times_out(
    db_ready: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    from scraper.ingest import run_ingestion

    async def executor(
        _search: object,
        _term: str,
        _sites: list[str],
        _timeout: float,
    ) -> list[dict[str, str]]:
        await asyncio.sleep(0.4)
        async with session_scope() as session:
            stored = await get_job_by_source_id(session, Source.workday, "wd-kept")
            assert stored is not None
        raise QueryTimeoutError(1)

    async def workday(*_args: object, **_kwargs: object) -> list[RawPosting]:
        await asyncio.sleep(0.05)
        return [_workday_posting()]

    monkeypatch.setattr("scraper.ingest.fetch_all_workday", workday)
    summary = await run_ingestion(
        include_workday=True,
        search_capacity=1,
        jobspy_executor=executor,
    )
    assert summary.partial is True
    assert summary.upserted == 1
    async with session_scope() as session:
        stored = await get_job_by_source_id(session, Source.workday, "wd-kept")
        assert stored is not None
        assert stored.discovery_query is None or isinstance(stored.discovery_query, str)


async def test_duplicate_queries_and_repeat_runs_keep_one_row(db_ready: Path) -> None:
    del db_ready
    from scraper.ingest import run_ingestion

    async def executor(
        _search: object,
        term: str,
        _sites: list[str],
        _timeout: float,
    ) -> list[dict[str, str]]:
        del term
        return [_record("li-same", title="Product Manager Intern")]

    first = await run_ingestion(
        include_workday=False,
        search_capacity=2,
        jobspy_executor=executor,
    )
    assert first.upserted == 1

    async def renamed(
        _search: object,
        _term: str,
        _sites: list[str],
        _timeout: float,
    ) -> list[dict[str, str]]:
        return [_record("li-same", title="MBA Product Manager Intern")]

    second = await run_ingestion(
        include_workday=False,
        search_capacity=1,
        jobspy_executor=renamed,
    )
    assert second.upserted == 1
    async with session_scope() as session:
        rows = (await session.exec(select(Job).where(Job.external_id == "li-same"))).all()
        assert len(rows) == 1
        assert rows[0].id is not None
        assert rows[0].title == "MBA Product Manager Intern"
        assert rows[0].discovery_query


async def test_cancel_keeps_the_committed_query(db_ready: Path) -> None:
    del db_ready
    from scraper.ingest import run_ingestion

    started = asyncio.Event()

    async def executor(
        _search: object,
        _term: str,
        _sites: list[str],
        _timeout: float,
    ) -> list[dict[str, str]]:
        if not started.is_set():
            started.set()
            return [_record("li-kept")]
        await asyncio.sleep(30)
        return []

    task = asyncio.create_task(
        run_ingestion(
            include_workday=False,
            search_capacity=2,
            jobspy_executor=executor,
        )
    )
    await asyncio.wait_for(started.wait(), timeout=5)
    for _ in range(50):
        async with session_scope() as session:
            stored = await get_job_by_source_id(session, Source.linkedin, "li-kept")
        if stored is not None:
            break
        await asyncio.sleep(0.05)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    async with session_scope() as session:
        stored = await get_job_by_source_id(session, Source.linkedin, "li-kept")
        assert stored is not None
        assert stored.external_id == "li-kept"


_BIG_WORKER = """
import json, sys
first = True
for line in sys.stdin:
    if not line.strip():
        continue
    json.loads(line)
    if first:
        desc = "M" * 3_000_000
        body = {
            "ok": True,
            "records": [{
                "site": "linkedin",
                "id": "li-big",
                "title": "Product Manager Intern",
                "company": "Acme",
                "job_url": "https://www.linkedin.com/jobs/view/li-big",
                "description": desc,
            }],
        }
        first = False
    else:
        body = {"ok": True, "records": []}
    sys.stdout.write(json.dumps(body) + "\\n")
    sys.stdout.flush()
"""


async def test_multi_megabyte_worker_line_is_persisted(
    db_ready: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    from scraper.ingest import run_ingestion
    from scraper.jobspy_process import STDOUT_LIMIT

    assert STDOUT_LIMIT > 64 * 1024
    monkeypatch.setattr(
        "scraper.linkedin_jobspy.worker_argv",
        lambda: [sys.executable, "-c", _BIG_WORKER],
    )
    summary = await run_ingestion(include_workday=False, search_capacity=1)
    assert summary.upserted == 1
    assert summary.partial is False
    async with session_scope() as session:
        stored = await get_job_by_source_id(session, Source.linkedin, "li-big")
        assert stored is not None
        assert stored.title == "Product Manager Intern"


async def test_worker_startup_failure_does_not_hang() -> None:
    worker = LineWorker(["/no/such/jobspy-worker"])
    with pytest.raises(FileNotFoundError):
        await asyncio.wait_for(worker.request({"term": "x"}, timeout=5), timeout=3)
    await worker.close()


async def test_early_worker_exit_is_reaped() -> None:
    worker = LineWorker([sys.executable, "-c", "import sys; sys.exit(0)"])
    with pytest.raises(RuntimeError):
        await asyncio.wait_for(worker.request({"term": "x"}, timeout=5), timeout=3)
    assert worker.proc is None


async def test_malformed_worker_output_stops_at_the_query_timeout(tmp_path: Path) -> None:
    pid_path = tmp_path / "malformed.pid"
    script = """
import os, sys, time
open(sys.argv[1], "w", encoding="utf-8").write(str(os.getpid()))
sys.stdout.write("not-json\\n")
sys.stdout.flush()
time.sleep(30)
"""
    worker = LineWorker([sys.executable, "-c", script, str(pid_path)])
    with pytest.raises(QueryTimeoutError):
        await asyncio.wait_for(worker.request({"term": "x"}, timeout=0.5), timeout=3)
    pid = int(pid_path.read_text(encoding="utf-8"))
    with pytest.raises(ProcessLookupError):
        os.kill(pid, 0)
    await worker.close()


async def test_oversized_line_kills_the_worker(tmp_path: Path) -> None:
    pid_path = tmp_path / "oversize.pid"
    script = """
import os, sys, time
open(sys.argv[1], "w", encoding="utf-8").write(str(os.getpid()))
sys.stdout.write('{"ok": true, "pad": "%s"}\\n' % ("y" * 4000))
sys.stdout.flush()
time.sleep(30)
"""
    worker = LineWorker(
        [sys.executable, "-c", script, str(pid_path)],
        stream_limit=128,
    )
    with pytest.raises(RuntimeError, match="reader limit"):
        await asyncio.wait_for(worker.request({"term": "x"}, timeout=5), timeout=3)
    pid = int(pid_path.read_text(encoding="utf-8"))
    with pytest.raises(ProcessLookupError):
        os.kill(pid, 0)
    assert worker.proc is None


async def test_failed_commit_can_be_retried_by_a_later_query(
    db_ready: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    from sqlmodel.ext.asyncio.session import AsyncSession

    from scraper.ingest import run_ingestion

    original = AsyncSession.commit
    state = {"failed": 0}

    async def commit(self: AsyncSession) -> None:
        identity = getattr(self, "identity_map", None)
        values = identity.values() if identity is not None else ()
        pending_job = any(isinstance(obj, Job) for obj in values)
        if pending_job and state["failed"] == 0:
            state["failed"] = 1
            raise RuntimeError("api_key=supersecret")
        await original(self)

    monkeypatch.setattr(AsyncSession, "commit", commit)

    async def executor(
        _search: object,
        _term: str,
        _sites: list[str],
        _timeout: float,
    ) -> list[dict[str, str]]:
        return [_record("li-retry")]

    summary = await run_ingestion(
        include_workday=False,
        search_capacity=2,
        jobspy_executor=executor,
    )
    assert summary.upserted == 1
    assert summary.discovered == 1
    assert summary.partial is True
    assert summary.errors
    assert all("supersecret" not in error for error in summary.errors)
    async with session_scope() as session:
        rows = (await session.exec(select(Job).where(Job.external_id == "li-retry"))).all()
        assert len(rows) == 1
        assert rows[0].discovery_query


async def test_source_failure_log_is_redacted(
    db_ready: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    from scraper.ingest import run_ingestion

    async def boom(*_args: object, **_kwargs: object) -> list[RawPosting]:
        raise RuntimeError("postgresql://user:supersecret@db.example/neondb")

    monkeypatch.setattr("scraper.ingest.fetch_linkedin_indeed", boom)
    summary = await run_ingestion(include_workday=False, search_capacity=1)
    assert summary.partial is True
    assert summary.upserted == 0
    assert summary.errors
    assert all("supersecret" not in error for error in summary.errors)


async def test_hits_plus_error_marks_the_run_partial(db_ready: Path) -> None:
    del db_ready
    from scraper.ingest import run_ingestion

    async def executor(
        _search: object,
        _term: str,
        _sites: list[str],
        _timeout: float,
    ) -> list[dict[str, str]]:
        return [
            _record("li-partial"),
            {
                "site": "not-a-board",
                "id": "x",
                "title": "Product Manager Intern",
                "company": "Acme",
                "job_url": "https://example.com/x",
                "description": _DESC,
            },
        ]

    summary = await run_ingestion(
        include_workday=False,
        search_capacity=1,
        jobspy_executor=executor,
    )
    assert summary.partial is True
    assert summary.queries_failed == 0
    assert summary.upserted == 1
    assert summary.coverage is not None
    linkedin = [row for row in summary.coverage.queries if row.source == "linkedin"]
    assert linkedin
    assert all(row.status is SearchStatus.partial for row in linkedin)
    assert all(row.status is not SearchStatus.empty for row in linkedin)
    assert all(row.status is not SearchStatus.failed for row in linkedin)
    assert linkedin[0].hits
    async with session_scope() as session:
        stored = await get_job_by_source_id(session, Source.linkedin, "li-partial")
        assert stored is not None


_SITE_WORKER = """
import json, os, sys, time
pid_path = sys.argv[1]
for line in sys.stdin:
    req = json.loads(line)
    sites = req.get("sites") or []
    site = sites[0] if sites else ""
    if site == "google":
        with open(pid_path, "w", encoding="utf-8") as handle:
            handle.write(str(os.getpid()))
        time.sleep(60)
    if site == "zip_recruiter":
        sys.stdout.write(json.dumps({"ok": False, "error": "zip exploded"}) + "\\n")
        sys.stdout.flush()
        continue
    record = {
        "site": "linkedin",
        "id": "shared-id",
        "title": "Product Manager Intern",
        "company": "Acme",
        "job_url": f"https://www.example.com/jobs/{site}",
        "description": "Product Manager Intern. Requirements. Current MBA student.",
    }
    sys.stdout.write(json.dumps({"ok": True, "records": [record]}) + "\\n")
    sys.stdout.flush()
"""


def _two_site_plan(*sites: str) -> DiscoveryPlan:
    return DiscoveryPlan(
        capacity_requested=1,
        capacity_usable=1,
        capacity_assigned=1,
        families=(),
        bucket_assigned={},
        searches=(PlannedSearch("FAMILY", "BUCKET", "Intern"),),
        jobspy_sites=sites,
        workday_enabled=False,
    )


async def test_hanging_site_does_not_drop_the_other_sites_rows(tmp_path: Path) -> None:
    pid_path = tmp_path / "google.pid"
    saved: list[RawPosting] = []
    notes: list = []

    async def _keep(batch: list[RawPosting]) -> None:
        saved.extend(batch)

    await fetch_linkedin_indeed(
        Targets(search=SearchConfig(terms=["Intern"], sites=["linkedin", "google"])),
        plan=_two_site_plan("linkedin", "google"),
        observations=notes,
        on_batch=_keep,
        timeout=0.4,
        command=[sys.executable, "-c", _SITE_WORKER, str(pid_path)],
    )
    assert [item.external_id for item in saved] == ["shared-id"]
    linkedin = [note for note in notes if note.source == "linkedin"]
    google = [note for note in notes if note.source == "google"]
    assert linkedin and linkedin[0].status is not SearchStatus.failed
    assert google and google[0].status is SearchStatus.failed
    assert "worker process was stopped" in (google[0].error or "")
    pid = int(pid_path.read_text(encoding="utf-8"))
    with pytest.raises(ProcessLookupError):
        os.kill(pid, 0)


async def test_site_exception_keeps_the_other_sites_rows(tmp_path: Path) -> None:
    saved: list[RawPosting] = []
    notes: list = []

    async def _keep(batch: list[RawPosting]) -> None:
        saved.extend(batch)

    await fetch_linkedin_indeed(
        Targets(search=SearchConfig(terms=["Intern"], sites=["linkedin", "zip_recruiter"])),
        plan=_two_site_plan("linkedin", "zip_recruiter"),
        observations=notes,
        on_batch=_keep,
        timeout=2,
        command=[sys.executable, "-c", _SITE_WORKER, str(tmp_path / "unused.pid")],
    )
    assert [item.external_id for item in saved] == ["shared-id"]
    linkedin = [note for note in notes if note.source == "linkedin"]
    failed = [note for note in notes if note.source == "zip_recruiter"]
    assert linkedin[0].status is not SearchStatus.failed
    assert failed[0].status is SearchStatus.failed
    assert "zip exploded" in (failed[0].error or "")


async def test_same_source_id_from_two_site_passes_is_kept_once(tmp_path: Path) -> None:
    saved: list[RawPosting] = []

    async def _keep(batch: list[RawPosting]) -> None:
        saved.extend(batch)

    await fetch_linkedin_indeed(
        Targets(search=SearchConfig(terms=["Intern"], sites=["linkedin", "indeed"])),
        plan=_two_site_plan("linkedin", "indeed"),
        on_batch=_keep,
        timeout=2,
        command=[sys.executable, "-c", _SITE_WORKER, str(tmp_path / "unused.pid")],
    )
    # The worker labels both passes as LinkedIn with one id. Dedup is
    # (source, external_id), so Indeed being asked does not create a second row.
    assert [(item.source, item.external_id) for item in saved] == [
        (Source.linkedin, "shared-id")
    ]


async def test_posting_cap_still_limits_separately_returned_sites(
    db_ready: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    from scraper.ingest import run_ingestion

    async def executor(
        _search: object,
        _term: str,
        _sites: list[str],
        _timeout: float,
    ) -> list[dict[str, str]]:
        return [_record("cap-a"), _record("cap-b")]

    monkeypatch.setenv("INGEST_POSTING_CAP", "1")
    from config.settings import get_settings

    get_settings.cache_clear()
    summary = await run_ingestion(
        include_workday=False,
        search_capacity=1,
        jobspy_executor=executor,
    )
    assert summary.upserted == 1

"""Job Agent CLI — schedule, run-once, poll, send-reviews, webhook, baselines, suggest."""

from __future__ import annotations

import argparse
import asyncio
import sys
from collections.abc import Callable, Coroutine
from typing import Any

from config.settings import get_settings
from core.logging import configure_logging


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="job-agent",
        description="Agentic human-in-the-loop job search and application engine",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("serve", help="Run scheduler + Telegram poller (default)")
    sub.add_parser("run-once", help="Run the full pipeline once and exit")
    sub.add_parser("poll", help="Only run the Telegram long-poller")
    sub.add_parser("send-reviews", help="Send pending Telegram review cards once")
    sub.add_parser(
        "prep-pack",
        help="Generate and send LinkedIn/Indeed application prep pack via Telegram",
    )
    sub.add_parser(
        "send-suggestions",
        help="Send pending skill-suggestion cards via Telegram",
    )
    tailor = sub.add_parser(
        "tailor-resume",
        help="Generate a Typst-tailored resume for one job (baseline + approved suggestions)",
    )
    tailor.add_argument("job_id", type=int, help="Database job id to tailor for")
    baseline = sub.add_parser(
        "build-baseline",
        help="Aggregate ~15-20 role JDs into a baseline resume",
    )
    baseline.add_argument("role", help="Role name / title cluster (e.g. 'Software Engineer')")
    baseline.add_argument(
        "--refresh",
        action="store_true",
        help="Rebuild even if a baseline already exists",
    )
    baseline.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Max JDs to aggregate (default: RESUME_BASELINE_JD_LIMIT)",
    )
    suggest = sub.add_parser(
        "suggest",
        help="Diff a job against its role baseline and queue Telegram suggestions",
    )
    suggest.add_argument("job_id", type=int, help="Database job id")
    suggest.add_argument("--role", default=None, help="Override role name for baseline lookup")
    bench = sub.add_parser(
        "benchmark",
        help="Compare your profile against LinkedIn peers for one job",
    )
    bench.add_argument("job_id", type=int, help="Database job id")
    bench.add_argument(
        "--urls",
        nargs="*",
        default=None,
        help="Peer LinkedIn profile URLs (semi-automated discovery)",
    )
    bench.add_argument(
        "--search-url",
        default=None,
        help="LinkedIn people-search URL (informational unless LINKEDIN_AUTO_SEARCH)",
    )
    bench.add_argument(
        "--scrape",
        action="store_true",
        help="Actually scrape peer URLs (requires ENABLE_LINKEDIN_SCRAPE + session)",
    )
    bench.add_argument(
        "--auto",
        action="store_true",
        help=(
            "Auto-discover peers via LinkedIn People Search for this job's title, "
            "then scrape them (requires ENABLE_LINKEDIN_SCRAPE + saved session)"
        ),
    )
    sub.add_parser(
        "save-linkedin-session",
        help="One-time headful LinkedIn login; saves storage/sessions/linkedin.json",
    )
    apply_list = sub.add_parser(
        "list-apply",
        help="List staged jobs eligible for Workday auto-fill (incl. LinkedIn→Workday URLs)",
    )
    apply_list.add_argument(
        "--apply",
        action="store_true",
        help="Also run apply_pending on eligible jobs (needs per-tenant sessions)",
    )
    webhook = sub.add_parser(
        "webhook",
        help="Serve FastAPI Telegram webhook via uvicorn (optional alt to poll)",
    )
    webhook.add_argument("--host", default="0.0.0.0")
    webhook.add_argument("--port", type=int, default=8000)
    doctor = sub.add_parser("doctor", help="Print a pipeline health report and exit")
    doctor.add_argument("--json", action="store_true", help="Emit machine-readable JSON")

    return parser


async def _cmd_serve() -> None:
    from orchestrator.service import run_service

    await run_service(run_poller=True)


async def _cmd_run_once() -> None:
    from orchestrator.pipeline import run_pipeline

    summary = await run_pipeline()
    print(summary)


async def _cmd_poll() -> None:
    from bot.poller import run_polling

    await run_polling()


async def _cmd_send_reviews() -> None:
    from bot.review import send_pending_reviews

    summary = await send_pending_reviews()
    print(summary)


async def _cmd_prep_pack() -> None:
    from bot import send_prep_pack

    summary = await send_prep_pack()
    print(summary)


async def _cmd_send_suggestions() -> None:
    from bot.suggest import send_pending_suggestions

    summary = await send_pending_suggestions()
    print(summary)


async def _cmd_tailor_resume(job_id: int) -> None:
    from bot.suggest import apply_decided_suggestions
    from core.db import SuggestionStatus, get_suggestions_for_job, session_scope
    from resume import compile_for_job
    from resume.diff import apply_approved_suggestions_to_resume_data, generate_suggestions_for_job

    # Ensure suggestions exist; if all decided, apply; else compile baseline-aware resume
    await generate_suggestions_for_job(job_id)
    path = await apply_decided_suggestions(job_id)
    if path:
        print(path)
        return

    async with session_scope() as session:
        suggestions = await get_suggestions_for_job(session, job_id)
    pending = [s for s in suggestions if s.status == SuggestionStatus.pending]
    if pending:
        print(
            f"Waiting on {len(pending)} Telegram suggestion(s) for job {job_id}. "
            "Run: uv run python main.py send-suggestions"
        )
        return

    # No suggestions needed — compile from baseline/profile
    from config.profile import load_profile
    from core.db import get_job_by_id, get_role_baseline_by_role
    from resume.selector import build_resume_data

    profile = load_profile()
    async with session_scope() as session:
        job = await get_job_by_id(session, job_id)
        if job is None:
            raise ValueError(f"Job {job_id} not found")
        role = profile.preferences.titles[0] if profile.preferences.titles else job.title
        baseline = await get_role_baseline_by_role(session, role) if role else None
        resume_data = (
            dict(baseline.resume_data)
            if baseline and baseline.resume_data
            else build_resume_data(profile, job)
        )
        if suggestions:
            resume_data = apply_approved_suggestions_to_resume_data(resume_data, suggestions)
    path = await compile_for_job(job_id, profile=profile, resume_data=resume_data)
    print(path)


async def _cmd_build_baseline(role: str, *, refresh: bool, limit: int | None) -> None:
    from resume.baseline import build_role_baseline

    baseline = await build_role_baseline(role, refresh=refresh, limit=limit)
    print(
        f"baseline id={baseline.id} role={baseline.role!r} "
        f"skills={len(baseline.skills)} pdf={baseline.pdf_path}"
    )


async def _cmd_suggest(job_id: int, role: str | None) -> None:
    from resume.diff import generate_suggestions_for_job

    suggestions = await generate_suggestions_for_job(job_id, role=role)
    print(f"queued {len(suggestions)} suggestion(s) for job {job_id}")


async def _cmd_benchmark(
    job_id: int,
    *,
    urls: list[str] | None,
    search_url: str | None,
    scrape: bool,
    auto: bool = False,
) -> None:
    from benchmark.engine import run_benchmark

    try:
        summary = await run_benchmark(
            job_id,
            peer_urls=urls,
            search_url=search_url,
            scrape=scrape,
            auto_discover=auto,
        )
    except RuntimeError as exc:
        print(f"benchmark failed: {exc}")
        return
    report = summary.report
    if report is None:
        print("benchmark failed")
        return
    print(
        f"score={report.overall_score} percentile={report.percentile} "
        f"peers={report.peer_count} path={summary.report_path}"
    )


def _cmd_webhook(host: str, port: int) -> None:
    import uvicorn

    from bot.webhook import app

    uvicorn.run(app, host=host, port=port)


async def _cmd_save_linkedin_session() -> None:
    from scraper.linkedin_session import save_linkedin_session

    path = await save_linkedin_session()
    print(f"LinkedIn session saved: {path}")


async def _cmd_list_apply(*, do_apply: bool) -> None:
    from automation.runner import _eligible, apply_pending
    from automation.vault import has_saved_session
    from core.apply_url import classify_apply_url, workday_parts
    from core.db import Status, get_jobs_by_status, init_db, session_scope

    await init_db()
    async with session_scope() as session:
        jobs = await get_jobs_by_status(session, Status.staged, limit=500)

    eligible = [j for j in jobs if _eligible(j)]
    print(f"staged={len(jobs)} workday_eligible={len(eligible)}")
    for j in eligible:
        parts = workday_parts(j.url or "")
        tenant = (j.tenant or (parts.tenant if parts else "") or "?").lower()
        has_sess = has_saved_session(tenant) if tenant != "?" else False
        kind = classify_apply_url(j.url or "")
        print(
            f"  id={j.id} source={j.source.value} tenant={tenant} "
            f"session={'yes' if has_sess else 'NO'} kind={kind.value} "
            f"{j.title[:40]} @ {j.company}"
        )
        if not has_sess and parts is not None:
            print(
                f"    → save session: uv run python -c \"import asyncio; "
                f"from automation import save_session; "
                f"print(asyncio.run(save_session({j.url!r})))\""
            )

    company = [
        j
        for j in jobs
        if j.resume_path and classify_apply_url(j.url or "").value == "company"
    ]
    if company:
        print(f"\ncompany_site_manual={len(company)} (prep pack / manual apply)")
        for j in company[:12]:
            print(f"  id={j.id} {j.company}: {j.url[:70]}")

    if do_apply:
        summary = await apply_pending()
        print(summary)


OUTCOME_AWAITING_DAYS = 14


def _unwrap(value: Any) -> Any:
    """First element of a row tuple; scalars pass through."""
    if isinstance(value, tuple):
        return value[0] if value else None
    return value


async def _count_jobs(session: Any, *criteria: Any) -> int:
    from sqlalchemy import func
    from sqlmodel import select

    from core.db import Job

    statement = select(func.count()).select_from(Job).where(*criteria)
    result = await session.exec(statement)
    raw = _unwrap(result.one())
    return int(raw or 0)


async def _build_doctor_report() -> dict[str, Any]:
    """Read-only pipeline health snapshot. No LLM calls."""
    from datetime import UTC, datetime, timedelta

    from sqlmodel import col, select

    from config.settings import get_settings
    from core.db import (
        Job,
        Outcome,
        Status,
        Tier,
        get_recently_applied_companies,
        init_db,
        session_scope,
    )

    await init_db()
    settings = get_settings()

    async with session_scope() as session:
        status_counts = {
            status.value: await _count_jobs(session, col(Job.status) == status)
            for status in Status
        }
        active = [
            Status.staged,
            Status.pending_review,
            Status.submitted,
            Status.manual_review,
        ]
        tier_counts = {
            tier.value: await _count_jobs(
                session,
                col(Job.tier) == tier,
                col(Job.status).in_(active),  # type: ignore[union-attr]
            )
            for tier in Tier
        }

        score_result = await session.exec(
            select(Job.score).where(col(Job.score).is_not(None))  # type: ignore[union-attr]
        )
        scores: list[int] = []
        for item in score_result.all():
            value = _unwrap(item)
            if isinstance(value, int):
                scores.append(value)
        score_stats: dict[str, Any] = {
            "count": len(scores),
            "avg": round(sum(scores) / len(scores), 1) if scores else None,
            "min": min(scores) if scores else None,
            "max": max(scores) if scores else None,
        }

        discovered_states = (
            "discovered",
            "staged",
            "pending_review",
            "submitted",
            "manual_review",
            "error",
        )
        staged_states = ("staged", "pending_review", "submitted", "manual_review")
        total_discovered = sum(status_counts.get(name, 0) for name in discovered_states)
        total_staged = sum(status_counts.get(name, 0) for name in staged_states)
        total_submitted = status_counts.get("submitted", 0)

        cooldown_companies = await get_recently_applied_companies(
            session, cooldown_days=settings.company_cooldown_days
        )

        submitted_rows = await session.exec(
            select(Job.tier, Job.outcome).where(col(Job.status) == Status.submitted)
        )
        outcome_counts = {item.value: 0 for item in Outcome}
        outcome_counts["unlabeled"] = 0
        positive = {
            Outcome.screening.value,
            Outcome.interview.value,
            Outcome.offer.value,
        }
        by_tier: dict[str, dict[str, int]] = {
            tier.value: {"labeled": 0, "positive": 0} for tier in Tier
        }
        for item in submitted_rows.all():
            tier_value, outcome_value = item[0], item[1]
            if isinstance(outcome_value, Outcome):
                label: str | None = outcome_value.value
            elif isinstance(outcome_value, str):
                label = outcome_value
            else:
                label = None
            if label in outcome_counts and label != "unlabeled":
                outcome_counts[label] += 1
                tier_name = tier_value.value if isinstance(tier_value, Tier) else tier_value
                bucket = by_tier.get(tier_name) if isinstance(tier_name, str) else None
                if bucket is not None:
                    bucket["labeled"] += 1
                    if label in positive:
                        bucket["positive"] += 1
            else:
                outcome_counts["unlabeled"] += 1

        awaiting_cutoff = datetime.now(UTC) - timedelta(days=OUTCOME_AWAITING_DAYS)
        awaiting_label = await _count_jobs(
            session,
            col(Job.status) == Status.submitted,
            col(Job.outcome).is_(None),
            col(Job.decided_at).is_not(None),
            col(Job.decided_at) < awaiting_cutoff,
        )
        outcome_by_tier = {
            name: {
                "labeled": counts["labeled"],
                "positive": counts["positive"],
                "positive_pct": (
                    round(counts["positive"] / counts["labeled"] * 100, 1)
                    if counts["labeled"]
                    else 0.0
                ),
            }
            for name, counts in by_tier.items()
        }

        error_result = await session.exec(
            select(Job)
            .where(
                col(Job.status) == Status.error,
                col(Job.last_error).is_not(None),  # type: ignore[union-attr]
            )
            .order_by(col(Job.updated_at).desc())
            .limit(5)
        )
        recent_errors = [
            {"id": job.id, "company": job.company, "error": job.last_error}
            for job in error_result.all()
        ]

        vector_reject = await _count_jobs(session, col(Job.vector_decision) == "reject")
        vector_pass = await _count_jobs(session, col(Job.vector_decision) == "pass")

    discovered_pct = (
        round(total_staged / total_discovered * 100, 1) if total_discovered else 0
    )
    submitted_pct = round(total_submitted / total_staged * 100, 1) if total_staged else 0
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "status_counts": status_counts,
        "tier_counts": tier_counts,
        "score_stats": score_stats,
        "conversion": {
            "discovered_to_staged_pct": discovered_pct,
            "staged_to_submitted_pct": submitted_pct,
        },
        "active_cooldowns": sorted(cooldown_companies),
        "cooldown_days": settings.company_cooldown_days,
        "outcomes": outcome_counts,
        "outcome_by_tier": outcome_by_tier,
        "awaiting_label": awaiting_label,
        "outcome_awaiting_days": OUTCOME_AWAITING_DAYS,
        "vector_gate": {
            "enabled": settings.vector_gate_enabled,
            "threshold": settings.vector_threshold,
            "reject": vector_reject,
            "pass": vector_pass,
        },
        "recent_errors": recent_errors,
    }


def _print_doctor_report(report: dict[str, Any]) -> None:
    """Human-readable health report. JSON mode prints the dict instead."""
    counts: dict[str, int] = report["status_counts"]
    width = max((len(name) for name in counts), default=12)
    print("=== Job Agent Health Report ===")
    print(f"Generated: {report['generated_at']}")
    print()
    print("--- Pipeline Funnel ---")
    for name, count in counts.items():
        print(f"  {name:<{width}}  {count}")

    tiers: dict[str, int] = report["tier_counts"]
    print()
    print("--- Tier Distribution (active) ---")
    print(
        "  "
        + "   ".join(
            f"tier_{label}: {tiers.get(key, 0)}"
            for key, label in (("one", "1"), ("two", "2"), ("three", "3"))
        )
    )

    stats: dict[str, Any] = report["score_stats"]
    avg = stats["avg"] if stats["avg"] is not None else "n/a"
    low = stats["min"] if stats["min"] is not None else "n/a"
    high = stats["max"] if stats["max"] is not None else "n/a"
    print()
    print("--- Score Distribution ---")
    print(f"  count={stats['count']}  avg={avg}  min={low}  max={high}")

    gate: dict[str, Any] = report["vector_gate"]
    print()
    print("--- Vector Gate ---")
    print(
        f"  enabled={gate['enabled']}  threshold={gate['threshold']}  "
        f"pass={gate['pass']}  reject={gate['reject']}"
    )

    conversion: dict[str, float] = report["conversion"]
    print()
    print("--- Conversion Rates ---")
    print(f"  discovered -> staged    {conversion['discovered_to_staged_pct']}%")
    print(f"  staged -> submitted     {conversion['staged_to_submitted_pct']}%")

    outcomes: dict[str, int] = report["outcomes"]
    outcome_width = max((len(name) for name in outcomes), default=12)
    print()
    print("--- Outcomes (submitted) ---")
    for name, count in outcomes.items():
        print(f"  {name:<{outcome_width}}  {count}")
    awaiting_days = report["outcome_awaiting_days"]
    print(f"  awaiting_label ({awaiting_days}d+)  {report['awaiting_label']}")
    print()
    print("--- Outcomes by tier ---")
    for name, bucket in report["outcome_by_tier"].items():
        print(
            f"  tier {name}: labeled={bucket['labeled']}  "
            f"positive={bucket['positive']}  {bucket['positive_pct']}%"
        )

    cooldowns: list[str] = report["active_cooldowns"]
    print()
    print(f"--- Active Company Cooldowns ({report['cooldown_days']}-day) ---")
    print(f"  {', '.join(cooldowns) if cooldowns else '(none)'}")

    print()
    print("--- Recent Errors ---")
    errors: list[dict[str, Any]] = report["recent_errors"]
    if not errors:
        print("  (none)")
        return
    for item in errors:
        message = (item.get("error") or "").replace("\n", " ")
        print(f"  id={item.get('id')} {item.get('company')}: {message[:160]}")


async def _cmd_doctor(json_output: bool = False) -> dict[str, Any]:
    import json as _json

    report = await _build_doctor_report()
    if json_output:
        print(_json.dumps(report, indent=2))
    else:
        _print_doctor_report(report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    command = args.command or "serve"

    settings = get_settings()
    configure_logging(settings.log_level)

    if command == "webhook":
        _cmd_webhook(args.host, args.port)
        return 0

    if command == "tailor-resume":
        asyncio.run(_cmd_tailor_resume(args.job_id))
        return 0

    if command == "build-baseline":
        asyncio.run(
            _cmd_build_baseline(args.role, refresh=args.refresh, limit=args.limit)
        )
        return 0

    if command == "suggest":
        asyncio.run(_cmd_suggest(args.job_id, args.role))
        return 0

    if command == "benchmark":
        asyncio.run(
            _cmd_benchmark(
                args.job_id,
                urls=args.urls,
                search_url=args.search_url,
                scrape=args.scrape,
                auto=args.auto,
            )
        )
        return 0

    if command == "save-linkedin-session":
        asyncio.run(_cmd_save_linkedin_session())
        return 0

    if command == "list-apply":
        asyncio.run(_cmd_list_apply(do_apply=args.apply))
        return 0

    if command == "doctor":
        asyncio.run(_cmd_doctor(json_output=args.json))
        return 0

    async_commands: dict[str, Callable[[], Coroutine[Any, Any, Any]]] = {
        "serve": _cmd_serve,
        "run-once": _cmd_run_once,
        "poll": _cmd_poll,
        "send-reviews": _cmd_send_reviews,
        "prep-pack": _cmd_prep_pack,
        "send-suggestions": _cmd_send_suggestions,
    }

    if command not in async_commands:
        parser.error(f"Unknown command: {command}")
        return 2

    asyncio.run(async_commands[command]())
    return 0


if __name__ == "__main__":
    sys.exit(main())

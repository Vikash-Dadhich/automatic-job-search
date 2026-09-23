"""Telegram delivery and apply path for skill suggestions."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

import structlog

from bot.telegram import SuggestAction, TelegramClient, encode_suggest_callback
from config.profile import load_profile
from config.settings import get_settings
from core.db import (
    Job,
    RoleBaseline,
    SkillSuggestion,
    SuggestionStatus,
    get_job_by_id,
    get_pending_suggestions_for_job,
    get_role_baseline_by_id,
    get_skill_suggestion_by_id,
    get_suggestions_for_job,
    get_unsent_suggestion_jobs,
    init_db,
    session_scope,
)
from resume.compiler import compile_for_job
from resume.diff import apply_approved_suggestions_to_resume_data

log = structlog.get_logger(__name__)


@dataclass
class SuggestSummary:
    sent: int = 0
    skipped: int = 0
    errors: int = 0
    applied: int = 0
    error_details: list[str] = field(default_factory=list)


def _suggestion_keyboard(suggestions: list[SkillSuggestion]) -> dict[str, Any]:
    rows: list[list[dict[str, str]]] = []
    for sug in suggestions:
        if sug.id is None:
            continue
        label = sug.skill[:28] + ("…" if len(sug.skill) > 28 else "")
        rows.append(
            [
                {
                    "text": f"✅ {label}",
                    "callback_data": encode_suggest_callback(
                        SuggestAction.approve, sug.id
                    ),
                },
                {
                    "text": "✏️",
                    "callback_data": encode_suggest_callback(SuggestAction.edit, sug.id),
                },
                {
                    "text": "❌",
                    "callback_data": encode_suggest_callback(
                        SuggestAction.reject, sug.id
                    ),
                },
            ]
        )
    return {"inline_keyboard": rows}


def _format_card(job: Job, suggestions: list[SkillSuggestion]) -> str:
    lines = [
        f"Skill suggestions for {job.title} @ {job.company}",
        f"Job id: {job.id}",
        "",
        "Approve to add, Edit to rewrite, Reject to skip:",
        "",
    ]
    for sug in suggestions:
        prov = sug.provenance.value if hasattr(sug.provenance, "value") else sug.provenance
        lines.append(f"• {sug.skill} [{prov}]")
        if sug.proposed_text and sug.proposed_text != sug.skill:
            lines.append(f"  → {sug.proposed_text}")
    text = "\n".join(lines)
    if len(text) > 3900:
        return text[:3899] + "…"
    return text


async def send_pending_suggestions(
    *,
    client: TelegramClient | None = None,
    limit: int | None = None,
) -> SuggestSummary:
    """Send Telegram cards for jobs with unsent pending suggestions."""
    await init_db()
    client = client or TelegramClient()
    summary = SuggestSummary()

    async with session_scope() as session:
        jobs = await get_unsent_suggestion_jobs(session, limit=limit)

    if not jobs:
        log.info("suggest_send_empty")
        return summary

    for job in jobs:
        if job.id is None:
            continue
        try:
            async with session_scope() as session:
                pending = await get_pending_suggestions_for_job(session, job.id)
            # Only those not yet attached to a message
            unsent = [s for s in pending if s.review_message_id is None]
            if not unsent:
                summary.skipped += 1
                continue
            text = _format_card(job, unsent)
            result = await client.send_message(
                text,
                reply_markup=_suggestion_keyboard(unsent),
            )
            message_id = result.get("message_id")
            chat = result.get("chat") or {}
            chat_id = chat.get("id")
            async with session_scope() as session:
                for sug in unsent:
                    if sug.id is None:
                        continue
                    target = await get_skill_suggestion_by_id(session, sug.id)
                    if target is None:
                        continue
                    if message_id is not None:
                        target.review_message_id = int(message_id)
                    target.updated_at = datetime.now(UTC)
                    session.add(target)
                # Also stamp job chat id for edit replies
                if chat_id is not None:
                    job_row = await get_job_by_id(session, job.id)
                    if job_row is not None and not job_row.review_chat_id:
                        job_row.review_chat_id = str(chat_id)
                        session.add(job_row)
            summary.sent += 1
        except Exception as exc:
            log.warning("suggest_send_failed", job_id=job.id, error=str(exc))
            summary.errors += 1
            summary.error_details.append(f"job {job.id}: {exc}")

    log.info(
        "suggest_send_complete",
        sent=summary.sent,
        skipped=summary.skipped,
        errors=summary.errors,
    )
    return summary


async def apply_decided_suggestions(job_id: int) -> str | None:
    """If all suggestions for a job are decided, recompile resume with approvals.

    Returns the new resume path, or None if still waiting on pending items.
    """
    await init_db()
    profile = load_profile()
    settings = get_settings()

    async with session_scope() as session:
        suggestions = await get_suggestions_for_job(session, job_id)
        job = await get_job_by_id(session, job_id)

    if job is None:
        raise ValueError(f"Job {job_id} not found")
    if not suggestions:
        return None
    if any(s.status == SuggestionStatus.pending for s in suggestions):
        return None

    baseline: RoleBaseline | None = None
    baseline_id = next((s.baseline_id for s in suggestions if s.baseline_id), None)
    if baseline_id is not None:
        async with session_scope() as session:
            baseline = await get_role_baseline_by_id(session, baseline_id)

    if baseline is not None and baseline.resume_data:
        resume_data = copy.deepcopy(baseline.resume_data)
    else:
        from resume.selector import build_resume_data

        resume_data = build_resume_data(profile, job)

    merged = apply_approved_suggestions_to_resume_data(resume_data, suggestions)
    path = await compile_for_job(job_id, profile=profile, resume_data=merged)
    log.info(
        "suggestions_applied",
        job_id=job_id,
        path=str(path),
        approved=sum(
            1
            for s in suggestions
            if s.status in {SuggestionStatus.approved, SuggestionStatus.edited}
        ),
        resumes_dir=str(settings.resumes_path),
    )
    return str(path)


async def decide_suggestion(
    suggestion_id: int,
    action: SuggestAction,
    *,
    edited_text: str | None = None,
) -> SuggestionStatus:
    """Mark a suggestion approved/rejected/edited and maybe recompile."""
    await init_db()
    now = datetime.now(UTC)

    async with session_scope() as session:
        sug = await get_skill_suggestion_by_id(session, suggestion_id)
        if sug is None:
            raise ValueError(f"Suggestion {suggestion_id} not found")
        if sug.status != SuggestionStatus.pending:
            return sug.status

        if action == SuggestAction.approve:
            sug.status = SuggestionStatus.approved
        elif action == SuggestAction.reject:
            sug.status = SuggestionStatus.rejected
        elif action == SuggestAction.edit:
            sug.status = SuggestionStatus.edited
            if edited_text and edited_text.strip():
                sug.proposed_text = edited_text.strip()
        else:
            raise ValueError(f"Unknown suggest action: {action}")

        sug.decided_at = now
        sug.updated_at = now
        job_id = sug.job_id
        session.add(sug)

    await apply_decided_suggestions(job_id)
    async with session_scope() as session:
        refreshed = await get_skill_suggestion_by_id(session, suggestion_id)
    return refreshed.status if refreshed else SuggestionStatus.pending

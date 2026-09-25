"""LLM match evaluator: score, tier, and persist discovered jobs."""

from __future__ import annotations

import asyncio
import json
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime

import structlog

from config.profile import Profile, load_profile
from config.settings import get_settings
from core.db import (
    Job,
    Status,
    Tier,
    get_job_by_id,
    get_jobs_by_status,
    init_db,
    session_scope,
)
from core.textmatch import company_matches
from scorer.clients import (
    AnthropicClient,
    GeminiClient,
    LLMClient,
    build_llm_client,
    system_blocks_to_text,
)
from scorer.outreach import generate_outreach as draft_outreach
from scorer.prerank import prerank_jobs
from scorer.prompts import build_scoring_system_blocks, build_scoring_user
from scorer.schemas import SCORE_JSON_SCHEMA, Evaluation, ScoreRaw
from scraper.filters import evaluate_job

# Re-exported so callers and tests keep importing the client layer from scorer.engine.
__all__ = [
    "AnthropicClient",
    "Evaluation",
    "GeminiClient",
    "LLMClient",
    "ScoreSummary",
    "Scorer",
    "build_llm_client",
    "compute_tier",
    "parse_score",
    "score_pending",
]

_system_blocks_to_text = system_blocks_to_text

log = structlog.get_logger(__name__)

_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)```", re.IGNORECASE)


def _extract_json_object(text: str) -> str | None:
    """First brace-balanced JSON object, ignoring braces inside string literals."""
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    return None


def parse_score(text: str) -> ScoreRaw:
    """Extract compact {"s","t","r"} JSON from model output (tolerant)."""
    if not text or not text.strip():
        raise ValueError("Empty model response")

    cleaned = text.strip()
    fence = _FENCE_RE.search(cleaned)
    if fence:
        cleaned = fence.group(1).strip()

    candidates = [cleaned]
    extracted = _extract_json_object(cleaned)
    if extracted and extracted != cleaned:
        candidates.append(extracted)

    last_error: Exception | None = None
    for candidate in candidates:
        try:
            data = json.loads(candidate)
            if isinstance(data, dict):
                return ScoreRaw.model_validate(data)
        except (json.JSONDecodeError, ValueError) as exc:
            last_error = exc
            continue

    raise ValueError(f"Could not parse score JSON from: {text[:200]!r}") from last_error


def is_dream_company(company: str, profile: Profile) -> bool:
    """Dream-company match tolerant of legal suffixes ('Google' == 'Google LLC')."""
    return any(
        company_matches(company, dream)
        for dream in profile.preferences.dream_companies
        if dream.strip()
    )


def compute_tier(score: int, company: str, profile: Profile) -> Tier:
    """Deterministic tier from score + dream-company override (thresholds in settings)."""
    settings = get_settings()
    if score >= settings.tier_one_min_score or is_dream_company(company, profile):
        return Tier.one
    if score >= settings.tier_two_min_score:
        return Tier.two
    return Tier.three


def _status_for_tier(tier: Tier) -> Status:
    if tier == Tier.three:
        return Status.filtered_out
    return Status.staged


@dataclass
class ScoreSummary:
    scored: int = 0
    staged: int = 0
    filtered_out: int = 0
    errors: int = 0
    skipped: int = 0
    by_tier: dict[str, int] = field(default_factory=dict)
    error_details: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class _JobOutcome:
    kind: str  # staged | filtered_out | error
    tier: str | None = None
    detail: str | None = None


class Scorer:
    """Score discovered jobs and persist tiered results."""

    def __init__(
        self,
        *,
        client: LLMClient | None = None,
        profile: Profile | None = None,
    ) -> None:
        self._client = client
        self._profile = profile

    def _resolve_client(self) -> LLMClient:
        if self._client is not None:
            return self._client
        return build_llm_client()

    def _resolve_profile(self) -> Profile:
        if self._profile is not None:
            return self._profile
        return load_profile()

    async def score_job(
        self,
        job: Job,
        *,
        client: LLMClient | None = None,
        profile: Profile | None = None,
        generate_outreach: bool = True,
    ) -> Evaluation:
        """Score a single job and optionally draft Tier-1 outreach."""
        client = client or self._resolve_client()
        profile = profile or self._resolve_profile()
        settings = get_settings()

        # Cheap backlog guard: re-apply hard negatives without an LLM call.
        gate = evaluate_job(job, profile)
        if not gate.passed:
            reason = gate.reason or "hard-negative filter"
            log.info("score_job_prefilter", job_id=job.id, reason=reason)
            return Evaluation(
                score=0,
                tier=Tier.three,
                reasons=[reason],
                outreach=None,
            )

        system_blocks = build_scoring_system_blocks(profile)
        user = build_scoring_user(job)
        raw_text = await client.complete(
            model=settings.active_scorer_model,
            system_blocks=system_blocks,
            user=user,
            max_tokens=settings.score_max_tokens,
            temperature=0.0,
            json_mode=True,
            json_schema=SCORE_JSON_SCHEMA,
            thinking_level=settings.gemini_scorer_thinking_level,
        )
        raw = parse_score(raw_text)
        tier = compute_tier(raw.s, job.company, profile)
        outreach: str | None = None
        if generate_outreach and tier == Tier.one:
            # A failed draft must not discard a valid score: outreach is a bonus,
            # and Tier 1 is exactly where losing the job to Status.error hurts most.
            try:
                outreach = await draft_outreach(job, profile, client)
            except Exception as exc:
                log.warning("outreach_failed", job_id=job.id, error=str(exc)[:200])

        return Evaluation(
            score=raw.s,
            tier=tier,
            reasons=raw.r,
            outreach=outreach,
        )

    async def _score_and_persist(
        self,
        job: Job,
        *,
        client: LLMClient,
        profile: Profile,
        generate_outreach: bool,
    ) -> _JobOutcome:
        """Score one job and persist; never raises (returns error outcome)."""
        try:
            evaluation = await self.score_job(
                job,
                client=client,
                profile=profile,
                generate_outreach=generate_outreach,
            )
            new_status = _status_for_tier(evaluation.tier)
            now = datetime.now(UTC)
            async with session_scope() as session:
                if job.id is None:
                    return _JobOutcome(kind="error", detail="job missing id")
                target = await get_job_by_id(session, job.id)
                if target is None:
                    return _JobOutcome(kind="error", detail=f"job {job.id} missing")

                target.score = evaluation.score
                target.tier = evaluation.tier
                target.justification = evaluation.reasons or [
                    f"score={evaluation.score}"
                ]
                target.outreach_draft = evaluation.outreach
                target.scored_at = now
                target.status = new_status
                target.updated_at = now
                session.add(target)

            if new_status == Status.staged:
                return _JobOutcome(kind="staged", tier=evaluation.tier.value)
            return _JobOutcome(kind="filtered_out", tier=evaluation.tier.value)
        except Exception as exc:
            log.warning("score_job_failed", job_id=job.id, error=str(exc))
            try:
                if job.id is not None:
                    async with session_scope() as session:
                        target = await get_job_by_id(session, job.id)
                        if target is not None:
                            target.status = Status.error
                            target.last_error = str(exc)
                            target.alerted_at = None
                            target.updated_at = datetime.now(UTC)
                            session.add(target)
            except Exception as persist_exc:
                log.warning(
                    "score_error_persist_failed",
                    job_id=job.id,
                    error=str(persist_exc),
                )
            return _JobOutcome(kind="error", detail=f"job {job.id}: {exc}")

    async def score_pending(
        self,
        *,
        client: LLMClient | None = None,
        profile: Profile | None = None,
        limit: int | None = None,
        generate_outreach: bool = True,
        concurrency: int | None = None,
        stop_after_staged: int | None = None,
    ) -> ScoreSummary:
        """Score discovered jobs with bounded concurrency; optional early-stop."""
        await init_db()
        client = client or self._resolve_client()
        profile = profile or self._resolve_profile()
        settings = get_settings()
        workers = max(1, concurrency if concurrency is not None else settings.scorer_concurrency)
        summary = ScoreSummary()

        async with session_scope() as session:
            jobs = await get_jobs_by_status(session, Status.discovered, limit=limit)

        if not jobs:
            log.info("score_pending_empty")
            return summary

        # Prerank so the LLM budget is always spent best-first. When a
        # score_budget is set, only the weakest tail is deferred to a later run.
        jobs = prerank_jobs(jobs, profile)
        budget = settings.score_budget
        if budget is not None and len(jobs) > budget:
            deferred = len(jobs) - budget
            jobs = jobs[:budget]
            summary.skipped += deferred
            log.info("score_pending_budget_applied", budget=budget, deferred=deferred)

        semaphore = asyncio.Semaphore(workers)
        # Checked per job rather than per wave so stop_after_staged=2 never
        # pays for a full wave of 8 LLM calls.
        target_reached = asyncio.Event()
        staged_so_far = 0

        async def run_one(job: Job) -> _JobOutcome | None:
            nonlocal staged_so_far
            if target_reached.is_set():
                return None
            async with semaphore:
                if target_reached.is_set():
                    return None
                outcome = await self._score_and_persist(
                    job,
                    client=client,
                    profile=profile,
                    generate_outreach=generate_outreach,
                )
            if outcome.kind == "staged":
                staged_so_far += 1
                if stop_after_staged is not None and staged_so_far >= stop_after_staged:
                    target_reached.set()
            return outcome

        outcomes = await asyncio.gather(*[run_one(job) for job in jobs])

        for outcome in outcomes:
            if outcome is None:
                summary.skipped += 1
                continue
            if outcome.kind == "error":
                summary.errors += 1
                if outcome.detail:
                    summary.error_details.append(outcome.detail)
                continue
            summary.scored += 1
            if outcome.tier:
                summary.by_tier[outcome.tier] = summary.by_tier.get(outcome.tier, 0) + 1
            if outcome.kind == "staged":
                summary.staged += 1
            else:
                summary.filtered_out += 1

        log.info(
            "score_pending_complete",
            scored=summary.scored,
            staged=summary.staged,
            filtered_out=summary.filtered_out,
            errors=summary.errors,
            skipped=summary.skipped,
            by_tier=summary.by_tier,
            concurrency=workers,
            stop_after_staged=stop_after_staged,
        )
        return summary


async def score_pending(
    *,
    client: LLMClient | None = None,
    profile: Profile | None = None,
    limit: int | None = None,
    generate_outreach: bool = True,
    concurrency: int | None = None,
    stop_after_staged: int | None = None,
) -> ScoreSummary:
    """Module-level entry point used by README / Step 7."""
    return await Scorer(client=client, profile=profile).score_pending(
        client=client,
        profile=profile,
        limit=limit,
        generate_outreach=generate_outreach,
        concurrency=concurrency,
        stop_after_staged=stop_after_staged,
    )

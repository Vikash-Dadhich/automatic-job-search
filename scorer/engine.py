"""LLM match evaluator: score, tier, and persist discovered jobs."""

from __future__ import annotations

import asyncio
import json
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime

import structlog
from sqlmodel import col, select

from config.profile import Profile, load_profile
from config.settings import get_settings
from core.db import (
    Job,
    Status,
    Tier,
    get_job_by_id,
    get_jobs_by_status,
    get_recently_applied_companies,
    init_db,
    session_scope,
)
from core.textmatch import company_matches
from scorer.clients import (
    AnthropicClient,
    GeminiClient,
    LLMBillingError,
    LLMClient,
    TokenUsage,
    build_llm_client,
    is_permanent_account_error,
    system_blocks_to_text,
)
from scorer.cover_letter import generate_cover_letter as draft_cover_letter
from scorer.embeddings import (
    Embedder,
    build_embedder,
    clears_threshold,
    cosine,
    jd_vector,
    job_embed_text,
    load_profile_embedding,
    profile_embed_text,
    profile_hash,
    save_profile_embedding,
    stored_score,
    text_is_too_short,
)
from scorer.outreach import generate_outreach as draft_outreach
from scorer.prerank import prerank_jobs
from scorer.schemas import Evaluation, ScoreRaw
from scraper.filters import evaluate_job

# Re-exported so callers and tests keep importing the client layer from scorer.engine.
__all__ = [
    "AnthropicClient",
    "Evaluation",
    "GeminiClient",
    "LLMClient",
    "ScoreSummary",
    "Scorer",
    "TokenUsage",
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
    vector_rejected: int = 0
    vector_errors: int = 0
    by_tier: dict[str, int] = field(default_factory=dict)
    error_details: list[str] = field(default_factory=list)
    scored_ids: list[int] = field(default_factory=list)
    token_usage: TokenUsage | None = field(default=None)


@dataclass(frozen=True, slots=True)
class _JobOutcome:
    kind: str  # staged | filtered_out | error
    job_id: int | None = None
    tier: str | None = None
    detail: str | None = None


def _hard_blocked(job: Job, profile: Profile, cooldown: set[str]) -> bool:
    """Hard negative or company cooldown. Those jobs are not embedded."""
    if not evaluate_job(job, profile).passed:
        return True
    if cooldown and job.company:
        return any(company_matches(job.company, blocked) for blocked in cooldown)
    return False


def _log_embed_failure(exc: BaseException) -> None:
    if isinstance(exc, LLMBillingError) or is_permanent_account_error(exc):
        log.warning("vector_gate_billing", error=str(exc)[:200])
        return
    log.warning("vector_gate_embed_failed", error=str(exc)[:200])


async def _resolve_profile_vector(
    profile: Profile,
    embedder: Embedder | None,
) -> tuple[str, list[float] | None]:
    """Profile vector from disk, or one embed call. ``None`` means fail open."""
    settings = get_settings()
    text = profile_embed_text(profile)
    digest = profile_hash(text)
    cached = load_profile_embedding(
        digest,
        model=settings.openai_embedding_model,
        dimensions=settings.vector_dimensions,
    )
    if cached is not None:
        return digest, cached
    if embedder is None:
        return digest, None
    try:
        vectors = await embedder.embed([text])
    except Exception as exc:
        _log_embed_failure(exc)
        return digest, None
    width = settings.vector_dimensions
    if len(vectors) != 1 or len(vectors[0]) != width:
        log.warning("vector_gate_profile_mismatch")
        return digest, None
    save_profile_embedding(
        digest,
        vectors[0],
        model=settings.openai_embedding_model,
        dimensions=width,
    )
    return digest, vectors[0]


async def _save_vector(
    job: Job,
    vector: list[float],
    score: float,
    digest: str,
    decision: str,
    *,
    reason: str | None = None,
) -> None:
    job.embedding = vector
    job.vector_score = score
    job.vector_profile_hash = digest
    job.vector_decision = decision
    job.embedding_model = get_settings().openai_embedding_model
    if job.id is None:
        return
    now = datetime.now(UTC)
    async with session_scope() as session:
        target = await get_job_by_id(session, job.id)
        if target is None:
            return
        target.embedding = vector
        target.vector_score = score
        target.vector_profile_hash = digest
        target.vector_decision = decision
        target.embedding_model = job.embedding_model
        if decision == "reject":
            target.score = 0
            target.tier = Tier.three
            target.justification = [reason or f"vector gate: {score:.2f}"]
            target.status = Status.filtered_out
            target.scored_at = now
            target.outreach_draft = None
            target.cover_letter = None
        target.updated_at = now
        session.add(target)


async def _decide_vector(
    job: Job,
    vector: list[float],
    score: float,
    digest: str,
    profile: Profile,
) -> str:
    """Persist pass or reject. Dream companies always pass."""
    dream = is_dream_company(job.company or "", profile)
    if dream or clears_threshold(score):
        await _save_vector(job, vector, score, digest, "pass")
        if dream and not clears_threshold(score):
            log.info("vector_gate_dream_bypass", job_id=job.id, score=round(score, 4))
        return "accept"
    threshold = get_settings().vector_threshold
    reason = f"vector gate: {score:.2f} < {threshold:.2f}"
    await _save_vector(job, vector, score, digest, "reject", reason=reason)
    return "reject"


async def _embed_texts(
    texts: list[str],
    embedder: Embedder | None,
) -> list[list[float]] | None:
    if embedder is None or not texts:
        return None
    try:
        vectors = await embedder.embed(texts)
    except Exception as exc:
        _log_embed_failure(exc)
        return None
    if len(vectors) != len(texts):
        log.warning(
            "vector_gate_embed_mismatch",
            expected=len(texts),
            got=len(vectors),
        )
        return None
    return vectors


async def _reopen_vector_rejects(profile: Profile, embedder: Embedder | None) -> None:
    """Send stored rejects back to discovered when they now clear the threshold."""
    settings = get_settings()
    async with session_scope() as session:
        result = await session.exec(
            select(Job).where(
                col(Job.status) == Status.filtered_out,
                col(Job.vector_decision) == "reject",
            )
        )
        rows = list(result.all())
    if not rows:
        return
    width = settings.vector_dimensions
    digest = profile_hash(profile_embed_text(profile))
    needs_profile = any(
        jd_vector(row, width, model=settings.openai_embedding_model) is not None
        and (row.vector_profile_hash != digest or row.vector_score is None)
        for row in rows
    )
    profile_vector: list[float] | None = None
    if needs_profile:
        digest, profile_vector = await _resolve_profile_vector(profile, embedder)

    for row in rows:
        vector = jd_vector(row, width, model=settings.openai_embedding_model)
        if vector is None or row.id is None:
            continue
        if row.vector_profile_hash == digest and row.vector_score is not None:
            score = float(row.vector_score)
            changed = False
        elif profile_vector is None:
            continue
        else:
            try:
                score = cosine(profile_vector, vector)
            except ValueError:
                continue
            changed = True
        if clears_threshold(score):
            await _reopen_job(row.id, score, digest)
        elif changed:
            await _touch_vector_score(row.id, score, digest)


async def _reopen_job(job_id: int, score: float, digest: str) -> None:
    async with session_scope() as session:
        target = await get_job_by_id(session, job_id)
        if target is None:
            return
        target.status = Status.discovered
        target.score = None
        target.tier = None
        target.justification = None
        target.scored_at = None
        target.vector_score = score
        target.vector_profile_hash = digest
        target.updated_at = datetime.now(UTC)
        session.add(target)


async def _touch_vector_score(job_id: int, score: float, digest: str) -> None:
    async with session_scope() as session:
        target = await get_job_by_id(session, job_id)
        if target is None:
            return
        target.vector_score = score
        target.vector_profile_hash = digest
        target.updated_at = datetime.now(UTC)
        session.add(target)


async def _apply_vector_gate(
    jobs: list[Job],
    profile: Profile,
    cooldown: set[str],
    embedder: Embedder | None,
) -> tuple[list[Job], int, int, int]:
    """Walk best-first. Rejects do not consume ``score_budget``.

    Returns accepted jobs, deferred count, reject count, and fail-open count.
    """
    settings = get_settings()
    ranked = prerank_jobs(jobs, profile)
    budget = settings.score_budget
    width = settings.vector_dimensions
    accepted: list[Job] = []
    rejected = 0
    errors = 0
    digest = profile_hash(profile_embed_text(profile))
    profile_vector: list[float] | None = None
    profile_ready = False

    async def profile_vec() -> list[float] | None:
        nonlocal digest, profile_vector, profile_ready
        if not profile_ready:
            digest, profile_vector = await _resolve_profile_vector(profile, embedder)
            profile_ready = True
        return profile_vector

    async def accept_or_reject(job: Job, vector: list[float], score: float) -> None:
        nonlocal rejected
        choice = await _decide_vector(job, vector, score, digest, profile)
        if choice == "accept":
            accepted.append(job)
        else:
            rejected += 1

    i = 0
    while i < len(ranked):
        if budget is not None and len(accepted) >= budget:
            break
        job = ranked[i]
        if _hard_blocked(job, profile, cooldown):
            accepted.append(job)
            i += 1
            continue
        text = job_embed_text(job)
        if text_is_too_short(text):
            accepted.append(job)
            i += 1
            continue

        embed_model = settings.openai_embedding_model
        cached = stored_score(job, digest, width, model=embed_model)
        existing = jd_vector(job, width, model=embed_model)
        if cached is not None and existing is not None:
            await accept_or_reject(job, existing, cached)
            i += 1
            continue
        if existing is not None:
            pvec = await profile_vec()
            if pvec is None:
                errors += 1
                accepted.append(job)
            else:
                try:
                    score = cosine(pvec, existing)
                except ValueError:
                    errors += 1
                    accepted.append(job)
                else:
                    await accept_or_reject(job, existing, score)
            i += 1
            continue

        batch: list[Job] = []
        texts: list[str] = []
        k = i
        while k < len(ranked) and len(batch) < settings.vector_batch_size:
            if budget is not None and len(accepted) + len(batch) >= budget and batch:
                break
            cand = ranked[k]
            if _hard_blocked(cand, profile, cooldown):
                break
            ctext = job_embed_text(cand)
            if text_is_too_short(ctext):
                break
            if (
                stored_score(cand, digest, width, model=embed_model) is not None
                or jd_vector(cand, width, model=embed_model) is not None
            ):
                break
            batch.append(cand)
            texts.append(ctext)
            k += 1
            if budget is not None and len(accepted) + len(batch) >= budget:
                break

        pvec = await profile_vec()
        vectors = await _embed_texts(texts, embedder) if pvec is not None else None
        processed = 0
        for offset, cand in enumerate(batch):
            if budget is not None and len(accepted) >= budget:
                break
            vector = None if vectors is None else vectors[offset]
            if pvec is None or vector is None or len(vector) != width:
                errors += 1
                accepted.append(cand)
            else:
                try:
                    score = cosine(pvec, vector)
                except ValueError:
                    errors += 1
                    accepted.append(cand)
                else:
                    await accept_or_reject(cand, vector, score)
            processed += 1
        i += processed

    return accepted, len(ranked) - i, rejected, errors


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
        generate_cover_letter: bool = True,
        cooldown_companies: set[str] | None = None,
    ) -> Evaluation:
        """Score a single job and optionally draft Tier-1 outreach and a cover letter."""
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
                cover_letter=None,
            )

        if cooldown_companies and job.company:
            if any(company_matches(job.company, blocked) for blocked in cooldown_companies):
                log.info("score_job_company_cooldown", job_id=job.id, company=job.company)
                return Evaluation(
                    score=0,
                    tier=Tier.three,
                    reasons=[f"company cooldown: {job.company} applied to recently"],
                    outreach=None,
                    cover_letter=None,
                )

        from scorer.fit import evaluate_fit

        decision = await evaluate_fit(
            job,
            profile,
            client,
            model=settings.active_scorer_model,
            max_tokens=settings.score_max_tokens,
        )
        if not decision.available or decision.score is None:
            return Evaluation(
                score=0,
                tier=Tier.three,
                reasons=decision.evidence,
                outreach=None,
                cover_letter=None,
                fit_available=False,
                fit_confidence=decision.confidence,
                fit_strengths=decision.strengths,
                fit_gaps=decision.gaps,
                fit_evidence=decision.evidence,
                fit_dimensions=decision.dimensions,
                fit_content_hash=decision.content_hash,
                fit_profile_hash=decision.profile_hash,
            )
        tier = compute_tier(decision.score, job.company, profile)
        outreach: str | None = None
        if generate_outreach and tier == Tier.one:
            # A failed draft must not discard a valid score: outreach is a bonus,
            # and Tier 1 is exactly where losing the job to Status.error hurts most.
            try:
                outreach = await draft_outreach(job, profile, client)
            except Exception as exc:
                log.warning("outreach_failed", job_id=job.id, error=str(exc)[:200])

        cover_letter: str | None = None
        if generate_cover_letter and tier == Tier.one:
            try:
                cover_letter = await draft_cover_letter(job, profile, client)
            except Exception as exc:
                log.warning("cover_letter_failed", job_id=job.id, error=str(exc)[:200])

        return Evaluation(
            score=decision.score,
            tier=tier,
            reasons=decision.evidence or decision.strengths,
            outreach=outreach,
            cover_letter=cover_letter,
            fit_confidence=decision.confidence,
            fit_strengths=decision.strengths,
            fit_gaps=decision.gaps,
            fit_evidence=decision.evidence,
            fit_dimensions=decision.dimensions,
            fit_content_hash=decision.content_hash,
            fit_profile_hash=decision.profile_hash,
        )

    async def _score_and_persist(
        self,
        job: Job,
        *,
        client: LLMClient,
        profile: Profile,
        generate_outreach: bool,
        generate_cover_letter: bool = True,
        cooldown_companies: set[str] | None = None,
    ) -> _JobOutcome:
        """Score one job and persist; never raises (returns error outcome)."""
        try:
            evaluation = await self.score_job(
                job,
                client=client,
                profile=profile,
                generate_outreach=generate_outreach,
                generate_cover_letter=generate_cover_letter,
                cooldown_companies=cooldown_companies,
            )
            new_status = _status_for_tier(evaluation.tier)
            now = datetime.now(UTC)
            async with session_scope() as session:
                if job.id is None:
                    return _JobOutcome(kind="error", detail="job missing id")
                target = await get_job_by_id(session, job.id)
                if target is None:
                    return _JobOutcome(kind="error", detail=f"job {job.id} missing")

                if not evaluation.fit_available:
                    target.fit_confidence = evaluation.fit_confidence
                    target.fit_strengths = evaluation.fit_strengths
                    target.fit_gaps = evaluation.fit_gaps
                    target.fit_evidence = evaluation.fit_evidence
                    target.fit_dimensions = evaluation.fit_dimensions or None
                    target.fit_version = "phase6-v1"
                    target.fit_content_hash = evaluation.fit_content_hash
                    target.fit_profile_hash = evaluation.fit_profile_hash
                    target.justification = evaluation.reasons
                    target.updated_at = now
                    session.add(target)
                    return _JobOutcome(kind="unavailable", job_id=job.id)

                target.score = evaluation.score
                target.tier = evaluation.tier
                target.justification = evaluation.reasons or [
                    f"score={evaluation.score}"
                ]
                target.outreach_draft = evaluation.outreach
                target.cover_letter = evaluation.cover_letter
                target.scored_at = now
                target.status = new_status
                target.fit_confidence = evaluation.fit_confidence
                target.fit_strengths = evaluation.fit_strengths or None
                target.fit_gaps = evaluation.fit_gaps or None
                target.fit_evidence = evaluation.fit_evidence or None
                target.fit_dimensions = evaluation.fit_dimensions or None
                target.fit_version = "phase6-v1"
                target.fit_content_hash = evaluation.fit_content_hash or target.content_hash
                target.fit_profile_hash = evaluation.fit_profile_hash
                target.updated_at = now
                session.add(target)

            if new_status == Status.staged:
                return _JobOutcome(kind="staged", job_id=job.id, tier=evaluation.tier.value)
            return _JobOutcome(
                kind="filtered_out",
                job_id=job.id,
                tier=evaluation.tier.value,
            )
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
        generate_outreach: bool | None = None,
        generate_cover_letter: bool | None = None,
        concurrency: int | None = None,
        stop_after_staged: int | None = None,
        embedder: Embedder | None = None,
    ) -> ScoreSummary:
        """Score discovered jobs with bounded concurrency; optional early-stop."""
        await init_db()
        client = client or self._resolve_client()
        profile = profile or self._resolve_profile()
        settings = get_settings()
        if generate_outreach is None:
            generate_outreach = settings.tier_one_drafts_enabled
        if generate_cover_letter is None:
            generate_cover_letter = settings.tier_one_drafts_enabled
        workers = max(1, concurrency if concurrency is not None else settings.scorer_concurrency)
        summary = ScoreSummary()
        active_embedder = embedder
        if settings.vector_gate_enabled and active_embedder is None:
            active_embedder = build_embedder()
        if settings.vector_gate_enabled:
            await _reopen_vector_rejects(profile, active_embedder)

        async with session_scope() as session:
            jobs = await get_jobs_by_status(session, Status.discovered, limit=limit)

        if not jobs:
            log.info("score_pending_empty")
            summary.token_usage = getattr(client, "usage", None)
            return summary

        async with session_scope() as session:
            cooldown_companies = await get_recently_applied_companies(
                session, cooldown_days=settings.company_cooldown_days
            )

        if settings.vector_gate_enabled:
            gated = await _apply_vector_gate(
                jobs,
                profile,
                cooldown_companies,
                active_embedder,
            )
            jobs, deferred, summary.vector_rejected, summary.vector_errors = gated
            summary.skipped += deferred
            summary.filtered_out += summary.vector_rejected
        else:
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
                    generate_cover_letter=generate_cover_letter,
                    cooldown_companies=cooldown_companies,
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
            if outcome.kind == "unavailable":
                summary.skipped += 1
                continue
            summary.scored += 1
            if outcome.job_id is not None:
                summary.scored_ids.append(outcome.job_id)
            if outcome.tier:
                summary.by_tier[outcome.tier] = summary.by_tier.get(outcome.tier, 0) + 1
            if outcome.kind == "staged":
                summary.staged += 1
            else:
                summary.filtered_out += 1

        summary.token_usage = getattr(client, "usage", None)

        log.info(
            "score_pending_complete",
            scored=summary.scored,
            staged=summary.staged,
            filtered_out=summary.filtered_out,
            errors=summary.errors,
            skipped=summary.skipped,
            vector_rejected=summary.vector_rejected,
            vector_errors=summary.vector_errors,
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
    generate_outreach: bool | None = None,
    generate_cover_letter: bool | None = None,
    concurrency: int | None = None,
    stop_after_staged: int | None = None,
    embedder: Embedder | None = None,
) -> ScoreSummary:
    """Module-level entry point used by README / Step 7."""
    return await Scorer(client=client, profile=profile).score_pending(
        client=client,
        profile=profile,
        limit=limit,
        generate_outreach=generate_outreach,
        generate_cover_letter=generate_cover_letter,
        concurrency=concurrency,
        stop_after_staged=stop_after_staged,
        embedder=embedder,
    )

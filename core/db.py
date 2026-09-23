"""Async SQLModel persistence for jobs, scoring, and workflow state.

Supports SQLite (local / tests via aiosqlite) and Neon Postgres (asyncpg).
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any, ClassVar

from sqlalchemy import JSON, Column, DateTime
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import Field, SQLModel, UniqueConstraint, col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from config.settings import PROJECT_ROOT, get_settings


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _tz_datetime(*, nullable: bool = False, default_factory: Any = None) -> Any:
    """UTC-aware DateTime column (TIMESTAMPTZ on Postgres; works on SQLite too)."""
    kwargs: dict[str, Any] = {
        "sa_column": Column(DateTime(timezone=True), nullable=nullable),
    }
    if default_factory is not None:
        kwargs["default_factory"] = default_factory
    elif nullable:
        kwargs["default"] = None
    return Field(**kwargs)


class Source(StrEnum):
    linkedin = "linkedin"
    indeed = "indeed"
    workday = "workday"


class Status(StrEnum):
    discovered = "discovered"
    filtered_out = "filtered_out"
    scored = "scored"
    staged = "staged"
    pending_review = "pending_review"
    submitted = "submitted"
    manual_review = "manual_review"
    ignored = "ignored"
    error = "error"


class Tier(StrEnum):
    one = "one"
    two = "two"
    three = "three"


class SuggestionStatus(StrEnum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    edited = "edited"


class SkillProvenance(StrEnum):
    grounded = "grounded"
    inferred = "inferred"


class SkillPlacement(StrEnum):
    skills = "skills"
    experience = "experience"


class Job(SQLModel, table=True):
    """Core job record threaded through discovery → scoring → application."""

    __tablename__: ClassVar[str] = "jobs"
    __table_args__ = (UniqueConstraint("source", "external_id", name="uq_source_external_id"),)

    id: int | None = Field(default=None, primary_key=True)

    # Identity / dedup
    source: Source
    external_id: str = Field(index=True, max_length=512)
    tenant: str | None = Field(default=None, max_length=256)
    content_hash: str | None = Field(default=None, max_length=64)

    # Posting
    title: str = Field(max_length=512)
    company: str = Field(max_length=512)
    location: str | None = Field(default=None, max_length=512)
    url: str = Field(max_length=2048)
    description_clean: str | None = Field(default=None)
    posted_at: datetime | None = _tz_datetime(nullable=True)
    discovered_at: datetime = _tz_datetime(default_factory=_utcnow)

    # Scoring (nullable until Step 3)
    score: int | None = Field(default=None, ge=0, le=100)
    tier: Tier | None = Field(default=None)
    justification: list[str] | None = Field(default=None, sa_column=Column(JSON, nullable=True))
    outreach_draft: str | None = Field(default=None)
    scored_at: datetime | None = _tz_datetime(nullable=True)

    # Workflow
    status: Status = Field(default=Status.discovered, index=True)
    resume_path: str | None = Field(default=None, max_length=1024)
    screenshot_path: str | None = Field(default=None, max_length=1024)
    application_answers: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    review_message_id: int | None = Field(default=None)
    review_chat_id: str | None = Field(default=None, max_length=64)
    decided_at: datetime | None = _tz_datetime(nullable=True)
    last_error: str | None = Field(default=None)
    alerted_at: datetime | None = _tz_datetime(nullable=True)
    prep_pack_sent_at: datetime | None = _tz_datetime(nullable=True)
    created_at: datetime = _tz_datetime(default_factory=_utcnow)
    updated_at: datetime = _tz_datetime(default_factory=_utcnow)


class RoleBaseline(SQLModel, table=True):
    """Per-role baseline resume built from aggregating ~15-20 JDs."""

    __tablename__: ClassVar[str] = "role_baselines"

    id: int | None = Field(default=None, primary_key=True)
    role: str = Field(index=True, max_length=256)
    title_terms: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    skills: list[dict[str, Any]] = Field(
        default_factory=list,
        sa_column=Column(JSON, nullable=False),
    )
    resume_data: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON, nullable=False),
    )
    pdf_path: str | None = Field(default=None, max_length=1024)
    job_ids: list[int] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    created_at: datetime = _tz_datetime(default_factory=_utcnow)
    updated_at: datetime = _tz_datetime(default_factory=_utcnow)


class SkillSuggestion(SQLModel, table=True):
    """Per-JD skill addition proposed against a role baseline (Telegram approval)."""

    __tablename__: ClassVar[str] = "skill_suggestions"

    id: int | None = Field(default=None, primary_key=True)
    job_id: int = Field(index=True, foreign_key="jobs.id")
    baseline_id: int | None = Field(default=None, foreign_key="role_baselines.id")
    skill: str = Field(max_length=256)
    category: str = Field(default="hard", max_length=32)
    placement: SkillPlacement = Field(default=SkillPlacement.skills)
    proposed_text: str = Field(default="")
    provenance: SkillProvenance = Field(default=SkillProvenance.inferred)
    status: SuggestionStatus = Field(default=SuggestionStatus.pending, index=True)
    review_message_id: int | None = Field(default=None)
    created_at: datetime = _tz_datetime(default_factory=_utcnow)
    updated_at: datetime = _tz_datetime(default_factory=_utcnow)
    decided_at: datetime | None = _tz_datetime(nullable=True)


class PeerProfile(SQLModel, table=True):
    """Parsed LinkedIn profile used for peer benchmarking."""

    __tablename__: ClassVar[str] = "peer_profiles"

    id: int | None = Field(default=None, primary_key=True)
    url: str = Field(max_length=2048, index=True)
    is_self: bool = Field(default=False, index=True)
    full_name: str | None = Field(default=None, max_length=256)
    headline: str | None = Field(default=None, max_length=512)
    current_title: str | None = Field(default=None, max_length=256)
    years_experience: float | None = Field(default=None)
    companies: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    education_level: str | None = Field(default=None, max_length=128)
    skills: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    seniority: str | None = Field(default=None, max_length=64)
    raw_text: str | None = Field(default=None)
    created_at: datetime = _tz_datetime(default_factory=_utcnow)
    updated_at: datetime = _tz_datetime(default_factory=_utcnow)


class Benchmark(SQLModel, table=True):
    """Benchmark of the candidate vs peers for one job."""

    __tablename__: ClassVar[str] = "benchmarks"

    id: int | None = Field(default=None, primary_key=True)
    job_id: int = Field(index=True, foreign_key="jobs.id")
    overall_score: int = Field(default=0, ge=0, le=100)
    percentile: float | None = Field(default=None)
    dimensions: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON, nullable=False),
    )
    strengths: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    gaps: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    recommendations: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSON, nullable=False),
    )
    peer_ids: list[int] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    report_path: str | None = Field(default=None, max_length=1024)
    created_at: datetime = _tz_datetime(default_factory=_utcnow)


_engine = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def normalize_database_url(url: str) -> str:
    """Normalize DATABASE_URL for SQLAlchemy async engines.

    - Relative sqlite paths become absolute under PROJECT_ROOT.
    - Plain ``postgresql://`` becomes ``postgresql+asyncpg://``.
    - Neon ``channel_binding=require`` is dropped (asyncpg does not need it).
    """
    raw = (url or "").strip()
    if not raw:
        return raw

    # Neon / postgres connection strings from the console omit the async driver.
    if raw.startswith("postgresql://"):
        raw = "postgresql+asyncpg://" + raw.removeprefix("postgresql://")
    elif raw.startswith("postgres://"):
        raw = "postgresql+asyncpg://" + raw.removeprefix("postgres://")

    # asyncpg wants ssl=require (not libpq sslmode). Drop Prisma/libpq params it rejects.
    _DROP_QUERY = {"channel_binding", "connection_limit", "connect_timeout", "pgbouncer"}
    _needs_rewrite = ("channel_binding=", "sslmode=", "connection_limit=", "connect_timeout=")
    if any(k in raw for k in _needs_rewrite):
        from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

        parsed = urlparse(raw)
        query: list[tuple[str, str]] = []
        for k, v in parse_qsl(parsed.query, keep_blank_values=True):
            if k in _DROP_QUERY:
                continue
            if k == "sslmode":
                query.append(("ssl", v if v != "prefer" else "require"))
                continue
            query.append((k, v))
        raw = urlunparse(parsed._replace(query=urlencode(query)))

    return _absolute_sqlite_url(raw)


def _absolute_sqlite_url(url: str) -> str:
    """Make relative sqlite paths absolute so cwd does not matter."""
    prefix = "sqlite+aiosqlite:///"
    if not url.startswith(prefix):
        return url
    rest = url[len(prefix) :]
    if rest == ":memory:" or rest.startswith("/"):
        return url
    abs_path = (PROJECT_ROOT / rest).resolve()
    return f"{prefix}{abs_path}"


def _is_sqlite_url(url: str) -> bool:
    return url.startswith("sqlite+")


def _is_postgres_url(url: str) -> bool:
    return url.startswith("postgresql+") or url.startswith("postgres+")


def get_engine():
    global _engine, _session_factory
    if _engine is None:
        settings = get_settings()
        url = normalize_database_url(settings.database_url)
        connect_args: dict[str, object] = {}
        engine_kwargs: dict[str, object] = {"echo": False}
        # Neon / PgBouncer transaction poolers break asyncpg prepared-statement cache.
        if _is_postgres_url(url) and "-pooler." in url:
            connect_args["statement_cache_size"] = 0
        if _is_postgres_url(url):
            # Detect and discard stale connections before use. Long pipeline runs
            # (15+ min) exceed Neon's pooler idle-connection timeout; without
            # pre_ping the next stage gets an "InterfaceError: connection is closed".
            engine_kwargs["pool_pre_ping"] = True
            # Belt-and-suspenders: recycle connections after 4 min regardless.
            engine_kwargs["pool_recycle"] = 240
        _engine = create_async_engine(url, connect_args=connect_args, **engine_kwargs)
        _session_factory = async_sessionmaker(
            _engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    get_engine()
    assert _session_factory is not None
    return _session_factory


async def reset_engine() -> None:
    """Dispose the global engine (used by tests to switch DATABASE_URL)."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _session_factory = None


@asynccontextmanager
async def session_scope() -> AsyncIterator[AsyncSession]:
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    """Create storage directories and ensure all tables exist."""
    settings = get_settings()
    for path in (
        settings.resumes_path,
        settings.screenshots_path,
        settings.sessions_path,
        settings.prep_packs_path,
        settings.baselines_path,
        settings.benchmarks_path,
        PROJECT_ROOT / "storage",
    ):
        Path(path).mkdir(parents=True, exist_ok=True)

    # Ensure parent of sqlite file exists (Postgres has no local file).
    url = normalize_database_url(settings.database_url)
    if _is_sqlite_url(url) and not url.endswith(":memory:"):
        db_path = Path(url.removeprefix("sqlite+aiosqlite:///"))
        db_path.parent.mkdir(parents=True, exist_ok=True)

    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


# Scored-but-not-yet-acted-on states, safe to rewind when the JD text changes.
_RESCORABLE_STATUSES = frozenset({Status.scored, Status.staged})


async def upsert_job(session: AsyncSession, job: Job) -> Job:
    """Insert a job or update mutable fields when (source, external_id) already exists.

    Re-runs within 24h are idempotent: identity fields stay; description and
    metadata refresh; scoring/workflow fields are left alone if already set.
    A materially rewritten JD resets an unreviewed job for re-scoring.
    """
    statement = select(Job).where(
        Job.source == job.source,
        Job.external_id == job.external_id,
    )
    result = await session.exec(statement)
    existing = result.first()

    now = datetime.now(UTC)
    if existing is None:
        job.created_at = now
        job.updated_at = now
        session.add(job)
        await session.flush()
        await session.refresh(job)
        return job

    # Refresh posting content; keep post-scoring workflow unless still pre-score
    content_changed = (
        job.content_hash is not None
        and existing.content_hash is not None
        and job.content_hash != existing.content_hash
    )
    existing.title = job.title
    existing.company = job.company
    existing.location = job.location
    existing.url = job.url
    if job.description_clean is not None:
        existing.description_clean = job.description_clean
    if job.content_hash is not None:
        existing.content_hash = job.content_hash
    if job.tenant is not None:
        existing.tenant = job.tenant
    if job.posted_at is not None:
        existing.posted_at = job.posted_at
    if existing.status in {Status.discovered, Status.filtered_out}:
        existing.status = job.status
        if job.justification is not None:
            existing.justification = job.justification
    elif content_changed and existing.status in _RESCORABLE_STATUSES:
        # The employer edited the JD; the old score was judged on stale text.
        # Only rewind states the human has not acted on yet.
        existing.status = Status.discovered
        existing.score = None
        existing.tier = None
        existing.scored_at = None
        existing.justification = None
        existing.outreach_draft = None
    existing.updated_at = now
    session.add(existing)
    await session.flush()
    await session.refresh(existing)
    return existing


async def get_job_by_source_id(
    session: AsyncSession,
    source: Source,
    external_id: str,
) -> Job | None:
    statement = select(Job).where(
        col(Job.source) == source,
        col(Job.external_id) == external_id,
    )
    result = await session.exec(statement)
    return result.first()


async def get_job_by_id(session: AsyncSession, job_id: int) -> Job | None:
    statement = select(Job).where(col(Job.id) == job_id)
    result = await session.exec(statement)
    return result.first()


async def get_jobs_by_status(
    session: AsyncSession,
    status: Status,
    *,
    limit: int | None = None,
) -> list[Job]:
    """Return jobs with the given status, oldest first."""
    statement = select(Job).where(col(Job.status) == status).order_by(col(Job.id))
    if limit is not None:
        statement = statement.limit(limit)
    result = await session.exec(statement)
    return list(result.all())


async def get_unsent_pending_reviews(
    session: AsyncSession,
    *,
    limit: int | None = None,
) -> list[Job]:
    """pending_review jobs that have not yet been sent to Telegram."""
    statement = (
        select(Job)
        .where(
            col(Job.status) == Status.pending_review,
            col(Job.review_message_id).is_(None),  # type: ignore[union-attr]
        )
        .order_by(col(Job.id))
    )
    if limit is not None:
        statement = statement.limit(limit)
    result = await session.exec(statement)
    return list(result.all())


async def get_unsent_alerts(
    session: AsyncSession,
    *,
    limit: int | None = None,
) -> list[Job]:
    """manual_review / error jobs that have not yet been alerted on Telegram."""
    statement = (
        select(Job)
        .where(
            col(Job.status).in_([Status.manual_review, Status.error]),  # type: ignore[union-attr]
            col(Job.alerted_at).is_(None),  # type: ignore[union-attr]
        )
        .order_by(col(Job.id))
    )
    if limit is not None:
        statement = statement.limit(limit)
    result = await session.exec(statement)
    return list(result.all())


async def get_unsent_prep_pack_jobs(
    session: AsyncSession,
    *,
    limit: int | None = None,
) -> list[Job]:
    """Staged LinkedIn/Indeed jobs not yet included in a prep pack (score desc)."""
    statement = (
        select(Job)
        .where(
            col(Job.status) == Status.staged,
            col(Job.source).in_([Source.linkedin, Source.indeed]),  # type: ignore[union-attr]
            col(Job.prep_pack_sent_at).is_(None),  # type: ignore[union-attr]
        )
        .order_by(col(Job.score).desc(), col(Job.id))
    )
    if limit is not None:
        statement = statement.limit(limit)
    result = await session.exec(statement)
    return list(result.all())


async def get_jobs_for_role(
    session: AsyncSession,
    title_terms: list[str],
    *,
    limit: int = 20,
) -> list[Job]:
    """Return recent jobs whose title matches any of the role title terms.

    Matching is case-insensitive substring. Prefer jobs with a cleaned
    description so skill extraction has something to work with.
    """
    terms = [t.strip().lower() for t in title_terms if t and t.strip()]
    if not terms:
        return []

    # SQLite: pull a recent window then filter in Python for portable matching.
    statement = (
        select(Job)
        .where(col(Job.description_clean).is_not(None))  # type: ignore[union-attr]
        .order_by(col(Job.discovered_at).desc(), col(Job.id).desc())
        .limit(max(limit * 10, 100))
    )
    result = await session.exec(statement)
    candidates = list(result.all())

    matched: list[Job] = []
    for job in candidates:
        title_l = (job.title or "").lower()
        if any(term in title_l for term in terms):
            matched.append(job)
            if len(matched) >= limit:
                break
    return matched


async def get_role_baseline_by_role(
    session: AsyncSession,
    role: str,
) -> RoleBaseline | None:
    statement = (
        select(RoleBaseline)
        .where(col(RoleBaseline.role) == role)
        .order_by(col(RoleBaseline.id).desc())
    )
    result = await session.exec(statement)
    return result.first()


async def get_role_baseline_by_id(
    session: AsyncSession,
    baseline_id: int,
) -> RoleBaseline | None:
    statement = select(RoleBaseline).where(col(RoleBaseline.id) == baseline_id)
    result = await session.exec(statement)
    return result.first()


async def get_skill_suggestion_by_id(
    session: AsyncSession,
    suggestion_id: int,
) -> SkillSuggestion | None:
    statement = select(SkillSuggestion).where(col(SkillSuggestion.id) == suggestion_id)
    result = await session.exec(statement)
    return result.first()


async def get_pending_suggestions_for_job(
    session: AsyncSession,
    job_id: int,
) -> list[SkillSuggestion]:
    statement = (
        select(SkillSuggestion)
        .where(
            col(SkillSuggestion.job_id) == job_id,
            col(SkillSuggestion.status) == SuggestionStatus.pending,
        )
        .order_by(col(SkillSuggestion.id))
    )
    result = await session.exec(statement)
    return list(result.all())


async def get_suggestions_for_job(
    session: AsyncSession,
    job_id: int,
) -> list[SkillSuggestion]:
    statement = (
        select(SkillSuggestion)
        .where(col(SkillSuggestion.job_id) == job_id)
        .order_by(col(SkillSuggestion.id))
    )
    result = await session.exec(statement)
    return list(result.all())


async def get_unsent_suggestion_jobs(
    session: AsyncSession,
    *,
    limit: int | None = None,
) -> list[Job]:
    """Jobs that have pending suggestions not yet sent to Telegram."""
    statement = (
        select(SkillSuggestion)
        .where(
            col(SkillSuggestion.status) == SuggestionStatus.pending,
            col(SkillSuggestion.review_message_id).is_(None),  # type: ignore[union-attr]
        )
        .order_by(col(SkillSuggestion.job_id), col(SkillSuggestion.id))
    )
    result = await session.exec(statement)
    suggestions = list(result.all())
    job_ids: list[int] = []
    seen: set[int] = set()
    for sug in suggestions:
        if sug.job_id in seen:
            continue
        seen.add(sug.job_id)
        job_ids.append(sug.job_id)
        if limit is not None and len(job_ids) >= limit:
            break

    jobs: list[Job] = []
    for jid in job_ids:
        job = await get_job_by_id(session, jid)
        if job is not None:
            jobs.append(job)
    return jobs


def job_to_dict(job: Job) -> dict[str, Any]:
    return job.model_dump()

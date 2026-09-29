"""Async SQLModel persistence for jobs, scoring, and workflow state.

Supports SQLite (local / tests via aiosqlite) and Neon Postgres (asyncpg).
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from pathlib import Path
from typing import Any, ClassVar

from sqlalchemy import JSON, Column, DateTime, text, update
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import Field, SQLModel, UniqueConstraint, col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from config.settings import PROJECT_ROOT, get_settings


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _as_utc(value: datetime | None) -> datetime | None:
    """SQLite returns naive datetimes; attach UTC before any comparison."""
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


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
    google = "google"
    zip_recruiter = "zip_recruiter"
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


class Outcome(StrEnum):
    """Post-submission result. Stored as VARCHAR, validated in Python."""

    ghosted = "ghosted"
    screening = "screening"
    interview = "interview"
    rejected = "rejected"
    offer = "offer"


# Nullable columns added after the original jobs table. init_db alters old
# SQLite files and Neon in place; create_all does not.
_JOB_COLUMN_DDL: dict[str, dict[str, str]] = {
    "sqlite": {
        "cover_letter": "TEXT",
        "outcome": "VARCHAR(32)",
        "outcome_at": "DATETIME",
        "outcome_message_id": "INTEGER",
        "embedding": "TEXT",
        "vector_score": "REAL",
        "vector_profile_hash": "VARCHAR(64)",
        "vector_decision": "VARCHAR(16)",
        "embedding_model": "VARCHAR(64)",
        "discovery_family": "VARCHAR(64)",
        "discovery_bucket": "VARCHAR(64)",
        "discovery_query": "VARCHAR(256)",
        "jd_status": "VARCHAR(16)",
        "jd_char_count": "INTEGER",
        "jd_truncated": "INTEGER",
        "jd_extraction_path": "VARCHAR(32)",
        "role_family": "VARCHAR(64)",
        "role_subfamily": "VARCHAR(64)",
        "role_confidence": "VARCHAR(16)",
        "role_evidence": "JSON",
        "role_classifier_version": "VARCHAR(32)",
        "role_content_hash": "VARCHAR(64)",
        "role_family_weight": "INTEGER",
        "role_family_weight_version": "VARCHAR(32)",
        "company_intelligence_id": "INTEGER",
        "eligibility_state": "VARCHAR(32)",
        "eligibility_reasons": "JSON",
        "eligibility_evidence": "JSON",
        "eligibility_dimensions": "JSON",
        "eligibility_version": "VARCHAR(32)",
        "eligibility_content_hash": "VARCHAR(64)",
        "eligibility_profile_hash": "VARCHAR(64)",
        "fit_confidence": "VARCHAR(16)",
        "fit_strengths": "JSON",
        "fit_gaps": "JSON",
        "fit_evidence": "JSON",
        "fit_dimensions": "JSON",
        "fit_version": "VARCHAR(32)",
        "fit_content_hash": "VARCHAR(64)",
        "fit_profile_hash": "VARCHAR(64)",
    },
    "postgresql": {
        "cover_letter": "TEXT",
        "outcome": "VARCHAR(32)",
        "outcome_at": "TIMESTAMP WITH TIME ZONE",
        "outcome_message_id": "INTEGER",
        "embedding": "JSON",
        "vector_score": "DOUBLE PRECISION",
        "vector_profile_hash": "VARCHAR(64)",
        "vector_decision": "VARCHAR(16)",
        "embedding_model": "VARCHAR(64)",
        "discovery_family": "VARCHAR(64)",
        "discovery_bucket": "VARCHAR(64)",
        "discovery_query": "VARCHAR(256)",
        "jd_status": "VARCHAR(16)",
        "jd_char_count": "INTEGER",
        "jd_truncated": "BOOLEAN",
        "jd_extraction_path": "VARCHAR(32)",
        "role_family": "VARCHAR(64)",
        "role_subfamily": "VARCHAR(64)",
        "role_confidence": "VARCHAR(16)",
        "role_evidence": "JSON",
        "role_classifier_version": "VARCHAR(32)",
        "role_content_hash": "VARCHAR(64)",
        "role_family_weight": "INTEGER",
        "role_family_weight_version": "VARCHAR(32)",
        "company_intelligence_id": "INTEGER",
        "eligibility_state": "VARCHAR(32)",
        "eligibility_reasons": "JSON",
        "eligibility_evidence": "JSON",
        "eligibility_dimensions": "JSON",
        "eligibility_version": "VARCHAR(32)",
        "eligibility_content_hash": "VARCHAR(64)",
        "eligibility_profile_hash": "VARCHAR(64)",
        "fit_confidence": "VARCHAR(16)",
        "fit_strengths": "JSON",
        "fit_gaps": "JSON",
        "fit_evidence": "JSON",
        "fit_dimensions": "JSON",
        "fit_version": "VARCHAR(32)",
        "fit_content_hash": "VARCHAR(64)",
        "fit_profile_hash": "VARCHAR(64)",
    },
}


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


class CompanyIntelligence(SQLModel, table=True):
    """Factual employer record shared by jobs. Not a score and not a preference."""

    __tablename__: ClassVar[str] = "company_intelligence"

    id: int | None = Field(default=None, primary_key=True)
    lookup_key: str = Field(max_length=512, unique=True, index=True)
    company_name: str = Field(max_length=512)
    canonical_name: str = Field(max_length=512)
    website: str | None = Field(default=None, max_length=2048)
    industry: str | None = Field(default=None, max_length=128)
    company_type: str | None = Field(default=None, max_length=64)
    public_private: str | None = Field(default=None, max_length=16)
    headquarters: str | None = Field(default=None, max_length=256)
    employee_range: str | None = Field(default=None, max_length=128)
    founded_year: int | None = Field(default=None)
    parent_company: str | None = Field(default=None, max_length=512)
    business_description: str | None = Field(default=None)
    sources: list[dict[str, Any]] = Field(
        default_factory=list,
        sa_column=Column(JSON, nullable=False),
    )
    confidence: str | None = Field(default=None, max_length=16)
    status: str = Field(default="unresolved", max_length=16, index=True)
    intelligence_version: str = Field(default="phase8-v1", max_length=32)
    retrieved_at: datetime | None = _tz_datetime(nullable=True)
    created_at: datetime = _tz_datetime(default_factory=_utcnow)
    updated_at: datetime = _tz_datetime(default_factory=_utcnow)


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
    cover_letter: str | None = Field(default=None)
    scored_at: datetime | None = _tz_datetime(nullable=True)
    # JD embedding and the cosine it produced against one profile text.
    # vector_decision is "pass" or "reject"; only rejects are reopened.
    embedding: list[float] | None = Field(default=None, sa_column=Column(JSON, nullable=True))
    vector_score: float | None = Field(default=None)
    vector_profile_hash: str | None = Field(default=None, max_length=64)
    vector_decision: str | None = Field(default=None, max_length=16)
    embedding_model: str | None = Field(default=None, max_length=64)
    # How the posting entered discovery. Independent of the fit score.
    discovery_family: str | None = Field(default=None, max_length=64)
    discovery_bucket: str | None = Field(default=None, max_length=64)
    discovery_query: str | None = Field(default=None, max_length=256)
    # Description extraction quality. Separate from discovery provenance and fit.
    jd_status: str | None = Field(default=None, max_length=16)
    jd_char_count: int | None = Field(default=None)
    jd_truncated: bool | None = Field(default=None)
    jd_extraction_path: str | None = Field(default=None, max_length=32)
    # What the posting is. Not a candidate-fit score and not the discovery label.
    role_family: str | None = Field(default=None, max_length=64)
    role_subfamily: str | None = Field(default=None, max_length=64)
    role_confidence: str | None = Field(default=None, max_length=16)
    role_evidence: list[str] | None = Field(default=None, sa_column=Column(JSON, nullable=True))
    role_classifier_version: str | None = Field(default=None, max_length=32)
    role_content_hash: str | None = Field(default=None, max_length=64)
    # Portfolio importance of role_family. Not a fit score and not search capacity.
    role_family_weight: int | None = Field(default=None)
    role_family_weight_version: str | None = Field(default=None, max_length=32)
    # Factual employer record. Does not change fit, weight, tier, or status.
    company_intelligence_id: int | None = Field(
        default=None,
        foreign_key="company_intelligence.id",
        index=True,
    )
    # Visa and eligibility. Not a fit score and not a rank.
    eligibility_state: str | None = Field(default=None, max_length=32)
    eligibility_reasons: list[str] | None = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    eligibility_evidence: list[str] | None = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    eligibility_dimensions: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    eligibility_version: str | None = Field(default=None, max_length=32)
    eligibility_content_hash: str | None = Field(default=None, max_length=64)
    eligibility_profile_hash: str | None = Field(default=None, max_length=64)
    # Candidate-to-JD fit. `score` stays the compatibility value when fit is available.
    fit_confidence: str | None = Field(default=None, max_length=16)
    fit_strengths: list[str] | None = Field(default=None, sa_column=Column(JSON, nullable=True))
    fit_gaps: list[str] | None = Field(default=None, sa_column=Column(JSON, nullable=True))
    fit_evidence: list[str] | None = Field(default=None, sa_column=Column(JSON, nullable=True))
    fit_dimensions: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
    )
    fit_version: str | None = Field(default=None, max_length=32)
    fit_content_hash: str | None = Field(default=None, max_length=64)
    fit_profile_hash: str | None = Field(default=None, max_length=64)

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
    # Post-submit label. outcome_message_id: NULL = not sent, 0 = send in
    # progress, positive = Telegram message id. Kept off decided_at so a
    # label tap does not reset the company cooldown window.
    outcome: str | None = Field(default=None, max_length=32)
    outcome_at: datetime | None = _tz_datetime(nullable=True)
    outcome_message_id: int | None = Field(default=None)
    last_error: str | None = Field(default=None)
    alerted_at: datetime | None = _tz_datetime(nullable=True)
    prep_pack_sent_at: datetime | None = _tz_datetime(nullable=True)
    created_at: datetime = _tz_datetime(default_factory=_utcnow)
    updated_at: datetime = _tz_datetime(default_factory=_utcnow)


class PlatformPacing(SQLModel, table=True):
    """Gap between apply sessions for one platform. The runner uses ``workday``."""

    __tablename__: ClassVar[str] = "platform_pacing"

    platform: str = Field(primary_key=True, max_length=64)
    multiplier: int = Field(default=1, ge=1)
    clean_streak: int = Field(default=0, ge=0)
    blocked_until: datetime | None = _tz_datetime(nullable=True)
    next_eligible_at: datetime | None = _tz_datetime(nullable=True)
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
        await _ensure_job_columns(conn)


def _dialect_name(conn: Any) -> str:
    dialect = getattr(conn, "dialect", None)
    name = getattr(dialect, "name", None)
    if isinstance(name, str) and name:
        return name
    sync = getattr(conn, "sync_connection", None)
    if sync is not None:
        return str(sync.dialect.name)
    raise RuntimeError("cannot determine database dialect")


async def _job_column_names(conn: Any) -> set[str]:
    """Column names on jobs, or empty when the table does not exist yet."""
    dialect = _dialect_name(conn)
    if dialect == "sqlite":
        rows = (await conn.execute(text("PRAGMA table_info(jobs)"))).fetchall()
        return {str(row[1]) for row in rows}
    rows = (
        await conn.execute(
            text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = 'jobs' AND table_schema = current_schema()"
            )
        )
    ).fetchall()
    return {str(row[0]) for row in rows}


async def _ensure_job_columns(conn: Any) -> None:
    """Add Phase 2 columns to an existing jobs table. No-op when already present."""
    existing = await _job_column_names(conn)
    if not existing:
        return
    dialect = _dialect_name(conn)
    ddl = _JOB_COLUMN_DDL.get(dialect, _JOB_COLUMN_DDL["postgresql"])
    for name, col_type in ddl.items():
        if name in existing:
            continue
        await conn.execute(text(f"ALTER TABLE jobs ADD COLUMN {name} {col_type}"))


# Scored-but-not-yet-acted-on states, safe to rewind when the JD text changes.
_RESCORABLE_STATUSES = frozenset({Status.scored, Status.staged})


def _incoming_description_unusable(job: Job) -> bool:
    """Missing or suspiciously short text. A real rewrite is still usable."""
    if job.jd_status in {"missing", "suspicious"}:
        return True
    if job.jd_status is None and not (job.description_clean or "").strip():
        return True
    return False


def _stored_description_usable(job: Job) -> bool:
    if job.jd_status in {"present", "truncated"}:
        return True
    if job.jd_status is None:
        return len((job.description_clean or "").strip()) >= 80
    return False


def _stamp_role_family_weight(job: Job) -> None:
    """Set the portfolio weight from the classified family. Fit and status stay put."""
    from scorer.role_weights import ROLE_WEIGHT_VERSION, get_role_family_weight

    job.role_family_weight = get_role_family_weight(job.role_family)
    job.role_family_weight_version = ROLE_WEIGHT_VERSION


def _role_classification_current(job: Job) -> bool:
    from scorer.role_classify import classification_is_current

    return classification_is_current(
        role_family=job.role_family,
        role_content_hash=job.role_content_hash,
        role_classifier_version=job.role_classifier_version,
        content_hash=job.content_hash,
    )


def _keep_stored_description(existing: Job, incoming: Job) -> bool:
    """Do not replace a usable JD with an empty or too-short refetch."""
    return _incoming_description_unusable(incoming) and _stored_description_usable(existing)


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
        _stamp_role_family_weight(job)
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
    keep_existing_jd = _keep_stored_description(existing, job)
    if keep_existing_jd:
        content_changed = False
    else:
        if job.description_clean is not None:
            existing.description_clean = job.description_clean
        if job.content_hash is not None:
            existing.content_hash = job.content_hash
        if job.jd_status is not None:
            existing.jd_status = job.jd_status
        if job.jd_char_count is not None:
            existing.jd_char_count = job.jd_char_count
        if job.jd_truncated is not None:
            existing.jd_truncated = job.jd_truncated
        if job.jd_extraction_path is not None:
            existing.jd_extraction_path = job.jd_extraction_path
    if job.tenant is not None:
        existing.tenant = job.tenant
    if job.posted_at is not None:
        existing.posted_at = job.posted_at
    # First discovery provenance stays. A later hit may fill a blank field only.
    if job.discovery_family and not existing.discovery_family:
        existing.discovery_family = job.discovery_family
    if job.discovery_bucket and not existing.discovery_bucket:
        existing.discovery_bucket = job.discovery_bucket
    if job.discovery_query and not existing.discovery_query:
        existing.discovery_query = job.discovery_query
    if content_changed:
        existing.embedding = None
        existing.vector_score = None
        existing.vector_profile_hash = None
        existing.vector_decision = None
        existing.embedding_model = None
        existing.role_family = None
        existing.role_subfamily = None
        existing.role_confidence = None
        existing.role_evidence = None
        existing.role_classifier_version = None
        existing.role_content_hash = None
        existing.fit_confidence = None
        existing.fit_strengths = None
        existing.fit_gaps = None
        existing.fit_evidence = None
        existing.fit_dimensions = None
        existing.fit_version = None
        existing.fit_content_hash = None
        existing.fit_profile_hash = None
        existing.eligibility_state = None
        existing.eligibility_reasons = None
        existing.eligibility_evidence = None
        existing.eligibility_dimensions = None
        existing.eligibility_version = None
        existing.eligibility_content_hash = None
        existing.eligibility_profile_hash = None
    if job.role_family is not None and (
        content_changed
        or not _role_classification_current(existing)
    ):
        existing.role_family = job.role_family
        existing.role_subfamily = job.role_subfamily
        existing.role_confidence = job.role_confidence
        existing.role_evidence = job.role_evidence
        existing.role_classifier_version = job.role_classifier_version
        existing.role_content_hash = job.role_content_hash or existing.content_hash
    _stamp_role_family_weight(existing)
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
        existing.cover_letter = None
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
    """manual_review jobs that have not yet been alerted on Telegram.

    Scoring failures stay in the database and are not sent as per-job alerts.
    """
    statement = (
        select(Job)
        .where(
            col(Job.status) == Status.manual_review,
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
    """Staged non-Workday (manual-apply) jobs not yet in a prep pack (score desc)."""
    statement = (
        select(Job)
        .where(
            col(Job.status) == Status.staged,
            col(Job.source).in_(  # type: ignore[union-attr]
                [Source.linkedin, Source.indeed, Source.google, Source.zip_recruiter]
            ),
            col(Job.prep_pack_sent_at).is_(None),  # type: ignore[union-attr]
        )
        .order_by(col(Job.score).desc(), col(Job.id))
    )
    if limit is not None:
        statement = statement.limit(limit)
    result = await session.exec(statement)
    return list(result.all())


def _company_name(row: Any) -> str | None:
    """Unwrap a single-column select row into a company string."""
    value = row[0] if isinstance(row, tuple) else row
    if isinstance(value, str) and value.strip():
        return value
    return None


async def claim_outcome_prompt(session: AsyncSession, job_id: int) -> bool:
    """Mark a submitted job as 'send in progress'. True only for the winner."""
    statement = (
        update(Job)
        .where(col(Job.id) == job_id)
        .where(col(Job.status) == Status.submitted)
        .where(col(Job.outcome_message_id).is_(None))
        .values(outcome_message_id=0)
    )
    result = await session.exec(statement)  # type: ignore[call-overload]
    return int(result.rowcount or 0) > 0


async def release_outcome_prompt(session: AsyncSession, job_id: int) -> None:
    """Clear an in-progress send so the next run can retry."""
    statement = (
        update(Job)
        .where(col(Job.id) == job_id)
        .where(col(Job.outcome_message_id) == 0)
        .values(outcome_message_id=None)
    )
    await session.exec(statement)  # type: ignore[call-overload]


async def finish_outcome_prompt(
    session: AsyncSession,
    job_id: int,
    message_id: int,
) -> bool:
    """Store the Telegram message id. Only replaces the in-progress sentinel."""
    if message_id <= 0:
        return False
    statement = (
        update(Job)
        .where(col(Job.id) == job_id)
        .where(col(Job.outcome_message_id) == 0)
        .values(outcome_message_id=message_id)
    )
    result = await session.exec(statement)  # type: ignore[call-overload]
    return int(result.rowcount or 0) > 0


async def get_jobs_needing_outcome_prompt(
    session: AsyncSession,
    limit: int | None = None,
) -> list[Job]:
    """Submitted jobs that have not been sent an outcome keyboard."""
    statement = (
        select(Job)
        .where(col(Job.status) == Status.submitted)
        .where(col(Job.outcome_message_id).is_(None))
        .order_by(col(Job.id))
    )
    if limit is not None:
        statement = statement.limit(limit)
    result = await session.exec(statement)
    return list(result.all())


async def get_recently_applied_companies(
    session: AsyncSession,
    *,
    cooldown_days: int = 30,
) -> set[str]:
    """Companies we submitted to within the cooldown window.

    Statuses included: submitted, pending_review, manual_review.
    ``ignored`` is excluded — the human rejected the job, so the company
    slot should stay open for future roles. Rows without ``decided_at``
    are excluded so an in-flight card does not block the company forever.
    """
    cutoff = datetime.now(UTC) - timedelta(days=cooldown_days)
    statement = select(Job.company).where(
        col(Job.status).in_(  # type: ignore[union-attr]
            [Status.submitted, Status.pending_review, Status.manual_review]
        ),
        col(Job.decided_at) >= cutoff,  # type: ignore[operator]
        col(Job.decided_at).is_not(None),  # type: ignore[union-attr]
    )
    result = await session.exec(statement)
    return {name for row in result.all() if (name := _company_name(row))}


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

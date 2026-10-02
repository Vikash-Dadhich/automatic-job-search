"""Record what happened to an application. This does not score or rank jobs."""

from __future__ import annotations

from datetime import datetime

import structlog
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.apply_url import is_automateable_apply_url
from core.db import (
    Application,
    ApplicationEvent,
    ApplicationEventType,
    ApplicationMethod,
    ApplicationState,
    Job,
    Outcome,
    Source,
    Status,
    _as_utc,
    _utcnow,
    get_application_events,
    get_application_for_job,
    get_job_by_id,
    session_scope,
)

log = structlog.get_logger(__name__)

TRACKER_VERSION = "phase15-v1"
_OUTCOMES = {item.value for item in Outcome}


def application_method(job: Job) -> str:
    """Workday when the posting is a Workday application. Otherwise manual."""
    if job.source == Source.workday or is_automateable_apply_url(job.url or ""):
        return ApplicationMethod.workday.value
    return ApplicationMethod.manual.value


async def _event_exists(session: AsyncSession, application_id: int, event_type: str) -> bool:
    statement = select(ApplicationEvent).where(
        col(ApplicationEvent.application_id) == application_id,
        col(ApplicationEvent.event_type) == event_type,
    )
    result = await session.exec(statement)
    return result.first() is not None


async def _add_event(
    session: AsyncSession,
    application: Application,
    event_type: str,
    occurred_at: datetime,
    source: str,
    note: str | None,
) -> bool:
    if application.id is None:
        return False
    if await _event_exists(session, application.id, event_type):
        return False
    session.add(
        ApplicationEvent(
            application_id=application.id,
            event_type=event_type,
            occurred_at=occurred_at,
            source=source,
            note=(note or "")[:500] or None,
        )
    )
    return True


async def _get_or_create(
    session: AsyncSession,
    job: Job,
    occurred_at: datetime,
    source: str,
    *,
    record_started: bool,
) -> Application:
    assert job.id is not None
    existing = await get_application_for_job(session, job.id)
    if existing is not None:
        return existing
    created = Application(
        job_id=job.id,
        state=ApplicationState.in_progress.value,
        method=application_method(job),
        started_at=occurred_at,
        last_status_at=occurred_at,
        tracker_version=TRACKER_VERSION,
    )
    session.add(created)
    await session.flush()
    if record_started:
        await _add_event(
            session,
            created,
            ApplicationEventType.started.value,
            occurred_at,
            source,
            None,
        )
    return created


def _stamp(value: datetime | None) -> datetime:
    return _as_utc(value) or _utcnow()


async def record_prefill(job_id: int, *, occurred_at: datetime, source: str = "workday") -> None:
    """A Workday pre-fill started. This is not a submission."""
    moment = _stamp(occurred_at)
    async with session_scope() as session:
        job = await get_job_by_id(session, job_id)
        if job is None:
            return
        app = await _get_or_create(session, job, moment, source, record_started=True)
        if app.state == ApplicationState.submitted.value or app.submitted_at is not None:
            return
        if app.state != ApplicationState.in_progress.value:
            return
        session.add(app)


async def record_submitted(
    job_id: int,
    *,
    occurred_at: datetime,
    source: str,
    record_started: bool = True,
) -> None:
    """Record a real submission. The first submitted_at is kept."""
    moment = _stamp(occurred_at)
    async with session_scope() as session:
        job = await get_job_by_id(session, job_id)
        if job is None:
            return
        app = await _get_or_create(
            session,
            job,
            moment,
            source,
            record_started=record_started,
        )
        changed = False
        if app.submitted_at is None:
            app.submitted_at = moment
            changed = True
        if app.state != ApplicationState.submitted.value:
            app.state = ApplicationState.submitted.value
            app.last_status_at = moment
            changed = True
        added = await _add_event(
            session,
            app,
            ApplicationEventType.submitted.value,
            moment,
            source,
            None,
        )
        if changed or added:
            app.updated_at = _utcnow()
            session.add(app)


async def record_manual_review(
    job_id: int,
    *,
    occurred_at: datetime,
    source: str,
    note: str | None = None,
) -> None:
    """Hand-off or a blocked submit. Does not mark the application submitted."""
    moment = _stamp(occurred_at)
    async with session_scope() as session:
        job = await get_job_by_id(session, job_id)
        if job is None:
            return
        app = await _get_or_create(session, job, moment, source, record_started=True)
        if app.submitted_at is not None or app.state == ApplicationState.submitted.value:
            return
        changed = app.state != ApplicationState.manual_review.value
        app.state = ApplicationState.manual_review.value
        if changed:
            app.last_status_at = moment
        added = await _add_event(
            session,
            app,
            ApplicationEventType.manual_review.value,
            moment,
            source,
            note,
        )
        if changed or added:
            app.updated_at = _utcnow()
            session.add(app)


async def record_withdrawn(job_id: int, *, occurred_at: datetime, source: str) -> None:
    """Abandon an attempt that already exists. A discard with no attempt is ignored."""
    moment = _stamp(occurred_at)
    async with session_scope() as session:
        job = await get_job_by_id(session, job_id)
        if job is None or job.id is None:
            return
        app = await get_application_for_job(session, job.id)
        if app is None or app.state == ApplicationState.submitted.value:
            return
        app.state = ApplicationState.withdrawn.value
        app.last_status_at = moment
        await _add_event(
            session,
            app,
            ApplicationEventType.withdrawn.value,
            moment,
            source,
            None,
        )
        app.updated_at = _utcnow()
        session.add(app)


async def record_outcome(
    job_id: int,
    outcome: Outcome,
    *,
    occurred_at: datetime,
    source: str,
) -> None:
    """Copy a post-submission outcome onto the application and keep the prior event."""
    if outcome.value not in _OUTCOMES:
        return
    moment = _stamp(occurred_at)
    async with session_scope() as session:
        job = await get_job_by_id(session, job_id)
        if job is None or job.status != Status.submitted:
            return
        submitted_at = _stamp(job.decided_at) if job.decided_at is not None else moment
        app = await _get_or_create(
            session,
            job,
            submitted_at,
            source,
            record_started=False,
        )
        if app.submitted_at is None:
            app.submitted_at = submitted_at
        if app.state != ApplicationState.submitted.value:
            app.state = ApplicationState.submitted.value
        await _add_event(
            session,
            app,
            ApplicationEventType.submitted.value,
            app.submitted_at,
            source,
            None,
        )
        if app.outcome == outcome.value:
            session.add(app)
            return
        app.outcome = outcome.value
        app.outcome_at = moment
        app.last_status_at = moment
        app.updated_at = _utcnow()
        await _add_event(session, app, outcome.value, moment, source, None)
        session.add(app)


async def backfill_submitted_applications() -> int:
    """Create one application for each submitted job that does not have one.

    Uses decided_at when it is present. Does not invent a separate start event.
    Copies an outcome only when the job already has one.
    """
    async with session_scope() as session:
        result = await session.exec(select(Job).where(col(Job.status) == Status.submitted))
        rows = list(result.all())
    created = 0
    for job in rows:
        if job.id is None:
            continue
        async with session_scope() as session:
            if await get_application_for_job(session, job.id) is not None:
                continue
        moment = _stamp(job.decided_at or job.updated_at)
        await record_submitted(
            job.id,
            occurred_at=moment,
            source="backfill",
            record_started=False,
        )
        if job.outcome in _OUTCOMES:
            when = _stamp(job.outcome_at or job.decided_at or job.updated_at)
            await record_outcome(
                job.id,
                Outcome(job.outcome),
                occurred_at=when,
                source="backfill",
            )
        created += 1
    if created:
        log.info("application_backfill", created=created)
    return created


async def application_history(job_id: int) -> list[ApplicationEvent]:
    async with session_scope() as session:
        app = await get_application_for_job(session, job_id)
        if app is None or app.id is None:
            return []
        return await get_application_events(session, app.id)

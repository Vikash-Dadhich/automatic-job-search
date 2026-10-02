"""Feedback rates come from submitted applications and do not change scores."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from core.db import (
    Application,
    ApplicationEvent,
    Job,
    Source,
    Status,
    get_application_events,
    get_job_by_id,
    session_scope,
    upsert_job,
)
from scorer.feedback import (
    INSUFFICIENT,
    SUFFICIENT,
    FeedbackCase,
    build_feedback,
    load_feedback_cases,
    load_feedback_config,
    load_persisted_feedback,
    persist_feedback,
    shrink_rate,
)
from scorer.role_weights import get_role_family_weight

JAN1 = datetime(2026, 1, 1, tzinfo=UTC)
JAN15 = datetime(2026, 1, 15, tzinfo=UTC)
JAN20 = datetime(2026, 1, 20, tzinfo=UTC)
FEB1 = datetime(2026, 2, 1, tzinfo=UTC)
MAR1 = datetime(2026, 3, 1, tzinfo=UTC)


def _config(**overrides: object) -> dict[str, object]:
    loaded = load_feedback_config()
    block = dict(loaded["feedback"])
    block.update(overrides)
    return {"version": loaded["version"], "feedback": block}


def _case(
    application_id: int,
    submitted_at: datetime,
    events: list[tuple[str, datetime]],
    **kwargs: object,
) -> FeedbackCase:
    data: dict[str, object] = {
        "application_id": application_id,
        "submitted_at": submitted_at,
        "fit_score": 80,
        "priority_score": 80,
        "role_family": "PRODUCT_MANAGEMENT",
        "role_subfamily": "PM_CORE",
        "eligibility_state": "LIKELY_ELIGIBLE",
        "method": "workday",
        "source": "workday",
        "events": tuple(events),
    }
    data.update(kwargs)
    return FeedbackCase(**data)  # type: ignore[arg-type]


def _signal(report: object, dimension: str, segment: str) -> object:
    matches = [
        item
        for item in report.signals  # type: ignore[attr-defined]
        if item.dimension == dimension and item.segment == segment
    ]
    assert len(matches) == 1
    return matches[0]


def test_feedback_config_keeps_priority_integration_off() -> None:
    loaded = load_feedback_config()
    assert loaded["version"] == "phase16-v1"
    assert loaded["feedback"]["priority_integration"] is False
    assert loaded["feedback"]["minimum_overall"] == 20
    assert loaded["feedback"]["minimum_segment"] == 10
    assert loaded["feedback"]["max_adjustment"] == 5
    assert get_role_family_weight("PRODUCT_MANAGEMENT") == 40


def test_funnel_does_not_treat_unknown_as_rejection() -> None:
    cases = [
        _case(1, JAN1, [("screening", JAN1)]),
        _case(2, JAN1, [("interview", JAN1)]),
        _case(3, JAN1, [("offer", JAN1)]),
        _case(4, JAN1, [("rejected", JAN1)]),
        _case(5, JAN1, [("ghosted", JAN1)]),
        _case(6, JAN1, []),
    ]
    report = build_feedback(cases, as_of=MAR1, config=_config(minimum_overall=1))
    overall = _signal(report, "overall", "all")
    assert overall.sample_size == 6  # type: ignore[attr-defined]
    assert overall.known_outcomes == 5  # type: ignore[attr-defined]
    assert overall.rates["known_outcome_rate"] == round(5 / 6, 6)  # type: ignore[attr-defined]
    assert overall.rates["rejected_rate"] == round(1 / 6, 6)  # type: ignore[attr-defined]
    assert overall.rates["ghosted_rate"] == round(1 / 6, 6)  # type: ignore[attr-defined]
    assert overall.rates["offer_rate"] == round(1 / 6, 6)  # type: ignore[attr-defined]
    assert overall.rates["strong_positive_rate"] == round(2 / 6, 6)  # type: ignore[attr-defined]
    assert overall.rates["early_positive_rate"] == round(3 / 6, 6)  # type: ignore[attr-defined]
    assert "company" not in {item.dimension for item in report.signals}


def test_cutoff_hides_future_submissions_and_outcomes() -> None:
    early = _case(1, JAN1, [("interview", FEB1)])
    later = _case(2, JAN20, [("offer", FEB1)])
    settings = _config(minimum_overall=1)
    before = build_feedback([early, later], as_of=JAN15, config=settings)
    after = build_feedback([early, later], as_of=MAR1, config=settings)
    assert before.total_applications == 1
    assert _signal(before, "overall", "all").known_outcomes == 0  # type: ignore[attr-defined]
    assert _signal(before, "overall", "all").rates["interview_rate"] == 0.0  # type: ignore[attr-defined]
    assert after.total_applications == 2
    assert _signal(after, "overall", "all").rates["interview_rate"] == 0.5  # type: ignore[attr-defined]
    assert build_feedback([early, later], as_of=JAN15, config=settings) == before


def test_bands_families_and_sparse_subfamily() -> None:
    cases = [
        _case(1, JAN1, [], fit_score=49, priority_score=64, role_family="CONSULTING"),
        _case(2, JAN1, [], fit_score=85, priority_score=75, role_family=None, role_subfamily=None),
        _case(3, JAN1, [], fit_score=70, priority_score=70, role_family="UNKNOWN"),
        _case(
            4,
            JAN1,
            [("offer", JAN1)],
            fit_score=60,
            priority_score=10,
            eligibility_state="CLEARLY_INELIGIBLE",
            method="manual",
            source="linkedin",
            role_subfamily=None,
        ),
    ]
    report = build_feedback(
        cases,
        as_of=MAR1,
        config=_config(minimum_segment=1, minimum_subfamily=20),
    )
    assert _signal(report, "fit_band", "0-49").sample_size == 1  # type: ignore[attr-defined]
    assert _signal(report, "fit_band", "85-100").sample_size == 1  # type: ignore[attr-defined]
    assert _signal(report, "priority_band", "50-64").sample_size == 1  # type: ignore[attr-defined]
    assert _signal(report, "priority_band", "75-84").sample_size == 1  # type: ignore[attr-defined]
    assert _signal(report, "role_family", "UNKNOWN").sample_size == 2  # type: ignore[attr-defined]
    assert _signal(report, "role_family", "CONSULTING").sample_size == 1  # type: ignore[attr-defined]
    sparse = _signal(report, "role_subfamily", "PM_CORE")
    assert sparse.sample_size == 2  # type: ignore[attr-defined]
    assert sparse.evidence_status == INSUFFICIENT  # type: ignore[attr-defined]
    assert sparse.adjustment == 0  # type: ignore[attr-defined]
    assert _signal(report, "eligibility", "CLEARLY_INELIGIBLE").sample_size == 1  # type: ignore[attr-defined]
    assert _signal(report, "method", "manual").sample_size == 1  # type: ignore[attr-defined]
    assert _signal(report, "source", "linkedin").sample_size == 1  # type: ignore[attr-defined]
    assert get_role_family_weight("CONSULTING") == 40


def test_shrinkage_and_adjustment_bounds() -> None:
    assert shrink_rate(1.0, 10, 0.1, 20) == round((10 + 2) / 30, 6)
    large = shrink_rate(1.0, 1000, 0.1, 20)
    assert large > shrink_rate(1.0, 10, 0.1, 20)
    assert abs(large - 1.0) < abs(shrink_rate(1.0, 10, 0.1, 20) - 1.0)
    weak = [_case(index, JAN1, []) for index in range(4)]
    report = build_feedback(weak, as_of=MAR1, config=_config(minimum_segment=10))
    family = _signal(report, "role_family", "PRODUCT_MANAGEMENT")
    assert family.evidence_status == INSUFFICIENT  # type: ignore[attr-defined]
    assert family.adjustment == 0  # type: ignore[attr-defined]
    strong = [
        _case(index, JAN1, [("offer", JAN1)], role_family="CONSULTING") for index in range(30)
    ]
    baseline = [_case(1000 + index, JAN1, [], role_family="OTHER") for index in range(30)]
    bounded = build_feedback(
        strong + baseline,
        as_of=MAR1,
        config=_config(minimum_segment=10, minimum_overall=1, max_adjustment=5),
    )
    consulting = _signal(bounded, "role_family", "CONSULTING")
    assert consulting.evidence_status == SUFFICIENT  # type: ignore[attr-defined]
    assert consulting.adjustment == 5  # type: ignore[attr-defined]
    assert -5 <= consulting.adjustment <= 5  # type: ignore[attr-defined]


async def test_persisted_feedback_does_not_change_scores_or_history(db_ready: Path) -> None:
    del db_ready
    async with session_scope() as session:
        job = await upsert_job(
            session,
            Job(
                source=Source.linkedin,
                external_id="fb-1",
                title="Intern",
                company="Acme",
                url="https://jobs.example.com/fb-1",
                status=Status.submitted,
                score=82,
                priority_score=77,
                role_family="PRODUCT_MANAGEMENT",
                role_family_weight=40,
                eligibility_state="LIKELY_ELIGIBLE",
            ),
        )
        assert job.id is not None
        application = Application(
            job_id=job.id,
            state="submitted",
            method="manual",
            started_at=JAN1,
            submitted_at=JAN1,
            last_status_at=JAN1,
        )
        session.add(application)
        await session.flush()
        assert application.id is not None
        session.add(
            ApplicationEvent(
                application_id=application.id,
                event_type="interview",
                occurred_at=FEB1,
                source="test",
            )
        )
        other = await upsert_job(
            session,
            Job(
                source=Source.linkedin,
                external_id="fb-open",
                title="Intern",
                company="Other",
                url="https://jobs.example.com/fb-open",
                status=Status.pending_review,
            ),
        )
        assert other.id is not None
        session.add(
            Application(
                job_id=other.id,
                state="in_progress",
                method="manual",
                started_at=JAN1,
                submitted_at=None,
                last_status_at=JAN1,
            )
        )
    cases = await load_feedback_cases()
    assert len(cases) == 1
    hidden = build_feedback(cases, as_of=JAN15, config=_config(minimum_overall=1))
    visible = build_feedback(cases, as_of=MAR1, config=_config(minimum_overall=1))
    assert _signal(hidden, "overall", "all").rates["interview_rate"] == 0.0  # type: ignore[attr-defined]
    assert _signal(visible, "overall", "all").rates["interview_rate"] == 1.0  # type: ignore[attr-defined]
    first_id = await persist_feedback(visible)
    second = build_feedback(cases, as_of=MAR1, config=_config(minimum_overall=1))
    assert second.signals == visible.signals
    second_id = await persist_feedback(second)
    run, signals = await load_persisted_feedback(first_id)
    assert run is not None
    assert run.version == "phase16-v1"
    assert run.total_applications == 1
    assert signals[0].adjustment == visible.signals[0].adjustment
    assert second_id != first_id
    async with session_scope() as session:
        saved = await get_job_by_id(session, job.id)
        assert saved is not None
        assert saved.score == 82
        assert saved.priority_score == 77
        assert saved.role_family_weight == 40
        assert saved.eligibility_state == "LIKELY_ELIGIBLE"
        history = await get_application_events(session, application.id)
        assert len(history) == 1

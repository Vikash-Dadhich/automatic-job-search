"""Temporal checks of feedback. They do not change scores or application history."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
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
from scorer.calibration import (
    INSUFFICIENT_HISTORY,
    CalibrationMetricRow,
    CalibrationReport,
    brier_score,
    build_calibration,
    load_calibration_config,
    load_persisted_calibration,
    persist_calibration,
    run_calibration,
)
from scorer.feedback import FeedbackCase, load_feedback_config

DAY = datetime(2026, 1, 1, tzinfo=UTC)


def _feedback(**overrides: object) -> dict[str, object]:
    loaded = load_feedback_config()
    block = dict(loaded["feedback"])
    block.update(overrides)
    return {"version": loaded["version"], "feedback": block}


def _calibration(**overrides: object) -> dict[str, object]:
    loaded = load_calibration_config()
    block = dict(loaded["calibration"])
    block.update(overrides)
    return {"version": loaded["version"], "calibration": block}


def _case(
    application_id: int,
    day: int,
    events: list[tuple[str, int]],
    **kwargs: object,
) -> FeedbackCase:
    submitted = DAY + timedelta(days=day)
    data: dict[str, object] = {
        "application_id": application_id,
        "submitted_at": submitted,
        "fit_score": 80,
        "priority_score": 80,
        "role_family": "PRODUCT_MANAGEMENT",
        "role_subfamily": "PM_CORE",
        "eligibility_state": "LIKELY_ELIGIBLE",
        "method": "workday",
        "source": "workday",
        "events": tuple((name, submitted + timedelta(days=offset)) for name, offset in events),
    }
    data.update(kwargs)
    return FeedbackCase(**data)  # type: ignore[arg-type]


def _rows(report: CalibrationReport, dimension: str, segment: str) -> list[CalibrationMetricRow]:
    return [
        item
        for item in report.metrics
        if item.dimension == dimension and item.segment == segment
    ]


def test_calibration_defaults_stay_off_the_production_path() -> None:
    loaded = load_calibration_config()
    assert loaded["version"] == "phase17-v1"
    assert loaded["calibration"]["hypothetical_adjustment"] is False
    assert loaded["calibration"]["evaluation_maturity_days"] == 45
    assert load_feedback_config()["feedback"]["priority_integration"] is False


def test_brier_score_is_mean_squared_error() -> None:
    assert brier_score([(1.0, 1), (0.0, 0)]) == 0.0
    assert brier_score([(0.5, 1), (0.5, 0)]) == 0.25
    assert brier_score([]) is None


def test_future_outcomes_and_unknowns_do_not_count_as_failures() -> None:
    training = [
        _case(index, 0, [("rejected", 0)], role_family="OTHER", role_subfamily=None)
        for index in range(1, 4)
    ]
    leaked = _case(4, 0, [("interview", 40)], role_family="OTHER", role_subfamily=None)
    unknown = _case(5, 20, [("rejected", 0)], role_family="OTHER", role_subfamily=None)
    hit = _case(6, 21, [("interview", 0), ("offer", 1), ("screening", 0)])
    silent = _case(7, 22, [], role_family="PRODUCT_MANAGEMENT")
    settings = _calibration(
        fold_count=1,
        evaluation_maturity_days=0,
        minimum_training_applications=4,
        minimum_holdout_applications=1,
        minimum_holdout_segment=1,
    )
    learned = _feedback(
        minimum_overall=1,
        minimum_segment=1,
        minimum_subfamily=1,
        shrinkage_prior=0,
    )
    report = build_calibration(
        training + [leaked, unknown, hit, silent],
        config=settings,
        feedback_config=learned,
    )
    assert report.status == "ok"
    fold = report.folds[0]
    assert leaked.application_id in fold.training_ids
    assert hit.application_id in fold.holdout_ids
    assert unknown.application_id in fold.holdout_ids
    assert silent.application_id in fold.holdout_ids
    assert fold.matured_holdout_applications == 3
    assert fold.evaluated_applications == 2
    overall = _rows(report, "overall", "all")[0]
    assert overall.holdout_count == 2
    assert overall.holdout_positive_count == 1
    family = _rows(report, "role_family", "OTHER")[0]
    assert family.training_prediction == 0.0  # type: ignore[attr-defined]


def test_feedback_brier_beats_baseline_without_naming_a_winner() -> None:
    training = [
        _case(1, 0, [("offer", 0)]),
        _case(2, 0, [("offer", 0)]),
        _case(3, 0, [("rejected", 0)], role_family="OTHER", role_subfamily=None),
        _case(4, 0, [("rejected", 0)], role_family="OTHER", role_subfamily=None),
    ]
    holdout = [_case(5, 30, [("offer", 0)]), _case(6, 31, [("offer", 0)])]
    settings = _calibration(
        fold_count=1,
        evaluation_maturity_days=0,
        minimum_training_applications=4,
        minimum_holdout_applications=2,
        minimum_holdout_segment=1,
    )
    learned = _feedback(
        minimum_overall=1,
        minimum_segment=2,
        minimum_subfamily=2,
        shrinkage_prior=0,
    )
    report = build_calibration(training + holdout, config=settings, feedback_config=learned)
    overall = _rows(report, "role_family", "all")[0]
    assert overall.baseline_brier_score == 0.25  # type: ignore[attr-defined]
    assert overall.brier_score == 0.0  # type: ignore[attr-defined]
    assert overall.brier_delta == -0.25  # type: ignore[attr-defined]
    segment = _rows(report, "role_family", "PRODUCT_MANAGEMENT")[0]
    assert segment.training_prediction == 1.0  # type: ignore[attr-defined]
    assert segment.holdout_rate == 1.0  # type: ignore[attr-defined]
    assert segment.calibration_error == 0.0  # type: ignore[attr-defined]
    assert segment.evidence_status == "sufficient"  # type: ignore[attr-defined]
    assert build_calibration(training + holdout, config=settings, feedback_config=learned) == report


def test_immature_applications_and_sparse_segments_fall_back() -> None:
    training = [_case(index, 0, [("offer", 0)]) for index in range(1, 5)]
    fresh = _case(5, 1, [("rejected", 0)])
    settings = _calibration(
        fold_count=1,
        evaluation_maturity_days=45,
        minimum_training_applications=4,
        minimum_holdout_applications=1,
        minimum_holdout_segment=1,
    )
    learned = _feedback(minimum_overall=1, minimum_segment=10, shrinkage_prior=0)
    report = build_calibration(training + [fresh], config=settings, feedback_config=learned)
    assert report.folds[0].holdout_applications == 1
    assert report.folds[0].matured_holdout_applications == 0
    assert report.folds[0].evaluated_applications == 0


def test_folds_are_chronological_and_do_not_overlap() -> None:
    cases = [_case(index, index, [("rejected", 0)], role_subfamily=None) for index in range(1, 9)]
    settings = _calibration(
        fold_count=2,
        evaluation_maturity_days=0,
        minimum_training_applications=4,
        minimum_holdout_applications=2,
        minimum_holdout_segment=1,
    )
    learned = _feedback(minimum_overall=1, minimum_segment=1, shrinkage_prior=0)
    report = build_calibration(cases, config=settings, feedback_config=learned)
    assert len(report.folds) == 2
    first, second = report.folds
    assert set(first.holdout_ids).isdisjoint(first.training_ids)
    assert set(second.holdout_ids).isdisjoint(second.training_ids)
    assert second.training_applications > first.training_applications
    assert first.train_as_of < second.train_as_of
    assert set(first.holdout_ids).isdisjoint(second.holdout_ids)


def test_too_little_history_is_a_report_not_a_failure() -> None:
    report = build_calibration([_case(1, 0, []), _case(2, 1, [])])
    assert report.status == INSUFFICIENT_HISTORY
    assert report.metrics == ()
    assert report.available_applications == 2
    assert report.required_applications == 40


async def test_persisted_calibration_leaves_scores_and_events_unchanged(db_ready: Path) -> None:
    del db_ready
    async with session_scope() as session:
        job = await upsert_job(
            session,
            Job(
                source=Source.linkedin,
                external_id="cal-1",
                title="Intern",
                company="Acme",
                url="https://jobs.example.com/cal-1",
                status=Status.submitted,
                score=81,
                priority_score=76,
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
            started_at=DAY,
            submitted_at=DAY,
            last_status_at=DAY,
        )
        session.add(application)
        await session.flush()
        assert application.id is not None
        session.add(
            ApplicationEvent(
                application_id=application.id,
                event_type="offer",
                occurred_at=DAY,
                source="test",
            )
        )
    report = await run_calibration()
    assert report.status == INSUFFICIENT_HISTORY
    saved_id = await persist_calibration(report)
    again = await run_calibration()
    assert again == report
    loaded, metrics = await load_persisted_calibration(saved_id)
    assert loaded is not None
    assert loaded.version == "phase17-v1"
    assert loaded.status == INSUFFICIENT_HISTORY
    assert metrics == []
    async with session_scope() as session:
        saved = await get_job_by_id(session, job.id)
        assert saved is not None
        assert saved.score == 81
        assert saved.priority_score == 76
        assert saved.role_family_weight == 40
        assert saved.eligibility_state == "LIKELY_ELIGIBLE"
        assert saved.status == Status.submitted
        history = await get_application_events(session, application.id)
        assert [event.event_type for event in history] == ["offer"]

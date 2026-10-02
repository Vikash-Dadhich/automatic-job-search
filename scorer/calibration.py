"""Temporal check of Phase 16 feedback. This does not change scores or ranking."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from core.db import (
    CalibrationMetric,
    CalibrationRun,
    _as_utc,
    get_calibration_metrics,
    get_calibration_run,
    init_db,
    save_calibration_run,
    session_scope,
)
from scorer.feedback import (
    SUFFICIENT,
    FeedbackCase,
    FeedbackObservation,
    FeedbackReport,
    build_feedback,
    feedback_config_hash,
    load_feedback_cases,
    load_feedback_config,
    segment_for,
)

CALIBRATION_VERSION = "phase17-v1"
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "calibration.yaml"
INSUFFICIENT_HISTORY = "insufficient_history"
INSUFFICIENT = "insufficient_evidence"
OK = "ok"
_KNOWN = ("screening", "interview", "offer", "rejected", "ghosted")
_SegmentRows = dict[str, list[tuple[FeedbackCase, set[str], float, FeedbackObservation | None]]]


@dataclass(frozen=True, slots=True)
class CalibrationFold:
    fold_id: str
    train_as_of: datetime
    evaluation_start: datetime
    evaluation_end: datetime
    training_applications: int
    holdout_applications: int
    matured_holdout_applications: int
    evaluated_applications: int
    training_ids: tuple[int, ...]
    holdout_ids: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class CalibrationMetricRow:
    fold_id: str
    dimension: str
    segment: str
    training_prediction: float | None
    holdout_count: int
    holdout_positive_count: int
    holdout_rate: float | None
    brier_score: float | None
    baseline_brier_score: float | None
    brier_delta: float | None
    calibration_error: float | None
    coverage: float | None
    evidence_status: str
    direction_match: bool | None


@dataclass(frozen=True, slots=True)
class CalibrationReport:
    version: str
    config_hash: str
    status: str
    available_applications: int
    required_applications: int
    folds: tuple[CalibrationFold, ...]
    metrics: tuple[CalibrationMetricRow, ...]


def _require_int(name: str, value: object, *, lower: int, upper: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < lower or value > upper:
        raise ValueError(f"{name} must be an integer from {lower} through {upper}")
    return value


def _validate(raw: object) -> dict[str, Any]:
    if not isinstance(raw, dict) or raw.get("version") != CALIBRATION_VERSION:
        raise ValueError(f"calibration version must be {CALIBRATION_VERSION}")
    block = raw.get("calibration")
    if not isinstance(block, dict):
        raise ValueError("calibration config must contain a calibration mapping")
    buckets = block.get("probability_buckets")
    if not isinstance(buckets, list) or not buckets:
        raise ValueError("probability buckets must be a non-empty list")
    parsed_buckets = []
    for bucket in buckets:
        if not isinstance(bucket, dict):
            raise ValueError("each probability bucket must be a mapping")
        parsed_buckets.append(
            {
                "name": str(bucket["name"]),
                "min": float(bucket["min"]),
                "max": float(bucket["max"]),
            }
        )
    top_k = block.get("top_k")
    if not isinstance(top_k, list) or not top_k:
        raise ValueError("top_k must be a non-empty list")
    hypothetical = block.get("hypothetical_adjustment")
    if not isinstance(hypothetical, bool):
        raise ValueError("hypothetical_adjustment must be true or false")
    return {
        "version": CALIBRATION_VERSION,
        "calibration": {
            "fold_count": _require_int("fold_count", block["fold_count"], lower=1, upper=12),
            "evaluation_maturity_days": _require_int(
                "evaluation_maturity_days",
                block["evaluation_maturity_days"],
                lower=0,
                upper=3650,
            ),
            "minimum_training_applications": _require_int(
                "minimum_training_applications",
                block["minimum_training_applications"],
                lower=1,
                upper=100000,
            ),
            "minimum_holdout_applications": _require_int(
                "minimum_holdout_applications",
                block["minimum_holdout_applications"],
                lower=1,
                upper=100000,
            ),
            "minimum_holdout_segment": _require_int(
                "minimum_holdout_segment",
                block["minimum_holdout_segment"],
                lower=1,
                upper=100000,
            ),
            "strong_positive": [str(item) for item in block["strong_positive"]],
            "final_positive": [str(item) for item in block["final_positive"]],
            "probability_buckets": parsed_buckets,
            "top_k": [float(item) for item in top_k],
            "hypothetical_adjustment": hypothetical,
        },
    }


@lru_cache
def load_calibration_config(path: str | None = None) -> dict[str, Any]:
    target = Path(path) if path else CONFIG_PATH
    with target.open(encoding="utf-8") as handle:
        raw: Any = yaml.safe_load(handle)
    return _validate(raw)


def calibration_config_hash(config: dict[str, Any], feedback_config: dict[str, Any]) -> str:
    payload = {
        "calibration": config,
        "feedback": feedback_config_hash(feedback_config),
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def brier_score(pairs: list[tuple[float, int]]) -> float | None:
    """Mean squared error of predicted rates against 0/1 outcomes."""
    if not pairs:
        return None
    total = sum((predicted - actual) ** 2 for predicted, actual in pairs)
    return round(total / len(pairs), 6)


def _ordered(cases: list[FeedbackCase]) -> list[FeedbackCase]:
    return sorted(cases, key=lambda case: (_as_utc(case.submitted_at), case.application_id))


def _windows(
    cases: list[FeedbackCase],
    config: dict[str, Any],
) -> list[tuple[list[FeedbackCase], list[FeedbackCase], datetime]]:
    block = config["calibration"]
    ordered = _ordered(cases)
    train_min = int(block["minimum_training_applications"])
    hold_min = int(block["minimum_holdout_applications"])
    folds = int(block["fold_count"])
    if len(ordered) < train_min + hold_min:
        return []
    tail = len(ordered) - train_min
    possible = min(folds, tail // hold_min)
    if possible <= 0:
        return []
    base = tail // possible
    extra = tail % possible
    cursor = train_min
    windows: list[tuple[list[FeedbackCase], list[FeedbackCase], datetime]] = []
    for index in range(possible):
        size = base + (1 if index < extra else 0)
        stop = cursor + size
        train = list(ordered[:cursor])
        raw_hold = list(ordered[cursor:stop])
        train_as_of = _as_utc(train[-1].submitted_at)
        if train_as_of is None:
            cursor = stop
            continue
        kept_train = list(train)
        hold: list[FeedbackCase] = []
        for case in raw_hold:
            submitted = _as_utc(case.submitted_at)
            if submitted is not None and submitted <= train_as_of:
                kept_train.append(case)
            else:
                hold.append(case)
        next_end = ordered[stop].submitted_at if stop < len(ordered) else ordered[-1].submitted_at
        evaluation_end = _as_utc(next_end) or train_as_of
        if len(kept_train) >= train_min and len(hold) >= hold_min:
            windows.append((kept_train, hold, evaluation_end))
        cursor = stop
    return windows


def _events_in_window(case: FeedbackCase, start: datetime, end: datetime) -> set[str]:
    found: set[str] = set()
    for event_type, occurred_at in case.events:
        moment = _as_utc(occurred_at)
        if moment is None or moment <= start or moment > end:
            continue
        if event_type in _KNOWN:
            found.add(event_type)
    return found


def _matured(case: FeedbackCase, evaluation_end: datetime, maturity_days: int) -> bool:
    submitted = _as_utc(case.submitted_at)
    end = _as_utc(evaluation_end)
    if submitted is None or end is None:
        return False
    return submitted + timedelta(days=maturity_days) <= end


def _lookup(
    report: FeedbackReport,
) -> dict[tuple[str, str], FeedbackObservation]:
    return {(item.dimension, item.segment): item for item in report.signals}


def _predict(
    case: FeedbackCase,
    dimension: str,
    feedback_config: dict[str, Any],
    signals: dict[tuple[str, str], FeedbackObservation],
    baseline: float,
) -> tuple[float, bool, FeedbackObservation | None]:
    if dimension == "overall":
        return baseline, False, signals.get(("overall", "all"))
    segment = segment_for(case, dimension, feedback_config)
    if segment is None:
        return baseline, False, None
    signal = signals.get((dimension, segment))
    if signal is None or signal.evidence_status != SUFFICIENT or signal.adjusted_rate is None:
        return baseline, False, signal
    return signal.adjusted_rate, True, signal


def _rate(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return round(numerator / denominator, 6)


def _direction(adjustment: int, holdout_rate: float | None, baseline: float) -> bool | None:
    if holdout_rate is None or adjustment == 0:
        return None
    if adjustment > 0:
        return holdout_rate > baseline
    return holdout_rate < baseline


def _bucket_name(prediction: float, buckets: list[dict[str, float | str]]) -> str:
    for index, bucket in enumerate(buckets):
        low = float(bucket["min"])
        high = float(bucket["max"])
        last = index == len(buckets) - 1
        if prediction >= low and (prediction < high or (last and prediction <= high)):
            return str(bucket["name"])
    return str(buckets[-1]["name"])


def _topk_count(total: int, fraction: float) -> int:
    if total <= 0 or fraction <= 0:
        return 0
    count = int(total * fraction + 0.5)
    if count < 1:
        return 1 if total >= 1 else 0
    if count > total:
        return total
    return count


def build_calibration(
    cases: list[FeedbackCase],
    *,
    config: dict[str, Any] | None = None,
    feedback_config: dict[str, Any] | None = None,
) -> CalibrationReport:
    """Score Phase 16 feedback on later applications. Training cannot see those outcomes."""
    loaded = config if config is not None else load_calibration_config()
    learned = feedback_config if feedback_config is not None else load_feedback_config()
    block = loaded["calibration"]
    required = int(block["minimum_training_applications"]) + int(
        block["minimum_holdout_applications"]
    )
    digest = calibration_config_hash(loaded, learned)
    windows = _windows(cases, loaded)
    if not windows:
        return CalibrationReport(
            version=CALIBRATION_VERSION,
            config_hash=digest,
            status=INSUFFICIENT_HISTORY,
            available_applications=len(cases),
            required_applications=required,
            folds=(),
            metrics=(),
        )
    maturity = int(block["evaluation_maturity_days"])
    strong_labels = list(block["strong_positive"])
    holdout_segment_min = int(block["minimum_holdout_segment"])
    holdout_min = int(block["minimum_holdout_applications"])
    folds: list[CalibrationFold] = []
    metrics: list[CalibrationMetricRow] = []
    dimensions = list(learned["feedback"]["dimensions"])
    for index, (train, hold, evaluation_end) in enumerate(windows, start=1):
        train_as_of = _as_utc(train[-1].submitted_at)
        if train_as_of is None:
            continue
        report = build_feedback(cases, as_of=train_as_of, config=learned)
        signals = _lookup(report)
        overall = signals.get(("overall", "all"))
        baseline = 0.0 if overall is None else float(overall.rates["strong_positive_rate"])
        matured = [case for case in hold if _matured(case, evaluation_end, maturity)]
        evaluated: list[tuple[FeedbackCase, set[str]]] = []
        for case in matured:
            labels = _events_in_window(case, train_as_of, evaluation_end)
            if labels:
                evaluated.append((case, labels))
        fold_id = f"fold-{index}"
        folds.append(
            CalibrationFold(
                fold_id=fold_id,
                train_as_of=train_as_of,
                evaluation_start=train_as_of,
                evaluation_end=evaluation_end,
                training_applications=len(train),
                holdout_applications=len(hold),
                matured_holdout_applications=len(matured),
                evaluated_applications=len(evaluated),
                training_ids=tuple(case.application_id for case in train),
                holdout_ids=tuple(case.application_id for case in hold),
            )
        )
        if len(evaluated) < holdout_min:
            metrics.append(
                CalibrationMetricRow(
                    fold_id=fold_id,
                    dimension="overall",
                    segment="all",
                    training_prediction=baseline,
                    holdout_count=len(evaluated),
                    holdout_positive_count=0,
                    holdout_rate=_rate(
                        sum(1 for _case, labels in evaluated if _hit(labels, strong_labels)),
                        len(evaluated),
                    ),
                    brier_score=None,
                    baseline_brier_score=None,
                    brier_delta=None,
                    calibration_error=None,
                    coverage=None,
                    evidence_status=INSUFFICIENT,
                    direction_match=None,
                )
            )
            continue
        for dimension in dimensions:
            pairs_feedback: list[tuple[float, int]] = []
            pairs_baseline: list[tuple[float, int]] = []
            supported = 0
            grouped: _SegmentRows = {}
            for case, labels in evaluated:
                predicted, used, signal = _predict(case, dimension, learned, signals, baseline)
                actual = 1 if _hit(labels, strong_labels) else 0
                pairs_feedback.append((predicted, actual))
                pairs_baseline.append((baseline, actual))
                if used:
                    supported += 1
                segment = segment_for(case, dimension, learned) or "missing"
                if dimension == "overall":
                    segment = "all"
                grouped.setdefault(segment, []).append((case, labels, predicted, signal))
            feedback_brier = brier_score(pairs_feedback)
            baseline_brier = brier_score(pairs_baseline)
            delta = None
            if feedback_brier is not None and baseline_brier is not None:
                delta = round(feedback_brier - baseline_brier, 6)
            coverage = round(supported / len(evaluated), 6) if dimension != "overall" else None
            metrics.append(
                CalibrationMetricRow(
                    fold_id=fold_id,
                    dimension=dimension,
                    segment="all",
                    training_prediction=baseline,
                    holdout_count=len(evaluated),
                    holdout_positive_count=sum(actual for _predicted, actual in pairs_feedback),
                    holdout_rate=_rate(
                        sum(actual for _predicted, actual in pairs_feedback),
                        len(evaluated),
                    ),
                    brier_score=feedback_brier,
                    baseline_brier_score=baseline_brier,
                    brier_delta=delta,
                    calibration_error=None,
                    coverage=coverage,
                    evidence_status=SUFFICIENT if len(evaluated) >= holdout_min else INSUFFICIENT,
                    direction_match=None,
                )
            )
            if dimension == "overall":
                continue
            for segment in sorted(grouped):
                rows = grouped[segment]
                positives = sum(
                    1 for _case, labels, _pred, _signal in rows if _hit(labels, strong_labels)
                )
                hold_rate = _rate(positives, len(rows))
                signal = rows[0][3]
                training_ok = signal is not None and signal.evidence_status == SUFFICIENT
                predicted = baseline
                if training_ok and signal is not None and signal.adjusted_rate is not None:
                    predicted = signal.adjusted_rate
                status = INSUFFICIENT
                if training_ok and len(rows) >= holdout_segment_min:
                    status = SUFFICIENT
                error = None
                if hold_rate is not None:
                    error = round(abs(predicted - hold_rate), 6)
                adjustment = 0 if signal is None else signal.adjustment
                actuals = [
                    (predicted, 1 if _hit(labels, strong_labels) else 0)
                    for _case, labels, _pred, _signal in rows
                ]
                base_pairs = [
                    (baseline, 1 if _hit(labels, strong_labels) else 0)
                    for _case, labels, _pred, _signal in rows
                ]
                matched = None
                if status == SUFFICIENT:
                    matched = _direction(adjustment, hold_rate, baseline)
                metrics.append(
                    CalibrationMetricRow(
                        fold_id=fold_id,
                        dimension=dimension,
                        segment=segment,
                        training_prediction=predicted,
                        holdout_count=len(rows),
                        holdout_positive_count=positives,
                        holdout_rate=hold_rate,
                        brier_score=brier_score(actuals),
                        baseline_brier_score=brier_score(base_pairs),
                        brier_delta=None,
                        calibration_error=error,
                        coverage=None,
                        evidence_status=status,
                        direction_match=matched,
                    )
                )
        _append_buckets(metrics, fold_id, evaluated, learned, signals, baseline, block)
        _append_topk(metrics, fold_id, evaluated, strong_labels, block, learned, signals, baseline)
    ordered_metrics = tuple(
        sorted(metrics, key=lambda item: (item.fold_id, item.dimension, item.segment))
    )
    return CalibrationReport(
        version=CALIBRATION_VERSION,
        config_hash=digest,
        status=OK,
        available_applications=len(cases),
        required_applications=required,
        folds=tuple(folds),
        metrics=ordered_metrics,
    )


def _hit(labels: set[str], wanted: list[str]) -> bool:
    return any(label in labels for label in wanted)


def _append_buckets(
    metrics: list[CalibrationMetricRow],
    fold_id: str,
    evaluated: list[tuple[FeedbackCase, set[str]]],
    feedback_config: dict[str, Any],
    signals: dict[tuple[str, str], FeedbackObservation],
    baseline: float,
    block: dict[str, Any],
) -> None:
    strong_labels = list(block["strong_positive"])
    buckets: list[dict[str, float | str]] = block["probability_buckets"]
    grouped: dict[str, list[tuple[float, int]]] = {str(bucket["name"]): [] for bucket in buckets}
    for case, labels in evaluated:
        predicted, _used, _signal = _predict(
            case,
            "role_family",
            feedback_config,
            signals,
            baseline,
        )
        grouped[_bucket_name(predicted, buckets)].append(
            (predicted, 1 if _hit(labels, strong_labels) else 0)
        )
    for bucket in buckets:
        name = str(bucket["name"])
        rows = grouped[name]
        positives = sum(actual for _predicted, actual in rows)
        rate = _rate(positives, len(rows))
        mean_predicted = None if not rows else round(sum(item[0] for item in rows) / len(rows), 6)
        error = None
        if rate is not None and mean_predicted is not None:
            error = round(abs(mean_predicted - rate), 6)
        metrics.append(
            CalibrationMetricRow(
                fold_id=fold_id,
                dimension="probability_bucket",
                segment=name,
                training_prediction=mean_predicted,
                holdout_count=len(rows),
                holdout_positive_count=positives,
                holdout_rate=rate,
                brier_score=None,
                baseline_brier_score=None,
                brier_delta=None,
                calibration_error=error,
                coverage=None,
                evidence_status=SUFFICIENT if rows else INSUFFICIENT,
                direction_match=None,
            )
        )


def _append_topk(
    metrics: list[CalibrationMetricRow],
    fold_id: str,
    evaluated: list[tuple[FeedbackCase, set[str]]],
    strong_labels: list[str],
    block: dict[str, Any],
    feedback_config: dict[str, Any],
    signals: dict[tuple[str, str], FeedbackObservation],
    baseline: float,
) -> None:
    ranked = sorted(
        evaluated,
        key=lambda item: (
            -(item[0].priority_score if item[0].priority_score is not None else -1),
            item[0].application_id,
        ),
    )
    hypothetical = bool(block["hypothetical_adjustment"])
    adjusted = sorted(
        evaluated,
        key=lambda item: (
            -(
                (item[0].priority_score if item[0].priority_score is not None else -1)
                + _family_adjustment(item[0], feedback_config, signals)
            ),
            item[0].application_id,
        ),
    )
    for fraction in block["top_k"]:
        count = _topk_count(len(ranked), float(fraction))
        label = f"top_{int(float(fraction) * 100)}"
        _append_slice(metrics, fold_id, "priority_topk", label, ranked[:count], strong_labels)
        if hypothetical:
            _append_slice(
                metrics,
                fold_id,
                "hypothetical_priority_topk",
                label,
                adjusted[:count],
                strong_labels,
            )


def _family_adjustment(
    case: FeedbackCase,
    feedback_config: dict[str, Any],
    signals: dict[tuple[str, str], FeedbackObservation],
) -> int:
    segment = segment_for(case, "role_family", feedback_config)
    if segment is None:
        return 0
    signal = signals.get(("role_family", segment))
    if signal is None or signal.evidence_status != SUFFICIENT:
        return 0
    return signal.adjustment


def _append_slice(
    metrics: list[CalibrationMetricRow],
    fold_id: str,
    dimension: str,
    segment: str,
    rows: list[tuple[FeedbackCase, set[str]]],
    strong_labels: list[str],
) -> None:
    positives = sum(1 for _case, labels in rows if _hit(labels, strong_labels))
    metrics.append(
        CalibrationMetricRow(
            fold_id=fold_id,
            dimension=dimension,
            segment=segment,
            training_prediction=None,
            holdout_count=len(rows),
            holdout_positive_count=positives,
            holdout_rate=_rate(positives, len(rows)),
            brier_score=None,
            baseline_brier_score=None,
            brier_delta=None,
            calibration_error=None,
            coverage=None,
            evidence_status=SUFFICIENT if rows else INSUFFICIENT,
            direction_match=None,
        )
    )


async def run_calibration(
    cases: list[FeedbackCase] | None = None,
    *,
    config: dict[str, Any] | None = None,
    feedback_config: dict[str, Any] | None = None,
) -> CalibrationReport:
    """Benchmark stored application history. Does not write job or application rows."""
    source = cases if cases is not None else await load_feedback_cases()
    return build_calibration(source, config=config, feedback_config=feedback_config)


async def persist_calibration(report: CalibrationReport) -> int:
    await init_db()
    run = CalibrationRun(
        version=report.version,
        config_hash=report.config_hash,
        status=report.status,
        available_applications=report.available_applications,
        required_applications=report.required_applications,
        fold_count=len(report.folds),
    )
    metrics = [
        CalibrationMetric(
            run_id=0,
            fold_id=item.fold_id,
            dimension=item.dimension,
            segment=item.segment,
            training_prediction=item.training_prediction,
            holdout_count=item.holdout_count,
            holdout_positive_count=item.holdout_positive_count,
            holdout_rate=item.holdout_rate,
            brier_score=item.brier_score,
            baseline_brier_score=item.baseline_brier_score,
            brier_delta=item.brier_delta,
            calibration_error=item.calibration_error,
            coverage=item.coverage,
            evidence_status=item.evidence_status,
            direction_match=item.direction_match,
        )
        for item in report.metrics
    ]
    async with session_scope() as session:
        saved = await save_calibration_run(session, run, metrics)
        assert saved.id is not None
        return saved.id


async def load_persisted_calibration(
    run_id: int,
) -> tuple[CalibrationRun | None, list[CalibrationMetric]]:
    await init_db()
    async with session_scope() as session:
        run = await get_calibration_run(session, run_id)
        metrics = await get_calibration_metrics(session, run_id)
    return run, metrics

"""Offline tests for the doctor health report."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

from core.db import Job, Source, Status, Tier, session_scope
from main import _cmd_doctor


def _job(
    external_id: str,
    *,
    company: str,
    status: Status,
    decided_at: datetime | None = None,
    score: int | None = None,
    tier: Tier | None = None,
    last_error: str | None = None,
    outcome: str | None = None,
) -> Job:
    return Job(
        source=Source.linkedin,
        external_id=external_id,
        title="Product Manager",
        company=company,
        location="Remote",
        url=f"https://example.com/{external_id}",
        description_clean="Python product role.",
        status=status,
        decided_at=decided_at,
        score=score,
        tier=tier,
        last_error=last_error,
        outcome=outcome,
    )


async def test_doctor_empty_db(db_ready: Path) -> None:
    report = await _cmd_doctor(json_output=True)
    assert report["status_counts"]["discovered"] == 0
    assert report["status_counts"]["submitted"] == 0
    assert report["score_stats"]["count"] == 0
    assert report["active_cooldowns"] == []
    assert report["recent_errors"] == []
    assert report["conversion"]["discovered_to_staged_pct"] == 0
    assert report["vector_gate"]["reject"] == 0
    assert report["vector_gate"]["pass"] == 0


async def test_doctor_with_jobs(db_ready: Path) -> None:
    async with session_scope() as session:
        session.add(_job("staged-a", company="A", status=Status.staged, score=80, tier=Tier.two))
        session.add(_job("staged-b", company="B", status=Status.staged, score=70, tier=Tier.two))
        session.add(
            _job(
                "submitted-a",
                company="C",
                status=Status.submitted,
                score=90,
                tier=Tier.one,
                decided_at=datetime.now(UTC),
            )
        )
        session.add(
            _job(
                "error-a",
                company="D",
                status=Status.error,
                last_error="llm timeout",
            )
        )

    report = await _cmd_doctor(json_output=True)
    assert report["status_counts"]["staged"] == 2
    assert report["status_counts"]["submitted"] == 1
    assert report["status_counts"]["error"] == 1
    assert report["tier_counts"]["one"] == 1
    assert report["tier_counts"]["two"] == 2
    assert report["score_stats"]["count"] == 3
    assert report["score_stats"]["min"] == 70
    assert report["score_stats"]["max"] == 90
    assert report["recent_errors"][0]["company"] == "D"
    assert report["recent_errors"][0]["error"] == "llm timeout"
    assert report["conversion"]["discovered_to_staged_pct"] == 75.0
    assert report["conversion"]["staged_to_submitted_pct"] == 33.3


async def test_doctor_cooldown(db_ready: Path) -> None:
    now = datetime.now(UTC)
    async with session_scope() as session:
        session.add(
            _job(
                "fresh",
                company="Acme",
                status=Status.submitted,
                decided_at=now,
            )
        )
        session.add(
            _job(
                "stale",
                company="OldCo",
                status=Status.submitted,
                decided_at=now - timedelta(days=31),
            )
        )
        session.add(
            _job(
                "ignored",
                company="SkipCo",
                status=Status.ignored,
                decided_at=now,
            )
        )
        session.add(
            _job(
                "undecided",
                company="WaitCo",
                status=Status.pending_review,
                decided_at=None,
            )
        )

    report = await _cmd_doctor(json_output=True)
    assert report["active_cooldowns"] == ["Acme"]
    assert report["cooldown_days"] == 30


async def test_doctor_outcomes(db_ready: Path) -> None:
    now = datetime.now(UTC)
    async with session_scope() as session:
        session.add(
            _job(
                "iv",
                company="InterviewCo",
                status=Status.submitted,
                tier=Tier.one,
                decided_at=now,
                outcome="interview",
            )
        )
        session.add(
            _job(
                "off",
                company="OfferCo",
                status=Status.submitted,
                tier=Tier.one,
                decided_at=now,
                outcome="offer",
            )
        )
        session.add(
            _job(
                "rej",
                company="NoCo",
                status=Status.submitted,
                tier=Tier.two,
                decided_at=now,
                outcome="rejected",
            )
        )
        session.add(
            _job(
                "fresh-blank",
                company="WaitCo",
                status=Status.submitted,
                tier=Tier.two,
                decided_at=now,
            )
        )
        session.add(
            _job(
                "old-blank",
                company="GhostCo",
                status=Status.submitted,
                tier=Tier.two,
                decided_at=now - timedelta(days=15),
            )
        )

    report = await _cmd_doctor(json_output=True)
    assert report["outcomes"]["interview"] == 1
    assert report["outcomes"]["offer"] == 1
    assert report["outcomes"]["rejected"] == 1
    assert report["outcomes"]["ghosted"] == 0
    assert report["outcomes"]["unlabeled"] == 2
    assert report["awaiting_label"] == 1
    tier_one = report["outcome_by_tier"]["one"]
    assert tier_one["labeled"] == 2
    assert tier_one["positive"] == 2
    assert tier_one["positive_pct"] == 100.0
    tier_two = report["outcome_by_tier"]["two"]
    assert tier_two["labeled"] == 1
    assert tier_two["positive"] == 0
    assert tier_two["positive_pct"] == 0.0


async def test_doctor_vector_gate(db_ready: Path) -> None:
    async with session_scope() as session:
        rejected = _job(
            "vec-reject",
            company="A",
            status=Status.filtered_out,
            score=0,
            tier=Tier.three,
        )
        rejected.vector_decision = "reject"
        passed = _job(
            "vec-pass",
            company="B",
            status=Status.staged,
            score=80,
            tier=Tier.two,
        )
        passed.vector_decision = "pass"
        session.add(rejected)
        session.add(passed)

    report = await _cmd_doctor(json_output=True)
    assert report["vector_gate"]["reject"] == 1
    assert report["vector_gate"]["pass"] == 1
    assert report["vector_gate"]["enabled"] is False
    assert report["vector_gate"]["threshold"] == 0.5

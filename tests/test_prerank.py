"""Tests for the deterministic pre-rank (scorer.prerank)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from config.profile import Profile
from core.db import Job, Source
from scorer.prerank import prerank_jobs, prerank_score


def _job(title: str, *, company: str = "Acme", source: Source = Source.linkedin,
         location: str = "Remote", job_id: int = 1,
         posted: datetime | None = None) -> Job:
    return Job(
        id=job_id,
        source=source,
        external_id=f"ext-{job_id}",
        title=title,
        company=company,
        location=location,
        url=f"https://example.com/{job_id}",
        posted_at=posted,
    )


def test_intern_title_outranks_fulltime(profile: Profile) -> None:
    intern = _job("Product Manager Intern", job_id=1)
    fulltime = _job("Senior Product Manager", job_id=2)
    assert prerank_score(intern, profile) > prerank_score(fulltime, profile)


def test_summer_signal_scores_above_bare_title(profile: Profile) -> None:
    summer = _job("Corporate Strategy MBA, Summer 2027", job_id=1)
    bare = _job("Random Role", job_id=2)
    assert prerank_score(summer, profile) > prerank_score(bare, profile)


def test_prerank_jobs_orders_best_first(profile: Profile) -> None:
    jobs = [
        _job("Senior Product Manager", job_id=1),
        _job("Product Manager Intern", job_id=2),
        _job("Data Entry Clerk", job_id=3),
    ]
    ordered = prerank_jobs(jobs, profile)
    assert ordered[0].title == "Product Manager Intern"


def test_recency_boost(profile: Profile) -> None:
    now = datetime.now(UTC)
    fresh = _job("Product Manager Intern", job_id=1, posted=now - timedelta(hours=2))
    stale = _job("Product Manager Intern", job_id=2, posted=now - timedelta(days=5))
    assert prerank_score(fresh, profile) > prerank_score(stale, profile)


def test_new_source_scored_without_error(profile: Profile) -> None:
    for src in (Source.google, Source.zip_recruiter):
        job = _job("Strategy Intern", source=src, job_id=10)
        assert prerank_score(job, profile) > 0

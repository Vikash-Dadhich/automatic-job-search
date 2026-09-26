"""Regression tests for scoring isolation, profile-aware filters, and re-scoring."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest

from config.profile import Profile, load_profile
from config.settings import get_settings
from core.db import (
    Job,
    Source,
    Status,
    Tier,
    get_job_by_id,
    session_scope,
    upsert_job,
)
from scorer.engine import Scorer, compute_tier, is_dream_company, parse_score
from scraper.filters import evaluate, max_acceptable_years
from scraper.models import RawPosting


class ScoreOnlyClient:
    """Scores fine but always fails the outreach call."""

    def __init__(self, score_payload: str = '{"s":95,"t":1,"r":["great fit"]}') -> None:
        self.score_payload = score_payload
        self.outreach_attempts = 0

    async def complete(self, *, user: str, **_kwargs: Any) -> str:
        if "cover letter" in user.lower():
            raise RuntimeError("503 UNAVAILABLE")
        if "outreach" in user.lower() or "Rewrite without" in user:
            self.outreach_attempts += 1
            raise RuntimeError("503 UNAVAILABLE")
        return self.score_payload


def _posting(**overrides: Any) -> RawPosting:
    base: dict[str, Any] = {
        "source": Source.linkedin,
        "external_id": "p1",
        "title": "Product Manager",
        "company": "GoodCo",
        "location": "Seattle, WA",
        "url": "https://example.com/job/1",
        "description_clean": "Build product roadmaps with engineering partners.",
    }
    base.update(overrides)
    return RawPosting(**base)


def test_parse_score_handles_braces_inside_strings() -> None:
    raw = 'Here you go: {"s": 81, "t": 2, "r": ["uses {curly} tokens", "fit"]} done'
    parsed = parse_score(raw)
    assert parsed.s == 81
    assert "uses {curly} tokens" in parsed.r


def test_parse_score_rejects_non_numeric_score() -> None:
    """A garbage score must error, not silently become 0 / Tier 3."""
    with pytest.raises(ValueError):
        parse_score('{"s":"not-a-number","r":["x"]}')


def test_dream_company_match_tolerates_suffix(profile: Profile) -> None:
    dreamed = profile.preferences.dream_companies
    if not dreamed:
        pytest.skip("profile lists no dream companies")
    target = dreamed[0]
    assert is_dream_company(f"{target} LLC", profile)
    assert compute_tier(10, f"{target}, Inc.", profile) is Tier.one


def test_tier_thresholds_come_from_settings(profile: Profile) -> None:
    settings = get_settings()
    assert compute_tier(settings.tier_one_min_score, "Nobody", profile) is Tier.one
    assert compute_tier(settings.tier_two_min_score, "Nobody", profile) is Tier.two
    assert compute_tier(settings.tier_two_min_score - 1, "Nobody", profile) is Tier.three


def test_yoe_ceiling_follows_profile(profile: Profile) -> None:
    ceiling = max_acceptable_years(profile)
    reachable = evaluate(
        _posting(
            description_clean=(
                f"We need {max(1, ceiling - 1)}+ years of experience building products."
            )
        ),
        profile,
    )
    assert reachable.passed

    unreachable = evaluate(
        _posting(
            description_clean=f"Requires {ceiling + 6}+ years of experience in product."
        ),
        profile,
    )
    assert not unreachable.passed


def test_yoe_keeps_job_when_a_lower_band_is_reachable(profile: Profile) -> None:
    """JDs often list a reachable minimum plus an aspirational 'preferred'."""
    ceiling = max_acceptable_years(profile)
    result = evaluate(
        _posting(
            description_clean=(
                f"{max(1, ceiling - 1)}+ years of experience required. "
                f"{ceiling + 8}+ years of experience preferred."
            )
        ),
        profile,
    )
    assert result.passed


def test_company_blocklist_does_not_match_lookalikes(profile: Profile) -> None:
    blocked = Profile.model_validate(
        {
            **profile.model_dump(),
            "exclusions": {**profile.exclusions.model_dump(), "companies": ["Meta"]},
        }
    )
    assert evaluate(_posting(company="MetLife"), blocked).passed
    assert not evaluate(_posting(company="Meta Platforms"), blocked).passed


@pytest.mark.asyncio
async def test_outreach_failure_still_persists_tier_one_score(db_ready: None) -> None:
    """A dead outreach call must not push a valid Tier-1 job into Status.error."""
    profile = load_profile()
    async with session_scope() as session:
        job = await upsert_job(
            session,
            Job(
                source=Source.linkedin,
                external_id="iso-1",
                title="Product Manager",
                company="GoodCo",
                location="Seattle, WA",
                url="https://example.com/job/iso",
                description_clean="Own the product roadmap and work with engineers.",
                status=Status.discovered,
            ),
        )
        job_id = job.id

    client = ScoreOnlyClient()
    summary = await Scorer(client=client, profile=profile).score_pending(
        generate_outreach=True,
        generate_cover_letter=False,
    )

    assert client.outreach_attempts > 0, "outreach path must actually be exercised"
    assert summary.errors == 0
    assert summary.staged == 1
    async with session_scope() as session:
        assert job_id is not None
        stored = await get_job_by_id(session, job_id)
        assert stored is not None
        assert stored.status is Status.staged
        assert stored.score == 95
        assert stored.tier is Tier.one
        assert stored.outreach_draft is None


@pytest.mark.asyncio
async def test_rewritten_jd_resets_staged_job_for_rescore(db_ready: None) -> None:
    async with session_scope() as session:
        job = await upsert_job(
            session,
            Job(
                source=Source.linkedin,
                external_id="rescore-1",
                title="Product Manager",
                company="GoodCo",
                url="https://example.com/job/rescore",
                description_clean="Original description.",
                content_hash="hash-v1",
                status=Status.discovered,
            ),
        )
        job.status = Status.staged
        job.score = 88
        job.tier = Tier.one
        job.cover_letter = "Letter written against the old posting."
        job.outreach_draft = "Old outreach."
        session.add(job)
        job_id = job.id

    async with session_scope() as session:
        await upsert_job(
            session,
            Job(
                source=Source.linkedin,
                external_id="rescore-1",
                title="Product Manager",
                company="GoodCo",
                url="https://example.com/job/rescore",
                description_clean="Employer rewrote the requirements.",
                content_hash="hash-v2",
                status=Status.discovered,
            ),
        )

    async with session_scope() as session:
        assert job_id is not None
        stored = await get_job_by_id(session, job_id)
        assert stored is not None
        assert stored.status is Status.discovered
        assert stored.score is None
        assert stored.cover_letter is None
        assert stored.outreach_draft is None


@pytest.mark.asyncio
async def test_unchanged_jd_keeps_staged_status(db_ready: None) -> None:
    async with session_scope() as session:
        job = await upsert_job(
            session,
            Job(
                source=Source.linkedin,
                external_id="stable-1",
                title="Product Manager",
                company="GoodCo",
                url="https://example.com/job/stable",
                description_clean="Same description.",
                content_hash="hash-same",
                status=Status.discovered,
            ),
        )
        job.status = Status.staged
        job.score = 77
        session.add(job)
        job_id = job.id

    async with session_scope() as session:
        await upsert_job(
            session,
            Job(
                source=Source.linkedin,
                external_id="stable-1",
                title="Product Manager",
                company="GoodCo",
                url="https://example.com/job/stable",
                description_clean="Same description.",
                content_hash="hash-same",
                status=Status.discovered,
            ),
        )

    async with session_scope() as session:
        assert job_id is not None
        stored = await get_job_by_id(session, job_id)
        assert stored is not None
        assert stored.status is Status.staged
        assert stored.score == 77


@pytest.mark.asyncio
async def test_rewritten_jd_leaves_submitted_outcome_alone(db_ready: None) -> None:
    decided = datetime(2026, 1, 1, tzinfo=UTC)
    labeled = datetime(2026, 1, 2, tzinfo=UTC)
    async with session_scope() as session:
        job = await upsert_job(
            session,
            Job(
                source=Source.linkedin,
                external_id="submitted-1",
                title="Product Manager",
                company="GoodCo",
                url="https://example.com/job/submitted",
                description_clean="Original description.",
                content_hash="hash-v1",
                status=Status.discovered,
            ),
        )
        job.status = Status.submitted
        job.decided_at = decided
        job.outcome = "interview"
        job.outcome_at = labeled
        job.outcome_message_id = 15
        job.cover_letter = "Keep this letter."
        session.add(job)
        job_id = job.id

    async with session_scope() as session:
        await upsert_job(
            session,
            Job(
                source=Source.linkedin,
                external_id="submitted-1",
                title="Product Manager",
                company="GoodCo",
                url="https://example.com/job/submitted",
                description_clean="Employer rewrote the requirements.",
                content_hash="hash-v2",
                status=Status.discovered,
            ),
        )

    async with session_scope() as session:
        assert job_id is not None
        stored = await get_job_by_id(session, job_id)
        assert stored is not None
        assert stored.status is Status.submitted
        assert stored.outcome == "interview"
        assert stored.outcome_at is not None
        assert stored.outcome_at.replace(tzinfo=UTC) == labeled
        assert stored.outcome_message_id == 15
        assert stored.decided_at is not None
        assert stored.decided_at.replace(tzinfo=UTC) == decided
        assert stored.cover_letter == "Keep this letter."

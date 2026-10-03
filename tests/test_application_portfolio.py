"""Application capacity. It does not score jobs or move them between statuses."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from automation.runner import apply_pending
from automation.workday import ApplyResult
from config.settings import get_settings
from core.db import Job, Source, Status, Tier, get_job_by_id, session_scope, upsert_job
from orchestrator.pipeline import run_pipeline
from scorer.application_portfolio import (
    ALLOCATED,
    BLOCKED_COMPANY,
    DEFERRED,
    allocate_portfolio,
    allocated_jobs,
    apply_portfolio,
    load_portfolio_config,
    portfolio_config_hash,
)

NOW = datetime(2026, 10, 2, 12, 0, tzinfo=UTC)


def _job(external_id: str, **kwargs: object) -> Job:
    data: dict[str, object] = {
        "source": Source.linkedin,
        "external_id": external_id,
        "title": "Intern",
        "company": external_id,
        "location": "Seattle, WA",
        "url": f"https://jobs.example.com/{external_id}",
        "status": Status.staged,
        "score": 80,
        "priority_score": 80,
        "tier": Tier.two,
        "role_family": "PRODUCT_MANAGEMENT",
        "eligibility_state": "LIKELY_ELIGIBLE",
        "posted_at": NOW,
        "discovered_at": NOW,
    }
    data.update(kwargs)
    return Job(**data)  # type: ignore[arg-type]


def test_portfolio_config_reuses_phase7_weights() -> None:
    loaded = load_portfolio_config()
    assert loaded["version"] == "phase14-v2"
    assert loaded["portfolio"]["enabled"] is True
    assert loaded["portfolio"]["max_applications_per_company"] == 2
    assert loaded["portfolio"]["balance_margin"] == 5
    first = portfolio_config_hash(
        max_per_company=2,
        capacity=10,
        cooldown_days=30,
        balance_margin=5,
    )
    assert first == portfolio_config_hash(
        max_per_company=2,
        capacity=10,
        cooldown_days=30,
        balance_margin=5,
    )
    assert first != portfolio_config_hash(
        max_per_company=2,
        capacity=10,
        cooldown_days=30,
        balance_margin=6,
    )


def test_config_rejects_a_bool_cap(tmp_path: Path) -> None:
    path = tmp_path / "portfolio.yaml"
    path.write_text(
        "version: phase14-v2\n"
        "portfolio:\n"
        "  enabled: true\n"
        "  max_applications_per_company: true\n"
        "  balance_margin: 5\n"
    )
    with pytest.raises(ValueError):
        load_portfolio_config(str(path))


def test_daily_capacity_defers_the_rest() -> None:
    jobs = [
        _job(f"j{index}", id=index, company=f"Co{index}", priority_score=100 - index)
        for index in range(1, 16)
    ]
    first = allocate_portfolio(jobs, cooldown_companies=set(), capacity=10, max_per_company=2)
    second = allocate_portfolio(jobs, cooldown_companies=set(), capacity=10, max_per_company=2)
    allocated = [item for item in first if item.decision == ALLOCATED]
    deferred = [item for item in first if item.decision == DEFERRED]
    assert len(allocated) == 10
    assert len(deferred) == 5
    assert [item.job.external_id for item in allocated] == [f"j{index}" for index in range(1, 11)]
    assert [(item.job.external_id, item.decision) for item in first] == [
        (item.job.external_id, item.decision) for item in second
    ]
    assert jobs[14].status == Status.staged
    assert jobs[14].priority_score == 85


def test_company_cap_is_per_run_and_suffix_aware() -> None:
    acme = [
        _job(f"a{index}", id=index, company="Acme, Inc.", priority_score=90 - index)
        for index in range(5)
    ]
    beta = [
        _job(f"b{index}", id=10 + index, company="Beta LLC", priority_score=70 - index)
        for index in range(5)
    ]
    decisions = allocate_portfolio(
        acme + beta,
        cooldown_companies=set(),
        capacity=10,
        max_per_company=2,
    )
    chosen = [item.job for item in decisions if item.decision == ALLOCATED]
    assert sum(1 for job in chosen if job.external_id.startswith("a")) == 2
    assert sum(1 for job in chosen if job.external_id.startswith("b")) == 2
    blocked = [item for item in decisions if item.decision == BLOCKED_COMPANY]
    assert len(blocked) == 6
    assert all(item.reason == "blocked_company_concentration" for item in blocked)
    jobs = [
        _job("a-pm", id=1, company="Acme", priority_score=90),
        _job("b-pm", id=2, company="Beta", priority_score=89),
        _job(
            "a-consult",
            id=3,
            company="Acme LLC",
            role_family="CONSULTING",
            priority_score=88,
        ),
    ]
    balanced = allocate_portfolio(
        jobs,
        cooldown_companies=set(),
        capacity=2,
        max_per_company=1,
        balance_margin=5,
    )
    chosen_ids = [item.job.external_id for item in balanced if item.decision == ALLOCATED]
    assert chosen_ids == ["a-pm", "b-pm"]


def test_ignored_job_does_not_consume_a_slot() -> None:
    ignored = _job("old", id=1, company="Acme", status=Status.ignored, priority_score=99)
    fresh = _job("new", id=2, company="Acme", priority_score=50)
    decisions = allocate_portfolio(
        [ignored, fresh],
        cooldown_companies=set(),
        capacity=1,
        max_per_company=2,
    )
    assert [item.job.external_id for item in decisions] == ["new"]
    assert decisions[0].decision == ALLOCATED
    assert ignored.status == Status.ignored


def test_cooldown_blocks_the_company_and_leaves_scores() -> None:
    blocked = _job("acme", id=1, company="Acme LLC", priority_score=99, score=91)
    other = _job("beta", id=2, company="Beta", priority_score=40, score=70)
    before = (
        blocked.score,
        blocked.tier,
        blocked.priority_score,
        blocked.eligibility_state,
        blocked.role_family,
    )
    decisions = allocate_portfolio(
        [blocked, other],
        cooldown_companies={"Acme, Inc."},
        capacity=10,
        max_per_company=2,
    )
    assert decisions[0].job.external_id == "beta"
    assert decisions[0].decision == ALLOCATED
    cooled = next(item for item in decisions if item.job.external_id == "acme")
    assert cooled.decision == BLOCKED_COMPANY
    assert cooled.reason == "blocked_company_cooldown"
    after = (
        blocked.score,
        blocked.tier,
        blocked.priority_score,
        blocked.eligibility_state,
        blocked.role_family,
    )
    assert after == before
    assert blocked.status == Status.staged


def test_role_family_targets_are_soft() -> None:
    def batch(family: str, start: int, count: int, offset: int) -> list[Job]:
        return [
            _job(
                f"{family}-{index}",
                id=offset + index,
                company=f"{family}-{index}",
                role_family=family,
                priority_score=start - index,
            )
            for index in range(count)
        ]

    jobs = (
        batch("PRODUCT_MANAGEMENT", 90, 6, 1)
        + batch("CONSULTING", 80, 6, 20)
        + batch("STRATEGY_TRANSFORMATION", 70, 6, 40)
        + batch("OTHER", 60, 6, 60)
    )
    decisions = allocate_portfolio(jobs, cooldown_companies=set(), capacity=10, max_per_company=1)
    chosen = [item.job for item in decisions if item.decision == ALLOCATED]
    counts = {
        "PRODUCT_MANAGEMENT": 0,
        "CONSULTING": 0,
        "STRATEGY_TRANSFORMATION": 0,
        "OTHER": 0,
    }
    for job in chosen:
        counts[job.role_family or "OTHER"] += 1
    assert counts["PRODUCT_MANAGEMENT"] == 6
    assert counts["CONSULTING"] == 4
    assert counts["STRATEGY_TRANSFORMATION"] == 0
    assert counts["OTHER"] == 0
    assert "STRATEGY_TRANSFORMATION-0" not in {job.external_id for job in chosen}
    kept = {"CONSULTING-0", "CONSULTING-1"}
    short = [
        job
        for job in jobs
        if not job.external_id.startswith("CONSULTING-") or job.external_id in kept
    ]
    filled = allocate_portfolio(short, cooldown_companies=set(), capacity=10, max_per_company=1)
    allocated = [item.job for item in filled if item.decision == ALLOCATED]
    assert len(allocated) == 10
    assert sum(1 for job in allocated if job.role_family == "CONSULTING") == 2
    deferred = [item.job.external_id for item in filled if item.decision == DEFERRED]
    assert deferred
    again = allocate_portfolio(
        [job for job in short if job.external_id in set(deferred)],
        cooldown_companies=set(),
        capacity=10,
        max_per_company=1,
    )
    assert any(item.decision == ALLOCATED for item in again)

    strong = _job("pm-strong", id=100, company="Strong", priority_score=94)
    weak = _job(
        "consult-weak",
        id=101,
        company="Weak",
        role_family="CONSULTING",
        priority_score=82,
    )
    protected = allocate_portfolio(
        [strong, weak],
        cooldown_companies=set(),
        capacity=1,
        max_per_company=2,
    )
    assert [item.job.external_id for item in protected if item.decision == ALLOCATED] == [
        "pm-strong"
    ]
    close_pm = _job("pm-close", id=102, company="ClosePM", priority_score=89)
    close_consult = _job(
        "consult-close",
        id=103,
        company="CloseC",
        role_family="CONSULTING",
        priority_score=87,
    )
    balanced = allocate_portfolio(
        [close_pm, close_consult],
        cooldown_companies=set(),
        capacity=1,
        max_per_company=2,
    )
    assert [item.job.external_id for item in balanced if item.decision == ALLOCATED] == [
        "consult-close"
    ]
    hybrid = _job(
        "hybrid",
        id=104,
        company="Hybrid",
        role_family="PRODUCT_MANAGEMENT",
        role_secondary_family="CONSULTING",
        priority_score=88,
    )
    seated = allocate_portfolio(
        [hybrid, close_consult],
        cooldown_companies=set(),
        capacity=1,
        max_per_company=2,
        balance_margin=0,
    )
    assert [item.job.external_id for item in seated if item.decision == ALLOCATED] == ["hybrid"]
    unranked = _job("none", id=105, company="NoneCo", priority_score=None)
    skipped = allocate_portfolio(
        [unranked, strong],
        cooldown_companies=set(),
        capacity=2,
        max_per_company=2,
    )
    missing = next(item for item in skipped if item.job.external_id == "none")
    assert missing.decision == DEFERRED
    assert missing.reason == "deferred_missing_priority"
    assert unranked.status == Status.staged
    assert unranked.priority_score is None


def test_priority_order_and_zero_capacity() -> None:
    low = _job("low", id=1, company="A", priority_score=10)
    high = _job("high", id=2, company="B", priority_score=90)
    decisions = allocate_portfolio(
        [low, high],
        cooldown_companies=set(),
        capacity=1,
        max_per_company=2,
    )
    assert allocated_jobs(decisions)[0].external_id == "high"
    assert low.priority_score == 10
    none = allocate_portfolio(
        [high],
        cooldown_companies=set(),
        capacity=0,
        max_per_company=2,
    )
    assert none[0].decision == "BLOCKED_CAPACITY"
    assert high.status == Status.staged


def test_ineligible_and_review_jobs_are_not_candidates() -> None:
    blocked = _job("nope", id=1, eligibility_state="CLEARLY_INELIGIBLE", priority_score=99)
    review = _job("review", id=2, status=Status.pending_review, priority_score=98)
    done = _job("done", id=3, status=Status.submitted, priority_score=97)
    manual = _job("manual", id=4, status=Status.manual_review, priority_score=96)
    failed = _job("failed", id=5, status=Status.error, priority_score=95)
    ready = _job("ready", id=6, company="ReadyCo", priority_score=10)
    decisions = allocate_portfolio(
        [blocked, review, done, manual, failed, ready],
        cooldown_companies=set(),
        capacity=5,
        max_per_company=2,
    )
    assert [item.job.external_id for item in decisions] == ["ready"]
    assert blocked.eligibility_state == "CLEARLY_INELIGIBLE"
    assert review.status == Status.pending_review
    assert done.status == Status.submitted
    assert manual.status == Status.manual_review
    assert failed.status == Status.error


class _Spy:
    def __init__(self) -> None:
        self.calls: list[int | None] = []

    async def apply(self, job: Job) -> ApplyResult:
        self.calls.append(job.id)
        return ApplyResult(screenshot_path="/tmp/review.png", reached_review=True)


async def test_pipeline_applies_only_allocated_staged_jobs(
    db_ready: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    async with session_scope() as session:
        review = await upsert_job(
            session,
            _job(
                "in-review",
                status=Status.pending_review,
                priority_score=200,
                company="ReviewCo",
                source=Source.workday,
                resume_path="/tmp/review.pdf",
            ),
        )
        high = await upsert_job(
            session,
            _job(
                "high",
                priority_score=90,
                company="HighCo",
                source=Source.workday,
                resume_path="/tmp/high.pdf",
            ),
        )
        mid = await upsert_job(
            session,
            _job(
                "mid",
                priority_score=80,
                company="MidCo",
                source=Source.workday,
                resume_path="/tmp/mid.pdf",
            ),
        )
        low = await upsert_job(
            session,
            _job(
                "low",
                priority_score=10,
                company="LowCo",
                source=Source.workday,
                resume_path="/tmp/low.pdf",
            ),
        )
        assert review.id and high.id and mid.id and low.id
        ids = {"review": review.id, "high": high.id, "mid": mid.id, "low": low.id}

    monkeypatch.setenv("APPLY_LIMIT", "2")
    get_settings.cache_clear()
    spy = _Spy()
    seen: list[list[int]] = []

    async def record_apply(**kwargs: object) -> object:
        raw = kwargs.get("job_ids")
        values = raw if isinstance(raw, list) else []
        seen.append([item for item in values if isinstance(item, int)])
        return await apply_pending(applicator=spy, job_ids=seen[-1])

    async def noop() -> None:
        return None

    import orchestrator.pipeline as pipeline_mod

    async def noop_stage() -> dict[str, list[int]]:
        return {"selected_ids": []}

    monkeypatch.setattr(pipeline_mod, "_run_ingestion", noop)
    monkeypatch.setattr(pipeline_mod, "_score_pending", noop)
    monkeypatch.setattr(pipeline_mod, "_shortlist_stage", noop_stage)
    monkeypatch.setattr(pipeline_mod, "_prepare_shortlisted_resumes", noop)
    monkeypatch.setattr(pipeline_mod, "_apply_pending", record_apply)

    await run_pipeline(
        enable_apply=True,
        enable_reviews=False,
        enable_prep_pack=False,
        enable_suggestions=False,
        enable_benchmark=False,
    )
    assert seen[0] == [ids["high"], ids["mid"]]
    assert spy.calls == [ids["high"], ids["mid"]]
    async with session_scope() as session:
        review_row = await get_job_by_id(session, ids["review"])
        low_row = await get_job_by_id(session, ids["low"])
        high_row = await get_job_by_id(session, ids["high"])
        assert review_row is not None and low_row is not None and high_row is not None
        assert review_row.status == Status.pending_review
        assert review_row.portfolio_decision is None
        assert low_row.status == Status.staged
        assert low_row.portfolio_decision == DEFERRED
        assert high_row.score == 80
        assert high_row.priority_score == 90
        assert high_row.eligibility_state == "LIKELY_ELIGIBLE"

    spy.calls.clear()
    await run_pipeline(
        enable_apply=True,
        enable_reviews=False,
        enable_prep_pack=False,
        enable_suggestions=False,
        enable_benchmark=False,
    )
    assert seen[1] == [ids["low"]]
    assert spy.calls == [ids["low"]]


async def test_real_cooldown_ignores_an_ignored_job(db_ready: Path) -> None:
    del db_ready
    async with session_scope() as session:
        await upsert_job(
            session,
            _job(
                "ignored-acme",
                company="Acme",
                status=Status.ignored,
                decided_at=NOW,
            ),
        )
        await upsert_job(
            session,
            _job(
                "submitted-beta",
                company="Beta",
                status=Status.submitted,
                decided_at=NOW,
            ),
        )
        acme = await upsert_job(
            session,
            _job(
                "staged-acme",
                company="Acme LLC",
                source=Source.workday,
                resume_path="/tmp/a.pdf",
                priority_score=70,
            ),
        )
        beta = await upsert_job(
            session,
            _job(
                "staged-beta",
                company="Beta",
                source=Source.workday,
                resume_path="/tmp/b.pdf",
                priority_score=90,
            ),
        )
        assert acme.id and beta.id
    summary = await apply_portfolio()
    assert acme.id in summary.allocated_ids
    assert beta.id not in summary.allocated_ids
    async with session_scope() as session:
        saved = await get_job_by_id(session, beta.id)
        assert saved is not None
        assert saved.status == Status.staged
        assert saved.portfolio_decision == BLOCKED_COMPANY
        assert saved.score == 80


def _workday(external_id: str, **kwargs: object) -> Job:
    return _job(
        external_id,
        source=Source.workday,
        resume_path=f"/tmp/{external_id}.pdf",
        **kwargs,
    )


class _NotStaged:
    def __init__(self, job_id: int) -> None:
        self.id = job_id
        self.status = Status.submitted
        self.eligibility_state = "LIKELY_ELIGIBLE"
        self.priority_score = 90
        self.resume_path = "/tmp/x.pdf"
        self.source = Source.workday
        self.url = "https://example.com/x"
        self.company = "Gone"


async def test_skipped_allocation_is_not_returned(
    db_ready: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    async with session_scope() as session:
        only = await upsert_job(session, _workday("only", company="Only", priority_score=90))
        assert only.id is not None
        only_id = only.id
    real_get = get_job_by_id

    async def skip(session: object, job_id: int) -> object:
        if job_id == only_id:
            return _NotStaged(job_id)
        return await real_get(session, job_id)  # type: ignore[arg-type]

    monkeypatch.setattr("scorer.application_portfolio.get_job_by_id", skip)
    summary = await apply_portfolio()
    assert summary.allocated_ids == ()
    assert summary.allocated == 0
    async with session_scope() as session:
        saved = await get_job_by_id(session, only_id)
        assert saved is not None
        assert saved.portfolio_decision is None
        assert saved.status == Status.staged


async def test_persisted_allocation_is_returned(db_ready: Path) -> None:
    del db_ready
    async with session_scope() as session:
        ready = await upsert_job(session, _workday("ready", company="Ready", priority_score=90))
        assert ready.id is not None
        ready_id = ready.id
    summary = await apply_portfolio()
    assert summary.allocated_ids == (ready_id,)
    assert summary.allocated == 1
    async with session_scope() as session:
        saved = await get_job_by_id(session, ready_id)
        assert saved is not None
        assert saved.portfolio_decision == ALLOCATED


async def test_mixed_persist_returns_only_the_saved_allocation(
    db_ready: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    monkeypatch.setenv("APPLY_LIMIT", "2")
    get_settings.cache_clear()
    async with session_scope() as session:
        first = await upsert_job(session, _workday("kept", company="Kept", priority_score=90))
        second = await upsert_job(session, _workday("lost", company="Lost", priority_score=80))
        assert first.id is not None and second.id is not None
        kept_id, lost_id = first.id, second.id
    real_get = get_job_by_id

    async def skip_lost(session: object, job_id: int) -> object:
        if job_id == lost_id:
            return _NotStaged(job_id)
        return await real_get(session, job_id)  # type: ignore[arg-type]

    monkeypatch.setattr("scorer.application_portfolio.get_job_by_id", skip_lost)
    summary = await apply_portfolio()
    assert summary.allocated == 1
    assert summary.allocated_ids == (kept_id,)
    async with session_scope() as session:
        lost = await get_job_by_id(session, lost_id)
        assert lost is not None
        assert lost.portfolio_decision is None
        assert lost.status == Status.staged


async def test_pipeline_apply_receives_only_persisted_ids(
    db_ready: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    monkeypatch.setenv("APPLY_LIMIT", "2")
    get_settings.cache_clear()
    async with session_scope() as session:
        first = await upsert_job(session, _workday("pipe-a", company="PipeA", priority_score=90))
        second = await upsert_job(session, _workday("pipe-b", company="PipeB", priority_score=70))
        assert first.id is not None and second.id is not None
        kept_id, lost_id = first.id, second.id
    real_get = get_job_by_id

    async def skip_lost(session: object, job_id: int) -> object:
        if job_id == lost_id:
            return _NotStaged(job_id)
        return await real_get(session, job_id)  # type: ignore[arg-type]

    monkeypatch.setattr("scorer.application_portfolio.get_job_by_id", skip_lost)
    seen: list[list[int]] = []

    async def record_apply(**kwargs: object) -> object:
        raw = kwargs.get("job_ids")
        values = raw if isinstance(raw, list) else []
        seen.append([item for item in values if isinstance(item, int)])
        return object()

    async def noop() -> None:
        return None

    import orchestrator.pipeline as pipeline_mod

    async def noop_stage() -> dict[str, list[int]]:
        return {"selected_ids": []}

    monkeypatch.setattr(pipeline_mod, "_run_ingestion", noop)
    monkeypatch.setattr(pipeline_mod, "_score_pending", noop)
    monkeypatch.setattr(pipeline_mod, "_shortlist_stage", noop_stage)
    monkeypatch.setattr(pipeline_mod, "_prepare_shortlisted_resumes", noop)
    monkeypatch.setattr(pipeline_mod, "_apply_pending", record_apply)
    await run_pipeline(
        enable_apply=True,
        enable_reviews=False,
        enable_prep_pack=False,
        enable_suggestions=False,
        enable_benchmark=False,
    )
    assert seen == [[kept_id]]


async def test_skipped_plan_does_not_consume_capacity(
    db_ready: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    monkeypatch.setenv("APPLY_LIMIT", "2")
    get_settings.cache_clear()
    async with session_scope() as session:
        first = await upsert_job(session, _workday("skip-me", company="Skip", priority_score=95))
        second = await upsert_job(session, _workday("take-me", company="Take", priority_score=70))
        third = await upsert_job(session, _workday("wait", company="Wait", priority_score=10))
        assert first.id and second.id and third.id
        skip_id, take_id, wait_id = first.id, second.id, third.id
    real_get = get_job_by_id

    async def skip_first(session: object, job_id: int) -> object:
        if job_id == skip_id:
            return _NotStaged(job_id)
        return await real_get(session, job_id)  # type: ignore[arg-type]

    monkeypatch.setattr("scorer.application_portfolio.get_job_by_id", skip_first)
    summary = await apply_portfolio()
    assert summary.allocated == len(summary.allocated_ids)
    assert summary.allocated <= 2
    assert summary.allocated_ids == (take_id,)
    assert wait_id not in summary.allocated_ids

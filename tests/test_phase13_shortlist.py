"""Review-queue selection. It orders staged jobs and does not discard the rest."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

from core.db import Job, Source, Status, get_job_by_id, session_scope, upsert_job
from scorer.shortlist import (
    SELECTED_BY_PRIORITY,
    SELECTED_FOR_PORTFOLIO_DIVERSITY,
    SHORTLIST_VERSION,
    apply_shortlist,
    config_hash,
    load_shortlist_config,
    select_shortlist,
)

NOW = datetime(2026, 9, 29, 12, 0, tzinfo=UTC)


def _config(**overrides: int) -> dict[str, Any]:
    loaded = load_shortlist_config()
    block = dict(loaded["shortlist"])
    block.update(overrides)
    return {"version": SHORTLIST_VERSION, "shortlist": block}


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
        "tier": None,
        "role_family": "PRODUCT_MANAGEMENT",
        "role_confidence": "high",
        "eligibility_state": "LIKELY_ELIGIBLE",
        "vector_score": 0.2,
        "vector_decision": "pass",
        "discovery_family": "CONSULTING",
        "discovery_bucket": "broad",
        "discovery_query": "strategy intern",
        "posted_at": NOW,
        "discovered_at": NOW,
    }
    data.update(kwargs)
    return Job(**data)  # type: ignore[arg-type]


def test_shortlist_config_loads_and_rejects_invalid(tmp_path: Path) -> None:
    loaded = load_shortlist_config()
    assert loaded["version"] == "phase13-v1"
    assert loaded["shortlist"] == {
        "max_size": 20,
        "max_per_company": 2,
        "diversity_margin": 5,
    }
    assert config_hash(loaded) == config_hash(load_shortlist_config())
    bad = tmp_path / "shortlist.yaml"
    bad.write_text(
        "version: other\n"
        "shortlist: {max_size: 1, max_per_company: 1, diversity_margin: 1}\n"
    )
    with pytest.raises(ValueError):
        load_shortlist_config(str(bad))
    flagged = tmp_path / "flag.yaml"
    flagged.write_text(
        "version: phase13-v1\n"
        "shortlist:\n"
        "  max_size: true\n"
        "  max_per_company: 2\n"
        "  diversity_margin: 5\n"
    )
    with pytest.raises(ValueError):
        load_shortlist_config(str(flagged))


def test_priority_order_and_phase12_ties() -> None:
    jobs = [
        _job("low", priority_score=10, id=1),
        _job("high", priority_score=90, id=2),
        _job("mid", priority_score=50, id=3),
    ]
    assert [pick.job.external_id for pick in select_shortlist(jobs, config=_config())] == [
        "high",
        "mid",
        "low",
    ]
    tied = [
        _job("weaker-fit", priority_score=70, score=10, id=4, posted_at=NOW),
        _job("stronger-fit", priority_score=70, score=90, id=5, posted_at=NOW),
        _job("missing-fit", priority_score=70, score=None, id=3, posted_at=NOW),
        _job("older", priority_score=70, score=90, id=2, posted_at=NOW - timedelta(days=3)),
        _job("newer", priority_score=70, score=90, id=9, posted_at=NOW),
        _job("no-priority", priority_score=None, score=100, id=1),
    ]
    picks = select_shortlist(tied, config=_config(max_size=6))
    assert [pick.job.external_id for pick in picks] == [
        "stronger-fit",
        "newer",
        "older",
        "weaker-fit",
        "missing-fit",
        "no-priority",
    ]
    assert picks[-1].reason == SELECTED_BY_PRIORITY


def test_size_and_company_cap() -> None:
    many = [_job(f"j{index}", priority_score=100 - index, id=index) for index in range(1, 26)]
    assert len(select_shortlist(many, config=_config())) == 20
    assert len(select_shortlist(many[:3], config=_config())) == 3
    assert select_shortlist(many, config=_config(max_size=0)) == []
    crowded = [
        _job("a1", company="Acme", priority_score=90, id=1),
        _job("a2", company="Acme, Inc.", priority_score=80, id=2),
        _job("a3", company="Acme LLC", priority_score=70, id=3),
        _job("b1", company="Beta", priority_score=60, id=4),
    ]
    chosen = select_shortlist(crowded, config=_config(max_per_company=2))
    assert [pick.job.external_id for pick in chosen] == ["a1", "a2", "b1"]
    assert crowded[2].status == Status.staged
    separate = [
        _job("meta", company="Meta", priority_score=90, id=1),
        _job("metlife", company="MetLife", priority_score=80, id=2),
    ]
    assert len(select_shortlist(separate, config=_config(max_per_company=1))) == 2
    blank = [
        _job("blank-a", company="", priority_score=90, id=1),
        _job("blank-b", company=" ", priority_score=80, id=2),
    ]
    assert len(select_shortlist(blank, config=_config(max_per_company=1, max_size=2))) == 2
    one_company = [
        _job(f"only{i}", company="OnlyCo", priority_score=50 - i, id=i) for i in range(5)
    ]
    assert len(select_shortlist(one_company, config=_config())) == 2
    wide_cap = [_job(f"same{i}", company="Same", priority_score=40 - i, id=i) for i in range(5)]
    assert len(select_shortlist(wide_cap, config=_config(max_size=3, max_per_company=10))) == 3


def test_family_diversity_is_a_soft_swap() -> None:
    pm = [
        _job(f"pm{index}", priority_score=90 - index, id=index, company=f"Co{index}")
        for index in range(4)
    ]
    close = _job(
        "consulting",
        company="ConsultCo",
        priority_score=84,
        id=10,
        role_family="CONSULTING",
    )
    picks = select_shortlist(pm + [close], config=_config(max_size=4))
    assert [pick.job.external_id for pick in picks] == ["pm0", "pm1", "pm2", "consulting"]
    assert picks[-1].reason == SELECTED_FOR_PORTFOLIO_DIVERSITY
    assert all(pick.reason == SELECTED_BY_PRIORITY for pick in picks[:-1])

    weak = _job("weak", company="ConsultCo", priority_score=70, id=11, role_family="CONSULTING")
    kept = select_shortlist(pm + [weak], config=_config(max_size=4))
    assert [pick.job.external_id for pick in kept] == ["pm0", "pm1", "pm2", "pm3"]

    unknown = _job("unknown", company="U", priority_score=84, id=12, role_family="UNKNOWN")
    no_boost = select_shortlist(pm + [unknown], config=_config(max_size=4))
    assert [pick.job.external_id for pick in no_boost] == ["pm0", "pm1", "pm2", "pm3"]

    strategy = _job(
        "strategy",
        company="Strat",
        priority_score=84,
        id=13,
        role_family="STRATEGY_TRANSFORMATION",
    )
    mixed = select_shortlist(pm + [strategy], config=_config(max_size=4))
    assert mixed[-1].job.external_id == "strategy"
    again = select_shortlist(pm + [close], config=_config(max_size=4))
    assert [pick.job.external_id for pick in again] == [pick.job.external_id for pick in picks]


def test_non_staged_jobs_are_ignored() -> None:
    staged = _job("ready", priority_score=10, id=1)
    protected = [
        _job("review", status=Status.pending_review, priority_score=99, id=2),
        _job("sent", status=Status.submitted, priority_score=99, id=3),
        _job("drop", status=Status.ignored, priority_score=99, id=4),
        _job("manual", status=Status.manual_review, priority_score=99, id=5),
        _job("filtered", status=Status.filtered_out, priority_score=99, id=6),
        _job("bad", status=Status.error, priority_score=99, id=7),
    ]
    picks = select_shortlist([staged, *protected], config=_config())
    assert [pick.job.external_id for pick in picks] == ["ready"]
    assert [job.status for job in protected] == [
        Status.pending_review,
        Status.submitted,
        Status.ignored,
        Status.manual_review,
        Status.filtered_out,
        Status.error,
    ]
    assert select_shortlist([], config=_config()) == []
    assert select_shortlist(protected, config=_config(max_size=5), occupied=5) == []


def test_selection_ignores_discovery_and_vector() -> None:
    left = _job(
        "left",
        id=1,
        priority_score=40,
        discovery_query="other",
        discovery_family="OTHER",
        discovery_bucket="x",
        vector_score=0.01,
    )
    right = _job(
        "right",
        id=2,
        priority_score=90,
        discovery_query="pm",
        discovery_family="PRODUCT_MANAGEMENT",
        discovery_bucket="PM_CORE",
        vector_score=0.99,
    )
    first = [pick.job.external_id for pick in select_shortlist([left, right], config=_config())]
    left.vector_score, right.vector_score = right.vector_score, left.vector_score
    left.discovery_query, right.discovery_query = right.discovery_query, left.discovery_query
    second = [pick.job.external_id for pick in select_shortlist([left, right], config=_config())]
    assert first == second == ["right", "left"]


def test_missing_dates_still_select() -> None:
    missing = _job("nodate", posted_at=None, discovered_at=None, priority_score=70, id=2)
    dated = _job("dated", priority_score=70, id=1)
    picks = select_shortlist([missing, dated], config=_config(max_size=2))
    assert [pick.job.external_id for pick in picks] == ["dated", "nodate"]
    assert missing.status == Status.staged


async def test_apply_shortlist_is_idempotent_and_preserves_scores(db_ready: Path) -> None:
    del db_ready
    saved: dict[str, int] = {}
    async with session_scope() as session:
        for index, priority in enumerate((95, 90, 80, 70)):
            row = await upsert_job(
                session,
                _job(
                    f"keep-{index}",
                    priority_score=priority,
                    score=50 + index,
                    company=f"Firm{index}",
                    vector_score=0.4,
                ),
            )
            assert row.id is not None
            saved[f"keep-{index}"] = row.id
        waiting = await upsert_job(
            session,
            _job("waiting", status=Status.pending_review, priority_score=99),
        )
        done = await upsert_job(session, _job("done", status=Status.submitted, priority_score=99))
        assert waiting.id is not None and done.id is not None
        saved["waiting"] = waiting.id
        saved["done"] = done.id

    small = _config(max_size=3)
    first = await apply_shortlist(config=small)
    assert first.selected == 2
    assert first.already_pending == 1
    async with session_scope() as session:
        top = await get_job_by_id(session, saved["keep-0"])
        assert top is not None
        rank = top.shortlist_rank
        reason = top.shortlist_reason
        digest = top.shortlist_config_hash
        score = top.score
        priority = top.priority_score
        family = top.role_family
        eligibility = top.eligibility_state
        vector = top.vector_score
        assert top.status == Status.pending_review
        assert top.shortlist_version == SHORTLIST_VERSION
    second = await apply_shortlist(config=small)
    assert second.selected == 0
    async with session_scope() as session:
        again = await get_job_by_id(session, saved["keep-0"])
        waiting = await get_job_by_id(session, saved["waiting"])
        done = await get_job_by_id(session, saved["done"])
        left = await get_job_by_id(session, saved["keep-3"])
        assert again is not None and waiting is not None and done is not None and left is not None
        assert again.shortlist_rank == rank
        assert again.shortlist_reason == reason
        assert again.shortlist_config_hash == digest
        assert again.score == score
        assert again.priority_score == priority
        assert again.role_family == family
        assert again.eligibility_state == eligibility
        assert again.vector_score == vector
        assert again.status == Status.pending_review
        assert waiting.status == Status.pending_review
        assert waiting.shortlist_rank is None
        assert done.status == Status.submitted
        assert left.status == Status.staged
        assert left.score == 53

    larger = _config(max_size=4)
    third = await apply_shortlist(config=larger)
    assert third.selected == 1
    assert third.config_hash != digest
    async with session_scope() as session:
        original = await get_job_by_id(session, saved["keep-0"])
        added = await get_job_by_id(session, saved["keep-2"])
        assert original is not None and added is not None
        assert original.shortlist_config_hash == digest
        assert added.status == Status.pending_review
        assert added.shortlist_config_hash == third.config_hash
        assert added.priority_score == 80

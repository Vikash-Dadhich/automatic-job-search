"""Priority orders stored jobs. It does not change fit or remove a job."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

from config.profile import Profile
from core.db import Job, Source, Status, session_scope, upsert_job
from scorer.priority import (
    PRIORITY_VERSION,
    apply_priority,
    calculate_priority,
    load_priority_config,
    priority_is_current,
    role_family_component,
    sort_by_priority,
)
from scorer.role_weights import get_role_family_weight

NOW = datetime(2026, 9, 29, 12, 0, tzinfo=UTC)


def _job(external_id: str = "p1", **kwargs: object) -> Job:
    data: dict[str, object] = {
        "source": Source.linkedin,
        "external_id": external_id,
        "title": "Product Manager Intern",
        "company": "Acme",
        "location": "Seattle, WA",
        "url": f"https://jobs.example.com/{external_id}",
        "description_clean": "Own the product roadmap for this internship. " * 4,
        "status": Status.staged,
        "score": 90,
        "fit_version": "phase6-v2",
        "role_family": "PRODUCT_MANAGEMENT",
        "role_subfamily": "PM_CORE",
        "role_confidence": "high",
        "eligibility_state": "LIKELY_ELIGIBLE",
        "jd_status": "present",
        "jd_truncated": False,
        "posted_at": NOW,
        "discovered_at": NOW - timedelta(days=1),
        "discovery_family": "CONSULTING",
        "discovery_bucket": "broad",
        "discovery_query": "strategy intern",
        "vector_score": 0.2,
    }
    data.update(kwargs)
    return Job(**data)  # type: ignore[arg-type]


def test_weights_sum_to_100() -> None:
    weights = load_priority_config()["weights"]
    assert sum(weights.values()) == 100
    assert PRIORITY_VERSION == "phase12-v1"


def test_fit_and_role_family_order_attention(profile: Profile) -> None:
    strong = _job("strong", score=91)
    weak = _job("weak", score=40)
    assert calculate_priority(strong, profile, now=NOW).score > calculate_priority(
        weak, profile, now=NOW
    ).score
    strategy = _job(
        "strategy",
        role_family="STRATEGY_TRANSFORMATION",
        role_subfamily="CORPORATE_STRATEGY",
    )
    other = _job("other", role_family="OTHER", role_subfamily=None, role_confidence="low")
    unknown = _job("unknown", role_family="UNKNOWN", role_confidence=None)
    assert role_family_component(strong) > role_family_component(strategy)
    assert role_family_component(strategy) > role_family_component(other)
    assert role_family_component(unknown) == round(get_role_family_weight("UNKNOWN") * 100 / 40)
    core = _job("core", role_subfamily="PM_CORE")
    technical = _job("tech", role_subfamily="TECHNICAL_PRODUCT")
    assert role_family_component(core) == role_family_component(technical)
    before = strong.score
    apply_priority(strong, profile, now=NOW)
    assert strong.score == before == 91


def test_eligibility_unknown_is_not_ineligible(profile: Profile) -> None:
    confirmed = _job("c", eligibility_state="CONFIRMED_ELIGIBLE")
    likely = _job("l", eligibility_state="LIKELY_ELIGIBLE")
    unknown = _job("u", eligibility_state="UNKNOWN")
    blocked = _job("b", eligibility_state="CLEARLY_INELIGIBLE")
    scores = [
        calculate_priority(job, profile, now=NOW).score
        for job in (confirmed, likely, unknown, blocked)
    ]
    assert scores[0] >= scores[1] > scores[2] > scores[3]
    assert 0 <= scores[3] <= 100
    assert blocked.status == Status.staged
    assert blocked.score == 90


def test_jd_and_freshness_do_not_discard(profile: Profile) -> None:
    complete = calculate_priority(_job("full"), profile, now=NOW).score
    truncated = _job("cut", jd_truncated=True, jd_status="truncated")
    missing = _job(
        "none",
        description_clean=None,
        jd_status="missing",
        score=None,
        fit_version=None,
    )
    suspicious = _job("short", jd_status="suspicious", description_clean="Intern.")
    assert calculate_priority(truncated, profile, now=NOW).score > 0
    assert truncated.status == Status.staged
    assert calculate_priority(missing, profile, now=NOW).components["fit"] is None
    assert 0 < calculate_priority(missing, profile, now=NOW).score <= 100
    assert calculate_priority(suspicious, profile, now=NOW).score > 0
    assert complete > calculate_priority(truncated, profile, now=NOW).score

    recent = _job("new", score=40, posted_at=NOW)
    older = _job("old", score=90, posted_at=NOW - timedelta(days=40))
    assert calculate_priority(older, profile, now=NOW).score > calculate_priority(
        recent, profile, now=NOW
    ).score
    fallback = _job("fallback", posted_at=None, discovered_at=NOW)
    assert calculate_priority(fallback, profile, now=NOW).components["freshness"] == 100


def test_dream_company_is_only_a_configured_boost(profile: Profile) -> None:
    plain = calculate_priority(_job("plain", company="OtherCo"), profile, now=NOW)
    assert plain.components["dream_company"] is None
    dreamed = profile.model_copy(
        update={
            "preferences": profile.preferences.model_copy(update={"dream_companies": ["Acme"]})
        }
    )
    match = _job("dream", company="Acme")
    other = _job("other-co", company="OtherCo")
    fit_before = match.score
    boosted = calculate_priority(match, dreamed, now=NOW)
    normal = calculate_priority(other, dreamed, now=NOW)
    assert boosted.components["dream_company"] == 100
    assert normal.components["dream_company"] == 0
    assert boosted.score > normal.score
    assert match.score == fit_before


def test_submitted_is_not_treated_as_untouched(profile: Profile) -> None:
    fresh = _job("fresh", status=Status.staged)
    done = _job("done", status=Status.submitted)
    assert calculate_priority(fresh, profile, now=NOW).score > calculate_priority(
        done, profile, now=NOW
    ).score
    assert done.status == Status.submitted


def test_priority_ignores_discovery_and_vector(profile: Profile) -> None:
    left = calculate_priority(
        _job("left", discovery_query="other query", vector_score=0.01),
        profile,
        now=NOW,
    )
    right = calculate_priority(
        _job(
            "right",
            discovery_family="PRODUCT_MANAGEMENT",
            discovery_bucket="PM_CORE",
            vector_score=0.99,
        ),
        profile,
        now=NOW,
    )
    assert left.score == right.score
    assert left.components == right.components


def test_priority_is_deterministic_and_bounded(profile: Profile) -> None:
    job = _job()
    assert calculate_priority(job, profile, now=NOW) == calculate_priority(job, profile, now=NOW)
    for state in ("CONFIRMED_ELIGIBLE", "LIKELY_ELIGIBLE", "UNKNOWN", "CLEARLY_INELIGIBLE", None):
        sample = _job(eligibility_state=state, score=None, role_family=None, posted_at=None)
        score = calculate_priority(sample, profile, now=NOW).score
        assert 0 <= score <= 100


def test_ties_break_on_fit_then_recency_then_id(profile: Profile) -> None:
    del profile
    older = _job("older", id=2, posted_at=NOW - timedelta(days=2))
    newer = _job("newer", id=3, posted_at=NOW)
    lower_fit = _job("lower", id=4, score=10)
    for job in (older, newer, lower_fit):
        job.priority_score = 70
    ordered = sort_by_priority([older, lower_fit, newer])
    assert [job.external_id for job in ordered] == ["newer", "older", "lower"]


async def test_priority_persists_and_reuses_until_inputs_change(
    db_ready: Path,
    profile: Profile,
) -> None:
    del db_ready
    async with session_scope() as session:
        saved = await upsert_job(session, _job("persist"))
        first = apply_priority(saved, profile, now=NOW)
        assert saved.priority_version == PRIORITY_VERSION
        components = saved.priority_components
        assert components is not None and components["fit"] == 90
        assert saved.priority_reasons
        saved.priority_reasons = ["sentinel"]
        assert priority_is_current(saved, profile)
        second = apply_priority(saved, profile)
        assert second.reasons == ["sentinel"]
        saved.eligibility_state = "CLEARLY_INELIGIBLE"
        assert not priority_is_current(saved, profile)
        third = apply_priority(saved, profile, now=NOW)
        assert third.score < first.score
        assert saved.score == 90
        assert saved.status == Status.staged

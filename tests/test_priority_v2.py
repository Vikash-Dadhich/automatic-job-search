"""Priority 2.0 attention order. Fit, eligibility, and portfolio stay separate."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

import scorer.priority as priority_mod
from config.profile import Profile
from core.db import Job, Source, Status
from scorer.priority import PRIORITY_VERSION, calculate_priority, load_priority_config

NOW = datetime(2026, 10, 2, 12, 0, tzinfo=UTC)


def _job(**kwargs: object) -> Job:
    data: dict[str, object] = {
        "source": Source.linkedin,
        "external_id": "p2",
        "title": "Intern",
        "company": "Acme",
        "url": "https://jobs.example.com/p2",
        "description_clean": "Own the product roadmap for this internship. " * 4,
        "status": Status.staged,
        "score": 80,
        "fit_version": "phase6-v2",
        "role_family": "PRODUCT_MANAGEMENT",
        "role_confidence": "high",
        "eligibility_state": "LIKELY_ELIGIBLE",
        "eligibility_version": "phase9-v1",
        "jd_status": "present",
        "jd_truncated": False,
        "posted_at": NOW,
        "discovered_at": NOW,
    }
    data.update(kwargs)
    return Job(**data)  # type: ignore[arg-type]


def _signal(name: str, value: object) -> dict[str, object]:
    return {"signal": name, "value": value, "basis": "explicit"}


def test_weights_are_the_documented_allocation() -> None:
    weights = load_priority_config()["weights"]
    assert PRIORITY_VERSION == "phase12-v2"
    assert sum(weights.values()) == 100
    assert weights == {
        "fit": 32,
        "primary_role_alignment": 12,
        "secondary_role_bonus": 3,
        "eligibility": 16,
        "role_confidence": 6,
        "jd_evidence_quality": 6,
        "program_evidence": 7,
        "company_domain_relevance": 5,
        "freshness": 6,
        "dream_company": 4,
        "workflow": 3,
    }
    source = open(priority_mod.__file__, encoding="utf-8").read()
    assert "build_llm_client" not in source
    assert "embed" not in source
    assert "prestige" not in source


def test_priority_stays_bounded_and_fit_is_only_an_input(profile: Profile) -> None:
    job = _job(score=91)
    before = (job.score, job.eligibility_state, job.role_family, job.role_family_weight, job.status)
    decision = calculate_priority(job, profile, now=NOW)
    assert 0 <= decision.score <= 100
    assert decision.components["fit"] == 91
    assert job.score == before[0]
    assert job.eligibility_state == before[1]
    assert job.role_family == before[2]
    assert job.role_family_weight == before[3]
    assert job.status == before[4]
    assert job.shortlist_rank is None


def test_eligibility_order_and_unknown(profile: Profile) -> None:
    def score(state: str | None) -> int:
        return calculate_priority(_job(eligibility_state=state), profile, now=NOW).score

    assert score("CONFIRMED_ELIGIBLE") > score("UNKNOWN")
    assert score("UNKNOWN") > score("CLEARLY_INELIGIBLE")
    blocked = _job(eligibility_state="CLEARLY_INELIGIBLE")
    calculate_priority(blocked, profile, now=NOW)
    assert blocked.status == Status.staged


def test_role_alignment_and_bounded_secondary(profile: Profile) -> None:
    primary = calculate_priority(_job(), profile, now=NOW)
    strategy = calculate_priority(
        _job(role_family="STRATEGY_TRANSFORMATION"),
        profile,
        now=NOW,
    )
    unknown = calculate_priority(
        _job(role_family="UNKNOWN", role_confidence=None),
        profile,
        now=NOW,
    )
    hybrid = calculate_priority(
        _job(role_secondary_family="STRATEGY_TRANSFORMATION", role_secondary_confidence="high"),
        profile,
        now=NOW,
    )
    assert primary.components["primary_role_alignment"] == 100
    assert strategy.components["primary_role_alignment"] == 70
    assert unknown.components["primary_role_alignment"] is None
    assert primary.components["secondary_role_bonus"] is None
    assert hybrid.components["secondary_role_bonus"] == 100
    assert hybrid.score >= primary.score
    assert hybrid.score - primary.score <= 3
    assert "Secondary STRATEGY_TRANSFORMATION responsibility." in hybrid.reasons


def test_confidence_and_structured_evidence(profile: Profile) -> None:
    high = calculate_priority(_job(role_confidence="high"), profile, now=NOW)
    low = calculate_priority(_job(role_confidence="low"), profile, now=NOW)
    assert high.score > low.score
    bare = calculate_priority(_job(), profile, now=NOW)
    assert bare.components["jd_evidence_quality"] == 80

    class _Section:
        def __init__(self, state: str) -> None:
            self.state = state

    class _Doc:
        version = "phase19-v1"
        availability = "available"
        responsibilities = _Section("explicit")
        qualifications = _Section("explicit")
        experience = _Section("explicit")
        education = _Section("explicit")
        functional = _Section("explicit")
        program = _Section("not_mentioned")
        work_model = _Section("not_mentioned")

    richer = calculate_priority(_job(), profile, now=NOW, structured=_Doc())
    quality = richer.components["jd_evidence_quality"]
    assert isinstance(quality, int) and quality > 80
    assert richer.score >= bare.score


def test_program_evidence_is_capped_and_not_mba_by_default(profile: Profile) -> None:
    generic = {"version": "phase8-v2", "signals": [_signal("internship_program", True)]}
    mba = {
        "version": "phase8-v2",
        "signals": [
            _signal("internship_program", True),
            _signal("mba_internship_program", True),
        ],
    }
    none = calculate_priority(_job(), profile, now=NOW)
    generic_score = calculate_priority(_job(), profile, now=NOW, company_context=generic)
    mba_score = calculate_priority(_job(), profile, now=NOW, company_context=mba)
    assert none.components["program_evidence"] is None
    assert generic_score.components["program_evidence"] == 40
    assert mba_score.components["program_evidence"] == 100
    assert mba_score.score > generic_score.score
    assert "Prestigious" not in " ".join(mba_score.reasons)


def test_domains_are_capped_and_irrelevant_domains_add_nothing(profile: Profile) -> None:
    software = {"signals": [_signal("domain:software", "software")]}
    many = {
        "signals": [
            _signal("domain:software", "software"),
            _signal("domain:cloud", "cloud"),
            _signal("domain:payments", "payments"),
        ]
    }
    retail = {"signals": [_signal("domain:retail", "retail")]}
    revenue = {"signals": [_signal("revenue", "$4 billion")]}
    base = calculate_priority(_job(), profile, now=NOW)
    one = calculate_priority(_job(), profile, now=NOW, company_context=software)
    extra = calculate_priority(_job(), profile, now=NOW, company_context=many)
    unrelated = calculate_priority(_job(), profile, now=NOW, company_context=retail)
    scale = calculate_priority(_job(), profile, now=NOW, company_context=revenue)
    assert one.components["company_domain_relevance"] == 100
    assert extra.components["company_domain_relevance"] == 100
    assert extra.score == one.score
    assert unrelated.components["company_domain_relevance"] is None
    assert unrelated.score == base.score
    assert scale.input_hash == base.input_hash
    assert scale.score == base.score


def test_us_presence_does_not_change_eligibility(profile: Profile) -> None:
    job = _job(eligibility_state="UNKNOWN")
    context = {
        "signals": [
            _signal("us_operations", True),
            _signal("sponsorship", "available"),
        ]
    }
    decision = calculate_priority(job, profile, now=NOW, company_context=context)
    without = calculate_priority(
        job,
        profile,
        now=NOW,
        company_context={"signals": [_signal("us_operations", True)]},
    )
    assert job.eligibility_state == "UNKNOWN"
    assert decision.components["program_evidence"] == 50
    assert decision.input_hash == without.input_hash
    assert decision.score == without.score


def test_missing_jd_is_omitted_and_truncated_stays_lower(profile: Profile) -> None:
    present = calculate_priority(_job(), profile, now=NOW)
    missing = calculate_priority(
        _job(description_clean=None, jd_status="missing"),
        profile,
        now=NOW,
    )
    suspicious = calculate_priority(
        _job(description_clean="Intern.", jd_status="suspicious"),
        profile,
        now=NOW,
    )
    truncated = calculate_priority(
        _job(jd_truncated=True, jd_status="truncated"),
        profile,
        now=NOW,
    )
    assert present.components["jd_evidence_quality"] == 80
    assert missing.components["jd_evidence_quality"] is None
    assert suspicious.components["jd_evidence_quality"] is None
    assert truncated.components["jd_evidence_quality"] == 40
    assert present.score > truncated.score


def test_secondary_role_must_be_a_different_target_family(profile: Profile) -> None:
    same = calculate_priority(
        _job(role_secondary_family="PRODUCT_MANAGEMENT"),
        profile,
        now=NOW,
    )
    other = calculate_priority(
        _job(role_secondary_family="OTHER"),
        profile,
        now=NOW,
    )
    consulting = calculate_priority(
        _job(role_secondary_family="CONSULTING"),
        profile,
        now=NOW,
    )
    assert same.components["secondary_role_bonus"] is None
    assert other.components["secondary_role_bonus"] is None
    assert consulting.components["secondary_role_bonus"] == 100
    assert consulting.components["primary_role_alignment"] == 100


def test_role_evidence_changes_the_priority_hash(profile: Profile) -> None:
    base = calculate_priority(_job(), profile, now=NOW)
    primary = calculate_priority(
        _job(role_evidence=["own the roadmap"]),
        profile,
        now=NOW,
    )
    secondary = calculate_priority(
        _job(role_secondary_evidence=["client workstream"]),
        profile,
        now=NOW,
    )
    assert primary.input_hash != base.input_hash
    assert secondary.input_hash != base.input_hash
    assert primary.score == base.score
    assert secondary.score == base.score


def test_priority_does_not_call_a_model(profile: Profile, monkeypatch: pytest.MonkeyPatch) -> None:
    def _boom(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("priority must not call a model")

    monkeypatch.setattr("scorer.fit.evaluate_fit", _boom)
    monkeypatch.setattr("scorer.embeddings.build_embedder", _boom)
    decision = calculate_priority(_job(), profile, now=NOW)
    assert decision.version == PRIORITY_VERSION
    assert decision.score == priority_mod.calculate_priority(_job(), profile, now=NOW).score

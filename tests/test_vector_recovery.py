"""Vector-gate rejects return to scoring only with independent role evidence."""

from __future__ import annotations

import pytest

from config.profile import Profile
from config.settings import get_settings
from core.db import (
    Job,
    Source,
    Status,
    StructuredJobDescription,
    get_job_by_id,
    session_scope,
)
from scorer.engine import ScoreSummary, score_pending
from scorer.vector_recovery import evaluate_recovery, load_recovery_config
from tests.test_scorer import FakeClient
from tests.test_vector_gate import FakeEmbedder, _enable, _map, _seed

_DESC = (
    "Python product role with 3 years experience and a focus on onboarding "
    "flows for new users across web and mobile."
)


def _doc(
    *,
    responsibilities: list[str] | None = None,
    qualifications: list[str] | None = None,
    mba_internship: bool | None = None,
) -> dict[str, object]:
    return {
        "responsibilities": {
            "items": [{"text": text} for text in responsibilities or []],
        },
        "qualifications": {
            "required": [{"text": text} for text in qualifications or []],
        },
        "program": {"mba_internship": mba_internship},
    }


async def _stamp(job: Job, **fields: object) -> None:
    async with session_scope() as session:
        assert job.id is not None
        target = await get_job_by_id(session, job.id)
        assert target is not None
        for key, value in fields.items():
            setattr(target, key, value)
        session.add(target)


async def _store_doc(job: Job, document: dict[str, object]) -> None:
    async with session_scope() as session:
        assert job.id is not None
        session.add(
            StructuredJobDescription(
                job_id=job.id,
                content_hash=f"structured-{job.id}",
                version="phase19-v1",
                availability="available",
                document=document,
            )
        )


async def _score(
    profile: Profile,
    jobs: list[tuple[Job, list[float]]],
    *,
    client: FakeClient | None = None,
) -> tuple[FakeClient, ScoreSummary]:
    embedder = FakeEmbedder(_map(profile, jobs))
    scorer = client or FakeClient()
    summary = await score_pending(
        client=scorer,
        profile=profile,
        embedder=embedder,
        generate_outreach=False,
        generate_cover_letter=False,
    )
    return scorer, summary


async def test_vector_accept_still_scores(
    db_ready: object,
    profile: Profile,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    _enable(monkeypatch)
    job = await _seed("near", title="Product Manager")
    client, summary = await _score(profile, [(job, [1.0, 0.0])])
    assert summary.scored == 1
    assert summary.vector_recovered == 0
    assert len(client.calls) == 1
    async with session_scope() as session:
        saved = await get_job_by_id(session, job.id or 0)
        assert saved is not None
        assert saved.vector_decision == "pass"
        assert saved.vector_recovery is None
        assert saved.score == 72


async def test_irrelevant_reject_stays_rejected(
    db_ready: object,
    profile: Profile,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    _enable(monkeypatch)
    job = await _seed("far", title="Warehouse Associate")
    client, summary = await _score(profile, [(job, [0.0, 1.0])])
    assert summary.scored == 0
    assert summary.vector_rejected == 1
    assert summary.vector_recovered == 0
    assert client.calls == []
    async with session_scope() as session:
        saved = await get_job_by_id(session, job.id or 0)
        assert saved is not None
        assert saved.status.value == "filtered_out"
        assert saved.vector_decision == "reject"
        assert saved.vector_recovery == "rejected"
        assert saved.vector_recovery_reason == "insufficient_evidence"
        assert saved.score == 0


async def test_strong_target_role_is_recovered(
    db_ready: object,
    profile: Profile,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    _enable(monkeypatch)
    job = await _seed("pm", title="MBA Intern")
    await _stamp(
        job,
        role_family="PRODUCT_MANAGEMENT",
        role_confidence="high",
        role_evidence=["own the product roadmap", "define requirements"],
    )
    await _store_doc(job, _doc(mba_internship=True, responsibilities=["Host weekly office hours"]))
    client, summary = await _score(profile, [(job, [0.0, 1.0])])
    assert summary.vector_recovered == 1
    assert summary.vector_rejected == 0
    assert summary.scored == 1
    assert len(client.calls) == 1
    async with session_scope() as session:
        saved = await get_job_by_id(session, job.id or 0)
        assert saved is not None
        assert saved.vector_decision == "recovered"
        assert saved.vector_recovery == "recovered"
        assert saved.vector_recovery_reason == "mba_program+primary_role"
        assert saved.score == 72
        assert saved.priority_score is not None
        assert saved.portfolio_decision is None
        assert saved.portfolio_version is None


async def test_secondary_and_responsibility_evidence_recovers(
    db_ready: object,
    profile: Profile,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    _enable(monkeypatch)
    job = await _seed("hybrid", title="Summer Associate")
    await _stamp(
        job,
        role_family="OTHER",
        role_confidence="low",
        role_evidence=["mentioned in passing"],
        role_secondary_family="CONSULTING",
        role_secondary_confidence="high",
        role_secondary_evidence=["lead the client workstream"],
    )
    await _store_doc(
        job,
        _doc(responsibilities=["Run the management consulting workstream for the region"]),
    )
    _client, summary = await _score(profile, [(job, [0.0, 1.0])])
    assert summary.vector_recovered == 1
    assert summary.scored == 1
    async with session_scope() as session:
        saved = await get_job_by_id(session, job.id or 0)
        assert saved is not None
        assert saved.vector_recovery_reason == "responsibility_function+secondary_role"
        assert saved.score == 72


async def test_weak_keyword_does_not_recover(
    db_ready: object,
    profile: Profile,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    _enable(monkeypatch)
    job = await _seed("weak", title="Strategy Intern")
    await _stamp(
        job,
        role_family="STRATEGY_TRANSFORMATION",
        role_confidence="low",
        role_evidence=["strategy"],
    )
    client, summary = await _score(profile, [(job, [0.0, 1.0])])
    assert client.calls == []
    assert summary.vector_rejected == 1
    assert summary.vector_recovered == 0


async def test_qualification_only_does_not_recover(
    db_ready: object,
    profile: Profile,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    _enable(monkeypatch)
    job = await _seed("qual", title="Operations Associate")
    await _stamp(job, role_family="UNKNOWN", role_confidence="low", role_evidence=["unclear"])
    await _store_doc(
        job,
        _doc(
            responsibilities=["Operate the warehouse overnight"],
            qualifications=["product management experience required"],
        ),
    )
    client, summary = await _score(profile, [(job, [0.0, 1.0])])
    assert client.calls == []
    assert summary.vector_recovered == 0
    assert summary.vector_rejected == 1


async def test_mba_wording_alone_does_not_recover(
    db_ready: object,
    profile: Profile,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    _enable(monkeypatch)
    job = await _seed("mba-only", title="Clinical Intern")
    await _stamp(
        job,
        role_family="OTHER",
        role_confidence="medium",
        role_evidence=["clinical care"],
    )
    await _store_doc(
        job,
        _doc(
            mba_internship=True,
            responsibilities=["Provide bedside nursing care"],
        ),
    )
    client, summary = await _score(profile, [(job, [0.0, 1.0])])
    assert client.calls == []
    assert summary.vector_rejected == 1
    async with session_scope() as session:
        saved = await get_job_by_id(session, job.id or 0)
        assert saved is not None
        assert saved.vector_recovery_reason == "insufficient_evidence:mba_program"


async def test_hard_filter_cannot_be_recovered(
    db_ready: object,
    profile: Profile,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    _enable(monkeypatch)
    job = await _seed(
        "clearance",
        title="Product Manager",
        description=_DESC + " security clearance required",
    )
    await _stamp(
        job,
        role_family="PRODUCT_MANAGEMENT",
        role_confidence="high",
        role_evidence=["own the roadmap"],
    )
    decision = evaluate_recovery(
        job,
        profile,
        document=_doc(mba_internship=True, responsibilities=["Own product management"]),
    )
    assert decision.recovered is False
    assert decision.reason == "hard_filter"
    client, summary = await _score(profile, [(job, [0.0, 1.0])])
    assert client.calls == []
    assert summary.vector_recovered == 0
    async with session_scope() as session:
        saved = await get_job_by_id(session, job.id or 0)
        assert saved is not None
        assert saved.vector_decision is None
        assert saved.vector_recovery is None
        assert saved.status.value == "filtered_out"


async def test_clearly_ineligible_cannot_be_recovered(
    db_ready: object,
    profile: Profile,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    _enable(monkeypatch)
    job = await _seed("blocked", title="Product Manager")
    await _stamp(
        job,
        role_family="PRODUCT_MANAGEMENT",
        role_confidence="high",
        role_evidence=["own the roadmap"],
        eligibility_state="CLEARLY_INELIGIBLE",
    )
    await _store_doc(job, _doc(mba_internship=True))
    client, summary = await _score(profile, [(job, [0.0, 1.0])])
    assert client.calls == []
    assert summary.vector_rejected == 1
    async with session_scope() as session:
        saved = await get_job_by_id(session, job.id or 0)
        assert saved is not None
        assert saved.status.value == "filtered_out"
        assert saved.vector_decision == "reject"
        assert saved.vector_recovery_reason == "clearly_ineligible"
        assert saved.eligibility_state == "CLEARLY_INELIGIBLE"


async def test_recovery_does_not_change_priority_or_portfolio(
    db_ready: object,
    profile: Profile,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    _enable(monkeypatch)
    accepted = await _seed("same-pass", title="Product Manager North", company="Acme")
    recovered = await _seed("same-back", title="Product Manager South", company="Acme")
    fields = {
        "role_family": "PRODUCT_MANAGEMENT",
        "role_confidence": "high",
        "role_evidence": ["own the product roadmap"],
    }
    await _stamp(accepted, **fields)
    await _stamp(recovered, **fields)
    document = _doc(mba_internship=True, responsibilities=["Own product management"])
    await _store_doc(accepted, document)
    await _store_doc(recovered, document)
    _client, summary = await _score(
        profile,
        [(accepted, [1.0, 0.0]), (recovered, [0.0, 1.0])],
    )
    assert summary.scored == 2
    assert summary.vector_recovered == 1
    async with session_scope() as session:
        passed = await get_job_by_id(session, accepted.id or 0)
        brought = await get_job_by_id(session, recovered.id or 0)
        assert passed is not None and brought is not None
        assert passed.vector_decision == "pass"
        assert brought.vector_decision == "recovered"
        assert passed.score == brought.score == 72
        assert passed.priority_score == brought.priority_score
        assert passed.priority_version == brought.priority_version
        assert brought.portfolio_decision is None
        assert brought.portfolio_config_hash is None


def test_recovery_is_deterministic(profile: Profile) -> None:
    job = Job(
        source=Source.linkedin,
        external_id="det",
        title="Product Manager",
        company="Acme",
        url="https://example.com/det",
        description_clean=_DESC,
        role_family="PRODUCT_MANAGEMENT",
        role_confidence="high",
        role_evidence=["own the roadmap"],
    )
    document = _doc(mba_internship=True)
    first = evaluate_recovery(job, profile, document=document, structured_hash="a")
    second = evaluate_recovery(job, profile, document=document, structured_hash="a")
    assert first == second
    assert first.recovered is True
    assert job.score is None
    assert job.priority_score is None
    assert job.portfolio_decision is None


async def test_stale_recovery_hash_is_reopened(
    db_ready: object,
    profile: Profile,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    _enable(monkeypatch)
    job = await _seed("stale", title="Product Manager", status=Status.filtered_out)
    await _stamp(
        job,
        status=Status.filtered_out,
        role_family="PRODUCT_MANAGEMENT",
        role_confidence="high",
        role_evidence=["own the product roadmap"],
        embedding=[0.0, 1.0],
        embedding_model=get_settings().openai_embedding_model,
        vector_score=0.0,
        vector_profile_hash="stale-profile",
        vector_decision="reject",
        vector_recovery="rejected",
        vector_recovery_reason="insufficient_evidence",
        vector_recovery_hash="old-hash",
        score=0,
    )
    await _store_doc(job, _doc(mba_internship=True))
    client, summary = await _score(profile, [(job, [0.0, 1.0])])
    assert summary.scored == 1
    assert summary.vector_recovered == 1
    assert len(client.calls) == 1
    async with session_scope() as session:
        saved = await get_job_by_id(session, job.id or 0)
        assert saved is not None
        assert saved.vector_decision == "recovered"
        assert saved.vector_recovery_hash != "old-hash"
        assert saved.score == 72


async def test_config_change_reopens_a_stored_reject(
    db_ready: object,
    profile: Profile,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    _enable(monkeypatch)
    job = await _seed("config", title="Product Manager")
    await _stamp(
        job,
        role_family="CONSULTING",
        role_confidence="high",
        role_evidence=["lead the engagement"],
    )
    client, summary = await _score(profile, [(job, [0.0, 1.0])])
    assert summary.vector_rejected == 1
    assert client.calls == []
    loosened = load_recovery_config()
    rules = dict(loosened["recovery"])
    rules["min_groups"] = 1
    patched = {"version": loosened["version"], "recovery": rules}
    monkeypatch.setattr(
        "scorer.vector_recovery.load_recovery_config",
        lambda path=None: patched,
    )
    again = FakeClient()
    summary = await score_pending(
        client=again,
        profile=profile,
        embedder=FakeEmbedder(_map(profile, [(job, [0.0, 1.0])])),
        generate_outreach=False,
        generate_cover_letter=False,
    )
    assert summary.scored == 1
    assert summary.vector_recovered == 1
    assert len(again.calls) == 1


async def test_embedder_failure_still_fails_open(
    db_ready: object,
    profile: Profile,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    _enable(monkeypatch)
    job = await _seed("down", title="Product Manager")
    embedder = FakeEmbedder({}, fail=True)
    client = FakeClient()
    summary = await score_pending(
        client=client,
        profile=profile,
        embedder=embedder,
        generate_outreach=False,
        generate_cover_letter=False,
    )
    assert summary.scored == 1
    assert summary.vector_rejected == 0
    assert summary.vector_recovered == 0
    assert len(client.calls) == 1
    async with session_scope() as session:
        saved = await get_job_by_id(session, job.id or 0)
        assert saved is not None
        assert saved.vector_recovery is None
        assert saved.score == 72


async def test_recovery_failure_keeps_the_vector_reject(
    db_ready: object,
    profile: Profile,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    _enable(monkeypatch)

    def _boom(*_args: object, **_kwargs: object) -> object:
        raise RuntimeError("recovery down")

    monkeypatch.setattr("scorer.engine.evaluate_recovery", _boom)
    job = await _seed("boom", title="Product Manager")
    client, summary = await _score(profile, [(job, [0.0, 1.0])])
    assert summary.scored == 0
    assert summary.vector_rejected == 1
    assert client.calls == []
    async with session_scope() as session:
        saved = await get_job_by_id(session, job.id or 0)
        assert saved is not None
        assert saved.status.value == "filtered_out"
        assert saved.vector_decision == "reject"
        assert saved.vector_recovery_reason == "recovery_failed"


async def test_repeated_scoring_is_stable(
    db_ready: object,
    profile: Profile,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    _enable(monkeypatch)
    job = await _seed("twice", title="Product Manager")
    await _stamp(
        job,
        role_family="PRODUCT_MANAGEMENT",
        role_confidence="high",
        role_evidence=["own the product roadmap"],
    )
    await _store_doc(job, _doc(mba_internship=True))
    first, summary = await _score(profile, [(job, [0.0, 1.0])])
    assert summary.scored == 1
    second, again = await _score(profile, [(job, [0.0, 1.0])], client=FakeClient())
    assert again.scored == 0
    assert again.vector_recovered == 0
    assert first.calls and second.calls == []
    async with session_scope() as session:
        saved = await get_job_by_id(session, job.id or 0)
        assert saved is not None
        assert saved.score == 72
        assert saved.vector_decision == "recovered"

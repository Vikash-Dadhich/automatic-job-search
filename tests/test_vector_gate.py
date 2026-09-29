"""Offline tests for the embedding gate in front of the LLM scorer."""

from __future__ import annotations

import pytest

from config.profile import Profile
from config.settings import get_settings
from core.db import Job, Source, Status, Tier, get_job_by_id, session_scope, upsert_job
from scorer.embeddings import (
    build_embedder,
    clears_threshold,
    cosine,
    job_embed_text,
    profile_embed_text,
    profile_hash,
)
from scorer.engine import score_pending
from tests.test_scorer import FakeClient


class FakeEmbedder:
    def __init__(self, vectors: dict[str, list[float]], *, fail: bool = False) -> None:
        self.vectors = vectors
        self.fail = fail
        self.calls: list[list[str]] = []

    async def embed(self, texts: list[str]) -> list[list[float]]:
        self.calls.append(list(texts))
        if self.fail:
            raise RuntimeError("embed down")
        return [self.vectors[text] for text in texts]


def _enable(monkeypatch: pytest.MonkeyPatch, **env: str) -> None:
    monkeypatch.setenv("VECTOR_GATE_ENABLED", "true")
    monkeypatch.setenv("VECTOR_DIMENSIONS", env.pop("VECTOR_DIMENSIONS", "2"))
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    get_settings.cache_clear()


_DESC = (
    "Python product role with 3 years experience and a focus on onboarding "
    "flows for new users across web and mobile."
)


async def _seed(
    external_id: str,
    *,
    title: str,
    company: str = "Acme",
    description: str | None = _DESC,
    status: Status = Status.discovered,
) -> Job:
    job = Job(
        source=Source.linkedin,
        external_id=external_id,
        title=title,
        company=company,
        location="Remote",
        url=f"https://example.com/{external_id}",
        description_clean=description,
        status=status,
    )
    async with session_scope() as session:
        return await upsert_job(session, job)


def _map(profile: Profile, jobs: list[tuple[Job, list[float]]]) -> dict[str, list[float]]:
    mapped = {profile_embed_text(profile): [1.0, 0.0]}
    for job, vector in jobs:
        mapped[job_embed_text(job)] = vector
    return mapped


def test_cosine_identical_and_orthogonal() -> None:
    assert cosine([1.0, 0.0], [1.0, 0.0]) == 1.0
    assert cosine([1.0, 0.0], [0.0, 1.0]) == 0.0
    with pytest.raises(ValueError):
        cosine([1.0, 0.0], [1.0, 0.0, 0.0])


def test_threshold_is_inclusive(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VECTOR_THRESHOLD", "0.50")
    get_settings.cache_clear()
    assert clears_threshold(0.50)
    assert not clears_threshold(0.49)


def test_build_embedder_without_key_returns_none(monkeypatch: pytest.MonkeyPatch) -> None:
    _enable(monkeypatch, OPENAI_API_KEY="")
    assert build_embedder() is None


async def test_gate_rejects_orthogonal_and_scores_match(
    db_ready: object,
    profile: Profile,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable(monkeypatch)
    near = await _seed("near", title="Product Manager", company="NearCo")
    far = await _seed("far", title="Product Manager", company="FarCo")
    embedder = FakeEmbedder(_map(profile, [(near, [1.0, 0.0]), (far, [0.0, 1.0])]))
    client = FakeClient()
    summary = await score_pending(
        client=client,
        profile=profile,
        embedder=embedder,
        generate_outreach=False,
        generate_cover_letter=False,
    )
    assert summary.vector_rejected == 1
    assert summary.vector_errors == 0
    assert summary.scored == 1
    assert len(client.calls) == 1
    async with session_scope() as session:
        assert near.id is not None and far.id is not None
        kept = await get_job_by_id(session, near.id)
        dropped = await get_job_by_id(session, far.id)
        assert kept is not None and dropped is not None
        assert kept.status == Status.staged
        assert kept.vector_decision == "pass"
        assert dropped.status == Status.filtered_out
        assert dropped.vector_decision == "reject"
        assert dropped.justification is not None
        assert dropped.justification[0].startswith("vector gate:")


async def test_dream_company_bypasses_low_cosine(
    db_ready: object,
    profile: Profile,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable(monkeypatch)
    tuned = profile.model_copy(deep=True)
    tuned.preferences.dream_companies = ["DreamCo"]
    job = await _seed("dream", title="Product Manager", company="DreamCo")
    embedder = FakeEmbedder(_map(tuned, [(job, [0.0, 1.0])]))
    client = FakeClient()
    summary = await score_pending(
        client=client,
        profile=tuned,
        embedder=embedder,
        generate_outreach=False,
        generate_cover_letter=False,
    )
    assert summary.vector_rejected == 0
    assert summary.scored == 1
    async with session_scope() as session:
        assert job.id is not None
        saved = await get_job_by_id(session, job.id)
        assert saved is not None
        assert saved.vector_decision == "pass"
        assert saved.status == Status.staged


async def test_clearance_is_not_embedded(
    db_ready: object,
    profile: Profile,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable(monkeypatch)
    await _seed(
        "clearance",
        title="Product Manager",
        description=_DESC + " security clearance required",
    )
    embedder = FakeEmbedder({})
    client = FakeClient()
    summary = await score_pending(
        client=client,
        profile=profile,
        embedder=embedder,
        generate_outreach=False,
        generate_cover_letter=False,
    )
    assert embedder.calls == []
    assert client.calls == []
    assert summary.vector_rejected == 0
    assert summary.filtered_out == 1


async def test_short_text_fails_open_without_embed(
    db_ready: object,
    profile: Profile,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable(monkeypatch)
    await _seed("tiny", title="PM", company="A", description="")
    embedder = FakeEmbedder({})
    client = FakeClient()
    summary = await score_pending(
        client=client,
        profile=profile,
        embedder=embedder,
        generate_outreach=False,
        generate_cover_letter=False,
    )
    assert embedder.calls == []
    assert summary.vector_errors == 0
    assert client.calls == []
    assert summary.scored == 0
    assert summary.skipped == 1


async def test_embedder_failure_scores_anyway(
    db_ready: object,
    profile: Profile,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable(monkeypatch)
    await _seed("a", title="Product Manager", company="Aco")
    await _seed("b", title="Product Manager", company="Bco")
    embedder = FakeEmbedder({}, fail=True)
    client = FakeClient()
    summary = await score_pending(
        client=client,
        profile=profile,
        embedder=embedder,
        generate_outreach=False,
        generate_cover_letter=False,
    )
    assert summary.vector_rejected == 0
    assert summary.vector_errors == 2
    assert summary.scored == 2


async def test_cached_embedding_skips_job_text(
    db_ready: object,
    profile: Profile,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable(monkeypatch)
    job = await _seed("cached", title="Product Manager", company="CacheCo")
    digest = profile_hash(profile_embed_text(profile))
    async with session_scope() as session:
        assert job.id is not None
        target = await get_job_by_id(session, job.id)
        assert target is not None
        target.embedding = [1.0, 0.0]
        target.embedding_model = get_settings().openai_embedding_model
        target.vector_score = 0.9
        target.vector_profile_hash = digest
        target.vector_decision = "pass"
        session.add(target)
    embedder = FakeEmbedder({})
    summary = await score_pending(
        client=FakeClient(),
        profile=profile,
        embedder=embedder,
        generate_outreach=False,
        generate_cover_letter=False,
    )
    assert embedder.calls == []
    assert summary.scored == 1
    assert summary.vector_rejected == 0


async def test_budget_skips_tail_after_a_reject(
    db_ready: object,
    profile: Profile,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable(monkeypatch, SCORE_BUDGET="1")
    first = await _seed("first", title="Product Manager Intern", company="FirstCo")
    second = await _seed("second", title="Product Manager", company="SecondCo")
    third = await _seed("third", title="Coordinator", company="ThirdCo")
    embedder = FakeEmbedder(
        _map(
            profile,
            [(first, [0.0, 1.0]), (second, [1.0, 0.0]), (third, [1.0, 0.0])],
        )
    )
    client = FakeClient()
    summary = await score_pending(
        client=client,
        profile=profile,
        embedder=embedder,
        generate_outreach=False,
        generate_cover_letter=False,
    )
    assert summary.vector_rejected == 1
    assert summary.scored == 1
    assert summary.skipped == 1
    assert len(client.calls) == 1
    sent = " ".join(call["user"] for call in client.calls)
    assert "SecondCo" in sent
    assert "ThirdCo" not in sent
    async with session_scope() as session:
        assert third.id is not None
        held = await get_job_by_id(session, third.id)
        assert held is not None
        assert held.status == Status.discovered


async def test_gate_disabled_does_not_embed(
    db_ready: object,
    profile: Profile,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("VECTOR_GATE_ENABLED", "false")
    get_settings.cache_clear()
    await _seed("off-a", title="Product Manager", company="Aco")
    await _seed("off-b", title="Product Manager", company="Bco")
    embedder = FakeEmbedder({}, fail=True)
    summary = await score_pending(
        client=FakeClient(),
        profile=profile,
        embedder=embedder,
        generate_outreach=False,
        generate_cover_letter=False,
    )
    assert embedder.calls == []
    assert summary.scored == 2
    assert summary.vector_rejected == 0


async def test_content_hash_change_clears_vector(db_ready: object) -> None:
    original = Job(
        source=Source.linkedin,
        external_id="hash-vec",
        title="Product Manager",
        company="Acme",
        location="Remote",
        url="https://example.com/hash-vec",
        description_clean=_DESC,
        content_hash="hash-v1",
        status=Status.discovered,
    )
    async with session_scope() as session:
        saved = await upsert_job(session, original)
        assert saved.id is not None
        saved.embedding = [1.0, 0.0]
        saved.vector_score = 0.2
        saved.vector_profile_hash = "abc"
        saved.vector_decision = "reject"
        session.add(saved)
        job_id = saved.id

    same = Job(
        source=Source.linkedin,
        external_id="hash-vec",
        title="Product Manager",
        company="Acme",
        location="Remote",
        url="https://example.com/hash-vec",
        description_clean=_DESC,
        content_hash="hash-v1",
        status=Status.discovered,
    )
    async with session_scope() as session:
        await upsert_job(session, same)
        kept = await get_job_by_id(session, job_id)
        assert kept is not None
        assert kept.embedding == [1.0, 0.0]
        assert kept.vector_decision == "reject"

    changed = Job(
        source=Source.linkedin,
        external_id="hash-vec",
        title="Product Manager",
        company="Acme",
        location="Remote",
        url="https://example.com/hash-vec",
        description_clean=_DESC + " updated duties",
        content_hash="hash-v2",
        status=Status.discovered,
    )
    async with session_scope() as session:
        await upsert_job(session, changed)
        cleared = await get_job_by_id(session, job_id)
        assert cleared is not None
        assert cleared.embedding is None
        assert cleared.vector_score is None
        assert cleared.vector_profile_hash is None
        assert cleared.vector_decision is None


async def test_reopen_when_threshold_drops(
    db_ready: object,
    profile: Profile,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable(monkeypatch, VECTOR_THRESHOLD="0.40")
    job = await _seed(
        "reopen",
        title="Product Manager",
        company="ReopenCo",
        status=Status.filtered_out,
    )
    digest = profile_hash(profile_embed_text(profile))
    async with session_scope() as session:
        assert job.id is not None
        target = await get_job_by_id(session, job.id)
        assert target is not None
        target.status = Status.filtered_out
        target.embedding = [1.0, 0.0]
        target.embedding_model = get_settings().openai_embedding_model
        target.vector_score = 0.42
        target.vector_profile_hash = digest
        target.vector_decision = "reject"
        target.score = 0
        target.tier = Tier.three
        session.add(target)
    embedder = FakeEmbedder({})
    summary = await score_pending(
        client=FakeClient(),
        profile=profile,
        embedder=embedder,
        generate_outreach=False,
        generate_cover_letter=False,
    )
    assert embedder.calls == []
    assert summary.scored == 1
    assert summary.vector_rejected == 0


async def test_reopen_stays_closed_when_still_below(
    db_ready: object,
    profile: Profile,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable(monkeypatch, VECTOR_THRESHOLD="0.50")
    job = await _seed(
        "stay",
        title="Product Manager",
        company="StayCo",
        status=Status.filtered_out,
    )
    digest = profile_hash(profile_embed_text(profile))
    async with session_scope() as session:
        assert job.id is not None
        target = await get_job_by_id(session, job.id)
        assert target is not None
        target.status = Status.filtered_out
        target.embedding = [1.0, 0.0]
        target.embedding_model = get_settings().openai_embedding_model
        target.vector_score = 0.42
        target.vector_profile_hash = digest
        target.vector_decision = "reject"
        session.add(target)
    summary = await score_pending(
        client=FakeClient(),
        profile=profile,
        embedder=FakeEmbedder({}),
        generate_outreach=False,
        generate_cover_letter=False,
    )
    assert summary.scored == 0
    assert summary.vector_rejected == 0
    async with session_scope() as session:
        assert job.id is not None
        saved = await get_job_by_id(session, job.id)
        assert saved is not None
        assert saved.status == Status.filtered_out


async def test_profile_change_reuses_jd_vector(
    db_ready: object,
    profile: Profile,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable(monkeypatch)
    job = await _seed(
        "profile-shift",
        title="Product Manager",
        company="ShiftCo",
        status=Status.filtered_out,
    )
    async with session_scope() as session:
        assert job.id is not None
        target = await get_job_by_id(session, job.id)
        assert target is not None
        target.status = Status.filtered_out
        target.embedding = [0.0, 1.0]
        target.embedding_model = get_settings().openai_embedding_model
        target.vector_score = 0.1
        target.vector_profile_hash = "old-hash"
        target.vector_decision = "reject"
        session.add(target)
    embedder = FakeEmbedder({profile_embed_text(profile): [1.0, 0.0]})
    summary = await score_pending(
        client=FakeClient(),
        profile=profile,
        embedder=embedder,
        generate_outreach=False,
        generate_cover_letter=False,
    )
    assert summary.scored == 0
    flat = [text for batch in embedder.calls for text in batch]
    assert job_embed_text(job) not in flat
    assert all(text == profile_embed_text(profile) for text in flat)
    async with session_scope() as session:
        assert job.id is not None
        saved = await get_job_by_id(session, job.id)
        assert saved is not None
        assert saved.status == Status.filtered_out
        assert saved.vector_profile_hash == profile_hash(profile_embed_text(profile))
        assert saved.vector_score == 0.0

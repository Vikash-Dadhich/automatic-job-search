"""Candidate-to-JD fit. Mocked model, no network."""

from __future__ import annotations

import json
from pathlib import Path

from config.profile import Profile
from core.db import Job, Source, Status, get_job_by_id, session_scope, upsert_job
from scorer.engine import Scorer
from scorer.fit import (
    DIMENSIONS,
    FIT_VERSION,
    build_fit_system_blocks,
    build_fit_user,
    evaluate_fit,
    fit_context_block,
    fit_is_current,
    profile_fit_hash,
)

_LONG = (
    "Own roadmap prioritization with engineering and design, define requirements, "
    "and analyze customer needs across the summer internship."
)


def _dims(risk: str = "unknown") -> dict[str, dict[str, str]]:
    dims = {name: {"judgment": "transferable_match", "note": "grounded"} for name in DIMENSIONS}
    dims["REQUIREMENTS_RISK"] = {"judgment": risk, "note": "requirement note"}
    return dims


def _payload(score: int, risk: str = "unknown", strengths: list[str] | None = None) -> str:
    return json.dumps(
        {
            "fit_score": score,
            "confidence": "high",
            "strengths": strengths
            or ["Roadmap ownership maps to the candidate's platform migration leadership."],
            "gaps": [],
            "evidence": ["The description asks for roadmap prioritization."],
            "dimensions": _dims(risk),
        }
    )


class _Client:
    def __init__(self, payload: str) -> None:
        self.payload = payload
        self.calls = 0
        self.user = ""
        self.system = ""

    async def complete(self, **kwargs: object) -> str:
        self.calls += 1
        self.user = str(kwargs.get("user") or "")
        blocks = kwargs.get("system_blocks")
        if isinstance(blocks, list) and blocks:
            self.system = str(blocks[0].get("text") if isinstance(blocks[0], dict) else "")
        return self.payload


def _job(profile_text: str = _LONG, **kwargs: object) -> Job:
    data: dict[str, object] = {
        "source": Source.linkedin,
        "external_id": "fit-1",
        "title": "Product Manager Intern",
        "company": "GoodCo",
        "location": "Remote",
        "url": "https://example.com/fit",
        "description_clean": profile_text,
        "content_hash": "jd-hash",
        "jd_status": "present",
        "role_family": "PRODUCT_MANAGEMENT",
        "role_subfamily": "PM_CORE",
        "role_confidence": "high",
        "discovery_family": "CONSULTING",
        "discovery_query": "Consulting Intern",
    }
    data.update(kwargs)
    return Job(**data)  # type: ignore[arg-type]


def test_fit_context_keeps_match_facts_and_drops_contact_details(profile: Profile) -> None:
    block = fit_context_block(profile)
    assert profile.education[0].degree in block
    assert profile.education[0].school in block
    assert profile.experience[0].title in block
    assert profile.experience[0].company in block
    assert profile.skills[0] in block
    assert profile.identity.location in block
    assert "remote_ok=" in block
    assert profile.identity.email not in block
    assert profile.identity.phone not in block
    assert profile.identity.linkedin_url not in block
    assert profile.identity.github_url not in block
    assert "sponsorship" not in block.lower()
    assert "f-1" not in block.lower()
    assert "dream" not in block.lower()


def test_fit_hash_tracks_match_facts_only(profile: Profile) -> None:
    original = profile_fit_hash(profile)
    with_skill = profile.model_copy(update={"skills": [*profile.skills, "Origami"]})
    bullet = profile.experience[0].model_copy(
        update={"bullets": [*profile.experience[0].bullets, "Added a delivery bullet."]}
    )
    with_bullet = profile.model_copy(
        update={"experience": [bullet, *profile.experience[1:]]}
    )
    school = profile.education[0].model_copy(update={"graduation_date": "2029-06"})
    with_school = profile.model_copy(update={"education": [school, *profile.education[1:]]})
    moved = profile.model_copy(
        update={
            "preferences": profile.preferences.model_copy(update={"remote_ok": False}),
            "identity": profile.identity.model_copy(update={"location": "Austin, TX"}),
        }
    )
    assert profile_fit_hash(with_skill) != original
    assert profile_fit_hash(with_bullet) != original
    assert profile_fit_hash(with_school) != original
    assert profile_fit_hash(moved) != original

    same = original
    for updated in (
        profile.model_copy(
            update={"identity": profile.identity.model_copy(update={"email": "other@example.com"})}
        ),
        profile.model_copy(
            update={"identity": profile.identity.model_copy(update={"phone": "+1-555-0100"})}
        ),
        profile.model_copy(
            update={
                "identity": profile.identity.model_copy(
                    update={"linkedin_url": "https://www.linkedin.com/in/someone-else"}
                )
            }
        ),
        profile.model_copy(
            update={
                "identity": profile.identity.model_copy(
                    update={"github_url": "https://github.com/someone-else"}
                )
            }
        ),
        profile.model_copy(
            update={"identity": profile.identity.model_copy(update={"full_name": "Other Name"})}
        ),
        profile.model_copy(
            update={
                "work_authorization": profile.work_authorization.model_copy(
                    update={"sponsorship_required": False, "needs_visa_sponsorship": False}
                )
            }
        ),
        profile.model_copy(
            update={
                "preferences": profile.preferences.model_copy(
                    update={"dream_companies": ["Acme Dream Co"]}
                )
            }
        ),
    ):
        assert profile_fit_hash(updated) == same


def test_phase6_v1_fit_is_stale(profile: Profile) -> None:
    job = _job()
    job.score = 80
    job.fit_confidence = "high"
    job.fit_content_hash = job.content_hash
    job.fit_profile_hash = profile_fit_hash(profile)
    job.fit_version = "phase6-v1"
    assert FIT_VERSION == "phase6-v2"
    assert fit_is_current(job, profile) is False
    job.fit_version = FIT_VERSION
    assert fit_is_current(job, profile) is True


async def test_fit_prompt_uses_profile_and_role_not_discovery(profile: Profile) -> None:
    job = _job()
    client = _Client(_payload(84))
    decision = await evaluate_fit(job, profile, client, model="test", max_tokens=256)
    assert decision.available is True
    assert decision.score == 84
    assert profile.identity.full_name not in client.system
    assert profile.skills[0] in client.system
    assert "transferable" in client.system.lower()
    assert "prestige" in client.system.lower()
    assert "PRODUCT_MANAGEMENT" in client.user
    assert "PM_CORE" in client.user
    assert "Consulting Intern" not in client.user
    assert client.calls == 1


async def test_company_and_vector_do_not_change_fit_score(profile: Profile) -> None:
    dream = profile.model_copy(
        update={
            "preferences": profile.preferences.model_copy(update={"dream_companies": ["DreamCo"]})
        }
    )
    first = await evaluate_fit(
        _job(company="DreamCo", vector_score=0.99),
        dream,
        _Client(_payload(60)),
        model="test",
        max_tokens=128,
    )
    second = await evaluate_fit(
        _job(company="UnknownCo", external_id="fit-2", vector_score=0.01),
        dream,
        _Client(_payload(60)),
        model="test",
        max_tokens=128,
    )
    assert first.score == second.score == 60


async def test_preferred_gap_required_gap_and_conflict(profile: Profile) -> None:
    preferred = await evaluate_fit(
        _job(),
        profile,
        _Client(_payload(78, "unknown")),
        model="test",
        max_tokens=128,
    )
    required = await evaluate_fit(
        _job(),
        profile,
        _Client(_payload(62, "gap")),
        model="test",
        max_tokens=128,
    )
    conflict = await evaluate_fit(
        _job(),
        profile,
        _Client(_payload(35, "conflict")),
        model="test",
        max_tokens=128,
    )
    assert preferred.score == 78
    assert preferred.dimensions["REQUIREMENTS_RISK"]["judgment"] == "unknown"
    assert required.score == 62
    assert required.dimensions["REQUIREMENTS_RISK"]["judgment"] == "gap"
    assert conflict.score == 35
    assert conflict.dimensions["REQUIREMENTS_RISK"]["judgment"] == "conflict"


async def test_truncated_jd_does_not_receive_a_fit_score(profile: Profile) -> None:
    client = _Client(_payload(91))
    job = _job(jd_truncated=True, jd_status="truncated")
    decision = await evaluate_fit(job, profile, client, model="test", max_tokens=64)
    assert decision.available is False
    assert decision.score is None
    assert client.calls == 0
    complete = await evaluate_fit(_job(), profile, client, model="test", max_tokens=64)
    assert complete.available is True
    assert complete.score == 91
    assert client.calls == 1
    missing = await evaluate_fit(
        _job(description_clean="", jd_status="missing"),
        profile,
        client,
        model="test",
        max_tokens=64,
    )
    assert missing.available is False
    assert missing.score is None


async def test_short_jd_skips_the_model(profile: Profile) -> None:
    client = _Client(_payload(0))
    decision = await evaluate_fit(
        _job(description_clean="Intern.", jd_status="suspicious", content_hash="short"),
        profile,
        client,
        model="test",
        max_tokens=64,
    )
    assert decision.available is False
    assert decision.score is None
    assert client.calls == 0


async def test_invalid_payload_and_invented_skill(profile: Profile) -> None:
    broken = await evaluate_fit(
        _job(),
        profile,
        _Client("not-json"),
        model="test",
        max_tokens=64,
    )
    assert broken.available is False
    invented = _payload(95, strengths=["Candidate completed a neurosurgery residency."])
    rejected = await evaluate_fit(
        _job(),
        profile,
        _Client(invented),
        model="test",
        max_tokens=64,
    )
    blob = " ".join(rejected.strengths + rejected.gaps + rejected.evidence).lower()
    assert "neurosurgery" not in blob
    bad_confidence = json.loads(_payload(80))
    bad_confidence["confidence"] = "extremely_sure"
    invalid = await evaluate_fit(
        _job(),
        profile,
        _Client(json.dumps(bad_confidence)),
        model="test",
        max_tokens=64,
    )
    assert invalid.available is False


async def test_fit_cache_tracks_jd_profile_and_version(profile: Profile, db_ready: Path) -> None:
    del db_ready
    job = _job()
    client = _Client(_payload(81))
    first = await evaluate_fit(job, profile, client, model="test", max_tokens=64)
    assert first.score == 81
    job.score = 81
    job.fit_confidence = "high"
    job.fit_version = FIT_VERSION
    job.fit_content_hash = job.content_hash
    job.fit_profile_hash = first.profile_hash
    job.fit_strengths = ["cached"]
    job.fit_evidence = ["cached"]
    cached = await evaluate_fit(job, profile, client, model="test", max_tokens=64)
    assert cached.score == 81
    assert cached.evidence == ["cached"]
    assert client.calls == 1

    job.content_hash = "new-jd"
    await evaluate_fit(job, profile, client, model="test", max_tokens=64)
    assert client.calls == 2

    job.content_hash = first.content_hash
    job.fit_content_hash = first.content_hash
    other = profile.model_copy(update={"skills": [*profile.skills, "Origami"]})
    await evaluate_fit(job, other, client, model="test", max_tokens=64)
    assert client.calls == 3

    job.fit_profile_hash = first.profile_hash
    job.fit_version = "phase6-v0"
    await evaluate_fit(job, profile, client, model="test", max_tokens=64)
    assert client.calls == 4


async def test_insufficient_fit_is_not_stored_as_zero(profile: Profile, db_ready: Path) -> None:
    del db_ready
    async with session_scope() as session:
        saved = await upsert_job(
            session,
            Job(
                source=Source.linkedin,
                external_id="thin-jd",
                title="Intern",
                company="GoodCo",
                url="https://example.com/thin",
                description_clean="Too short.",
                jd_status="suspicious",
                content_hash="thin",
                status=Status.discovered,
            ),
        )
        job_id = saved.id
    client = _Client(_payload(0))
    summary = await Scorer(client=client, profile=profile).score_pending(  # type: ignore[arg-type]
        client=client,  # type: ignore[arg-type]
        profile=profile,
        generate_outreach=False,
        concurrency=1,
    )
    assert client.calls == 0
    assert summary.scored == 0
    assert summary.filtered_out == 0
    async with session_scope() as session:
        assert job_id is not None
        row = await get_job_by_id(session, job_id)
        assert row is not None
        assert row.score is None
        assert row.status == Status.discovered
        assert row.fit_confidence == "low"


def test_fit_blocks_include_the_profile(profile: Profile) -> None:
    blocks = build_fit_system_blocks(profile)
    assert profile.skills[0] in blocks[0]["text"]
    assert profile.identity.full_name not in blocks[0]["text"]
    user = build_fit_user(_job())
    assert "Evaluate this job posting" in user

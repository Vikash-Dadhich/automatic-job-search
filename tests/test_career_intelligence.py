"""Career Intelligence is a separate reading. It does not change fit or shortlist."""

from __future__ import annotations

from pathlib import Path

import pytest
from sqlmodel import col, func, select

from bot.prep import send_prep_pack
from bot.telegram import TelegramClient
from config.profile import Profile
from config.settings import get_settings
from core.db import (
    CareerIntelligence,
    CompanyIntelligence,
    Job,
    Source,
    Status,
    get_job_by_id,
    session_scope,
    upsert_job,
)
from scorer.career_intelligence import (
    CAREER_INTELLIGENCE_VERSION,
    assess_career,
    attach_career_intelligence,
    career_input_hash,
    load_career_config,
)
from scorer.engine import score_pending
from scorer.shortlist import apply_shortlist
from tests.test_scorer import FakeClient
from tests.test_telegram import FakeTransport


def _job(
    description: str = "A readable posting with enough text for a career reading.",
    **fields: object,
) -> Job:
    payload: dict[str, object] = {
        "source": Source.linkedin,
        "external_id": "career-1",
        "title": "Summer Intern",
        "company": "Acme",
        "url": "https://example.com/career",
        "description_clean": description,
        "content_hash": "jd-1",
        "status": Status.staged,
        "score": 80,
        "priority_score": 70,
    }
    payload.update(fields)
    return Job(**payload)  # type: ignore[arg-type]


def _doc(
    lines: list[str] | None = None,
    *,
    program: dict[str, object] | None = None,
    minimum_years: int | None = None,
    mba: str | None = None,
    required: list[str] | None = None,
) -> dict[str, object]:
    return {
        "responsibilities": {"items": [{"text": line} for line in lines or []]},
        "program": program or {},
        "experience": {"minimum_years": minimum_years} if minimum_years is not None else {},
        "education": {"mba": mba} if mba else {},
        "qualifications": {"required": [{"text": line} for line in required or []]},
    }


def _read(
    profile: Profile,
    lines: list[str] | None = None,
    description: str | None = None,
    **doc_kwargs: object,
) -> object:
    document = _doc(lines, **doc_kwargs)  # type: ignore[arg-type]
    return assess_career(
        _job(description or "A readable posting with enough text for a career reading."),
        profile,
        document=document,  # type: ignore[arg-type]
        structured_hash="s",
        structured_version="phase19-v1",
    )


async def _save(job: Job) -> int:
    async with session_scope() as session:
        saved = await upsert_job(session, job)
        assert saved.id is not None
        return saved.id


async def test_record_is_versioned_and_unique(db_ready: Path, profile: Profile) -> None:
    del db_ready
    job_id = await _save(_job())
    first = await attach_career_intelligence(job_id, profile)
    second = await attach_career_intelligence(job_id, profile)
    assert first is not None and second is not None
    assert first.id == second.id
    assert first.version == CAREER_INTELLIGENCE_VERSION
    assert len(first.content_hash) == 64
    assert profile.identity.email not in first.content_hash
    async with session_scope() as session:
        count = (
            await session.exec(
                select(func.count()).select_from(CareerIntelligence).where(
                    col(CareerIntelligence.job_id) == job_id
                )
            )
        ).one()
    assert count == 1


def test_product_and_strategy_and_consulting_are_positive(profile: Profile) -> None:
    product = _read(profile, ["Own the product roadmap for the search surface."])
    strategy = _read(profile, ["Lead the corporate strategy review this summer."])
    consulting = _read(profile, ["Run the management consulting engagement."])
    assert product.transition.state in {"STRONG", "MODERATE"}  # type: ignore[attr-defined]
    assert strategy.transition.state in {"STRONG", "MODERATE"}  # type: ignore[attr-defined]
    assert consulting.transition.state in {"STRONG", "MODERATE"}  # type: ignore[attr-defined]
    assert consulting.transition.state != "WEAK"  # type: ignore[attr-defined]
    assert "consulting title" not in " ".join(consulting.transition.evidence).lower()  # type: ignore[attr-defined]


def test_unrelated_work_is_not_given_transition_credit(profile: Profile) -> None:
    reading = _read(profile, ["Operate the warehouse overnight."])
    assert reading.transition.state == "UNKNOWN"  # type: ignore[attr-defined]
    assert reading.story.state == "UNKNOWN"  # type: ignore[attr-defined]
    assert reading.opportunity_quality.state == "UNKNOWN"  # type: ignore[attr-defined]


def test_technology_bridge_needs_posting_evidence(profile: Profile) -> None:
    bridged = _read(
        profile,
        ["Own the product roadmap on the technology platform."],
    )
    assert bridged.story.state == "STRONG"  # type: ignore[attr-defined]
    assert any("technology" in line.lower() for line in bridged.story.evidence)  # type: ignore[attr-defined]
    plain = _read(profile, ["Stock shelves in the warehouse."])
    assert plain.story.evidence == ()  # type: ignore[attr-defined]


def test_mba_internship_is_recognized_without_inventing_quality(profile: Profile) -> None:
    rich = _read(
        profile,
        ["Own the product roadmap and lead cross-functional delivery."],
        program={"mba_internship": True},
    )
    assert rich.internship_quality.state == "STRONG"  # type: ignore[attr-defined]
    generic = _read(profile, ["Operate the warehouse overnight."], program={"internship": True})
    assert generic.internship_quality.state == "UNKNOWN"  # type: ignore[attr-defined]
    label_only = _read(
        profile,
        ["Operate the warehouse overnight."],
        program={"mba_internship": True},
    )
    assert label_only.internship_quality.state == "MODERATE"  # type: ignore[attr-defined]


def test_learning_and_quality_ignore_prestige(profile: Profile) -> None:
    reading = _read(
        profile,
        [
            "Own the product roadmap.",
            "Lead cross-functional stakeholder management.",
            "Run customer discovery with the executive team.",
        ],
    )
    assert reading.learning.state == "STRONG"  # type: ignore[attr-defined]
    famous = _read(
        profile,
        [],
        description="Google is a famous company with a well known brand and prestige.",
    )
    assert famous.opportunity_quality.state == "UNKNOWN"  # type: ignore[attr-defined]
    assert famous.learning.state == "UNKNOWN"  # type: ignore[attr-defined]


def test_conversion_requires_explicit_language(profile: Profile) -> None:
    confirmed = assess_career(
        _job("High-performing interns may receive a return offer at the end of summer."),
        profile,
        document=_doc(),
        structured_hash="s",
        structured_version="phase19-v1",
    )
    assert confirmed.conversion_signal == "CONFIRMED"
    assert "return offer" in confirmed.conversion_evidence[0].lower()
    silent = _read(profile, ["Own the product roadmap."])
    assert silent.conversion_signal == "NOT_FOUND"  # type: ignore[attr-defined]
    assert silent.overall_score != 0  # type: ignore[attr-defined]
    brand = assess_career(
        _job("A famous prestigious company with no program language in this posting text."),
        profile,
        document=_doc(),
        structured_hash="s",
        structured_version="phase19-v1",
        company_signals=["us_headquarters"],
    )
    assert brand.conversion_signal == "NOT_FOUND"


def test_competitiveness_does_not_treat_unknown_or_title_as_failure(profile: Profile) -> None:
    unknown = _read(profile, ["Own the product roadmap."])
    assert unknown.competitiveness.state == "UNKNOWN"  # type: ignore[attr-defined]
    title_gap = _read(profile, required=["Prior consulting title required"])
    assert title_gap.competitiveness.state != "WEAK"  # type: ignore[attr-defined]
    years = _read(profile, minimum_years=80)
    assert years.competitiveness.state == "WEAK"  # type: ignore[attr-defined]
    skill = profile.skills[0]
    matched = _read(profile, required=[f"{skill} experience required"], minimum_years=1)
    assert matched.competitiveness.state in {"STRONG", "MODERATE"}  # type: ignore[attr-defined]


def test_application_effort_is_stored_and_not_an_overall_penalty(profile: Profile) -> None:
    plain = _read(profile, ["Own the product roadmap."])
    heavy = assess_career(
        _job("Submit a cover letter and a portfolio with the application today."),
        profile,
        document=_doc(["Own the product roadmap."]),
        structured_hash="s",
        structured_version="phase19-v1",
    )
    assert plain.application_effort.state == "UNKNOWN"  # type: ignore[attr-defined]
    assert heavy.application_effort.state == "STRONG"
    assert heavy.application_effort.score == 100
    assert heavy.overall_score == plain.overall_score  # type: ignore[attr-defined]


def test_overall_score_omits_unknown_dimensions(profile: Profile) -> None:
    reading = _read(profile, ["Own the product roadmap."])
    config = load_career_config()
    present = [
        reading.transition.score,  # type: ignore[attr-defined]
        reading.story.score,  # type: ignore[attr-defined]
        reading.learning.score,  # type: ignore[attr-defined]
        reading.opportunity_quality.score,  # type: ignore[attr-defined]
    ]
    numbers = [score for score in present if score is not None]
    assert reading.overall_score == round(sum(numbers) / len(numbers))  # type: ignore[attr-defined]
    assert config["weights"]["application_effort"] == 0
    empty = assess_career(_job(""), profile)
    assert empty.availability == "unavailable"
    assert empty.overall_score is None
    assert empty.conversion_signal == "UNKNOWN"


async def test_cache_reuses_and_invalidates(db_ready: Path, profile: Profile) -> None:
    del db_ready
    job_id = await _save(_job())
    first = await attach_career_intelligence(job_id, profile)
    assert first is not None
    again = await attach_career_intelligence(job_id, profile)
    assert again is not None
    assert again.content_hash == first.content_hash
    async with session_scope() as session:
        saved = await get_job_by_id(session, job_id)
        assert saved is not None
        saved.description_clean = (
            "A rewritten posting that now mentions a return offer for interns."
        )
        saved.content_hash = "jd-2"
        session.add(saved)
    changed = await attach_career_intelligence(job_id, profile)
    assert changed is not None
    assert changed.content_hash != first.content_hash
    assert changed.conversion_signal == "CONFIRMED"

    shifted = profile.model_copy(deep=True)
    shifted.skills = [*shifted.skills, "Distinct Skill Token"]
    profile_changed = await attach_career_intelligence(job_id, shifted)
    assert profile_changed is not None
    assert profile_changed.content_hash != changed.content_hash

    loosened = load_career_config()
    patched = {
        "version": loosened["version"],
        "state_scores": {**loosened["state_scores"], "STRONG": 90},
        "signal_scores": loosened["signal_scores"],
        "weights": loosened["weights"],
    }
    before = career_input_hash(
        _job(),
        profile,
        structured_hash=None,
        structured_version=None,
        company_hash=None,
        company_version=None,
        config=loosened,
    )
    after = career_input_hash(
        _job(),
        profile,
        structured_hash=None,
        structured_version=None,
        company_hash=None,
        company_version=None,
        config=patched,
    )
    assert before != after


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("role_secondary_family", "CONSULTING"),
        ("role_secondary_subfamily", "STRATEGY_CONSULTING"),
        ("role_secondary_confidence", "high"),
        ("role_secondary_evidence", ["lead the client workstream"]),
    ],
)
def test_secondary_role_fields_change_the_input_hash(
    profile: Profile,
    field: str,
    value: object,
) -> None:
    kwargs = {
        "structured_hash": None,
        "structured_version": None,
        "company_hash": None,
        "company_version": None,
    }
    original = _job()
    edited = _job()
    setattr(edited, field, value)
    baseline = career_input_hash(original, profile, **kwargs)
    changed = career_input_hash(edited, profile, **kwargs)
    assert baseline != changed


async def test_role_and_company_inputs_change_the_hash(db_ready: Path, profile: Profile) -> None:
    del db_ready
    job_id = await _save(_job())
    first = await attach_career_intelligence(job_id, profile)
    assert first is not None
    async with session_scope() as session:
        saved = await get_job_by_id(session, job_id)
        assert saved is not None
        saved.role_family = "PRODUCT_MANAGEMENT"
        saved.role_confidence = "high"
        saved.role_classifier_version = "phase5-v4"
        company = CompanyIntelligence(
            lookup_key="acme-career",
            company_name="Acme",
            canonical_name="Acme",
            status="partial",
            intelligence_version="phase8-v2",
            context={
                "version": "phase8-v2",
                "content_hash": "company-1",
                "signals": [{"signal": "mba_internship_program"}],
            },
        )
        session.add(company)
        await session.flush()
        saved.company_intelligence_id = company.id
        session.add(saved)
    updated = await attach_career_intelligence(job_id, profile)
    assert updated is not None
    assert updated.content_hash != first.content_hash
    assert updated.mba_recruiting_signal == "CONFIRMED"
    async with session_scope() as session:
        saved = await get_job_by_id(session, job_id)
        assert saved is not None
        assert saved.score == 80
        assert saved.priority_score == 70
        assert saved.shortlist_rank is None


async def test_failure_does_not_change_fit_priority_or_shortlist(
    db_ready: Path,
    profile: Profile,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    job_id = await _save(
        Job(
            source=Source.linkedin,
            external_id="score-me",
            title="Product Manager Intern",
            company="Acme",
            url="https://example.com/score",
            description_clean="Product role with enough text to score and classify later.",
            status=Status.discovered,
        )
    )

    def _boom(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("career down")

    monkeypatch.setattr("scorer.career_intelligence.attach_career_intelligence", _boom)
    summary = await score_pending(
        client=FakeClient(),
        profile=profile,
        generate_outreach=False,
        generate_cover_letter=False,
    )
    assert summary.scored == 1
    async with session_scope() as session:
        saved = await get_job_by_id(session, job_id)
        assert saved is not None
        assert saved.score == 72
        assert saved.priority_score is not None
        priority = saved.priority_score
        saved.status = Status.staged
        session.add(saved)
    picks = await apply_shortlist()
    assert job_id in picks.selected_ids
    async with session_scope() as session:
        saved = await get_job_by_id(session, job_id)
        assert saved is not None
        assert saved.score == 72
        assert saved.priority_score == priority
        assert saved.shortlist_rank == 1
        row = (
            await session.exec(
                select(CareerIntelligence).where(col(CareerIntelligence.job_id) == job_id)
            )
        ).first()
    assert row is None


async def test_career_reading_does_not_change_telegram_order(
    db_ready: Path,
    profile: Profile,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    del db_ready
    monkeypatch.setenv("PREP_PACK_BRIEF", "true")
    monkeypatch.setenv("PREP_PACKS_DIR", str(tmp_path / "prep"))
    get_settings.cache_clear()
    first = await _save(
        _job(
            external_id="rank-1",
            title="First",
            shortlist_rank=1,
            shortlist_version=CAREER_INTELLIGENCE_VERSION,
            status=Status.pending_review,
        )
    )
    second = await _save(
        _job(
            external_id="rank-2",
            title="Second",
            description_clean="High-performing interns may receive a return offer this summer.",
            shortlist_rank=2,
            shortlist_version=CAREER_INTELLIGENCE_VERSION,
            status=Status.pending_review,
        )
    )
    await attach_career_intelligence(first, profile)
    await attach_career_intelligence(second, profile)
    summary = await send_prep_pack(TelegramClient(transport=FakeTransport(), chat_id="1"))
    text = Path(summary.markdown_path or "").read_text(encoding="utf-8")
    assert text.index("First") < text.index("Second")
    async with session_scope() as session:
        kept = await get_job_by_id(session, first)
        other = await get_job_by_id(session, second)
        assert kept is not None and other is not None
        assert kept.shortlist_rank == 1
        assert other.shortlist_rank == 2
    get_settings.cache_clear()


def test_assess_does_not_call_the_fit_model(
    profile: Profile,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _boom(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("fit model")

    monkeypatch.setattr("scorer.fit.evaluate_fit", _boom)
    reading = _read(profile, ["Own the product roadmap."])
    assert reading.transition.state in {"STRONG", "MODERATE"}  # type: ignore[attr-defined]

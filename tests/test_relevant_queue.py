"""Relevant queue: title families, the pre-scoring title gate, the 40/40/20 mix, reset."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from bot.reset import reset_queue
from bot.telegram import TelegramClient
from config.settings import get_settings
from core.db import Job, Source, Status, get_job_by_id, session_scope, upsert_job
from scorer.queue_mix import Mix, MixGroup, load_mix, seat_plan, select_mix
from scorer.shortlist import apply_shortlist, load_shortlist_config
from scraper.filters import evaluate, target_title_reason
from scraper.models import RawPosting
from scraper.title_family import (
    CONSULTING,
    GENERAL_MBA,
    MARKETING,
    PRODUCT,
    PRODUCT_MARKETING,
    STRATEGY,
    title_family,
)
from tests.test_telegram import FakeTransport

_counter = iter(range(1, 10_000))


@pytest.mark.parametrize(
    ("title", "family"),
    [
        ("Product Manager Intern (Content and Service Ads) - 2027 Summer (MBA)", PRODUCT),
        ("Associate Product Manager Intern", PRODUCT),
        ("Software Product Management Intern", PRODUCT),
        ("2027 Summer Intern - Card Product Management/B2B Payments", PRODUCT),
        ("Product Intern", PRODUCT),
        ("Management Consulting Intern", CONSULTING),
        ("MBA Summer Consultant", CONSULTING),
        ("Corporate Strategy MBA Intern", STRATEGY),
        ("Product Marketing Manager Intern", PRODUCT_MARKETING),
        ("Growth Marketing Intern", MARKETING),
        ("MBA Summer Associate", GENERAL_MBA),
        ("Data Scientist Intern, Product Analytics", None),
        ("Data Engineering Intern, Summer 2027", None),
        ("Software Engineer Intern, Product", None),
        ("Technical Support/Trainer Intern", None),
        ("Product Designer Intern", None),
        ("Value Engineering Intern", None),
        ("Intern", None),
        ("", None),
    ],
)
def test_title_family(title: str, family: str | None) -> None:
    assert title_family(title) == family


def test_target_reason_covers_unpaid_and_off_season() -> None:
    assert target_title_reason("Product Manager Intern") is None
    assert target_title_reason("Product & Strategy Intern (Net-Profit Share only)")
    assert target_title_reason("Product Manager Intern", "This is an unpaid internship.")
    assert target_title_reason("Consulting Intern (Spring 2027)") == "not a summer internship"
    assert target_title_reason("Spring/Summer 2027 Consulting Intern") is None
    assert "not a target role" in (target_title_reason("Data Scientist Intern") or "")


def _posting(title: str) -> RawPosting:
    return RawPosting(
        source=Source.linkedin,
        external_id=f"p-{next(_counter)}",
        title=title,
        company="Acme",
        location="Seattle, WA",
        url="https://example.com/job",
        description_clean="Summer internship.",
    )


def test_gate_is_off_unless_enabled(profile: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("INTERNSHIP_ONLY", "true")
    monkeypatch.setenv("TARGET_TITLES_ONLY", "false")
    get_settings.cache_clear()
    assert evaluate(_posting("Data Scientist Intern"), profile).passed
    monkeypatch.setenv("TARGET_TITLES_ONLY", "true")
    get_settings.cache_clear()
    result = evaluate(_posting("Data Scientist Intern"), profile)
    assert not result.passed
    assert "not a target role" in (result.reason or "")
    assert evaluate(_posting("Product Manager Intern"), profile).passed
    get_settings.cache_clear()


def test_default_mix_is_40_40_20() -> None:
    mix = load_mix()
    shares = {group.name: group.share for group in mix.groups}
    assert shares == {"product": 0.4, "consulting": 0.4, "other": 0.2}
    assert seat_plan(mix, 15) == {"product": 6, "consulting": 6, "other": 3}
    assert sum(seat_plan(mix, 7).values()) == 7
    assert seat_plan(mix, 0) == {"product": 0, "consulting": 0, "other": 0}


def _job(title: str, score: int | None, company: str | None = None, **kwargs: Any) -> Job:
    number = next(_counter)
    data: dict[str, Any] = {
        "id": number,
        "source": Source.linkedin,
        "external_id": f"j-{number}",
        "title": title,
        "company": company or f"Co {number}",
        "url": f"https://jobs.example.com/{number}",
        "status": Status.staged,
        "score": score,
        "priority_score": score,
    }
    data.update(kwargs)
    return Job(**data)


def test_mix_fills_each_group_by_fit() -> None:
    jobs = [_job("Product Manager Intern", 90 - i) for i in range(10)]
    jobs += [_job("Consulting Intern", 70 - i) for i in range(10)]
    jobs += [_job("Strategy Intern", 80 - i) for i in range(10)]
    jobs += [_job("Data Scientist Intern", 99)]
    picks = select_mix(jobs, seats=10)
    groups = [pick.group for pick in picks]
    assert groups.count("product") == 4
    assert groups.count("consulting") == 4
    assert groups.count("other") == 2
    assert all("Data Scientist" not in pick.job.title for pick in picks)
    assert groups == sorted(groups, key=["product", "consulting", "other"].index)


def test_empty_consulting_seats_spill_to_product_first() -> None:
    jobs = [_job("Product Manager Intern", 90 - i) for i in range(10)]
    jobs += [_job("Strategy Intern", 80 - i) for i in range(10)]
    jobs += [_job("Management Consulting Intern", 60)]
    picks = select_mix(jobs, seats=10)
    groups = [pick.group for pick in picks]
    assert groups.count("consulting") == 1
    assert groups.count("product") == 7
    assert groups.count("other") == 2


def test_company_cap_and_duplicate_titles() -> None:
    jobs = [
        _job("Product Manager Intern", 90, company="Pentair"),
        _job("Product Manager Intern (Summer 2027)", 89, company="Pentair"),
        _job("Product Strategy Intern", 88, company="Pentair"),
        _job("Product Owner Intern", 87, company="Pentair"),
    ]
    picks = select_mix(jobs, seats=4, max_per_company=2)
    titles = [pick.job.title for pick in picks]
    assert titles == ["Product Manager Intern", "Product Strategy Intern"]


def test_waiting_cards_count_toward_cap() -> None:
    waiting = [_job("Product Manager Intern", 90, company="TikTok", status=Status.pending_review)]
    jobs = [
        _job("Product Manager Intern", 85, company="TikTok"),
        _job("AI Product Manager Intern", 84, company="TikTok"),
    ]
    picks = select_mix(jobs, seats=5, max_per_company=2, taken=waiting)
    assert [pick.job.title for pick in picks] == ["AI Product Manager Intern"]


def test_unscored_and_non_staged_jobs_are_ignored() -> None:
    jobs = [
        _job("Product Manager Intern", 90, status=Status.submitted),
        _job("Product Manager Intern", None),
    ]
    assert select_mix(jobs, seats=3) == []


def test_mix_rejects_bad_config() -> None:
    from scorer.queue_mix import _parse

    with pytest.raises(ValueError):
        _parse({"groups": {"a": {"share": 0.5, "families": [PRODUCT]}}})
    with pytest.raises(ValueError):
        _parse({"groups": {"a": {"share": 1.0, "families": ["NOT_A_FAMILY"]}}})
    custom = Mix((MixGroup("all", 1.0, frozenset({PRODUCT})),), ("all",))
    assert seat_plan(custom, 3) == {"all": 3}


async def _save(job: Job) -> int:
    job.id = None
    async with session_scope() as session:
        saved = await upsert_job(session, job)
        assert saved.id is not None
        return saved.id


async def test_apply_shortlist_uses_mix_when_enabled(
    db_ready: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    del db_ready
    monkeypatch.setenv("QUEUE_MIX", "true")
    monkeypatch.setenv("QUEUE_DAILY_LIMIT", "5")
    get_settings.cache_clear()
    for i in range(6):
        await _save(_job("Data Engineer Intern", 99 - i))
    for i in range(4):
        await _save(_job("Product Manager Intern", 80 - i))
    for i in range(4):
        await _save(_job("Consulting Intern", 75 - i))
    config = load_shortlist_config()
    result = await apply_shortlist(config=config)
    assert result.selected == 5
    async with session_scope() as session:
        chosen = [await get_job_by_id(session, job_id) for job_id in result.selected_ids]
    titles = [job.title for job in chosen if job is not None]
    assert "Data Engineer Intern" not in titles
    assert titles.count("Product Manager Intern") >= 2
    assert titles.count("Consulting Intern") >= 2
    get_settings.cache_clear()


async def test_reset_returns_cards_and_drops_off_target(db_ready: Path) -> None:
    del db_ready
    waiting_pm = await _save(
        _job(
            "Product Manager Intern",
            80,
            status=Status.pending_review,
            review_message_id=50,
            review_chat_id="999",
            application_answers={"items": [{"question": "q", "answer": "a"}]},
        )
    )
    waiting_ds = await _save(
        _job(
            "Data Scientist Intern",
            85,
            status=Status.pending_review,
            review_message_id=52,
            review_chat_id="999",
        )
    )
    staged_bad = await _save(_job("Technical Support Intern", 75))
    unscored_bad = await _save(
        _job("Software Engineer Intern", None, status=Status.discovered)
    )
    applied = await _save(_job("Data Scientist Intern", 70, status=Status.submitted))
    transport = FakeTransport(responses={"deleteMessage": {"ok": True, "result": True}})
    summary = await reset_queue(TelegramClient(transport=transport, chat_id="999"))
    deleted = sorted(
        call["payload"]["message_id"]
        for call in transport.calls
        if call["method"] == "deleteMessage"
    )
    assert deleted == [50, 51, 52]
    assert summary.returned == 2
    assert summary.dropped == 3
    async with session_scope() as session:
        pm = await get_job_by_id(session, waiting_pm)
        ds = await get_job_by_id(session, waiting_ds)
        bad = await get_job_by_id(session, staged_bad)
        raw = await get_job_by_id(session, unscored_bad)
        done = await get_job_by_id(session, applied)
    assert pm is not None and pm.status == Status.staged and pm.review_message_id is None
    assert ds is not None and ds.status == Status.filtered_out
    assert bad is not None and bad.status == Status.filtered_out
    assert raw is not None and raw.status == Status.filtered_out
    assert raw.justification and "not a target role" in raw.justification[0]
    assert done is not None and done.status == Status.submitted

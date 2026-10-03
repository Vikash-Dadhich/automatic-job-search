"""Offline tests for the score shortlist and uncapped scoring."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from bot.prep import render_shortlist, select_shortlist, send_prep_pack
from bot.telegram import TelegramClient
from config.settings import get_settings
from core.db import Job, Source, Status, Tier, get_job_by_id, session_scope, upsert_job
from scorer.engine import score_pending
from tests.test_scorer import FakeClient
from tests.test_telegram import FakeTransport


def _job(job_id: int, score: int, *, sent: bool = False) -> Job:
    return Job(
        id=job_id,
        source=Source.workday if job_id % 2 == 0 else Source.linkedin,
        external_id=f"sl-{job_id}",
        title=f"Role {job_id}",
        company="Co",
        location="Remote",
        url=f"https://example.com/{job_id}",
        score=score,
        status=Status.staged if score >= 65 else Status.filtered_out,
        tier=Tier.one if score >= 85 else Tier.two if score >= 65 else Tier.three,
        prep_pack_sent_at=datetime.now(UTC) if sent else None,
    )


def test_shortlist_sends_every_score_above_75() -> None:
    strong = [_job(i, 76 + (i % 20)) for i in range(1, 26)]
    fill = [_job(100 + i, 60 + i) for i in range(15)]
    chosen = select_shortlist(strong + fill)
    assert len(chosen) == 25
    assert all((job.score or 0) > 75 for job in chosen)
    text = render_shortlist(chosen)
    assert "[fill]" not in text
    assert text.count("https://example.com/") == 25


def test_shortlist_fills_to_20_from_60() -> None:
    strong = [_job(i, 90 - i) for i in range(5)]
    fill = [_job(100 + i, 75 if i < 10 else 70 if i < 20 else 65) for i in range(30)]
    weak = [_job(200, 59), _job(201, 40)]
    chosen = select_shortlist(strong + fill + weak)
    assert len(chosen) == 20
    assert [job.score for job in chosen[:5]] == [90, 89, 88, 87, 86]
    assert [job.score for job in chosen[5:]] == [75] * 10 + [70] * 5
    text = render_shortlist(chosen)
    assert text.startswith("1. Role 0")
    assert "Fit: 90" in text
    assert "[fill]" not in text
    assert "59" not in text


def test_shortlist_leaves_slots_empty_under_60() -> None:
    chosen = select_shortlist([_job(1, 76), _job(2, 64), _job(3, 59), _job(4, 60)])
    assert [job.score for job in chosen] == [76, 64, 60]
    assert 59 not in [job.score for job in chosen]


def test_shortlist_skips_jobs_already_sent() -> None:
    chosen = select_shortlist(
        [_job(1, 95, sent=True), _job(2, 70), _job(3, 59)]
    )
    assert [job.id for job in chosen] == [2]


async def _seed(scores: list[int]) -> list[int]:
    ids: list[int] = []
    async with session_scope() as session:
        for index, score in enumerate(scores):
            job = await upsert_job(
                session,
                Job(
                    source=Source.workday if index == 0 else Source.linkedin,
                    external_id=f"doc-{index}-{score}",
                    title=f"Role {score}",
                    company="Co",
                    location="Seattle, WA",
                    url=f"https://example.com/doc/{index}",
                    description_clean="Product role",
                    status=Status.staged if score >= 65 else Status.filtered_out,
                    score=score,
                    tier=Tier.one if score >= 85 else None,
                ),
            )
            assert job.id is not None
            ids.append(job.id)
    return ids


async def test_shortlist_document_marks_sent(
    db_ready: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PREP_PACK_BRIEF", "true")
    get_settings.cache_clear()
    ids = await _seed([92, 70, 59])
    async with session_scope() as session:
        for job_id, rank in ((ids[0], 1), (ids[1], 2)):
            target = await get_job_by_id(session, job_id)
            assert target is not None
            target.shortlist_rank = rank
            target.shortlist_version = "phase13-v2"
            session.add(target)

    transport = FakeTransport()
    client = TelegramClient(transport=transport, chat_id="999")
    summary = await send_prep_pack(client, job_ids=ids)

    assert summary.sent == 1
    assert summary.jobs == 2
    assert transport.calls[0]["method"] == "sendDocument"
    assert transport.calls[0]["payload"]["caption"] == "2 jobs selected for review"
    assert summary.markdown_path is not None
    text = Path(summary.markdown_path).read_text(encoding="utf-8")
    assert "Fit: 92" in text
    assert "Fit: 70" in text
    assert "59" not in text
    assert "[fill]" not in text

    async with session_scope() as session:
        strong = await get_job_by_id(session, ids[0])
        fill = await get_job_by_id(session, ids[1])
        weak = await get_job_by_id(session, ids[2])
        assert strong is not None and strong.prep_pack_sent_at is not None
        assert fill is not None and fill.prep_pack_sent_at is not None
        assert weak is not None and weak.prep_pack_sent_at is None

    transport2 = FakeTransport()
    client2 = TelegramClient(transport=transport2, chat_id="999")
    summary2 = await send_prep_pack(client2, job_ids=ids)
    assert summary2.sent == 0
    assert summary2.skipped == 1
    assert transport2.calls == []
    get_settings.cache_clear()


async def test_no_score_budget_scores_every_eligible_job(
    db_ready: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("SCORE_BUDGET", raising=False)
    get_settings.cache_clear()
    assert get_settings().score_budget is None

    async with session_scope() as session:
        for index in range(12):
            await upsert_job(
                session,
                Job(
                    source=Source.linkedin,
                    external_id=f"uncapped-{index}",
                    title="Product Manager",
                    company=f"Co{index}",
                    location="Remote",
                    url=f"https://example.com/uncapped/{index}",
                    description_clean="Python product role",
                    status=Status.discovered,
                ),
            )

    client = FakeClient(score_payload='{"s":72,"t":2,"r":["fit"]}')
    summary = await score_pending(
        client=client,
        generate_outreach=False,
        generate_cover_letter=False,
    )
    assert summary.scored == 12
    assert summary.skipped == 0
    assert len(summary.scored_ids) == 12
    score_calls = [call for call in client.calls if call.get("json_mode") is True]
    assert len(score_calls) == 12
    get_settings.cache_clear()

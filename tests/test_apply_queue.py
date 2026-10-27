"""Apply queue: daily cap, snooze, cards, button taps, expiry and one-shot sync."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

from bot.handlers import handle_callback
from bot.queue import (
    QueueAction,
    build_queue_keyboard,
    build_queue_text,
    decode_queue_callback,
    encode_queue_callback,
    expire_queue,
    is_queue_callback,
    send_queue_cards,
    sync_telegram,
)
from bot.telegram import TelegramClient
from config.settings import get_settings
from core.db import Job, Source, Status, get_job_by_id, session_scope, upsert_job
from scorer.shortlist import apply_shortlist, load_shortlist_config
from tests.test_telegram import FakeTransport

NOW = datetime.now(UTC)


def _job(external_id: str, **kwargs: Any) -> Job:
    data: dict[str, Any] = {
        "source": Source.linkedin,
        "external_id": external_id,
        "title": "Product Manager Intern",
        "company": f"Co {external_id}",
        "location": "Seattle, WA",
        "url": f"https://jobs.example.com/{external_id}",
        "status": Status.staged,
        "score": 80,
        "priority_score": 80,
        "role_family": "PRODUCT_MANAGEMENT",
        "justification": ["Matches product background"],
    }
    data.update(kwargs)
    return Job(**data)


async def _save(job: Job) -> int:
    async with session_scope() as session:
        saved = await upsert_job(session, job)
        assert saved.id is not None
        return saved.id


async def _load(job_id: int) -> Job:
    async with session_scope() as session:
        job = await get_job_by_id(session, job_id)
    assert job is not None
    return job


def _config(max_size: int = 20) -> dict[str, Any]:
    loaded = load_shortlist_config()
    block = dict(loaded["shortlist"])
    block["max_size"] = max_size
    return {**loaded, "shortlist": block}


def _client() -> tuple[TelegramClient, FakeTransport]:
    transport = FakeTransport()
    return TelegramClient(transport=transport, chat_id="999"), transport


def _tap(action: QueueAction, job_id: int) -> dict[str, Any]:
    return {
        "update_id": 1,
        "callback_query": {
            "id": "cb1",
            "data": encode_queue_callback(action, job_id),
            "message": {"message_id": 43, "chat": {"id": 999}},
        },
    }


def test_callback_round_trip_and_detection() -> None:
    data = encode_queue_callback(QueueAction.later, 77)
    assert data == "q1|l|77"
    assert decode_queue_callback(data) == (QueueAction.later, 77)
    assert is_queue_callback(data)
    assert not is_queue_callback("v1|ok|1")
    with pytest.raises(ValueError):
        decode_queue_callback("q1|zz|1")
    with pytest.raises(ValueError):
        decode_queue_callback("v1|ok|1")


def test_keyboard_has_open_button_and_three_actions_and_no_submit() -> None:
    rows = build_queue_keyboard(5, "https://x.example/apply")["inline_keyboard"]
    assert rows[0] == [{"text": "Open job", "url": "https://x.example/apply"}]
    assert [button["text"] for button in rows[1]] == ["Applied", "Skip", "Later"]
    assert all(len(button["callback_data"].encode()) <= 64 for button in rows[1])
    assert len(build_queue_keyboard(5, "not a url")["inline_keyboard"]) == 1


def test_card_is_just_the_job() -> None:
    text = build_queue_text(_job("a", company="A & B", url="https://x.example/apply"))
    assert text.startswith("<b>Product Manager Intern</b>")
    assert "A &amp; B · Seattle, WA" in text
    assert "Matches product background" not in text
    assert "Fit" not in text and "Why" not in text


async def test_daily_cap_limits_new_seats(
    db_ready: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    del db_ready
    monkeypatch.setenv("QUEUE_DAILY_LIMIT", "2")
    get_settings.cache_clear()
    for index in range(5):
        await _save(_job(f"c{index}", priority_score=90 - index))
    first = await apply_shortlist(config=_config())
    assert first.selected == 2
    second = await apply_shortlist(config=_config())
    assert second.selected == 0
    get_settings.cache_clear()


async def test_cap_frees_up_after_24_hours(
    db_ready: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    del db_ready
    monkeypatch.setenv("QUEUE_DAILY_LIMIT", "1")
    get_settings.cache_clear()
    old = await _save(
        _job("old", status=Status.submitted, queued_at=NOW - timedelta(hours=30))
    )
    await _save(_job("fresh"))
    result = await apply_shortlist(config=_config())
    assert result.selected == 1
    assert (await _load(old)).status == Status.submitted
    get_settings.cache_clear()


async def test_snoozed_job_is_skipped_until_snooze_ends(db_ready: Path) -> None:
    del db_ready
    snoozed = await _save(_job("snz", snoozed_until=NOW + timedelta(days=2), priority_score=99))
    awake = await _save(_job("awk", snoozed_until=NOW - timedelta(days=1), priority_score=50))
    result = await apply_shortlist(config=_config())
    assert set(result.selected_ids) == {awake}
    assert (await _load(snoozed)).status == Status.staged
    job = await _load(awake)
    assert job.queued_at is not None
    assert job.snoozed_until is None


async def test_send_cards_once_and_record_message(db_ready: Path) -> None:
    del db_ready
    job_id = await _save(_job("send", status=Status.pending_review))
    client, transport = _client()
    first = await send_queue_cards(client)
    assert first.sent == 1
    sent = [call for call in transport.calls if call["method"] == "sendMessage"]
    assert len(sent) == 2
    header, card = sent[0]["payload"], sent[1]["payload"]
    assert "1 new role to apply to today" in header["text"]
    assert "disable_notification" not in header
    assert card["disable_notification"] is True
    assert card["reply_markup"]["inline_keyboard"][0][0]["url"] == "https://jobs.example.com/send"
    assert (await _load(job_id)).review_message_id == 43
    again = await send_queue_cards(client)
    assert again.sent == 0


async def test_applied_marks_submitted_without_any_submit(db_ready: Path) -> None:
    del db_ready
    job_id = await _save(_job("app", status=Status.pending_review))
    client, transport = _client()
    result = await handle_callback(_tap(QueueAction.applied, job_id), client=client)
    assert result == Status.submitted
    job = await _load(job_id)
    assert job.status == Status.submitted
    assert job.decided_at is not None
    methods = [call["method"] for call in transport.calls]
    assert "editMessageText" in methods
    assert "answerCallbackQuery" in methods


async def test_skip_marks_ignored(db_ready: Path) -> None:
    del db_ready
    job_id = await _save(_job("skp", status=Status.pending_review))
    client, _ = _client()
    assert await handle_callback(_tap(QueueAction.skip, job_id), client=client) == Status.ignored
    assert (await _load(job_id)).status == Status.ignored


async def test_later_returns_job_to_staged_with_snooze(db_ready: Path) -> None:
    del db_ready
    job_id = await _save(
        _job(
            "ltr",
            status=Status.pending_review,
            queued_at=NOW,
            review_message_id=43,
            review_chat_id="999",
        )
    )
    client, _ = _client()
    result = await handle_callback(_tap(QueueAction.later, job_id), client=client)
    assert result == Status.staged
    job = await _load(job_id)
    assert job.queued_at is None
    assert job.review_message_id is None
    assert job.snoozed_until is not None
    wake = job.snoozed_until if job.snoozed_until.tzinfo else job.snoozed_until.replace(tzinfo=UTC)
    assert wake > NOW + timedelta(days=2)


async def test_repeat_tap_changes_nothing(db_ready: Path) -> None:
    del db_ready
    job_id = await _save(_job("rep", status=Status.pending_review))
    client, _ = _client()
    await handle_callback(_tap(QueueAction.skip, job_id), client=client)
    again = await handle_callback(_tap(QueueAction.applied, job_id), client=client)
    assert again == Status.ignored
    assert (await _load(job_id)).status == Status.ignored


async def test_expire_closes_only_old_undecided_jobs(db_ready: Path) -> None:
    del db_ready
    old = await _save(
        _job("exo", status=Status.pending_review, queued_at=NOW - timedelta(days=9))
    )
    recent = await _save(
        _job("exr", status=Status.pending_review, queued_at=NOW - timedelta(days=1))
    )
    legacy_new = await _save(_job("exl", status=Status.pending_review))
    assert await expire_queue() == 1
    assert (await _load(old)).status == Status.ignored
    assert (await _load(recent)).status == Status.pending_review
    assert (await _load(legacy_new)).status == Status.pending_review


async def test_expire_closes_old_cards_from_before_the_queue(db_ready: Path) -> None:
    del db_ready
    job_id = await _save(_job("pre-queue", status=Status.pending_review))
    async with session_scope() as session:
        job = await get_job_by_id(session, job_id)
        assert job is not None
        job.updated_at = NOW - timedelta(days=18)
        session.add(job)
    assert await expire_queue() == 1
    assert (await _load(job_id)).status == Status.ignored


async def test_sync_applies_taps_then_confirms_offset(db_ready: Path) -> None:
    del db_ready
    job_id = await _save(_job("syn", status=Status.pending_review))
    transport = FakeTransport(
        responses={"getUpdates": {"ok": True, "result": [_tap(QueueAction.applied, job_id)]}}
    )
    client = TelegramClient(transport=transport, chat_id="999")
    assert await sync_telegram(client) == 1
    assert (await _load(job_id)).status == Status.submitted
    polls = [call for call in transport.calls if call["method"] == "getUpdates"]
    assert len(polls) == 2
    assert polls[1]["payload"]["offset"] == 2


async def test_sync_never_submits_on_a_stale_approve_button(db_ready: Path) -> None:
    del db_ready
    job_id = await _save(_job("old-card", status=Status.pending_review))
    stale = {
        "update_id": 5,
        "callback_query": {
            "id": "cb9",
            "data": f"v1|ok|{job_id}",
            "message": {"message_id": 43, "chat": {"id": 999}},
        },
    }
    transport = FakeTransport(responses={"getUpdates": {"ok": True, "result": [stale]}})
    client = TelegramClient(transport=transport, chat_id="999")
    await sync_telegram(client)
    assert (await _load(job_id)).status == Status.manual_review


async def test_sync_with_no_updates_does_not_confirm(db_ready: Path) -> None:
    del db_ready
    transport = FakeTransport(responses={"getUpdates": {"ok": True, "result": []}})
    client = TelegramClient(transport=transport, chat_id="999")
    assert await sync_telegram(client) == 0
    assert len([c for c in transport.calls if c["method"] == "getUpdates"]) == 1

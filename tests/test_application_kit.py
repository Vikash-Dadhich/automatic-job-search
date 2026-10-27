"""Application kit: resume label by role family, deadline detection, drafted answers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from automation.answers import AnswerResolver
from bot.queue import build_queue_text, send_queue_cards
from bot.telegram import TelegramClient
from config.profile import load_profile
from core.db import Job, Source, Status, get_job_by_id, session_scope, upsert_job
from resume.kit import KIT_QUESTIONS, build_answers, find_deadline, has_kit, resume_label
from tests.test_telegram import FakeTransport


class _Writer:
    def __init__(self, reply: str = "Grounded draft.") -> None:
        self.reply = reply
        self.calls = 0

    async def complete(self, **_kwargs: Any) -> str:
        self.calls += 1
        return self.reply


class _Broken:
    async def complete(self, **_kwargs: Any) -> str:
        raise RuntimeError("model down")


def _job(external_id: str = "k1", **kwargs: Any) -> Job:
    data: dict[str, Any] = {
        "source": Source.linkedin,
        "external_id": external_id,
        "title": "Product Manager Intern",
        "company": "Acme",
        "location": "Seattle, WA",
        "url": "https://jobs.example.com/k1",
        "status": Status.pending_review,
        "role_family": "PRODUCT_MANAGEMENT",
        "description_clean": "Great internship. Apply by March 15, 2027.",
    }
    data.update(kwargs)
    return Job(**data)


def test_resume_label_by_family_with_default() -> None:
    assert resume_label("PRODUCT_MANAGEMENT") == "Product resume"
    assert resume_label("CONSULTING") == "Consulting resume"
    assert resume_label("UNKNOWN") == "General resume"
    assert resume_label(None) == "General resume"


def test_deadline_found_only_when_stated() -> None:
    assert find_deadline("Please apply by March 15, 2027.") == "March 15, 2027"
    assert find_deadline("Applications close Nov 3rd") == "Nov 3rd"
    assert find_deadline("Application deadline: December 1") == "December 1"
    assert find_deadline("We hire year round in March.") is None
    assert find_deadline(None) is None


def test_card_shows_deadline_only() -> None:
    text = build_queue_text(_job())
    assert "Apply by March 15, 2027" in text
    assert "Resume" not in text


async def test_build_answers_uses_resolver_for_both_questions() -> None:
    writer = _Writer()
    resolver = AnswerResolver(load_profile(), client=writer)  # type: ignore[arg-type]
    payload = await build_answers(_job(), resolver)
    assert payload is not None
    assert [item["question"] for item in payload["items"]] == list(KIT_QUESTIONS)
    assert writer.calls == len(KIT_QUESTIONS)


async def test_build_answers_returns_none_when_model_fails() -> None:
    resolver = AnswerResolver(load_profile(), client=_Broken())  # type: ignore[arg-type]
    assert await build_answers(_job(), resolver) is None


async def test_build_answers_skips_without_api_key(monkeypatch: Any) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "")
    from config.settings import get_settings

    get_settings.cache_clear()
    assert await build_answers(_job()) is None
    get_settings.cache_clear()


async def test_send_cards_saves_answers_and_sends_them(db_ready: Path, monkeypatch: Any) -> None:
    del db_ready
    monkeypatch.setenv("KIT_ANSWERS", "true")
    from config.settings import get_settings

    get_settings.cache_clear()
    async with session_scope() as session:
        saved = await upsert_job(session, _job())
        assert saved.id is not None
        job_id = saved.id
    transport = FakeTransport()
    client = TelegramClient(transport=transport, chat_id="999")
    resolver = AnswerResolver(load_profile(), client=_Writer("Draft text."))  # type: ignore[arg-type]
    summary = await send_queue_cards(client, resolver=resolver)
    assert summary.sent == 1
    texts = [c["payload"]["text"] for c in transport.calls if c["method"] == "sendMessage"]
    assert len(texts) == 3
    assert "Draft text." in texts[2]
    async with session_scope() as session:
        stored = await get_job_by_id(session, job_id)
    assert stored is not None
    assert has_kit(stored)
    get_settings.cache_clear()


async def test_answers_are_off_by_default(db_ready: Path) -> None:
    del db_ready
    async with session_scope() as session:
        await upsert_job(session, _job("k3"))
    transport = FakeTransport()
    client = TelegramClient(transport=transport, chat_id="999")
    writer = _Writer("Draft text.")
    resolver = AnswerResolver(load_profile(), client=writer)  # type: ignore[arg-type]
    summary = await send_queue_cards(client, resolver=resolver)
    assert summary.sent == 1
    assert writer.calls == 0
    texts = [c for c in transport.calls if c["method"] == "sendMessage"]
    assert len(texts) == 2


async def test_card_still_sent_when_model_fails(db_ready: Path) -> None:
    del db_ready
    async with session_scope() as session:
        await upsert_job(session, _job("k2"))
    transport = FakeTransport()
    client = TelegramClient(transport=transport, chat_id="999")
    resolver = AnswerResolver(load_profile(), client=_Broken())  # type: ignore[arg-type]
    summary = await send_queue_cards(client, resolver=resolver)
    assert summary.sent == 1
    texts = [c for c in transport.calls if c["method"] == "sendMessage"]
    assert len(texts) == 2

"""Offline tests for the long-poll update processor."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from bot.poller import process_updates, run_polling
from bot.telegram import ReviewAction, TelegramClient, encode_callback
from core.db import Job, Source, Status, get_job_by_id, session_scope, upsert_job
from tests.test_handlers import FakeSubmitter
from tests.test_telegram import FakeTransport


async def test_process_updates_routes_callback(db_ready: Path) -> None:
    job = Job(
        source=Source.workday,
        external_id="wd-poll-1",
        title="Engineer",
        company="Co",
        url="https://co.wd1.myworkdayjobs.com/en-US/External/job/1",
        tenant="co",
        status=Status.pending_review,
        review_message_id=1,
        review_chat_id="999",
    )
    async with session_scope() as session:
        job = await upsert_job(session, job)
    assert job.id is not None

    transport = FakeTransport()
    client = TelegramClient(transport=transport, chat_id="999")
    submitter = FakeSubmitter(mode="ok")

    updates = [
        {
            "update_id": 100,
            "callback_query": {
                "id": "cq-100",
                "data": encode_callback(ReviewAction.discard, job.id),
                "message": {"message_id": 1, "chat": {"id": 999}},
            },
        }
    ]
    next_offset = await process_updates(updates, client=client, submitter=submitter)
    assert next_offset == 101

    async with session_scope() as session:
        refreshed = await get_job_by_id(session, job.id)
        assert refreshed is not None
        assert refreshed.status == Status.ignored


async def test_run_polling_max_iterations() -> None:
    class CountingTransport(FakeTransport):
        def __init__(self) -> None:
            super().__init__()
            self.n = 0

        async def post(
            self,
            method: str,
            payload: dict[str, Any] | None = None,
            *,
            files: dict[str, Any] | None = None,
            timeout: float | None = None,
        ) -> dict[str, Any]:
            self.n += 1
            self.calls.append(
                {
                    "method": method,
                    "payload": payload,
                    "files": files,
                    "timeout": timeout,
                }
            )
            return {"ok": True, "result": []}

    transport = CountingTransport()
    client = TelegramClient(transport=transport, chat_id="1")
    stop = asyncio.Event()
    await run_polling(
        client=client,
        submitter=FakeSubmitter(),
        stop_event=stop,
        max_iterations=2,
    )
    assert transport.n == 2
    assert all(c["method"] == "getUpdates" for c in transport.calls)

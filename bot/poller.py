"""Long-polling loop for Telegram callback_query updates."""

from __future__ import annotations

import asyncio
from typing import Any

import structlog

from bot.handlers import handle_callback, handle_message
from bot.submit import Submitter, WorkdaySubmitter
from bot.telegram import TelegramClient

log = structlog.get_logger(__name__)


async def process_updates(
    updates: list[dict[str, Any]],
    *,
    client: TelegramClient,
    submitter: Submitter,
) -> int | None:
    """Route a batch of updates; return the next offset (last update_id + 1)."""
    next_offset: int | None = None
    for update in updates:
        update_id = update.get("update_id")
        if isinstance(update_id, int):
            next_offset = update_id + 1
        if "callback_query" in update:
            await handle_callback(update, client=client, submitter=submitter)
        elif "message" in update:
            await handle_message(update, client=client)
    return next_offset


async def run_polling(
    *,
    client: TelegramClient | None = None,
    submitter: Submitter | None = None,
    stop_event: asyncio.Event | None = None,
    max_iterations: int | None = None,
) -> None:
    """Long-poll Telegram getUpdates until stop_event is set (or max_iterations).

    Primary runtime path for Step 6. For production (Step 7), prefer the webhook.
    """
    client = client or TelegramClient()
    submitter = submitter or WorkdaySubmitter()
    stop_event = stop_event or asyncio.Event()
    offset: int | None = None
    iterations = 0

    log.info("polling_start", offset=offset)
    while not stop_event.is_set():
        if max_iterations is not None and iterations >= max_iterations:
            break
        iterations += 1
        try:
            updates = await client.get_updates(offset=offset)
            if updates:
                new_offset = await process_updates(
                    updates,
                    client=client,
                    submitter=submitter,
                )
                if new_offset is not None:
                    offset = new_offset
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            log.warning("polling_iteration_failed", error=str(exc))
            await asyncio.sleep(2)
        # Cooperative yield so stop_event can be observed between long polls
        if stop_event.is_set():
            break

    log.info("polling_stop", offset=offset, iterations=iterations)

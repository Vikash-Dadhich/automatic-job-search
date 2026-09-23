"""FastAPI webhook for Telegram (ready for Step 7 production)."""

from __future__ import annotations

from typing import Any

import structlog
from fastapi import FastAPI, Header, HTTPException, Request

from bot.handlers import handle_callback, handle_message
from bot.submit import WorkdaySubmitter
from bot.telegram import TelegramClient
from config.settings import get_settings

log = structlog.get_logger(__name__)

app = FastAPI(title="Job Agent Telegram Webhook", version="0.1.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/telegram/webhook")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
) -> dict[str, Any]:
    """Receive Telegram updates. Validates optional secret token header."""
    settings = get_settings()
    expected = settings.telegram_webhook_secret
    if expected:
        if not x_telegram_bot_api_secret_token or x_telegram_bot_api_secret_token != expected:
            raise HTTPException(status_code=403, detail="Invalid secret token")

    try:
        update = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON") from exc

    if not isinstance(update, dict):
        raise HTTPException(status_code=400, detail="Update must be an object")

    if "callback_query" in update:
        client = TelegramClient()
        submitter = WorkdaySubmitter()
        status = await handle_callback(update, client=client, submitter=submitter)
        return {"ok": True, "status": status.value if status else None}

    if "message" in update:
        client = TelegramClient()
        await handle_message(update, client=client)
        return {"ok": True}

    return {"ok": True, "ignored": True}

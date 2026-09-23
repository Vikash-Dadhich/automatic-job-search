"""Telegram review bot (Step 6)."""

from __future__ import annotations

from bot.alerts import AlertSummary, send_pending_alerts
from bot.handlers import handle_callback
from bot.poller import process_updates, run_polling
from bot.prep import PrepSummary, send_prep_pack
from bot.review import ReviewSummary, send_pending_reviews
from bot.submit import SubmitResult, Submitter, WorkdaySubmitter
from bot.suggest import SuggestSummary, send_pending_suggestions
from bot.telegram import (
    ReviewAction,
    SuggestAction,
    TelegramClient,
    TelegramTransport,
    decode_callback,
    decode_suggest_callback,
    encode_callback,
    encode_suggest_callback,
)
from bot.webhook import app

__all__ = [
    "AlertSummary",
    "PrepSummary",
    "ReviewAction",
    "ReviewSummary",
    "SubmitResult",
    "Submitter",
    "SuggestAction",
    "SuggestSummary",
    "TelegramClient",
    "TelegramTransport",
    "WorkdaySubmitter",
    "app",
    "decode_callback",
    "decode_suggest_callback",
    "encode_callback",
    "encode_suggest_callback",
    "handle_callback",
    "process_updates",
    "run_polling",
    "send_pending_alerts",
    "send_pending_reviews",
    "send_pending_suggestions",
    "send_prep_pack",
]

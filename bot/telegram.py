"""Telegram Bot API client behind a mockable transport protocol."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Any, Protocol

import httpx
import structlog
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from config.settings import get_settings
from core.db import Outcome

log = structlog.get_logger(__name__)

CALLBACK_MAX_BYTES = 64
_LONG_POLL_BUFFER_S = 15.0


class ReviewAction(StrEnum):
    ok = "ok"  # Approve -> submit
    manual = "manual"
    discard = "discard"


class SuggestAction(StrEnum):
    approve = "approve"
    edit = "edit"
    reject = "reject"


def _should_retry_telegram(exc: BaseException) -> bool:
    """Retry transport errors and HTTP 5xx; never retry 4xx client errors."""
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
        return status >= 500
    return isinstance(exc, (httpx.TransportError, httpx.TimeoutException))


class TelegramTransport(Protocol):
    """Minimal async transport (mockable for offline tests)."""

    async def post(
        self,
        method: str,
        payload: dict[str, Any] | None = None,
        *,
        files: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]: ...


class HttpxTransport:
    """Real Telegram Bot API transport via httpx with retries."""

    def __init__(
        self,
        *,
        token: str | None = None,
        api_base: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        settings = get_settings()
        self._token = (token if token is not None else settings.telegram_bot_token) or ""
        if not self._token.strip():
            raise ValueError(
                "TELEGRAM_BOT_TOKEN is empty. Set it in .env before running the review bot."
            )
        base = (api_base if api_base is not None else settings.telegram_api_base).rstrip("/")
        self._url_prefix = f"{base}/bot{self._token.strip()}"
        self._timeout = timeout

    async def post(
        self,
        method: str,
        payload: dict[str, Any] | None = None,
        *,
        files: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        return await self._post_with_retry(
            method,
            payload,
            files=files,
            timeout=timeout,
        )

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
        retry=retry_if_exception(_should_retry_telegram),
    )
    async def _post_with_retry(
        self,
        method: str,
        payload: dict[str, Any] | None = None,
        *,
        files: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        import json

        url = f"{self._url_prefix}/{method}"
        data = dict(payload or {})
        # Multipart form requires nested objects as JSON strings
        if files and isinstance(data.get("reply_markup"), dict):
            data["reply_markup"] = json.dumps(data["reply_markup"])
        client_timeout = timeout if timeout is not None else self._timeout
        async with httpx.AsyncClient(timeout=client_timeout) as client:
            if files:
                response = await client.post(url, data=data, files=files)
            else:
                response = await client.post(url, json=data)
            response.raise_for_status()
            body = response.json()
        if not isinstance(body, dict):
            raise ValueError(f"Unexpected Telegram response type: {type(body).__name__}")
        if not body.get("ok"):
            raise RuntimeError(f"Telegram API error on {method}: {body}")
        return body


def encode_callback(action: ReviewAction | str, job_id: int) -> str:
    """Encode inline-keyboard callback_data: v1|<action>|<job_id> (<=64 bytes)."""
    act = ReviewAction(action) if not isinstance(action, ReviewAction) else action
    if job_id < 0:
        raise ValueError("job_id must be non-negative")
    data = f"v1|{act.value}|{job_id}"
    if len(data.encode("utf-8")) > CALLBACK_MAX_BYTES:
        raise ValueError(f"callback_data exceeds {CALLBACK_MAX_BYTES} bytes: {data!r}")
    return data


def decode_callback(data: str) -> tuple[ReviewAction, int]:
    """Decode callback_data into (action, job_id)."""
    parts = (data or "").strip().split("|")
    if len(parts) != 3 or parts[0] != "v1":
        raise ValueError(f"Invalid callback_data: {data!r}")
    action = ReviewAction(parts[1])
    job_id = int(parts[2])
    return action, job_id


def encode_suggest_callback(action: SuggestAction | str, suggestion_id: int) -> str:
    """Encode suggestion callback_data: s1|<action>|<suggestion_id> (<=64 bytes)."""
    act = SuggestAction(action) if not isinstance(action, SuggestAction) else action
    if suggestion_id < 0:
        raise ValueError("suggestion_id must be non-negative")
    data = f"s1|{act.value}|{suggestion_id}"
    if len(data.encode("utf-8")) > CALLBACK_MAX_BYTES:
        raise ValueError(f"callback_data exceeds {CALLBACK_MAX_BYTES} bytes: {data!r}")
    return data


def decode_suggest_callback(data: str) -> tuple[SuggestAction, int]:
    """Decode suggestion callback_data into (action, suggestion_id)."""
    parts = (data or "").strip().split("|")
    if len(parts) != 3 or parts[0] != "s1":
        raise ValueError(f"Invalid suggest callback_data: {data!r}")
    action = SuggestAction(parts[1])
    suggestion_id = int(parts[2])
    return action, suggestion_id


def is_suggest_callback(data: str) -> bool:
    return (data or "").startswith("s1|")


def encode_outcome_callback(outcome: Outcome | str, job_id: int) -> str:
    """Encode outcome callback_data: o1|<outcome>|<job_id> (<=64 bytes)."""
    label = outcome if isinstance(outcome, Outcome) else Outcome(outcome)
    if job_id < 0:
        raise ValueError("job_id must be non-negative")
    data = f"o1|{label.value}|{job_id}"
    if len(data.encode("utf-8")) > CALLBACK_MAX_BYTES:
        raise ValueError(f"callback_data exceeds {CALLBACK_MAX_BYTES} bytes: {data!r}")
    return data


def decode_outcome_callback(data: str) -> tuple[Outcome, int]:
    """Decode outcome callback_data into (outcome, job_id)."""
    parts = (data or "").strip().split("|")
    if len(parts) != 3 or parts[0] != "o1":
        raise ValueError(f"Invalid outcome callback_data: {data!r}")
    outcome = Outcome(parts[1])
    job_id = int(parts[2])
    return outcome, job_id


def is_outcome_callback(data: str) -> bool:
    return (data or "").startswith("o1|")


class TelegramClient:
    """High-level Telegram helpers used by review / handlers / poller."""

    def __init__(
        self,
        *,
        transport: TelegramTransport | None = None,
        chat_id: str | None = None,
    ) -> None:
        self._transport = transport
        settings = get_settings()
        self._chat_id = chat_id if chat_id is not None else settings.telegram_chat_id

    @property
    def chat_id(self) -> str | None:
        """Configured default chat id (may be None until set in .env)."""
        return self._chat_id

    def _resolve_transport(self) -> TelegramTransport:
        if self._transport is not None:
            return self._transport
        return HttpxTransport()

    def _require_chat_id(self, chat_id: str | None = None) -> str:
        cid = chat_id if chat_id is not None else self._chat_id
        if not cid:
            raise ValueError(
                "TELEGRAM_CHAT_ID is empty. Set it in .env before sending reviews."
            )
        return str(cid)

    async def send_message(
        self,
        text: str,
        *,
        chat_id: str | None = None,
        reply_markup: dict[str, Any] | None = None,
        parse_mode: str | None = None,
        disable_web_page_preview: bool = True,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "chat_id": self._require_chat_id(chat_id),
            "text": text,
            "disable_web_page_preview": disable_web_page_preview,
        }
        if reply_markup is not None:
            payload["reply_markup"] = reply_markup
        if parse_mode:
            payload["parse_mode"] = parse_mode
        result = await self._resolve_transport().post("sendMessage", payload)
        return result.get("result") or {}

    async def send_photo(
        self,
        photo_path: Path | str,
        *,
        caption: str | None = None,
        chat_id: str | None = None,
        reply_markup: dict[str, Any] | None = None,
        parse_mode: str | None = None,
    ) -> dict[str, Any]:
        path = Path(photo_path)
        if not path.is_file():
            raise FileNotFoundError(f"Screenshot not found: {path}")
        payload: dict[str, Any] = {"chat_id": self._require_chat_id(chat_id)}
        if caption is not None:
            payload["caption"] = caption
        if reply_markup is not None:
            payload["reply_markup"] = reply_markup
        if parse_mode:
            payload["parse_mode"] = parse_mode

        with path.open("rb") as handle:
            files = {"photo": (path.name, handle, "image/png")}
            result = await self._resolve_transport().post(
                "sendPhoto",
                payload,
                files=files,
            )
        return result.get("result") or {}

    async def send_document(
        self,
        document_path: Path | str,
        *,
        caption: str | None = None,
        chat_id: str | None = None,
        mime_type: str | None = None,
    ) -> dict[str, Any]:
        path = Path(document_path)
        if not path.is_file():
            raise FileNotFoundError(f"Document not found: {path}")
        payload: dict[str, Any] = {"chat_id": self._require_chat_id(chat_id)}
        if caption is not None:
            payload["caption"] = caption

        suffix = path.suffix.lower()
        mime = mime_type
        if mime is None:
            if suffix == ".pdf":
                mime = "application/pdf"
            elif suffix in {".md", ".markdown", ".txt"}:
                mime = "text/plain"
            else:
                mime = "application/octet-stream"

        with path.open("rb") as handle:
            files = {"document": (path.name, handle, mime)}
            result = await self._resolve_transport().post(
                "sendDocument",
                payload,
                files=files,
            )
        return result.get("result") or {}

    async def edit_message_caption(
        self,
        *,
        chat_id: str | int,
        message_id: int,
        caption: str,
        reply_markup: dict[str, Any] | None = None,
        parse_mode: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "chat_id": str(chat_id),
            "message_id": message_id,
            "caption": caption,
        }
        if reply_markup is not None:
            payload["reply_markup"] = reply_markup
        if parse_mode:
            payload["parse_mode"] = parse_mode
        result = await self._resolve_transport().post("editMessageCaption", payload)
        return result.get("result") or {}

    async def edit_message_text(
        self,
        *,
        chat_id: str | int,
        message_id: int,
        text: str,
        reply_markup: dict[str, Any] | None = None,
        parse_mode: str | None = None,
    ) -> dict[str, Any]:
        """Edit a text message. Outcome cards are text, not photos."""
        payload: dict[str, Any] = {
            "chat_id": str(chat_id),
            "message_id": message_id,
            "text": text,
        }
        if reply_markup is not None:
            payload["reply_markup"] = reply_markup
        if parse_mode:
            payload["parse_mode"] = parse_mode
        result = await self._resolve_transport().post("editMessageText", payload)
        return result.get("result") or {}

    async def edit_message_reply_markup(
        self,
        *,
        chat_id: str | int,
        message_id: int,
        reply_markup: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "chat_id": str(chat_id),
            "message_id": message_id,
            "reply_markup": reply_markup or {"inline_keyboard": []},
        }
        result = await self._resolve_transport().post("editMessageReplyMarkup", payload)
        return result.get("result") or {}

    async def answer_callback_query(
        self,
        callback_query_id: str,
        *,
        text: str | None = None,
        show_alert: bool = False,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"callback_query_id": callback_query_id}
        if text is not None:
            payload["text"] = text
        if show_alert:
            payload["show_alert"] = True
        result = await self._resolve_transport().post("answerCallbackQuery", payload)
        return result.get("result") or {}

    async def get_updates(
        self,
        *,
        offset: int | None = None,
        timeout: int | None = None,
        allowed_updates: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        settings = get_settings()
        poll_timeout = timeout if timeout is not None else settings.telegram_poll_timeout
        payload: dict[str, Any] = {
            "timeout": poll_timeout,
            "allowed_updates": allowed_updates
            if allowed_updates is not None
            else ["callback_query", "message"],
        }
        if offset is not None:
            payload["offset"] = offset
        # HTTP client timeout must exceed Telegram's long-poll timeout
        http_timeout = float(poll_timeout) + _LONG_POLL_BUFFER_S
        transport = self._resolve_transport()
        result = await transport.post("getUpdates", payload, timeout=http_timeout)
        updates = result.get("result") or []
        if not isinstance(updates, list):
            return []
        return updates

    async def set_webhook(
        self,
        url: str,
        *,
        secret_token: str | None = None,
        drop_pending_updates: bool = False,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "url": url,
            "allowed_updates": ["callback_query", "message"],
            "drop_pending_updates": drop_pending_updates,
        }
        if secret_token:
            payload["secret_token"] = secret_token
        result = await self._resolve_transport().post("setWebhook", payload)
        return result.get("result") or {}

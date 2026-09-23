"""Offline tests for Telegram codec + client (FakeTransport)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from bot.telegram import (
    CALLBACK_MAX_BYTES,
    ReviewAction,
    TelegramClient,
    decode_callback,
    encode_callback,
)


class FakeTransport:
    def __init__(self, *, responses: dict[str, dict[str, Any]] | None = None) -> None:
        self.calls: list[dict[str, Any]] = []
        self.responses = responses or {}

    async def post(
        self,
        method: str,
        payload: dict[str, Any] | None = None,
        *,
        files: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        self.calls.append(
            {
                "method": method,
                "payload": payload,
                "files": files,
                "timeout": timeout,
            }
        )
        if method in self.responses:
            return self.responses[method]
        if method == "sendPhoto":
            return {
                "ok": True,
                "result": {
                    "message_id": 42,
                    "chat": {"id": 999},
                },
            }
        if method == "sendDocument":
            return {
                "ok": True,
                "result": {
                    "message_id": 44,
                    "chat": {"id": 999},
                },
            }
        if method == "sendMessage":
            return {
                "ok": True,
                "result": {
                    "message_id": 43,
                    "chat": {"id": 999},
                },
            }
        if method == "answerCallbackQuery":
            return {"ok": True, "result": True}
        if method == "getUpdates":
            return {"ok": True, "result": []}
        return {"ok": True, "result": {}}


def test_encode_decode_roundtrip() -> None:
    data = encode_callback(ReviewAction.ok, 123)
    assert data == "v1|ok|123"
    assert len(data.encode("utf-8")) <= CALLBACK_MAX_BYTES
    action, job_id = decode_callback(data)
    assert action == ReviewAction.ok
    assert job_id == 123

    for action in (ReviewAction.manual, ReviewAction.discard):
        encoded = encode_callback(action, 7)
        decoded_action, decoded_id = decode_callback(encoded)
        assert decoded_action == action
        assert decoded_id == 7


def test_decode_invalid() -> None:
    with pytest.raises(ValueError):
        decode_callback("bad")
    with pytest.raises(ValueError):
        decode_callback("v1|nope|1")
    with pytest.raises(ValueError):
        encode_callback(ReviewAction.ok, -1)


async def test_send_photo_builds_payload(tmp_path: Path) -> None:
    png = tmp_path / "shot.png"
    png.write_bytes(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
        b"\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18"
        b"\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    transport = FakeTransport()
    client = TelegramClient(transport=transport, chat_id="999")
    keyboard = {
        "inline_keyboard": [[{"text": "Approve", "callback_data": "v1|ok|1"}]]
    }
    result = await client.send_photo(
        png,
        caption="Hello",
        reply_markup=keyboard,
    )
    assert result["message_id"] == 42
    assert transport.calls[0]["method"] == "sendPhoto"
    assert transport.calls[0]["payload"]["chat_id"] == "999"
    assert transport.calls[0]["payload"]["caption"] == "Hello"
    assert transport.calls[0]["payload"]["reply_markup"] == keyboard
    assert transport.calls[0]["files"] is not None


async def test_send_document_builds_payload(tmp_path: Path) -> None:
    doc = tmp_path / "prep.md"
    doc.write_text("# Prep\n", encoding="utf-8")
    transport = FakeTransport()
    client = TelegramClient(transport=transport, chat_id="999")
    result = await client.send_document(doc, caption="Prep pack")
    assert result["message_id"] == 44
    assert transport.calls[0]["method"] == "sendDocument"
    assert transport.calls[0]["payload"]["chat_id"] == "999"
    assert transport.calls[0]["payload"]["caption"] == "Prep pack"
    assert transport.calls[0]["files"] is not None


async def test_answer_callback() -> None:
    transport = FakeTransport()
    client = TelegramClient(transport=transport, chat_id="1")
    await client.answer_callback_query("cq-1", text="done")
    assert transport.calls[0]["method"] == "answerCallbackQuery"
    assert transport.calls[0]["payload"]["callback_query_id"] == "cq-1"
    assert transport.calls[0]["payload"]["text"] == "done"


async def test_get_updates_extends_http_timeout() -> None:
    transport = FakeTransport()
    client = TelegramClient(transport=transport, chat_id="1")
    updates = await client.get_updates(timeout=60)
    assert updates == []
    assert transport.calls[0]["method"] == "getUpdates"
    assert transport.calls[0]["payload"]["timeout"] == 60
    # HTTP client timeout = poll timeout + 15s buffer
    assert transport.calls[0]["timeout"] == 75.0


def test_should_retry_telegram() -> None:
    import httpx

    from bot.telegram import _should_retry_telegram

    assert _should_retry_telegram(httpx.ConnectError("boom"))
    assert _should_retry_telegram(httpx.ReadTimeout("slow"))

    request = httpx.Request("POST", "https://api.telegram.org/botX/getUpdates")
    resp_500 = httpx.Response(500, request=request)
    assert _should_retry_telegram(httpx.HTTPStatusError("err", request=request, response=resp_500))
    resp_400 = httpx.Response(400, request=request)
    assert not _should_retry_telegram(
        httpx.HTTPStatusError("err", request=request, response=resp_400)
    )
    assert not _should_retry_telegram(ValueError("nope"))


def test_chat_id_property() -> None:
    client = TelegramClient(transport=FakeTransport(), chat_id="42")
    assert client.chat_id == "42"

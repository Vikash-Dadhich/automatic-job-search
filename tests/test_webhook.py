"""Offline tests for FastAPI Telegram webhook."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from bot.webhook import app
from config.settings import get_settings
from core.db import Status


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_health(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_webhook_ignored_without_callback(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", "")
    get_settings.cache_clear()
    resp = client.post("/telegram/webhook", json={"update_id": 1})
    assert resp.status_code == 200
    assert resp.json()["ignored"] is True
    get_settings.cache_clear()


def test_webhook_rejects_bad_secret(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", "correct-secret")
    get_settings.cache_clear()
    resp = client.post(
        "/telegram/webhook",
        json={"update_id": 1},
        headers={"X-Telegram-Bot-Api-Secret-Token": "wrong"},
    )
    assert resp.status_code == 403
    get_settings.cache_clear()


def test_webhook_routes_callback(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", "s3cret")
    get_settings.cache_clear()

    fake = AsyncMock(return_value=Status.ignored)
    with patch("bot.webhook.handle_callback", fake):
        with patch("bot.webhook.TelegramClient"), patch("bot.webhook.WorkdaySubmitter"):
            resp = client.post(
                "/telegram/webhook",
                json={
                    "update_id": 2,
                    "callback_query": {
                        "id": "cq-1",
                        "data": "v1|discard|1",
                        "message": {"message_id": 1, "chat": {"id": 9}},
                    },
                },
                headers={"X-Telegram-Bot-Api-Secret-Token": "s3cret"},
            )
    assert resp.status_code == 200
    body: dict[str, Any] = resp.json()
    assert body["ok"] is True
    assert body["status"] == "ignored"
    fake.assert_awaited_once()
    get_settings.cache_clear()

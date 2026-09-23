"""DATABASE_URL normalization for SQLite + Neon Postgres."""

from __future__ import annotations

from core.db import normalize_database_url


def test_normalize_keeps_sqlite() -> None:
    url = normalize_database_url("sqlite+aiosqlite:///storage/job_agent.db")
    assert url.startswith("sqlite+aiosqlite:///")
    assert url.endswith("storage/job_agent.db")
    assert "/Users/" in url or url.count("/") >= 3


def test_normalize_upgrades_postgresql() -> None:
    raw = (
        "postgresql://user:pass@ep-x.us-west-2.aws.neon.tech/neondb"
        "?channel_binding=require&sslmode=require"
    )
    url = normalize_database_url(raw)
    assert url.startswith("postgresql+asyncpg://")
    assert "channel_binding" not in url
    assert "sslmode" not in url
    assert "ssl=require" in url
    assert "user:pass@" in url


def test_normalize_drops_prisma_connection_limit() -> None:
    raw = (
        "postgresql://user:pass@ep-x-pooler.c-3.us-west-2.aws.neon.tech/neondb"
        "?sslmode=require&connection_limit=5&channel_binding=require"
    )
    url = normalize_database_url(raw)
    assert "connection_limit" not in url
    assert "channel_binding" not in url
    assert "ssl=require" in url


def test_normalize_upgrades_postgres_scheme() -> None:
    url = normalize_database_url("postgres://u:p@host/db")
    assert url.startswith("postgresql+asyncpg://")

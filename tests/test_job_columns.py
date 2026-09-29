"""Idempotent ALTER for Phase 2 columns on an existing jobs table."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from sqlalchemy import text

from core.db import get_engine, init_db, reset_engine


async def test_ensure_job_columns_on_legacy_table(tmp_db: Path) -> None:
    raw = sqlite3.connect(tmp_db)
    raw.execute("CREATE TABLE jobs (id INTEGER PRIMARY KEY, title TEXT)")
    raw.commit()
    raw.close()

    await reset_engine()
    await init_db()
    engine = get_engine()
    async with engine.connect() as conn:
        rows = (await conn.execute(text("PRAGMA table_info(jobs)"))).fetchall()
    names = {row[1] for row in rows}
    assert {
        "cover_letter",
        "outcome",
        "outcome_at",
        "outcome_message_id",
        "embedding",
        "vector_score",
        "vector_profile_hash",
        "embedding_model",
        "discovery_family",
        "discovery_bucket",
        "discovery_query",
        "jd_status",
        "jd_char_count",
        "jd_truncated",
        "jd_extraction_path",
    } <= names

    await init_db()
    await reset_engine()

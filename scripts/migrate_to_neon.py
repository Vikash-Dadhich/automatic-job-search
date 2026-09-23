"""Copy local SQLite rows into the Neon Postgres database.

Reads storage/job_agent.db and writes to DATABASE_URL (must be Postgres).
Re-running is safe: primary-key conflicts are skipped. Sequences are reset
so later inserts do not collide with the copied ids.

Usage:
  uv run python scripts/migrate_to_neon.py
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from config.settings import PROJECT_ROOT, get_settings
from core.db import (
    Benchmark,
    Job,
    PeerProfile,
    RoleBaseline,
    SkillSuggestion,
    SQLModel,
    normalize_database_url,
)

BATCH = 50
SQLITE_URL = f"sqlite+aiosqlite:///{(PROJECT_ROOT / 'storage' / 'job_agent.db').resolve()}"

# FK-safe order.
TABLES = (Job, RoleBaseline, SkillSuggestion, PeerProfile, Benchmark)


def _cell(value: object) -> object:
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, datetime) and value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value


def _row(model: SQLModel) -> dict[str, object]:
    table = model.__table__  # type: ignore[attr-defined]
    return {col.name: _cell(getattr(model, col.name)) for col in table.columns}


async def _copy_table(
    src: AsyncSession,
    dst_engine,
    model: type[SQLModel],
) -> int:
    rows = list((await src.exec(select(model))).all())
    if not rows:
        return 0
    table = model.__table__  # type: ignore[attr-defined]
    payload = [_row(row) for row in rows]
    inserted = 0
    async with dst_engine.begin() as conn:
        for start in range(0, len(payload), BATCH):
            chunk = payload[start : start + BATCH]
            stmt = pg_insert(table).values(chunk).on_conflict_do_nothing(index_elements=["id"])
            result = await conn.execute(stmt)
            inserted += result.rowcount or 0
    return inserted


async def _reset_sequences(dst_engine) -> None:
    async with dst_engine.begin() as conn:
        for model in TABLES:
            table = model.__tablename__  # type: ignore[attr-defined]
            await conn.execute(
                text(
                    "SELECT setval("
                    "pg_get_serial_sequence(:table, 'id'), "
                    "COALESCE((SELECT MAX(id) FROM "
                    + table
                    + "), 1), true)"
                ),
                {"table": table},
            )


async def _counts(engine, label: str) -> dict[str, int]:
    out: dict[str, int] = {}
    async with engine.connect() as conn:
        for model in TABLES:
            table = model.__tablename__  # type: ignore[attr-defined]
            n = (await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))).scalar_one()
            out[table] = int(n)
    print(label, out)
    return out


async def main() -> None:
    sqlite_path = Path(SQLITE_URL.removeprefix("sqlite+aiosqlite:///"))
    if not sqlite_path.is_file():
        raise SystemExit(f"SQLite database not found: {sqlite_path}")

    settings = get_settings()
    neon_url = normalize_database_url(settings.database_url)
    if not neon_url.startswith("postgresql+"):
        raise SystemExit(
            "DATABASE_URL is not Postgres. Point .env at Neon before migrating."
        )

    src_engine = create_async_engine(SQLITE_URL, echo=False)
    connect_args: dict[str, object] = {}
    if "-pooler." in neon_url:
        connect_args["statement_cache_size"] = 0
    dst_engine = create_async_engine(neon_url, echo=False, connect_args=connect_args)

    src_factory = async_sessionmaker(src_engine, class_=AsyncSession, expire_on_commit=False)
    try:
        await _counts(src_engine, "sqlite")
        async with src_factory() as src:
            for model in TABLES:
                copied = await _copy_table(src, dst_engine, model)
                print(f"inserted {model.__tablename__}={copied}")  # type: ignore[attr-defined]
        await _reset_sequences(dst_engine)
        neon = await _counts(dst_engine, "neon")
        sqlite = await _counts(src_engine, "sqlite_check")
        mismatches = {
            name: (sqlite[name], neon[name])
            for name in sqlite
            if neon.get(name, 0) < sqlite[name]
        }
        if mismatches:
            raise SystemExit(f"Neon has fewer rows than SQLite: {mismatches}")
        print("PASS migration")
    finally:
        await src_engine.dispose()
        await dst_engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

"""Shared pytest fixtures — isolate DB and clear settings caches."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from pathlib import Path

import pytest

from config.profile import load_profile
from config.settings import get_settings
from config.targets import load_targets
from core.db import init_db, reset_engine
from scorer.clients import reset_openai_request_ledger


@pytest.fixture(autouse=True)
def _disable_apply_pacing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep the suite off the 7–18 minute Workday gap unless a test opts in."""
    monkeypatch.setenv("APPLY_PACING_ENABLED", "false")
    get_settings.cache_clear()


@pytest.fixture(autouse=True)
def _isolate_profile_embedding_cache(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Fake test vectors must never be written next to real cached profile vectors."""
    monkeypatch.setattr(
        "scorer.embeddings._cache_path",
        lambda digest: tmp_path / "embeddings" / f"profile-{digest}.json",
    )


@pytest.fixture(autouse=True)
def _disable_vector_gate(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep scoring offline unless a test opts into the embedding gate."""
    monkeypatch.setenv("VECTOR_GATE_ENABLED", "false")
    get_settings.cache_clear()


@pytest.fixture(autouse=True)
def _reset_openai_request_ledger_between_tests() -> Iterator[None]:
    """A billing halt is process-wide. Keep it inside the test that set it."""
    reset_openai_request_ledger()
    yield
    reset_openai_request_ledger()


@pytest.fixture(autouse=True)
def _internship_only_off(monkeypatch: pytest.MonkeyPatch) -> None:
    """Lock the code default. A developer .env may set INTERNSHIP_ONLY=true."""
    monkeypatch.setenv("INTERNSHIP_ONLY", "false")
    get_settings.cache_clear()


@pytest.fixture
def tmp_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    """Point DATABASE_URL at a temp sqlite file and clear cached settings/engine."""
    db_path = tmp_path / "test_job_agent.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    monkeypatch.setenv("RESUMES_DIR", str(tmp_path / "resumes"))
    monkeypatch.setenv("SCREENSHOTS_DIR", str(tmp_path / "screenshots"))
    monkeypatch.setenv("SESSIONS_DIR", str(tmp_path / "sessions"))
    monkeypatch.setenv("BASELINES_DIR", str(tmp_path / "baselines"))
    monkeypatch.setenv("BENCHMARKS_DIR", str(tmp_path / "benchmarks"))
    monkeypatch.setenv("PREP_PACKS_DIR", str(tmp_path / "prep_packs"))

    get_settings.cache_clear()
    load_profile.cache_clear()
    load_targets.cache_clear()
    try:
        from automation.vault import load_credentials

        load_credentials.cache_clear()
    except ImportError:
        pass

    yield db_path

    get_settings.cache_clear()
    load_profile.cache_clear()
    load_targets.cache_clear()
    try:
        from automation.vault import load_credentials

        load_credentials.cache_clear()
    except ImportError:
        pass


@pytest.fixture
async def db_ready(tmp_db: Path) -> AsyncIterator[Path]:
    """Initialize a fresh DB for each async test; dispose engine afterward."""
    await reset_engine()
    await init_db()
    yield tmp_db
    await reset_engine()


@pytest.fixture
def profile():
    """Load the project profile.yaml (placeholders are fine for filter tests)."""
    load_profile.cache_clear()
    return load_profile()

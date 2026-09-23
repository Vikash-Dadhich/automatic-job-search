"""Tests for credential vault and session path helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from automation.vault import (
    get_tenant_credentials,
    has_saved_session,
    load_credentials,
    reload_credentials,
    session_state_path,
)


def test_session_state_path(tmp_path: Path) -> None:
    path = session_state_path("AcmeCorp", sessions_dir=tmp_path)
    assert path == tmp_path / "acmecorp.json"


def test_session_state_path_rejects_empty() -> None:
    with pytest.raises(ValueError):
        session_state_path("  ")


def test_has_saved_session(tmp_path: Path) -> None:
    assert not has_saved_session("acme", sessions_dir=tmp_path)
    target = session_state_path("acme", sessions_dir=tmp_path)
    target.write_text("{}", encoding="utf-8")
    assert has_saved_session("acme", sessions_dir=tmp_path)


def test_load_credentials_missing_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CREDENTIALS_PATH", str(tmp_path / "missing.yaml"))
    from config.settings import get_settings

    get_settings.cache_clear()
    load_credentials.cache_clear()
    creds = reload_credentials()
    assert creds.tenants == {}
    get_settings.cache_clear()
    load_credentials.cache_clear()


def test_get_tenant_credentials_placeholder_skip(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "creds.yaml"
    path.write_text(
        """
tenants:
  PLACEHOLDER_TENANT:
    email: "you@example.com"
    password: "PLACEHOLDER_PASSWORD"
  realco:
    email: "me@real.com"
    password: "s3cret"
""",
        encoding="utf-8",
    )
    monkeypatch.setenv("CREDENTIALS_PATH", str(path))
    from config.settings import get_settings

    get_settings.cache_clear()
    load_credentials.cache_clear()

    assert get_tenant_credentials("PLACEHOLDER_TENANT") is None
    real = get_tenant_credentials("RealCo")
    assert real is not None
    assert real.email == "me@real.com"

    # Explicitly allow placeholders
    ph = get_tenant_credentials("PLACEHOLDER_TENANT", skip_placeholders=False)
    assert ph is not None
    assert ph.is_placeholder

    get_settings.cache_clear()
    load_credentials.cache_clear()

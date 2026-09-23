"""Per-tenant credentials and Playwright storage_state paths."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import structlog
import yaml
from pydantic import BaseModel, Field

from config.settings import get_settings

log = structlog.get_logger(__name__)


class TenantCredentials(BaseModel):
    email: str
    password: str

    @property
    def is_placeholder(self) -> bool:
        email_l = self.email.lower()
        pwd = self.password
        return (
            "placeholder" in email_l
            or "placeholder" in pwd.lower()
            or email_l.endswith("@example.com")
            or pwd.upper().startswith("PLACEHOLDER")
        )


class CredentialsFile(BaseModel):
    tenants: dict[str, TenantCredentials] = Field(default_factory=dict)


def session_state_path(tenant: str, *, sessions_dir: Path | None = None) -> Path:
    """Path to Playwright storage_state JSON for a Workday tenant slug."""
    slug = (tenant or "").strip().lower()
    if not slug:
        raise ValueError("tenant must be a non-empty string")
    base = sessions_dir if sessions_dir is not None else get_settings().sessions_path
    return Path(base) / f"{slug}.json"


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"Credentials YAML must be a mapping, got {type(data).__name__}")
    return data


@lru_cache
def load_credentials(path: str | None = None) -> CredentialsFile:
    """Load credentials.yaml (optional; missing file => empty tenants)."""
    settings = get_settings()
    cred_path = Path(path) if path else settings.credentials_file
    raw = _load_yaml(cred_path)
    if not raw:
        return CredentialsFile()
    return CredentialsFile.model_validate(raw)


def reload_credentials(path: str | None = None) -> CredentialsFile:
    load_credentials.cache_clear()
    return load_credentials(path)


def get_tenant_credentials(
    tenant: str,
    *,
    path: str | None = None,
    skip_placeholders: bool = True,
) -> TenantCredentials | None:
    """Look up credentials by tenant key (case-insensitive)."""
    key = (tenant or "").strip()
    if not key:
        return None
    creds = load_credentials(path)
    # Exact then case-insensitive match
    entry = creds.tenants.get(key)
    if entry is None:
        lower = key.lower()
        for name, value in creds.tenants.items():
            if name.lower() == lower:
                entry = value
                break
    if entry is None:
        return None
    if skip_placeholders and entry.is_placeholder:
        log.info("credentials_placeholder_skipped", tenant=key)
        return None
    return entry


def has_saved_session(tenant: str, *, sessions_dir: Path | None = None) -> bool:
    path = session_state_path(tenant, sessions_dir=sessions_dir)
    return path.is_file() and path.stat().st_size > 0

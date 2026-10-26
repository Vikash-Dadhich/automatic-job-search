"""Load and validate discovery targets (search terms + Workday tenants)."""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator

TARGETS_PATH = Path(__file__).resolve().parent / "targets.yaml"

_LOCALE_RE = re.compile(r"^[a-z]{2}(?:-[A-Z]{2})?$")
_HOST_RE = re.compile(
    r"^(?P<tenant>[a-zA-Z0-9_-]+)\.(?P<shard>wd\d+)\.myworkdayjobs\.com$",
    re.IGNORECASE,
)


class WorkdayParts(BaseModel):
    tenant: str
    shard: str
    site: str
    host: str

    @property
    def base_cxs(self) -> str:
        return f"https://{self.host}/wday/cxs/{self.tenant}/{self.site}"

    @property
    def public_base(self) -> str:
        return f"https://{self.host}/en-US/{self.site}"


def parse_workday_url(url: str) -> WorkdayParts:
    """Extract tenant, shard, and site from a Workday careers / job deep link.

    Walks past locale path segments (e.g. /en-US/, /fr-CA/) so site is not
    mistaken for a locale code.
    """
    parsed = urlparse(url.strip())
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"Invalid Workday URL (missing scheme/host): {url!r}")

    host_match = _HOST_RE.match(parsed.netloc.lower())
    if not host_match:
        raise ValueError(
            f"URL host is not a Workday careers host "
            f"(expected {{tenant}}.wdN.myworkdayjobs.com): {parsed.netloc!r}"
        )

    tenant = host_match.group("tenant")
    shard = host_match.group("shard")

    segments = [s for s in parsed.path.split("/") if s]
    # Drop CXS API prefix if present: /wday/cxs/{tenant}/{site}/...
    if (
        len(segments) >= 4
        and segments[0].lower() == "wday"
        and segments[1].lower() == "cxs"
    ):
        site = segments[3]
    else:
        # Skip leading locale segments like en-US / fr-CA
        idx = 0
        while idx < len(segments) and _LOCALE_RE.match(segments[idx]):
            idx += 1
        if idx >= len(segments):
            raise ValueError(f"Could not find site name in Workday URL path: {url!r}")
        site = segments[idx]
        # Site should not be the literal "job" path segment from a deep link
        if site.lower() == "job" and idx + 1 < len(segments):
            # Deep link like /en-US/External/job/City/Title_ID — site is previous
            raise ValueError(f"Ambiguous Workday site path: {url!r}")

    if not site or site.lower() in {"wday", "cxs", "job", "jobs"}:
        raise ValueError(f"Could not parse Workday site from URL: {url!r}")

    host = f"{tenant}.{shard}.myworkdayjobs.com"
    return WorkdayParts(tenant=tenant, shard=shard, site=site, host=host)


class SearchConfig(BaseModel):
    terms: list[str] = Field(default_factory=list)
    sites: list[str] = Field(default_factory=lambda: ["linkedin", "indeed"])
    location: str = "United States"
    distance: int = 50
    results_wanted: int = 25
    country_indeed: str = "USA"
    hours_old: int = 24
    linkedin_fetch_description: bool = True

    @field_validator("sites")
    @classmethod
    def validate_sites(cls, value: list[str]) -> list[str]:
        allowed = {"linkedin", "indeed", "google", "zip_recruiter"}
        normalized = [s.lower().strip() for s in value]
        bad = [s for s in normalized if s not in allowed]
        if bad:
            raise ValueError(f"Unsupported sites {bad}; allowed: {sorted(allowed)}")
        if not normalized:
            raise ValueError("search.sites must not be empty")
        return normalized

    @field_validator("terms")
    @classmethod
    def validate_terms(cls, value: list[str]) -> list[str]:
        return [t.strip() for t in value if t and t.strip()]


class WorkdayTenant(BaseModel):
    name: str
    url: str
    search_terms: list[str] = Field(default_factory=list)

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        # Soft-validate shape; real parse happens at fetch time so placeholders
        # can exist in the YAML until the user fills them in.
        value = value.strip()
        if not value.startswith("http"):
            raise ValueError("workday tenant url must be an http(s) URL")
        return value

    def parsed(self) -> WorkdayParts:
        return parse_workday_url(self.url)

    @property
    def is_placeholder(self) -> bool:
        return "placeholder" in self.url.lower() or self.name.upper().startswith(
            "PLACEHOLDER"
        )


ATS_PROVIDERS = ("greenhouse", "lever", "ashby")


class AtsBoard(BaseModel):
    """One company's public job board on Greenhouse, Lever, or Ashby."""

    name: str
    provider: str
    token: str
    startup: bool = False
    # False until someone has opened the board and seen it return jobs.
    verified: bool = False

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, value: str) -> str:
        value = value.lower().strip()
        if value not in ATS_PROVIDERS:
            raise ValueError(f"provider must be one of {ATS_PROVIDERS}, got {value!r}")
        return value

    @field_validator("token")
    @classmethod
    def validate_token(cls, value: str) -> str:
        value = value.strip()
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", value):
            raise ValueError(f"board token has unexpected characters: {value!r}")
        return value


class Targets(BaseModel):
    search: SearchConfig
    workday_tenants: list[WorkdayTenant] = Field(default_factory=list)
    ats_boards: list[AtsBoard] = Field(default_factory=list)

    @model_validator(mode="after")
    def _note_empty_tenants(self) -> Targets:
        # Empty list is allowed (LinkedIn/Indeed-only MVP runs).
        return self

    def active_workday_tenants(self) -> list[WorkdayTenant]:
        """Skip placeholder tenants until the user fills real URLs."""
        return [t for t in self.workday_tenants if not t.is_placeholder]


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Targets not found: {path}")
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Targets YAML must be a mapping, got {type(data).__name__}")
    return data


@lru_cache
def load_targets(path: str | None = None) -> Targets:
    """Load and validate targets.yaml. Cached after first successful load."""
    targets_path = Path(path) if path else TARGETS_PATH
    raw = _load_yaml(targets_path)
    targets = Targets.model_validate(raw)
    from scraper.discovery import enabled_query_texts

    terms = enabled_query_texts()
    if not terms:
        raise ValueError("discovery config has no enabled queries")
    targets.search.terms = terms
    return targets


def reload_targets(path: str | None = None) -> Targets:
    """Clear cache and reload (useful after editing targets.yaml)."""
    load_targets.cache_clear()
    return load_targets(path)

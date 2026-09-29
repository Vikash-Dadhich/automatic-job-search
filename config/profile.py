"""Load and validate the grounded candidate profile from YAML."""

from __future__ import annotations

import re
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator

PROFILE_PATH = Path(__file__).resolve().parent / "profile.yaml"

_MONTH_RE = re.compile(r"(\d{4})(?:[-/](\d{1,2}))?")


def _parse_month(value: str | None) -> date | None:
    """Parse 'YYYY-MM' / 'YYYY'; 'Present' and unparseable values return None."""
    text = (value or "").strip()
    if not text or text.lower() in {"present", "current", "now", "ongoing"}:
        return None
    match = _MONTH_RE.search(text)
    if not match:
        return None
    year = int(match.group(1))
    month = int(match.group(2) or 1)
    return date(year, min(max(month, 1), 12), 1)


class Address(BaseModel):
    street: str
    city: str
    state: str
    zip: str
    country: str = "United States"


class Identity(BaseModel):
    full_name: str
    email: str
    phone: str
    location: str
    linkedin_url: str
    github_url: str
    portfolio_url: str | None = None
    address: Address


class WorkAuthorization(BaseModel):
    status: str
    sponsorship_required: bool
    authorized_to_work_us: bool
    needs_visa_sponsorship: bool


class Education(BaseModel):
    degree: str
    field: str
    school: str
    location: str
    graduation_date: str  # YYYY-MM
    gpa: float | None = None

    @field_validator("graduation_date")
    @classmethod
    def validate_grad_date(cls, value: str) -> str:
        parts = value.split("-")
        if len(parts) != 2 or len(parts[0]) != 4 or len(parts[1]) != 2:
            raise ValueError("graduation_date must be YYYY-MM")
        return value


class Experience(BaseModel):
    title: str
    company: str
    location: str
    start_date: str
    end_date: str
    bullets: list[str] = Field(min_length=1)


class Preferences(BaseModel):
    titles: list[str] = Field(min_length=1)
    locations: list[str] = Field(min_length=1)
    remote_ok: bool = True
    relocation_ok: bool = False
    dream_companies: list[str] = Field(default_factory=list)


class Exclusions(BaseModel):
    companies: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    clearance_required: bool = True
    third_party_staffing: bool = True


class Profile(BaseModel):
    """Single Source of Truth for candidate facts. No LLM invention beyond this."""

    identity: Identity
    work_authorization: WorkAuthorization
    education: list[Education] = Field(min_length=1)
    experience: list[Experience] = Field(min_length=1)
    skills: list[str] = Field(min_length=1)
    preferences: Preferences
    exclusions: Exclusions = Field(default_factory=Exclusions)
    summary: str = ""

    def total_years_experience(self, *, today: date | None = None) -> float:
        """Approximate career length in years, spanning earliest start to latest end."""
        now = today or date.today()
        starts: list[date] = []
        ends: list[date] = []
        for entry in self.experience:
            start = _parse_month(entry.start_date)
            if start is None:
                continue
            starts.append(start)
            ends.append(_parse_month(entry.end_date) or now)
        if not starts:
            return 0.0
        span_days = (max(ends) - min(starts)).days
        return max(0.0, round(span_days / 365.25, 1))

    def static_context_block(self) -> str:
        """Compact, cacheable candidate summary for LLM system prompts (Step 3)."""
        edu = "; ".join(
            f"{e.degree} {e.field}, {e.school} ({e.graduation_date})"
            + (f", GPA {e.gpa}" if e.gpa is not None else "")
            for e in self.education
        )
        exp = "\n".join(
            f"- {e.title} @ {e.company} ({e.start_date}–{e.end_date}): "
            + " | ".join(e.bullets)
            for e in self.experience
        )
        summary = f"Summary: {self.summary.strip()}\n" if self.summary.strip() else ""
        return (
            f"Name: {self.identity.full_name}\n"
            f"Location: {self.identity.location}\n"
            f"Email: {self.identity.email}\n"
            f"Phone: {self.identity.phone}\n"
            f"LinkedIn: {self.identity.linkedin_url}\n"
            f"GitHub: {self.identity.github_url}\n"
            f"{summary}"
            f"Work auth: {self.work_authorization.status}; "
            f"sponsorship_required={self.work_authorization.sponsorship_required}; "
            f"authorized_to_work_us={self.work_authorization.authorized_to_work_us}; "
            f"needs_visa_sponsorship={self.work_authorization.needs_visa_sponsorship}\n"
            f"Education: {edu}\n"
            f"Experience:\n{exp}\n"
            f"Skills: {', '.join(self.skills)}\n"
            f"Target titles: {', '.join(self.preferences.titles)}\n"
            f"Target locations: {', '.join(self.preferences.locations)}; "
            f"remote_ok={self.preferences.remote_ok}; "
            f"relocation_ok={self.preferences.relocation_ok}"
        )


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Profile not found: {path}")
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Profile YAML must be a mapping, got {type(data).__name__}")
    return data


@lru_cache
def load_profile(path: str | None = None) -> Profile:
    """Load and validate profile.yaml. Cached after first successful load."""
    profile_path = Path(path) if path else PROFILE_PATH
    raw = _load_yaml(profile_path)
    return Profile.model_validate(raw)


def reload_profile(path: str | None = None) -> Profile:
    """Clear cache and reload (useful after editing profile.yaml)."""
    load_profile.cache_clear()
    return load_profile(path)

"""Classify job apply URLs (Workday vs LinkedIn listing vs other company ATS)."""

from __future__ import annotations

from enum import StrEnum
from urllib.parse import urlparse

from config.targets import WorkdayParts, parse_workday_url


class ApplyKind(StrEnum):
    """Where the candidate actually applies."""

    workday = "workday"
    linkedin = "linkedin"  # Easy Apply / listing page — manual
    indeed = "indeed"
    company = "company"  # External careers site (Greenhouse, Amazon, etc.)
    unknown = "unknown"


def _host(url: str) -> str:
    try:
        return (urlparse(url.strip()).netloc or "").lower()
    except Exception:
        return ""


def is_workday_url(url: str) -> bool:
    """True when the URL is a Workday careers / job deep link."""
    if not url or not url.strip():
        return False
    try:
        parse_workday_url(url)
        return True
    except ValueError:
        return False


def workday_parts(url: str) -> WorkdayParts | None:
    try:
        return parse_workday_url(url)
    except ValueError:
        return None


def classify_apply_url(url: str) -> ApplyKind:
    """Classify where application happens for a stored job URL."""
    host = _host(url)
    if not host:
        return ApplyKind.unknown
    if "myworkdayjobs.com" in host:
        return ApplyKind.workday
    if "linkedin.com" in host:
        return ApplyKind.linkedin
    if "indeed.com" in host:
        return ApplyKind.indeed
    return ApplyKind.company


def is_automateable_apply_url(url: str) -> bool:
    """URLs we can hand to WorkdayApplicator today."""
    return is_workday_url(url)

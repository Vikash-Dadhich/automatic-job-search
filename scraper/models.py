"""Normalized intermediate posting model and Job mapping."""

from __future__ import annotations

import hashlib
from datetime import datetime

from pydantic import BaseModel, Field

from core.db import Job, Source, Status
from scraper.textclean import content_hash, normalize_description


class RawPosting(BaseModel):
    """Source-agnostic posting produced by scrapers before DB persistence."""

    source: Source
    external_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    company: str = Field(min_length=1)
    location: str | None = None
    url: str = Field(min_length=1)
    description_html: str | None = None
    description_clean: str | None = None
    posted_at: datetime | None = None
    tenant: str | None = None
    discovery_family: str | None = None
    discovery_bucket: str | None = None
    discovery_query: str | None = None
    jd_status: str | None = None
    jd_char_count: int | None = None
    jd_truncated: bool | None = None
    jd_extraction_path: str | None = None

    def ensure_clean_description(self) -> str:
        """Normalize the best available JD and record extraction quality."""
        if self.description_clean and self.description_clean.strip():
            normalized = normalize_description(self.description_clean, from_html=False)
        elif self.description_html:
            normalized = normalize_description(self.description_html, from_html=True)
        else:
            normalized = normalize_description("", from_html=False)
        self.description_clean = normalized.text
        self.jd_status = normalized.status.value
        self.jd_char_count = normalized.char_count
        self.jd_truncated = normalized.truncated
        self.jd_extraction_path = normalized.extraction_path
        return self.description_clean


def hash_fallback(title: str, company: str) -> str:
    raw = f"{title}|{company}".encode()
    return hashlib.sha256(raw).hexdigest()


def to_job(
    posting: RawPosting,
    *,
    status: Status = Status.discovered,
    justification: list[str] | None = None,
) -> Job:
    """Map a RawPosting to a Job row, computing content_hash."""
    from core.apply_url import workday_parts

    clean = posting.ensure_clean_description()
    digest = content_hash(clean) if clean else hash_fallback(posting.title, posting.company)
    tenant = posting.tenant
    if not tenant:
        parts = workday_parts(posting.url)
        if parts is not None:
            tenant = parts.tenant
    return Job(
        source=posting.source,
        external_id=posting.external_id,
        tenant=tenant,
        content_hash=digest,
        title=posting.title,
        company=posting.company,
        location=posting.location,
        url=posting.url,
        description_clean=clean or None,
        posted_at=posting.posted_at,
        status=status,
        justification=justification,
        discovery_family=posting.discovery_family,
        discovery_bucket=posting.discovery_bucket,
        discovery_query=posting.discovery_query,
        jd_status=posting.jd_status,
        jd_char_count=posting.jd_char_count,
        jd_truncated=posting.jd_truncated,
        jd_extraction_path=posting.jd_extraction_path,
    )

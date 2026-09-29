"""Factual company records. Not fit, not eligibility, and not a ranking score."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Protocol
from urllib.parse import urlparse

import httpx
import structlog
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.db import CompanyIntelligence, Job
from scraper.textclean import html_to_text

log = structlog.get_logger(__name__)

INTELLIGENCE_VERSION = "phase8-v1"
_SOURCE_TYPES = frozenset({"official_website", "careers", "sec", "regulatory", "other"})
_LEGAL_SUFFIXES = frozenset(
    {
        "inc",
        "incorporated",
        "llc",
        "ltd",
        "limited",
        "corp",
        "corporation",
        "co",
        "plc",
        "lp",
        "llp",
        "gmbh",
        "sa",
        "ag",
        "nv",
        "bv",
    }
)
_INDUSTRIES = frozenset(
    {
        "software",
        "technology",
        "consulting",
        "financial",
        "healthcare",
        "retail",
        "manufacturing",
        "insurance",
    }
)
_FACT_FIELDS = (
    "industry",
    "public_private",
    "headquarters",
    "employee_range",
    "founded_year",
    "parent_company",
    "company_type",
    "business_description",
)
_SUFFIX_ALT = "|".join(sorted(_LEGAL_SUFFIXES, key=len, reverse=True))
_TRAILING_SUFFIX_RE = re.compile(
    rf"[\s,]+(?:{_SUFFIX_ALT})\.?[\s.,]*$",
    re.IGNORECASE,
)
_PUBLIC_RE = re.compile(r"\b(?:publicly traded|public company)\b", re.IGNORECASE)
_PRIVATE_RE = re.compile(r"\b(?:privately held|private company)\b", re.IGNORECASE)
_HQ_RE = re.compile(r"\bheadquartered in ([^.]+)", re.IGNORECASE)
_INDUSTRY_RE = re.compile(
    r"\b(" + "|".join(sorted(_INDUSTRIES)) + r")\s+company\b",
    re.IGNORECASE,
)
_EMPLOYEES_RE = re.compile(
    r"\b(?:approximately|about|around)?\s*\d[\d,]*\s+employees\b",
    re.IGNORECASE,
)
_FOUNDED_RE = re.compile(r"\bfounded in (\d{4})\b", re.IGNORECASE)
_PARENT_RE = re.compile(r"\bsubsidiary of ([^.]+)", re.IGNORECASE)
_SELF_RE = re.compile(r"\bdescribes itself as ([^.]+)", re.IGNORECASE)


def normalize_company_name(name: str | None) -> str:
    """Lookup key: trimmed, lowercased, trailing legal suffix removed.

    Interior punctuation stays. ``AT&T`` stays ``at&t``. ``Mercury`` and
    ``Mercury Systems`` stay different.
    """
    return _without_trailing_suffix(name).lower()


def canonical_company_name(name: str | None) -> str:
    """Display form of the lookup key, keeping the source casing."""
    return _without_trailing_suffix(name)


def _without_trailing_suffix(name: str | None) -> str:
    text = re.sub(r"\s+", " ", (name or "").strip())
    while True:
        updated = _TRAILING_SUFFIX_RE.sub("", text).strip()
        updated = re.sub(r"\s+", " ", updated).strip()
        if updated == text:
            return text
        text = updated


def extract_company_facts(text: str) -> dict[str, Any]:
    """Pull only phrases the source actually states. Missing phrases stay null."""
    facts: dict[str, Any] = {field: None for field in _FACT_FIELDS}
    if _PUBLIC_RE.search(text):
        facts["public_private"] = "public"
    elif _PRIVATE_RE.search(text):
        facts["public_private"] = "private"
    headquarters = _HQ_RE.search(text)
    if headquarters:
        facts["headquarters"] = headquarters.group(1).strip(" ,")
    industry = _INDUSTRY_RE.search(text)
    if industry:
        facts["industry"] = industry.group(1).lower()
    employees = _EMPLOYEES_RE.search(text)
    if employees:
        facts["employee_range"] = re.sub(r"\s+", " ", employees.group(0)).strip()
    founded = _FOUNDED_RE.search(text)
    if founded:
        facts["founded_year"] = int(founded.group(1))
    parent = _PARENT_RE.search(text)
    if parent:
        facts["parent_company"] = parent.group(1).strip(" ,")
        facts["company_type"] = "subsidiary"
    described = _SELF_RE.search(text)
    if described:
        facts["business_description"] = described.group(1).strip()
    return facts


def _reliable_source_url(url: str | None) -> str | None:
    if not url or not url.strip():
        return None
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    return url.strip()


def _source_type(value: str | None) -> str:
    if value in _SOURCE_TYPES:
        return value
    return "other"


@dataclass
class CompanySourceDocument:
    source_type: str
    url: str
    text: str
    retrieved_at: datetime


@dataclass
class CompanyLookupResult:
    """A fetched page, or an error. ``claimed`` is never stored on its own."""

    document: CompanySourceDocument | None = None
    error: str | None = None
    claimed: dict[str, Any] | None = None


class CompanyIntelProvider(Protocol):
    async def lookup(
        self,
        company_name: str,
        source_url: str,
        source_type: str = "official_website",
    ) -> CompanyLookupResult:
        """Fetch one explicit source URL. Do not search or invent a domain."""
        ...


class HttpCompanyIntelProvider:
    """One GET of a caller-supplied URL. No crawl and no domain guessing."""

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client

    async def lookup(
        self,
        company_name: str,
        source_url: str,
        source_type: str = "official_website",
    ) -> CompanyLookupResult:
        del company_name
        url = _reliable_source_url(source_url)
        if url is None:
            return CompanyLookupResult(error="malformed")
        try:
            if self._client is not None:
                response = await self._client.get(url)
            else:
                timeout = httpx.Timeout(10.0, connect=5.0)
                async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
                    response = await client.get(url)
            response.raise_for_status()
        except httpx.TimeoutException:
            return CompanyLookupResult(error="timeout")
        except httpx.HTTPError:
            return CompanyLookupResult(error="http_error")
        body = response.text or ""
        if not body.strip():
            return CompanyLookupResult(error="malformed")
        text = html_to_text(body) if "<" in body else body.strip()
        if not text.strip():
            return CompanyLookupResult(error="malformed")
        return CompanyLookupResult(
            document=CompanySourceDocument(
                source_type=_source_type(source_type),
                url=url,
                text=text,
                retrieved_at=datetime.now(UTC),
            )
        )


def _status_for(facts: dict[str, Any]) -> str:
    tracked = [
        facts[field]
        for field in (
            "industry",
            "public_private",
            "headquarters",
            "employee_range",
            "founded_year",
            "parent_company",
        )
    ]
    present = [value for value in tracked if value is not None]
    if not present:
        return "unresolved"
    if len(present) == len(tracked):
        return "complete"
    return "partial"


def _confidence_for(status: str, source_type: str) -> str:
    if status == "complete" and source_type in {"official_website", "sec", "regulatory"}:
        return "high"
    if status == "partial" and source_type in {"official_website", "careers", "sec", "regulatory"}:
        return "medium"
    return "low"


def _apply_facts(row: CompanyIntelligence, facts: dict[str, Any]) -> None:
    row.industry = facts["industry"]
    row.public_private = facts["public_private"]
    row.headquarters = facts["headquarters"]
    row.employee_range = facts["employee_range"]
    row.founded_year = facts["founded_year"]
    row.parent_company = facts["parent_company"]
    row.company_type = facts["company_type"]
    row.business_description = facts["business_description"]


def _clear_facts(row: CompanyIntelligence) -> None:
    _apply_facts(row, {field: None for field in _FACT_FIELDS})


async def _by_key(session: AsyncSession, lookup_key: str) -> CompanyIntelligence | None:
    statement = select(CompanyIntelligence).where(CompanyIntelligence.lookup_key == lookup_key)
    result = await session.exec(statement)
    return result.first()


async def get_company_intelligence(
    session: AsyncSession,
    company_name: str,
) -> CompanyIntelligence | None:
    """Return the stored record for this company, if one exists."""
    key = normalize_company_name(company_name)
    if not key:
        return None
    return await _by_key(session, key)


async def resolve_company(
    session: AsyncSession,
    company_name: str,
    *,
    source_url: str | None = None,
    source_type: str = "official_website",
    provider: CompanyIntelProvider | None = None,
    refresh: bool = False,
) -> CompanyIntelligence:
    """Find or create factual intelligence. Provider errors stay on the company row."""
    key = normalize_company_name(company_name) or "unknown"
    existing = await _by_key(session, key)
    if existing is not None and not refresh:
        log.info(
            "company_intelligence_reused",
            lookup_key=key,
            company_intelligence_id=existing.id,
            status=existing.status,
        )
        return existing

    url = _reliable_source_url(source_url)
    kind = _source_type(source_type)
    if url is None or provider is None:
        row = existing or _new_row(company_name, key)
        if existing is None:
            _clear_facts(row)
            row.website = None
            row.sources = []
            row.retrieved_at = None
            row.status = "unresolved"
            row.confidence = "low"
            row.intelligence_version = INTELLIGENCE_VERSION
            session.add(row)
            await session.flush()
        if row.status == "unresolved":
            log.info(
                "company_intelligence_unresolved",
                lookup_key=key,
                company_intelligence_id=row.id,
            )
        return row

    try:
        looked_up = await provider.lookup(company_name, url, kind)
    except Exception as exc:
        log.warning(
            "company_intelligence_provider_failure",
            lookup_key=key,
            error=type(exc).__name__,
        )
        return await _store_failure(session, existing, company_name, key)

    if looked_up.error or looked_up.document is None or not looked_up.document.text.strip():
        log.warning(
            "company_intelligence_provider_failure",
            lookup_key=key,
            error=looked_up.error or "malformed",
        )
        return await _store_failure(session, existing, company_name, key)

    document = looked_up.document
    facts = extract_company_facts(document.text)
    if looked_up.claimed:
        log.info(
            "company_intelligence_ignored_ungrounded_claims",
            lookup_key=key,
            fields=sorted(looked_up.claimed),
        )
    row = existing or _new_row(company_name, key)
    _apply_facts(row, facts)
    stored_type = _source_type(document.source_type or kind)
    row.sources = [
        {
            "source_type": stored_type,
            "url": document.url,
            "retrieved_at": document.retrieved_at.astimezone(UTC).isoformat(),
        }
    ]
    row.website = document.url if stored_type == "official_website" else row.website
    row.retrieved_at = document.retrieved_at
    row.status = _status_for(facts)
    row.confidence = _confidence_for(row.status, stored_type)
    row.intelligence_version = INTELLIGENCE_VERSION
    row.updated_at = datetime.now(UTC)
    if existing is None:
        session.add(row)
    await session.flush()
    event = {
        "partial": "company_intelligence_partial",
        "unresolved": "company_intelligence_unresolved",
    }.get(row.status, "company_intelligence_resolved")
    log.info(
        event,
        lookup_key=key,
        company_intelligence_id=row.id,
        status=row.status,
        confidence=row.confidence,
    )
    return row


async def refresh_company_intelligence(
    session: AsyncSession,
    company_name: str,
    *,
    source_url: str | None = None,
    source_type: str = "official_website",
    provider: CompanyIntelProvider | None = None,
) -> CompanyIntelligence:
    """Look up the company again. Does not recompute fit or role-family weight."""
    return await resolve_company(
        session,
        company_name,
        source_url=source_url,
        source_type=source_type,
        provider=provider,
        refresh=True,
    )


async def attach_company_intelligence(
    session: AsyncSession,
    job: Job,
    *,
    source_url: str | None = None,
    source_type: str = "official_website",
    provider: CompanyIntelProvider | None = None,
    refresh: bool = False,
) -> CompanyIntelligence:
    """Point the job at a company record without changing score, weight, or status."""
    record = await resolve_company(
        session,
        job.company,
        source_url=source_url,
        source_type=source_type,
        provider=provider,
        refresh=refresh,
    )
    job.company_intelligence_id = record.id
    return record


def _new_row(company_name: str, lookup_key: str) -> CompanyIntelligence:
    display = canonical_company_name(company_name) or company_name.strip() or lookup_key
    return CompanyIntelligence(
        lookup_key=lookup_key,
        company_name=company_name.strip() or display,
        canonical_name=display,
        sources=[],
        status="unresolved",
        confidence="low",
        intelligence_version=INTELLIGENCE_VERSION,
    )


async def _store_failure(
    session: AsyncSession,
    existing: CompanyIntelligence | None,
    company_name: str,
    lookup_key: str,
) -> CompanyIntelligence:
    """Record a failed first lookup. A later failure keeps facts already stored."""
    if existing is not None and existing.status in {"partial", "complete"}:
        return existing
    row = existing or _new_row(company_name, lookup_key)
    if existing is None:
        _clear_facts(row)
        row.sources = []
        row.website = None
    row.status = "failed"
    row.confidence = "low"
    row.intelligence_version = INTELLIGENCE_VERSION
    row.updated_at = datetime.now(UTC)
    if existing is None:
        session.add(row)
    await session.flush()
    return row

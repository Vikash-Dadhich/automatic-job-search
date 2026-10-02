"""Factual company records. Not fit, not eligibility, and not a ranking score."""

from __future__ import annotations

import hashlib
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

INTELLIGENCE_VERSION = "phase8-v2"
_SOURCE_RANK = {
    "official_website": 1,
    "careers": 2,
    "regulatory": 3,
    "sec": 4,
    "other": 5,
}
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
_DOMAIN_PATTERNS: tuple[tuple[str, str], ...] = (
    ("financial_services", r"\bfinancial services\b"),
    ("banking", r"\bbanking\b"),
    ("payments", r"\bpayments\b"),
    ("fintech", r"\bfintech\b"),
    ("healthcare", r"\bhealthcare\b"),
    ("software", r"\bsoftware\b"),
    ("cloud", r"\bcloud\b"),
    ("artificial_intelligence", r"\bartificial intelligence\b|\bmachine learning\b"),
    ("enterprise_software", r"\benterprise software\b"),
    ("consumer_technology", r"\bconsumer technology\b"),
    ("ecommerce", r"\be-commerce\b|\becommerce\b"),
    ("consulting", r"\bconsulting\b"),
    ("professional_services", r"\bprofessional services\b"),
    ("manufacturing", r"\bmanufacturing\b"),
    ("energy", r"\benergy\b"),
    ("automotive", r"\bautomotive\b"),
    ("telecommunications", r"\btelecommunications\b"),
    ("media", r"\bmedia\b"),
    ("retail", r"\bretail\b"),
    ("logistics", r"\blogistics\b"),
    ("travel", r"\btravel\b"),
    ("insurance", r"\binsurance\b"),
)
_PROGRAM_PATTERNS: tuple[tuple[str, str], ...] = (
    ("mba_internship_program", r"\bmba internship(?: program)?\b"),
    ("summer_internship_program", r"\bsummer internship(?: program)?\b"),
    ("graduate_internship_program", r"\bgraduate internship(?: program)?\b"),
    ("mba_recruiting", r"\bmba recruiting\b"),
    ("business_school_recruiting", r"\bbusiness school recruiting\b"),
    ("leadership_development_program", r"\bleadership development program\b"),
    ("internship_program", r"\binternship program\b"),
    ("full_time_mba_recruiting", r"\bfull-time mba recruiting\b"),
)
_US_PATTERNS: tuple[tuple[str, str], ...] = (
    ("us_headquarters", r"\bu\.?s\.? headquarters\b|\bheadquartered in the united states\b"),
    ("us_office", r"\bu\.?s\.? office\b|\bunited states office\b"),
    ("us_internship_program", r"\bu\.?s\.? internship\b|\bunited states internship\b"),
    ("us_careers", r"\bu\.?s\.? careers\b|\bunited states careers\b"),
    ("us_recruiting", r"\bu\.?s\.? recruiting\b|\bunited states recruiting\b"),
)
_US_OPERATIONS = re.compile(r"\bu\.?s\.? operations\b|\bunited states operations\b", re.IGNORECASE)
_US_OPERATIONS_NEG = re.compile(
    r"\b(?:no|without)\s+(?:u\.?s\.?|united states)\s+operations\b"
    r"|\bdoes not (?:have|operate)\b[^.]{0,40}\b(?:u\.?s\.?|united states)\s+operations\b",
    re.IGNORECASE,
)
_REVENUE_RE = re.compile(
    r"\b(?:annual revenue|revenue of)\s+\$?\d[\d,.]*\s*(?:billion|million)?\b",
    re.IGNORECASE,
)
_EXCHANGE_RE = re.compile(r"\blisted on the (NYSE|NASDAQ)\b", re.IGNORECASE)
_COUNTRIES_RE = re.compile(r"\boperates in (\d+) countries\b", re.IGNORECASE)
_OFFICES_RE = re.compile(r"\b(\d+) offices\b", re.IGNORECASE)
_LINES_RE = re.compile(r"\bbusiness lines include ([^.]+)", re.IGNORECASE)


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


def extract_company_signals(text: str) -> list[dict[str, Any]]:
    """Explicit employer signals. A missing phrase stays absent, not false."""
    signals: list[dict[str, Any]] = []
    for name, pattern in _DOMAIN_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            signals.append(_signal(f"domain:{name}", name, text, match))
    for name, pattern in _PROGRAM_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            signals.append(_signal(name, True, text, match))
    for name, pattern in _US_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            signals.append(_signal(name, True, text, match))
    if _US_OPERATIONS_NEG.search(text):
        match = _US_OPERATIONS_NEG.search(text)
        assert match is not None
        signals.append(_signal("us_operations", False, text, match))
    elif (match := _US_OPERATIONS.search(text)):
        signals.append(_signal("us_operations", True, text, match))
    if (match := _PUBLIC_RE.search(text)):
        signals.append(_signal("public_private", "public", text, match))
    elif (match := _PRIVATE_RE.search(text)):
        signals.append(_signal("public_private", "private", text, match))
    if (match := _REVENUE_RE.search(text)):
        signals.append(_signal("revenue", _compact(match.group(0)), text, match))
    if (match := _EXCHANGE_RE.search(text)):
        signals.append(_signal("exchange", match.group(1).upper(), text, match))
    if (match := _COUNTRIES_RE.search(text)):
        signals.append(_signal("country_count", int(match.group(1)), text, match))
    if (match := _OFFICES_RE.search(text)):
        signals.append(_signal("office_count", int(match.group(1)), text, match))
    if (match := _EMPLOYEES_RE.search(text)):
        signals.append(_signal("employee_count", _compact(match.group(0)), text, match))
    if (match := _LINES_RE.search(text)):
        signals.append(_signal("business_lines", match.group(1).strip(" ,"), text, match))
    return signals


def merge_company_signals(
    existing: list[dict[str, Any]] | None,
    incoming: list[dict[str, Any]],
    *,
    source_url: str,
) -> list[dict[str, Any]]:
    """Replace this source's signals, then keep the higher-priority source on a conflict."""
    kept = [item for item in existing or [] if item.get("source_url") != source_url]
    best: dict[str, dict[str, Any]] = {}
    for item in [*kept, *incoming]:
        key = str(item.get("signal") or "")
        if not key:
            continue
        current = best.get(key)
        if current is None or _prefer_signal(item, current):
            best[key] = item
    return [best[key] for key in sorted(best)]


def empty_company_context() -> dict[str, Any]:
    return {"version": INTELLIGENCE_VERSION, "signals": []}


def _signal(name: str, value: Any, text: str, match: re.Match[str]) -> dict[str, Any]:
    return {
        "signal": name,
        "value": value,
        "snippet": _snippet(text, match),
        "basis": "explicit",
    }


def _snippet(text: str, match: re.Match[str]) -> str:
    start = max(0, match.start() - 30)
    end = min(len(text), match.end() + 30)
    return _compact(text[start:end])[:180]


def _compact(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _prefer_signal(candidate: dict[str, Any], current: dict[str, Any]) -> bool:
    rank_candidate = _SOURCE_RANK.get(str(candidate.get("source_type")), 9)
    rank_current = _SOURCE_RANK.get(str(current.get("source_type")), 9)
    if rank_candidate != rank_current:
        return rank_candidate < rank_current
    return str(candidate.get("observed_at") or "") >= str(current.get("observed_at") or "")


def _stamp_signals(
    signals: list[dict[str, Any]],
    *,
    source_type: str,
    source_url: str,
    observed_at: datetime,
) -> list[dict[str, Any]]:
    stamped: list[dict[str, Any]] = []
    for item in signals:
        stamped.append(
            {
                **item,
                "source_type": source_type,
                "source_url": source_url,
                "observed_at": observed_at.astimezone(UTC).isoformat(),
            }
        )
    return stamped


def _context_from(signals: list[dict[str, Any]]) -> dict[str, Any]:
    payload = {"version": INTELLIGENCE_VERSION, "signals": signals}
    raw = repr(signals).encode()
    payload["content_hash"] = hashlib.sha256(raw).hexdigest()
    return payload


_JOB_BOARD_HOSTS = (
    "linkedin.com",
    "indeed.com",
    "glassdoor.com",
    "google.com",
    "ziprecruiter.com",
    "myworkdayjobs.com",
)


def trustworthy_company_source(url: str | None) -> tuple[str, str] | None:
    """Classify an already-supplied company URL. Does not invent a domain."""
    clean = _reliable_source_url(url)
    if clean is None:
        return None
    parsed = urlparse(clean)
    host = parsed.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    if any(host == board or host.endswith("." + board) for board in _JOB_BOARD_HOSTS):
        return None
    if "sec.gov" in host:
        kind = "sec"
    elif "careers" in host or "/careers" in parsed.path.lower():
        kind = "careers"
    else:
        kind = "official_website"
    return clean, kind


def _accumulate_sources(
    prior: list[dict[str, Any]] | None,
    new: dict[str, Any],
) -> list[dict[str, Any]]:
    """Keep earlier trustworthy sources and add a new URL once."""
    kept: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in prior or []:
        if not isinstance(item, dict):
            continue
        url = item.get("url")
        source_type = item.get("source_type")
        if not isinstance(url, str) or not url or url in seen:
            continue
        if source_type not in _SOURCE_TYPES:
            continue
        seen.add(url)
        kept.append(item)
    url = new.get("url")
    source_type = new.get("source_type")
    if isinstance(url, str) and url and url not in seen and source_type in _SOURCE_TYPES:
        kept.append(new)
    return kept


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


def merge_company_facts(existing: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
    """Keep a known fact when the newer page does not state a replacement."""
    merged: dict[str, Any] = {}
    for name in _FACT_FIELDS:
        incoming = new.get(name)
        if isinstance(incoming, str) and not incoming.strip():
            incoming = None
        merged[name] = existing.get(name) if incoming is None else incoming
    return merged


def _apply_context(row: CompanyIntelligence, document: CompanySourceDocument) -> None:
    """Refresh signals from this page. A bad extract leaves the previous context."""
    try:
        extracted = extract_company_signals(document.text)
    except Exception as exc:
        log.warning("company_context_extract_failed", error=type(exc).__name__)
        return
    prior: list[dict[str, Any]] = []
    if isinstance(row.context, dict) and isinstance(row.context.get("signals"), list):
        prior = [item for item in row.context["signals"] if isinstance(item, dict)]
    stamped = _stamp_signals(
        extracted,
        source_type=_source_type(document.source_type),
        source_url=document.url,
        observed_at=document.retrieved_at,
    )
    row.context = _context_from(
        merge_company_signals(prior, stamped, source_url=document.url)
    )


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
            row.context = empty_company_context()
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
    prior = {name: getattr(row, name) for name in _FACT_FIELDS}
    facts = merge_company_facts(prior, facts)
    _apply_facts(row, facts)
    _apply_context(row, document)
    stored_type = _source_type(document.source_type or kind)
    row.sources = _accumulate_sources(
        list(row.sources or []),
        {
            "source_type": stored_type,
            "url": document.url,
            "retrieved_at": document.retrieved_at.astimezone(UTC).isoformat(),
        },
    )
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
        row.context = empty_company_context()
    row.status = "failed"
    row.confidence = "low"
    row.intelligence_version = INTELLIGENCE_VERSION
    row.updated_at = datetime.now(UTC)
    if existing is None:
        session.add(row)
    await session.flush()
    return row

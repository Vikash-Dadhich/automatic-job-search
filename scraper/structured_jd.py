"""Structured reading of a normalized job description.

This layer records explicit JD evidence. It does not score, rank, classify a
role family, or decide eligibility.
"""

from __future__ import annotations

import re
from typing import Any, Literal

import structlog
from pydantic import BaseModel, Field
from sqlmodel import col, select

from core.db import Job, StructuredJobDescription, _utcnow
from scraper.filters import (
    citizenship_restriction,
    clearance_requirement,
    visa_sponsorship_signal,
)
from scraper.textclean import SUSPICIOUS_BELOW, content_hash

log = structlog.get_logger(__name__)

STRUCTURED_JD_VERSION = "phase19-v1"
_SNIPPET = 160

State = Literal["explicit", "not_mentioned", "unknown"]
DegreeState = Literal["required", "preferred", "not_mentioned", "unknown"]
SponsorshipState = Literal["available", "unavailable", "not_mentioned", "unknown"]
ClearanceState = Literal["required", "preferred", "not_mentioned", "unknown"]
YearsBasis = Literal["required", "preferred", "not_mentioned", "unknown"]
Availability = Literal["available", "partial", "unavailable"]

_FUNCTIONAL: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("product_management", (r"\bproduct management\b", r"\bproduct manager\b")),
    ("consulting", (r"\bmanagement consulting\b", r"\bconsulting engagement\b")),
    ("technology_strategy", (r"\btechnology strategy\b",)),
    ("strategy", (r"\bcorporate strategy\b", r"\bbusiness strategy\b")),
    ("business_transformation", (r"\bbusiness transformation\b",)),
    ("program_operations", (r"\bprogram operations\b", r"\bprogram management\b")),
    ("product_marketing", (r"\bproduct marketing\b",)),
    ("marketing", (r"\bmarketing\b",)),
    ("software_technology", (r"\bsoftware development\b", r"\bsoftware engineering\b")),
    ("data_analytics", (r"\bdata analytics\b", r"\bdata analysis\b")),
    ("ai_ml", (r"\bmachine learning\b", r"\bartificial intelligence\b", r"\bgenerative ai\b")),
    ("leadership", (r"\bpeople management\b", r"\bdirect reports\b")),
    ("go_to_market", (r"\bgo-to-market\b", r"\bgo to market\b")),
    ("operations", (r"\bbusiness operations\b",)),
    ("finance_analysis", (r"\bfinancial analysis\b", r"\bfinancial modeling\b")),
    ("domain_expertise", (r"\bdomain expertise\b", r"\bindustry expertise\b")),
)
_DOMAIN: tuple[tuple[str, str], ...] = (
    ("financial_services", r"\bfinancial services\b"),
    ("banking", r"\bbanking\b"),
    ("healthcare", r"\bhealthcare\b"),
    ("retail", r"\bretail\b"),
    ("cloud", r"\bcloud\b"),
    ("cybersecurity", r"\bcybersecurity\b"),
    ("saas", r"\bsaas\b"),
    ("ai", r"\bartificial intelligence\b|\bgenerative ai\b"),
    ("manufacturing", r"\bmanufacturing\b"),
    ("consumer_products", r"\bconsumer products\b"),
    ("automotive", r"\bautomotive\b"),
    ("payments", r"\bpayments\b"),
)
_HEADING = re.compile(
    r"(?im)^(?:#{1,6}\s*)?("
    r"responsibilities|what you(?:'|’)ll do|what you will do|"
    r"minimum qualifications|required qualifications|basic qualifications|"
    r"preferred qualifications|nice to have|requirements|qualifications"
    r")\s*:?\s*$"
)
_BULLET = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+(.+?)\s*$")
_PREFERRED_LINE = re.compile(
    r"\bpreferred\b|\bnice to have\b|\ba plus\b|\bis a plus\b",
    re.IGNORECASE,
)
_YEAR_RANGE = re.compile(
    r"\b(\d{1,2})\s*(?:-|–|to)\s*(\d{1,2})\s*(?:years?|yrs?)\b",
    re.IGNORECASE,
)
_YEAR_PLUS = re.compile(r"\b(\d{1,2})\s*\+\s*(?:years?|yrs?)\b", re.IGNORECASE)
_YEAR_PLAIN = re.compile(r"\b(\d{1,2})\s*(?:years?|yrs?)\b", re.IGNORECASE)
_PLACE = re.compile(r"\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)?),\s*([A-Z]{2})\b")
_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", "HI", "IA", "ID",
    "IL", "IN", "KS", "KY", "LA", "MA", "MD", "ME", "MI", "MN", "MO", "MS", "MT", "NC",
    "ND", "NE", "NH", "NJ", "NM", "NV", "NY", "OH", "OK", "OR", "PA", "RI", "SC", "SD",
    "TN", "TX", "UT", "VA", "VT", "WA", "WI", "WV", "WY",
}
_MONTH = (
    r"January|February|March|April|May|June|July|August|September|October|November|December"
)


class TextItem(BaseModel):
    text: str
    category: str
    basis: Literal["explicit"] = "explicit"
    snippet: str


class Responsibilities(BaseModel):
    state: State
    items: list[TextItem] = Field(default_factory=list)


class Qualifications(BaseModel):
    state: State
    required: list[TextItem] = Field(default_factory=list)
    preferred: list[TextItem] = Field(default_factory=list)


class ExperienceRequirement(BaseModel):
    state: State
    minimum_years: int | None = None
    maximum_years: int | None = None
    preferred_years: int | None = None
    years_basis: YearsBasis = "unknown"
    snippet: str | None = None


class EducationRequirement(BaseModel):
    state: State
    bachelors: DegreeState = "unknown"
    masters: DegreeState = "unknown"
    mba: DegreeState = "unknown"
    other: list[TextItem] = Field(default_factory=list)
    snippet: str | None = None


class FunctionalSignals(BaseModel):
    state: State
    areas: list[TextItem] = Field(default_factory=list)


class ProgramSignals(BaseModel):
    state: State
    internship: bool | None = None
    mba_internship: bool | None = None
    summer_internship: bool | None = None
    rotational_program: bool | None = None
    leadership_development_program: bool | None = None
    full_time: bool | None = None
    temporary_or_contract: bool | None = None
    duration: str | None = None
    timing: str | None = None
    snippets: list[str] = Field(default_factory=list)


class WorkModelSignals(BaseModel):
    state: State
    places: list[str] = Field(default_factory=list)
    remote: bool | None = None
    hybrid: bool | None = None
    onsite: bool | None = None
    travel: str | None = None
    relocation: str | None = None
    snippets: list[str] = Field(default_factory=list)


class AuthorizationEvidence(BaseModel):
    state: State
    sponsorship: SponsorshipState = "unknown"
    work_authorization_required: State = "unknown"
    citizenship_required: State = "unknown"
    permanent_residency_required: State = "unknown"
    security_clearance: ClearanceState = "unknown"
    other_restrictions: list[str] = Field(default_factory=list)
    snippets: list[str] = Field(default_factory=list)


class DomainSignals(BaseModel):
    state: State
    domains: list[TextItem] = Field(default_factory=list)


class StructuredJdDocument(BaseModel):
    version: str
    availability: Availability
    responsibilities: Responsibilities
    qualifications: Qualifications
    experience: ExperienceRequirement
    education: EducationRequirement
    functional: FunctionalSignals
    program: ProgramSignals
    work_model: WorkModelSignals
    authorization: AuthorizationEvidence
    domain: DomainSignals


def structured_jd_is_current(
    row: StructuredJobDescription | None,
    digest: str | None,
) -> bool:
    """True when this row was built for this normalized text and this version."""
    return bool(
        row is not None
        and digest
        and row.content_hash == digest
        and row.version == STRUCTURED_JD_VERSION
        and row.document
    )


def extract_structured_jd(
    text: str,
    *,
    jd_status: str | None = None,
) -> StructuredJdDocument:
    """Read explicit structure from normalized JD text. Absence stays unknown."""
    availability = _availability(text or "", jd_status)
    if availability == "unavailable":
        return _empty(availability)
    try:
        return _read(text, availability)
    except Exception as exc:
        log.warning("structured_jd_extract_failed", error=str(exc)[:200])
        return _empty("unavailable")


async def get_structured_jd(session: Any, job_id: int) -> StructuredJobDescription | None:
    statement = select(StructuredJobDescription).where(
        col(StructuredJobDescription.job_id) == job_id
    )
    result = await session.exec(statement)
    return result.first()


async def attach_structured_jd(session: Any, job: Job) -> StructuredJobDescription | None:
    """Persist a reading for this job. A failure here must not raise."""
    if job.id is None:
        return None
    try:
        digest = job.content_hash or content_hash(job.description_clean or "")
        existing = await get_structured_jd(session, job.id)
        if structured_jd_is_current(existing, digest):
            return existing
        document = extract_structured_jd(job.description_clean or "", jd_status=job.jd_status)
        now = _utcnow()
        if existing is None:
            existing = StructuredJobDescription(
                job_id=job.id,
                content_hash=digest,
                version=STRUCTURED_JD_VERSION,
                availability=document.availability,
                document=document.model_dump(),
                created_at=now,
                updated_at=now,
            )
        else:
            existing.content_hash = digest
            existing.version = STRUCTURED_JD_VERSION
            existing.availability = document.availability
            existing.document = document.model_dump()
            existing.updated_at = now
        session.add(existing)
        await session.flush()
        return existing
    except Exception as exc:
        log.warning("structured_jd_attach_failed", job_id=job.id, error=str(exc)[:200])
        return None


def _availability(text: str, jd_status: str | None) -> Availability:
    if jd_status in {"missing", "suspicious"} or not text.strip():
        return "unavailable"
    if len(text.strip()) < SUSPICIOUS_BELOW:
        return "unavailable"
    if jd_status == "truncated":
        return "partial"
    return "available"


def _empty(availability: Availability) -> StructuredJdDocument:
    unknown = "unknown"
    return StructuredJdDocument(
        version=STRUCTURED_JD_VERSION,
        availability=availability,
        responsibilities=Responsibilities(state=unknown),
        qualifications=Qualifications(state=unknown),
        experience=ExperienceRequirement(state=unknown, years_basis=unknown),
        education=EducationRequirement(state=unknown),
        functional=FunctionalSignals(state=unknown),
        program=ProgramSignals(state=unknown),
        work_model=WorkModelSignals(state=unknown),
        authorization=AuthorizationEvidence(state=unknown),
        domain=DomainSignals(state=unknown),
    )


def _clip(text: str) -> str:
    compact = " ".join(text.split())
    return compact[:_SNIPPET]


def _clauses(text: str) -> list[str]:
    parts = re.split(r"[\n;]+|(?<=[.!?])\s+", text)
    return [part.strip() for part in parts if part and part.strip()]


def _section_kind(heading: str) -> str:
    name = heading.lower().replace("’", "'")
    if name.startswith("responsibilit") or name.startswith("what you"):
        return "responsibilities"
    if "prefer" in name or name == "nice to have":
        return "preferred"
    return "required"


def _sections(text: str) -> list[tuple[str, list[str]]]:
    matches = list(_HEADING.finditer(text))
    found: list[tuple[str, list[str]]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        bullets = []
        for line in text[match.end() : end].splitlines():
            bullet = _BULLET.match(line)
            if bullet:
                bullets.append(bullet.group(1).strip())
        if bullets:
            found.append((_section_kind(match.group(1)), bullets))
    return found


def _item(text: str, category: str) -> TextItem:
    return TextItem(text=_clip(text), category=category, snippet=_clip(text))


def _responsibility_category(line: str) -> str:
    if re.search(r"\bpeople management\b|\bdirect reports\b|\blead a team\b", line, re.I):
        return "leadership"
    if re.search(r"\bstakeholder", line, re.I):
        return "stakeholder"
    if re.search(r"\bown(?:ership)?\b|\bend-to-end\b", line, re.I):
        return "ownership"
    if re.search(r"\bcross-functional\b|\bcollaborate\b|\bcollaboration\b", line, re.I):
        return "collaboration"
    return "duty"


def _qualification_category(line: str) -> str:
    if re.search(r"\bcertif", line, re.I):
        return "certification"
    if re.search(r"\b(?:bachelor|master|mba|ph\.?d|degree)\b", line, re.I):
        return "degree"
    if re.search(r"\byears?\b|\bexperience\b", line, re.I):
        return "experience"
    if any(re.search(pattern, line, re.I) for _name, pattern in _DOMAIN):
        return "domain"
    if re.search(r"\b(?:sql|python|excel|tableau|powerpoint)\b", line, re.I):
        return "technical"
    functional = any(
        re.search(pattern, line, re.I)
        for _name, patterns in _FUNCTIONAL
        for pattern in patterns
    )
    if functional:
        return "functional"
    return "other"


def _qualifications(sections: list[tuple[str, list[str]]], usable: bool) -> Qualifications:
    if not usable:
        return Qualifications(state="unknown")
    required: list[TextItem] = []
    preferred: list[TextItem] = []
    for kind, bullets in sections:
        if kind == "responsibilities":
            continue
        for line in bullets:
            item = _item(line, _qualification_category(line))
            if kind == "preferred" or _PREFERRED_LINE.search(line):
                preferred.append(item)
            else:
                required.append(item)
    state: State = "explicit" if required or preferred else "not_mentioned"
    return Qualifications(state=state, required=required, preferred=preferred)


def _responsibilities(sections: list[tuple[str, list[str]]], usable: bool) -> Responsibilities:
    if not usable:
        return Responsibilities(state="unknown")
    items = [
        _item(line, _responsibility_category(line))
        for kind, bullets in sections
        if kind == "responsibilities"
        for line in bullets
    ]
    return Responsibilities(state="explicit" if items else "not_mentioned", items=items)


def _preferred_clause(clause: str) -> bool:
    return _PREFERRED_LINE.search(clause) is not None


def _experience(text: str, usable: bool) -> ExperienceRequirement:
    if not usable:
        return ExperienceRequirement(state="unknown", years_basis="unknown")
    minimum: int | None = None
    maximum: int | None = None
    preferred: int | None = None
    snippet: str | None = None
    consumed: list[tuple[int, int]] = []
    for match in _YEAR_RANGE.finditer(text):
        clause = _clause_at(text, match.start())
        snippet = snippet or _clip(clause)
        consumed.append(match.span())
        if _preferred_clause(clause):
            preferred = preferred if preferred is not None else int(match.group(1))
            continue
        if minimum is None:
            minimum = int(match.group(1))
            maximum = int(match.group(2))
    for pattern in (_YEAR_PLUS, _YEAR_PLAIN):
        for match in pattern.finditer(text):
            if any(start <= match.start() < end for start, end in consumed):
                continue
            clause = _clause_at(text, match.start())
            snippet = snippet or _clip(clause)
            years = int(match.group(1))
            if _preferred_clause(clause):
                preferred = preferred if preferred is not None else years
            elif minimum is None:
                minimum = years
    if minimum is None and preferred is None:
        return ExperienceRequirement(state="not_mentioned", years_basis="not_mentioned")
    basis: YearsBasis = "required" if minimum is not None else "preferred"
    return ExperienceRequirement(
        state="explicit",
        minimum_years=minimum,
        maximum_years=maximum,
        preferred_years=preferred,
        years_basis=basis,
        snippet=snippet,
    )


def _clause_at(text: str, index: int) -> str:
    start = max(
        text.rfind("\n", 0, index),
        text.rfind(".", 0, index),
        text.rfind(";", 0, index),
    )
    ends = (text.find("\n", index), text.find(".", index), text.find(";", index))
    end_candidates = [pos for pos in ends if pos != -1]
    end = min(end_candidates) if end_candidates else len(text)
    return text[start + 1 : end].strip()


def _degree_state(text: str, pattern: str, usable: bool) -> DegreeState:
    if not usable:
        return "unknown"
    found: DegreeState = "not_mentioned"
    for clause in _clauses(text):
        if not re.search(pattern, clause, re.I):
            continue
        if re.search(r"\bmba\s+intern", clause, re.I) and not re.search(
            r"\brequired\b|\bmust\b|\bpreferred\b",
            clause,
            re.I,
        ):
            continue
        if _preferred_clause(clause):
            if found != "required":
                found = "preferred"
            continue
        if re.search(r"\brequired\b|\bmust\b|\bpursuing\b|\benrolled in\b", clause, re.I):
            return "required"
    return found


def _education(
    text: str,
    sections: list[tuple[str, list[str]]],
    usable: bool,
) -> EducationRequirement:
    if not usable:
        return EducationRequirement(state="unknown")
    joined = text
    bachelors = _degree_state(joined, r"\bbachelor(?:'s|s)?\b|\bb\.?s\.?\b", True)
    masters = _degree_state(joined, r"\bmaster(?:'s|s)?\b|\bm\.?s\.?\b", True)
    mba = _degree_state(joined, r"\bmba\b", True)
    other: list[TextItem] = []
    for clause in _clauses(text):
        if re.search(r"\bph\.?d\b|\bj\.?d\.?\b|\bm\.?d\.?\b", clause, re.I) and re.search(
            r"\brequired\b|\bpreferred\b|\bmust\b",
            clause,
            re.I,
        ):
            other.append(_item(clause, "degree"))
    for kind, bullets in sections:
        for line in bullets:
            if not re.search(r"\bbachelor|\bmaster|\bmba\b|\bdegree\b|\bph\.?d\b", line, re.I):
                continue
            if kind == "preferred" or _PREFERRED_LINE.search(line):
                if re.search(r"\bbachelor", line, re.I) and bachelors == "not_mentioned":
                    bachelors = "preferred"
                if re.search(r"\bmaster", line, re.I) and masters == "not_mentioned":
                    masters = "preferred"
                if re.search(r"\bmba\b", line, re.I) and mba == "not_mentioned":
                    if not re.search(r"\bmba\s+intern", line, re.I):
                        mba = "preferred"
            elif re.search(r"\brequired\b|\bmust\b", line, re.I) or kind == "required":
                if re.search(r"\bbachelor", line, re.I) and bachelors != "preferred":
                    bachelors = "required"
                if re.search(r"\bmaster", line, re.I) and masters != "preferred":
                    masters = "required"
                if (
                    re.search(r"\bmba\b", line, re.I)
                    and not re.search(r"\bmba\s+intern", line, re.I)
                    and mba != "preferred"
                ):
                    mba = "required"
    mentioned = (
        bachelors != "not_mentioned"
        or masters != "not_mentioned"
        or mba != "not_mentioned"
        or other
    )
    return EducationRequirement(
        state="explicit" if mentioned else "not_mentioned",
        bachelors=bachelors,
        masters=masters,
        mba=mba,
        other=other,
        snippet=_first_snippet(text, r"\b(?:bachelor|master|mba|ph\.?d|degree)\b"),
    )


def _first_snippet(text: str, pattern: str) -> str | None:
    match = re.search(pattern, text, re.I)
    if match is None:
        return None
    return _clip(_clause_at(text, match.start()))


def _functional_match(text: str, name: str, pattern: str) -> re.Match[str] | None:
    for match in re.finditer(pattern, text, re.I):
        if name == "marketing":
            prefix = text[max(0, match.start() - 8) : match.start()].lower()
            if prefix == "product ":
                continue
        return match
    return None


def _functional(text: str, usable: bool) -> FunctionalSignals:
    if not usable:
        return FunctionalSignals(state="unknown")
    areas: list[TextItem] = []
    for name, patterns in _FUNCTIONAL:
        for pattern in patterns:
            match = _functional_match(text, name, pattern)
            if match is not None:
                areas.append(_item(_clause_at(text, match.start()), name))
                break
    return FunctionalSignals(state="explicit" if areas else "not_mentioned", areas=areas)


def _flag(text: str, pattern: str) -> bool | None:
    return True if re.search(pattern, text, re.I) else None


def _summer_internship(text: str) -> bool | None:
    if re.search(r"\bsummer\s+intern(?:ship)?\b", text, re.I):
        return True
    for clause in _clauses(text):
        if re.search(r"\bsummer\b", clause, re.I) and re.search(r"\bintern", clause, re.I):
            return True
    return None


def _program(text: str, usable: bool) -> ProgramSignals:
    if not usable:
        return ProgramSignals(state="unknown")
    duration = re.search(r"\b(\d{1,2}(?:\s*-\s*\d{1,2})?\s*-?\s*weeks?)\b", text, re.I)
    timing = re.search(
        rf"\b((?:summer|fall|winter|spring)\s+20\d{{2}}|(?:start|starts|starting)\s+(?:in\s+)?(?:{_MONTH}))\b",
        text,
        re.I,
    )
    signals = ProgramSignals(
        state="not_mentioned",
        internship=_flag(text, r"\bintern(?:ship)?\b"),
        mba_internship=_flag(text, r"\bmba\s+intern(?:ship)?\b|\bintern(?:ship)?\b.{0,40}\bmba\b"),
        summer_internship=_summer_internship(text),
        rotational_program=_flag(text, r"\brotational program\b"),
        leadership_development_program=_flag(text, r"\bleadership development program\b"),
        full_time=_flag(text, r"\bfull[- ]time\b"),
        temporary_or_contract=_flag(text, r"\b(?:temporary|contract) role\b|\bcontractor\b"),
        duration=_clip(duration.group(1)) if duration else None,
        timing=_clip(timing.group(1)) if timing else None,
    )
    snippets = [
        _clip(match.group(0))
        for pattern in (
            r"\bmba\s+intern(?:ship)?\b",
            r"\bsummer\s+intern(?:ship)?\b",
            r"\bintern(?:ship)?\b",
            r"\brotational program\b",
            r"\bleadership development program\b",
            r"\bfull[- ]time\b",
            r"\d{1,2}(?:\s*-\s*\d{1,2})?\s*-?\s*weeks?\b",
        )
        if (match := re.search(pattern, text, re.I))
    ]
    signals.snippets = snippets[:4]
    populated = any(
        value is not None
        for value in (
            signals.internship,
            signals.mba_internship,
            signals.summer_internship,
            signals.rotational_program,
            signals.leadership_development_program,
            signals.full_time,
            signals.temporary_or_contract,
            signals.duration,
            signals.timing,
        )
    )
    signals.state = "explicit" if populated else "not_mentioned"
    return signals


def _negated(clause: str, word: str) -> bool:
    return re.search(rf"\b(?:not|no)\b.{{0,24}}\b{word}\b", clause, re.I) is not None


def _work_model(text: str, usable: bool) -> WorkModelSignals:
    if not usable:
        return WorkModelSignals(state="unknown")
    remote = hybrid = onsite = None
    snippets: list[str] = []
    for clause in _clauses(text):
        if re.search(r"\bremote\b", clause, re.I) and not _negated(clause, "remote"):
            remote = True
            snippets.append(_clip(clause))
        if re.search(r"\bhybrid\b", clause, re.I) and not _negated(clause, "hybrid"):
            hybrid = True
            snippets.append(_clip(clause))
        if re.search(r"\b(?:onsite|on-site|in[- ]office)\b", clause, re.I):
            onsite = True
            snippets.append(_clip(clause))
    places = []
    for match in _PLACE.finditer(text):
        if match.group(2) in _STATES:
            places.append(f"{match.group(1)}, {match.group(2)}")
    travel = re.search(r"\b(\d{1,3}%\s*travel|travel(?:\s+up)?\s+to\s+\d{1,3}%)\b", text, re.I)
    relocation = re.search(r"\b([^.!\n]*\brelocation\b[^.!\n]*)", text, re.I)
    model = WorkModelSignals(
        state="not_mentioned",
        places=places[:4],
        remote=remote,
        hybrid=hybrid,
        onsite=onsite,
        travel=_clip(travel.group(1)) if travel else None,
        relocation=_clip(relocation.group(1)) if relocation else None,
        snippets=snippets[:4],
    )
    filled = any(
        value is not None
        for value in (remote, hybrid, onsite, model.travel, model.relocation)
    )
    if filled or places:
        model.state = "explicit"
    return model


def _mentioned(flag: bool) -> State:
    return "explicit" if flag else "not_mentioned"


def _authorization(text: str, usable: bool) -> AuthorizationEvidence:
    if not usable:
        return AuthorizationEvidence(state="unknown")
    sponsorship_raw = visa_sponsorship_signal(text)
    sponsorship: SponsorshipState = "not_mentioned"
    if sponsorship_raw == "friendly":
        sponsorship = "available"
    elif sponsorship_raw == "hostile":
        sponsorship = "unavailable"
    clearance_raw = clearance_requirement(text)
    clearance: ClearanceState = "not_mentioned"
    if clearance_raw == "required":
        clearance = "required"
    elif clearance_raw == "preferred":
        clearance = "preferred"
    work_auth = _mentioned(
        bool(re.search(r"\bauthorized to work\b|\bwork authorization\b", text, re.I))
    )
    citizenship = _mentioned(citizenship_restriction(text))
    residency: State = "not_mentioned"
    for clause in _clauses(text):
        if re.search(r"\bpermanent resident\b|\bgreen card\b", clause, re.I) and re.search(
            r"\brequired\b|\bmust\b",
            clause,
            re.I,
        ):
            residency = "explicit"
            break
    other: list[str] = []
    if residency == "explicit":
        other.append("permanent residency")
    snippets = [
        snippet
        for snippet in (
            _first_snippet(text, r"\bsponsorship\b|\bsponsor\b"),
            _first_snippet(text, r"\bcitizen"),
            _first_snippet(text, r"\bclearance\b"),
            _first_snippet(text, r"\bauthorized to work\b|\bwork authorization\b"),
        )
        if snippet
    ]
    evidence = AuthorizationEvidence(
        state="not_mentioned",
        sponsorship=sponsorship,
        work_authorization_required=work_auth,
        citizenship_required=citizenship,
        permanent_residency_required=residency,
        security_clearance=clearance,
        other_restrictions=other,
        snippets=snippets[:4],
    )
    if (
        sponsorship != "not_mentioned"
        or work_auth == "explicit"
        or citizenship == "explicit"
        or residency == "explicit"
        or clearance != "not_mentioned"
    ):
        evidence.state = "explicit"
    return evidence


def _domain(text: str, usable: bool) -> DomainSignals:
    if not usable:
        return DomainSignals(state="unknown")
    domains = []
    for name, pattern in _DOMAIN:
        match = re.search(pattern, text, re.I)
        if match:
            domains.append(_item(_clause_at(text, match.start()), name))
    return DomainSignals(state="explicit" if domains else "not_mentioned", domains=domains)


def _read(text: str, availability: Availability) -> StructuredJdDocument:
    sections = _sections(text)
    return StructuredJdDocument(
        version=STRUCTURED_JD_VERSION,
        availability=availability,
        responsibilities=_responsibilities(sections, True),
        qualifications=_qualifications(sections, True),
        experience=_experience(text, True),
        education=_education(text, sections, True),
        functional=_functional(text, True),
        program=_program(text, True),
        work_model=_work_model(text, True),
        authorization=_authorization(text, True),
        domain=_domain(text, True),
    )

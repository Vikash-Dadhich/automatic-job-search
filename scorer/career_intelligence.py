"""Career-opportunity reading for one job. This is not a fit score.

Unknown evidence is omitted from the overall score. It is not treated as a miss.
The reading does not change fit, priority, shortlist membership, or applications.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from sqlmodel import col, select

from config.diagnostics import fingerprint_profile
from config.profile import Profile
from core.db import CareerIntelligence, Job, session_scope
from scraper.structured_jd import get_structured_jd

CAREER_INTELLIGENCE_VERSION = "career-intelligence-v1"
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "career_intelligence.yaml"
_TARGET_FAMILIES = frozenset(
    {
        "PRODUCT_MANAGEMENT",
        "CONSULTING",
        "STRATEGY_TRANSFORMATION",
        "PRODUCT_MARKETING",
        "MARKETING",
        "PROGRAM_PROJECT_OPERATIONS",
    }
)
_TRANSITION_GROUPS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("product", (r"\bproduct (?:management|manager|roadmap|ownership)\b", r"\bown the product\b")),
    (
        "strategy",
        (
            r"\b(?:corporate|business|technology) strategy\b",
            r"\bbusiness transformation\b",
        ),
    ),
    ("consulting", (r"\bmanagement consulting\b", r"\bconsulting engagement\b")),
    ("customer", (r"\bcustomer discovery\b", r"\buser research\b")),
    ("gtm", (r"\bgo-to-market\b", r"\bproduct marketing\b")),
    ("leadership", (r"\bcross-functional\b", r"\bstakeholder management\b")),
)
_LEARNING_GROUPS: tuple[tuple[str, str], ...] = (
    ("ownership", r"\bown(?:ership)?\b|\bproduct ownership\b"),
    ("strategy", r"\b(?:corporate|business|technology) strategy\b|\bstrategic\b"),
    ("customer", r"\bcustomer discovery\b|\buser research\b"),
    ("analytics", r"\banalytics\b|\bdata analysis\b"),
    ("gtm", r"\bgo-to-market\b|\bproduct marketing\b"),
    ("stakeholders", r"\bstakeholder\b|\bcross-functional\b"),
    ("transformation", r"\bbusiness transformation\b"),
    ("executive", r"\bexecutive(?:s| team)?\b"),
)
_QUALITY_GROUPS: tuple[tuple[str, str], ...] = (
    ("ownership", r"\bown(?:ership)?\b|\bproduct ownership\b"),
    ("cross_functional", r"\bcross-functional\b"),
    ("strategy", r"\b(?:corporate|business|technology) strategy\b|\bstrategic project\b"),
    ("leadership", r"\bstakeholder management\b|\blead(?:ership| a team)\b"),
    ("customer", r"\bcustomer discovery\b|\buser research\b|\bcustomer impact\b"),
)
_TECH_RE = re.compile(r"\b(?:software|technology|engineering|platform)\b", re.IGNORECASE)
_CONVERSION_RE = re.compile(
    r"\b(?:return offer|full-time offer|full time offer|convert to full-time|"
    r"conversion to full-time|internship-to-full-time|high-performing interns)\b",
    re.IGNORECASE,
)
_MBA_RE = re.compile(
    r"\bmba internship\b|\bmba recruiting\b|\bbusiness school\b|"
    r"\bgraduate recruiting\b|\bmba leadership\b",
    re.IGNORECASE,
)
_EFFORT_RES = (
    re.compile(r"\bcover letter\b", re.IGNORECASE),
    re.compile(r"\bportfolio\b", re.IGNORECASE),
    re.compile(r"\bessay\b", re.IGNORECASE),
    re.compile(r"\bwriting sample\b", re.IGNORECASE),
)
_MBA_COMPANY_SIGNALS = frozenset(
    {
        "mba_internship_program",
        "mba_recruiting",
        "business_school_recruiting",
        "full_time_mba_recruiting",
    }
)
_WEIGHT_KEYS = (
    "career_transition",
    "career_story",
    "internship_quality",
    "learning_value",
    "conversion_signal",
    "mba_recruiting",
    "opportunity_quality",
    "application_effort",
    "competitiveness",
)


@dataclass(frozen=True, slots=True)
class _Dimension:
    state: str
    evidence: tuple[str, ...]
    score: int | None


@dataclass(frozen=True, slots=True)
class CareerReading:
    availability: str
    content_hash: str
    transition: _Dimension
    story: _Dimension
    internship_quality: _Dimension
    learning: _Dimension
    conversion_signal: str
    conversion_evidence: tuple[str, ...]
    mba_recruiting_signal: str
    mba_evidence: tuple[str, ...]
    opportunity_quality: _Dimension
    application_effort: _Dimension
    competitiveness: _Dimension
    overall_score: int | None

    def evidence_document(self) -> dict[str, Any]:
        return {
            "career_transition": _dump(self.transition),
            "career_story": _dump(self.story),
            "internship_quality": _dump(self.internship_quality),
            "learning_value": _dump(self.learning),
            "conversion": {
                "state": self.conversion_signal,
                "evidence": list(self.conversion_evidence),
            },
            "mba_recruiting": {
                "state": self.mba_recruiting_signal,
                "evidence": list(self.mba_evidence),
            },
            "opportunity_quality": _dump(self.opportunity_quality),
            "application_effort": _dump(self.application_effort),
            "competitiveness": _dump(self.competitiveness),
        }


def _dump(item: _Dimension) -> dict[str, Any]:
    return {"state": item.state, "evidence": list(item.evidence)}


def _require_int(name: str, value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0 or value > 100:
        raise ValueError(f"{name} must be an integer from 0 through 100")
    return value


def _validate(raw: object) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ValueError("career intelligence config must be a mapping")
    if raw.get("version") != CAREER_INTELLIGENCE_VERSION:
        raise ValueError(f"career intelligence version must be {CAREER_INTELLIGENCE_VERSION}")
    states = raw.get("state_scores")
    signals = raw.get("signal_scores")
    weights = raw.get("weights")
    if not isinstance(states, dict) or set(states) != {"STRONG", "MODERATE", "WEAK"}:
        raise ValueError("state_scores must set STRONG, MODERATE, and WEAK")
    if not isinstance(signals, dict) or set(signals) != {"CONFIRMED"}:
        raise ValueError("signal_scores must set CONFIRMED")
    if not isinstance(weights, dict) or set(weights) != set(_WEIGHT_KEYS):
        raise ValueError("career intelligence weights are incomplete")
    return {
        "version": CAREER_INTELLIGENCE_VERSION,
        "state_scores": {
            key: _require_int(key, states[key]) for key in ("STRONG", "MODERATE", "WEAK")
        },
        "signal_scores": {"CONFIRMED": _require_int("CONFIRMED", signals["CONFIRMED"])},
        "weights": {key: _require_int(key, weights[key]) for key in _WEIGHT_KEYS},
    }


@lru_cache
def load_career_config(path: str | None = None) -> dict[str, Any]:
    target = Path(path) if path else CONFIG_PATH
    with target.open(encoding="utf-8") as handle:
        raw: Any = yaml.safe_load(handle)
    return _validate(raw)


def config_hash(config: dict[str, Any] | None = None) -> str:
    payload = config if config is not None else load_career_config()
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def _clip(text: str) -> str:
    return " ".join(text.split())[:160]


def _texts(document: dict[str, Any] | None, section: str, key: str) -> list[str]:
    if not document:
        return []
    block = document.get(section)
    if not isinstance(block, dict):
        return []
    items = block.get(key)
    if not isinstance(items, list):
        return []
    found: list[str] = []
    for item in items:
        if isinstance(item, dict) and isinstance(item.get("text"), str):
            found.append(item["text"])
        elif isinstance(item, str):
            found.append(item)
    return found


def _match_groups(
    lines: list[str],
    groups: tuple[tuple[str, tuple[str, ...]] | tuple[str, str], ...],
) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    seen: set[str] = set()
    for name, pattern in groups:
        patterns = pattern if isinstance(pattern, tuple) else (pattern,)
        for line in lines:
            if any(re.search(item, line, re.IGNORECASE) for item in patterns):
                if name not in seen:
                    seen.add(name)
                    found.append((name, _clip(line)))
                break
    return found


def _state_for_count(count: int, config: dict[str, Any]) -> str:
    if count >= 2:
        return "STRONG"
    if count == 1:
        return "MODERATE"
    return "UNKNOWN"


def _dimension(
    state: str,
    evidence: list[str],
    config: dict[str, Any],
) -> _Dimension:
    score = None if state == "UNKNOWN" else int(config["state_scores"][state])
    return _Dimension(state, tuple(evidence[:3]), score)


def _usable(description: str, responsibilities: list[str]) -> bool:
    return len(description.strip()) >= 40 or bool(responsibilities)


def _transition(
    lines: list[str],
    role_family: str | None,
    role_confidence: str | None,
    config: dict[str, Any],
) -> _Dimension:
    hits = _match_groups(lines, _TRANSITION_GROUPS)
    evidence = [f"Responsibility: {text}" for _name, text in hits]
    family = (role_family or "").strip()
    confidence = (role_confidence or "").strip().lower()
    if family in _TARGET_FAMILIES and confidence in {"high", "medium"}:
        evidence.append(f"Classified role family {family}.")
        hits.append((family, family))
    return _dimension(_state_for_count(len(hits), config), evidence, config)


def _story(lines: list[str], transition: _Dimension, config: dict[str, Any]) -> _Dimension:
    if transition.state == "UNKNOWN":
        return _dimension("UNKNOWN", [], config)
    joined = "\n".join(lines)
    tech = _TECH_RE.search(joined)
    if tech and transition.state in {"STRONG", "MODERATE"}:
        snippet = _clip(joined[max(0, tech.start() - 40) : tech.end() + 40])
        evidence = [f"Posting: {snippet}", *transition.evidence[:1]]
        return _dimension("STRONG", evidence, config)
    return _dimension("MODERATE", list(transition.evidence[:2]), config)


def _internship(
    document: dict[str, Any] | None,
    lines: list[str],
    config: dict[str, Any],
) -> _Dimension:
    program = document.get("program") if isinstance(document, dict) else None
    program = program if isinstance(program, dict) else {}
    substantive = bool(_match_groups(lines, _QUALITY_GROUPS))
    mba = program.get("mba_internship") is True
    summer = program.get("summer_internship") is True
    generic = program.get("internship") is True
    leadership = program.get("leadership_development_program") is True
    if mba and substantive:
        evidence = ["Structured reading: MBA internship is stated."]
        if lines:
            evidence.append(f"Responsibility: {_clip(lines[0])}")
        return _dimension("STRONG", evidence, config)
    if mba:
        return _dimension("MODERATE", ["Structured reading: MBA internship is stated."], config)
    if (summer or leadership or generic) and substantive:
        return _dimension(
            "MODERATE",
            ["Structured reading: internship program with substantive responsibilities."],
            config,
        )
    return _dimension("UNKNOWN", [], config)


def _themes(
    lines: list[str],
    groups: tuple[tuple[str, str], ...],
    config: dict[str, Any],
) -> _Dimension:
    hits = _match_groups(lines, groups)
    evidence = [f"Responsibility: {text}" for _name, text in hits]
    state = "STRONG" if len(hits) >= 3 else "MODERATE" if hits else "UNKNOWN"
    return _dimension(state, evidence, config)


def _clause(text: str, match: re.Match[str]) -> str:
    start = text.rfind("\n", 0, match.start())
    end = text.find("\n", match.end())
    chunk = text[start + 1 : end if end != -1 else len(text)]
    return _clip(chunk)


def _signal_in_text(text: str, pattern: re.Pattern[str], *, usable: bool) -> tuple[str, list[str]]:
    if not usable:
        return "UNKNOWN", []
    match = pattern.search(text)
    if match is None:
        return "NOT_FOUND", []
    return "CONFIRMED", [f"Posting: {_clause(text, match)}"]


def _mba_signal(
    text: str,
    document: dict[str, Any] | None,
    company_signals: list[str],
    *,
    usable: bool,
) -> tuple[str, list[str]]:
    program = document.get("program") if isinstance(document, dict) else None
    if isinstance(program, dict) and program.get("mba_internship") is True:
        return "CONFIRMED", ["Structured reading: MBA internship is stated."]
    state, evidence = _signal_in_text(text, _MBA_RE, usable=usable)
    if state == "CONFIRMED":
        return state, evidence
    named = [name for name in company_signals if name in _MBA_COMPANY_SIGNALS]
    if named:
        return "CONFIRMED", [f"Company intelligence signal: {named[0]}."]
    if not usable and not named:
        return "UNKNOWN", []
    return "NOT_FOUND", []


def _competitiveness(
    document: dict[str, Any] | None,
    profile: Profile,
    config: dict[str, Any],
) -> _Dimension:
    experience = document.get("experience") if isinstance(document, dict) else None
    education = document.get("education") if isinstance(document, dict) else None
    required = _texts(document, "qualifications", "required")
    matches: list[str] = []
    gaps: list[str] = []
    if isinstance(experience, dict) and isinstance(experience.get("minimum_years"), int):
        floor = int(experience["minimum_years"])
        years = profile.total_years_experience()
        if years >= floor:
            matches.append(f"Required {floor} years is within the profile experience.")
        else:
            gaps.append(f"Required {floor} years is above the profile experience.")
    has_mba = any("mba" in (item.degree or "").lower() for item in profile.education)
    if isinstance(education, dict) and education.get("mba") == "required":
        if has_mba:
            matches.append("Required MBA is present on the profile.")
        else:
            gaps.append("Required MBA is not present on the profile.")
    skills = " ".join(profile.skills).lower()
    for line in required:
        lowered = line.lower()
        if any(skill.lower() in lowered for skill in profile.skills if len(skill) >= 4):
            matches.append(f"Required qualification overlaps a profile skill: {_clip(line)}")
        elif skills and any(token in lowered for token in skills.split() if len(token) >= 5):
            matches.append(f"Required qualification overlaps a profile skill: {_clip(line)}")
    if gaps and not matches:
        return _dimension("WEAK", gaps, config)
    if len(matches) >= 2 and not gaps:
        return _dimension("STRONG", matches, config)
    if matches:
        return _dimension("MODERATE", [*matches, *gaps], config)
    return _dimension("UNKNOWN", [], config)


def _effort(text: str, *, usable: bool, config: dict[str, Any]) -> _Dimension:
    if not usable:
        return _dimension("UNKNOWN", [], config)
    hits = [pattern.pattern for pattern in _EFFORT_RES if pattern.search(text)]
    if len(hits) >= 2:
        return _dimension("STRONG", ["Posting states multiple application materials."], config)
    if len(hits) == 1:
        return _dimension("MODERATE", ["Posting states an extra application material."], config)
    return _dimension("UNKNOWN", [], config)


def _overall(parts: list[tuple[str, int | None]], config: dict[str, Any]) -> int | None:
    weights = config["weights"]
    total = 0
    weight = 0
    for name, score in parts:
        item_weight = int(weights[name])
        if item_weight <= 0 or score is None:
            continue
        total += item_weight * score
        weight += item_weight
    if weight == 0:
        return None
    return (total + weight // 2) // weight


def _signal_score(state: str, config: dict[str, Any]) -> int | None:
    if state != "CONFIRMED":
        return None
    return int(config["signal_scores"]["CONFIRMED"])


def career_input_hash(
    job: Job,
    profile: Profile,
    *,
    structured_hash: str | None,
    structured_version: str | None,
    company_hash: str | None,
    company_version: str | None,
    config: dict[str, Any] | None = None,
) -> str:
    """Identity of this reading. The raw profile is not included."""
    active = config if config is not None else load_career_config()
    description = hashlib.sha256((job.description_clean or "").encode()).hexdigest()
    payload = {
        "version": CAREER_INTELLIGENCE_VERSION,
        "config": config_hash(active),
        "profile": fingerprint_profile(profile),
        "content_hash": job.content_hash,
        "description": description,
        "structured_hash": structured_hash,
        "structured_version": structured_version,
        "role_family": job.role_family,
        "role_subfamily": job.role_subfamily,
        "role_confidence": job.role_confidence,
        "role_classifier_version": job.role_classifier_version,
        "role_evidence": job.role_evidence,
        "role_secondary_family": job.role_secondary_family,
        "company_hash": company_hash,
        "company_version": company_version,
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode()).hexdigest()


def assess_career(
    job: Job,
    profile: Profile,
    *,
    document: dict[str, Any] | None = None,
    structured_hash: str | None = None,
    structured_version: str | None = None,
    company_signals: list[str] | None = None,
    company_hash: str | None = None,
    company_version: str | None = None,
    config: dict[str, Any] | None = None,
) -> CareerReading:
    """Deterministic career reading. Does not call a model or read fit."""
    active = config if config is not None else load_career_config()
    digest = career_input_hash(
        job,
        profile,
        structured_hash=structured_hash,
        structured_version=structured_version,
        company_hash=company_hash,
        company_version=company_version,
        config=active,
    )
    lines = _texts(document, "responsibilities", "items")
    description = job.description_clean or ""
    usable = _usable(description, lines)
    if not usable:
        blank = _dimension("UNKNOWN", [], active)
        return CareerReading(
            availability="unavailable",
            content_hash=digest,
            transition=blank,
            story=blank,
            internship_quality=blank,
            learning=blank,
            conversion_signal="UNKNOWN",
            conversion_evidence=(),
            mba_recruiting_signal="UNKNOWN",
            mba_evidence=(),
            opportunity_quality=blank,
            application_effort=blank,
            competitiveness=blank,
            overall_score=None,
        )
    transition = _transition(lines, job.role_family, job.role_confidence, active)
    story = _story(lines, transition, active)
    internship = _internship(document, lines, active)
    learning = _themes(lines, _LEARNING_GROUPS, active)
    quality = _themes(lines, _QUALITY_GROUPS, active)
    conversion, conversion_evidence = _signal_in_text(description, _CONVERSION_RE, usable=True)
    mba_state, mba_evidence = _mba_signal(
        description,
        document,
        company_signals or [],
        usable=True,
    )
    effort = _effort(description, usable=True, config=active)
    competitiveness = _competitiveness(document, profile, active)
    overall = _overall(
        [
            ("career_transition", transition.score),
            ("career_story", story.score),
            ("internship_quality", internship.score),
            ("learning_value", learning.score),
            ("conversion_signal", _signal_score(conversion, active)),
            ("mba_recruiting", _signal_score(mba_state, active)),
            ("opportunity_quality", quality.score),
            ("application_effort", effort.score),
            ("competitiveness", competitiveness.score),
        ],
        active,
    )
    known = [
        transition.state,
        story.state,
        internship.state,
        learning.state,
        quality.state,
        competitiveness.state,
        conversion,
        mba_state,
    ]
    positive = any(item not in {"UNKNOWN", "NOT_FOUND"} for item in known)
    availability = "available" if positive else "partial"
    return CareerReading(
        availability=availability,
        content_hash=digest,
        transition=transition,
        story=story,
        internship_quality=internship,
        learning=learning,
        conversion_signal=conversion,
        conversion_evidence=tuple(conversion_evidence),
        mba_recruiting_signal=mba_state,
        mba_evidence=tuple(mba_evidence),
        opportunity_quality=quality,
        application_effort=effort,
        competitiveness=competitiveness,
        overall_score=overall,
    )


def _company_signals(context: dict[str, Any] | None) -> tuple[list[str], str | None, str | None]:
    if not isinstance(context, dict):
        return [], None, None
    signals = context.get("signals")
    names: list[str] = []
    if isinstance(signals, list):
        for item in signals:
            if isinstance(item, dict) and isinstance(item.get("signal"), str):
                names.append(item["signal"])
    version = context.get("version") if isinstance(context.get("version"), str) else None
    digest = context.get("content_hash") if isinstance(context.get("content_hash"), str) else None
    return names, digest, version


async def get_career_intelligence(job_id: int) -> CareerIntelligence | None:
    async with session_scope() as session:
        result = await session.exec(
            select(CareerIntelligence).where(col(CareerIntelligence.job_id) == job_id)
        )
        return result.first()


def _apply_reading(row: CareerIntelligence, reading: CareerReading) -> None:
    row.version = CAREER_INTELLIGENCE_VERSION
    row.content_hash = reading.content_hash
    row.availability = reading.availability
    row.career_transition_score = reading.transition.score
    row.career_story_score = reading.story.score
    row.internship_quality_score = reading.internship_quality.score
    row.learning_value_score = reading.learning.score
    row.conversion_signal = reading.conversion_signal
    row.mba_recruiting_signal = reading.mba_recruiting_signal
    row.opportunity_quality_score = reading.opportunity_quality.score
    row.application_effort_score = reading.application_effort.score
    row.competitiveness_score = reading.competitiveness.score
    row.overall_score = reading.overall_score
    row.evidence = reading.evidence_document()
    row.updated_at = datetime.now(UTC)


async def attach_career_intelligence(job_id: int, profile: Profile) -> CareerIntelligence | None:
    """Store one current reading. Does not write fit, priority, status, or shortlist."""
    async with session_scope() as session:
        job = await session.get(Job, job_id)
        if job is None:
            return None
        structured = await get_structured_jd(session, job_id)
        document = None
        if structured is not None and isinstance(structured.document, dict):
            document = structured.document
        company_context = None
        if job.company_intelligence_id is not None:
            from core.db import CompanyIntelligence

            company = await session.get(CompanyIntelligence, job.company_intelligence_id)
            if company is not None and isinstance(company.context, dict):
                company_context = company.context
        names, company_hash, company_version = _company_signals(company_context)
        reading = assess_career(
            job,
            profile,
            document=document,
            structured_hash=structured.content_hash if structured is not None else None,
            structured_version=structured.version if structured is not None else None,
            company_signals=names,
            company_hash=company_hash,
            company_version=company_version,
        )
        result = await session.exec(
            select(CareerIntelligence).where(col(CareerIntelligence.job_id) == job_id)
        )
        existing = result.first()
        if (
            existing is not None
            and existing.version == CAREER_INTELLIGENCE_VERSION
            and existing.content_hash == reading.content_hash
        ):
            return existing
        row = existing or CareerIntelligence(
            job_id=job_id,
            version=CAREER_INTELLIGENCE_VERSION,
            content_hash=reading.content_hash,
            availability=reading.availability,
            evidence={},
        )
        _apply_reading(row, reading)
        session.add(row)
        await session.flush()
        return row

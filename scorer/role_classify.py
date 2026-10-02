"""Classify what a job is. This does not score whether the candidate should apply."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, replace
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from scorer.clients import LLMClient

ROLE_CLASSIFIER_VERSION = "phase5-v4"

PRIMARY_FAMILIES = frozenset(
    {
        "PRODUCT_MANAGEMENT",
        "CONSULTING",
        "STRATEGY_TRANSFORMATION",
        "PRODUCT_MARKETING",
        "PROGRAM_PROJECT_OPERATIONS",
        "MARKETING",
        "OTHER",
        "UNKNOWN",
    }
)

SUBFAMILY_FAMILY = {
    "PM_CORE": "PRODUCT_MANAGEMENT",
    "APM_MBA_PM": "PRODUCT_MANAGEMENT",
    "TECHNICAL_PRODUCT": "PRODUCT_MANAGEMENT",
    "PRODUCT_STRATEGY": "PRODUCT_MANAGEMENT",
    "PRODUCT_OPERATIONS": "PRODUCT_MANAGEMENT",
    "MANAGEMENT_CONSULTING": "CONSULTING",
    "STRATEGY_CONSULTING": "CONSULTING",
    "TECHNOLOGY_CONSULTING": "CONSULTING",
    "BUSINESS_CONSULTING": "CONSULTING",
    "TRANSFORMATION_CONSULTING": "CONSULTING",
    "CORPORATE_STRATEGY": "STRATEGY_TRANSFORMATION",
    "BUSINESS_STRATEGY": "STRATEGY_TRANSFORMATION",
    "STRATEGY_OPERATIONS": "STRATEGY_TRANSFORMATION",
    "STRATEGIC_INITIATIVES": "STRATEGY_TRANSFORMATION",
    "BUSINESS_TRANSFORMATION": "STRATEGY_TRANSFORMATION",
    "GTM_STRATEGY": "STRATEGY_TRANSFORMATION",
    "CORPORATE_DEVELOPMENT": "STRATEGY_TRANSFORMATION",
    "TECHNOLOGY_STRATEGY": "STRATEGY_TRANSFORMATION",
    "PRODUCT_MARKETING": "PRODUCT_MARKETING",
    "MARKETING_GENERAL": "MARKETING",
    "PROGRAM_MANAGEMENT": "PROGRAM_PROJECT_OPERATIONS",
    "PROJECT_MANAGEMENT": "PROGRAM_PROJECT_OPERATIONS",
    "BUSINESS_OPERATIONS": "PROGRAM_PROJECT_OPERATIONS",
    "CUSTOMER_SUCCESS": "PROGRAM_PROJECT_OPERATIONS",
}

_EVIDENCE = {
    "PM_CORE": "JD emphasizes roadmap ownership and product prioritization.",
    "APM_MBA_PM": "Title or JD describes an associate product manager internship.",
    "TECHNICAL_PRODUCT": "JD describes a technical or platform product role.",
    "PRODUCT_STRATEGY": "JD focuses on product strategy and product vision.",
    "PRODUCT_OPERATIONS": "JD describes product operations work.",
    "MANAGEMENT_CONSULTING": "JD describes client-facing management consulting work.",
    "STRATEGY_CONSULTING": "JD describes strategy consulting for clients.",
    "TECHNOLOGY_CONSULTING": "JD describes technology consulting for clients.",
    "BUSINESS_CONSULTING": "JD describes business consulting for clients.",
    "TRANSFORMATION_CONSULTING": "JD describes transformation consulting for clients.",
    "CORPORATE_STRATEGY": "JD describes internal corporate or enterprise strategy.",
    "BUSINESS_STRATEGY": "JD describes business strategy work inside the company.",
    "STRATEGY_OPERATIONS": "JD describes strategy and operations work.",
    "STRATEGIC_INITIATIVES": "JD describes strategic initiatives or strategic planning.",
    "BUSINESS_TRANSFORMATION": "JD describes internal business transformation.",
    "GTM_STRATEGY": "JD describes go-to-market strategy.",
    "CORPORATE_DEVELOPMENT": "JD describes corporate development and acquisition evaluation.",
    "TECHNOLOGY_STRATEGY": "JD describes internal technology or digital strategy.",
    "PRODUCT_MARKETING": "JD owns positioning, messaging, or product launch work.",
    "MARKETING_GENERAL": "JD describes brand, consumer, or marketing strategy work.",
    "PROGRAM_MANAGEMENT": "JD describes program management.",
    "PROJECT_MANAGEMENT": "JD describes project management.",
    "BUSINESS_OPERATIONS": "JD describes business operations.",
    "CUSTOMER_SUCCESS": "JD describes customer success work.",
    "OTHER": "JD describes a function outside the target role families.",
    "UNKNOWN": "Title and description do not identify a role.",
}

# Longer phrases are listed first and matched as substrings.
_PHRASES: dict[str, tuple[str, ...]] = {
    "TECHNICAL_PRODUCT": ("technical product", "platform roadmap", "api product"),
    "PRODUCT_STRATEGY": ("product strategy", "product vision"),
    "PRODUCT_OPERATIONS": ("product operations", "product ops"),
    "APM_MBA_PM": ("associate product manager",),
    "PM_CORE": (
        "product roadmap",
        "product prioritization",
        "own the product",
        "product requirements",
        "product owner",
    ),
    "STRATEGY_CONSULTING": ("strategy consulting", "strategy consultant"),
    "TECHNOLOGY_CONSULTING": (
        "technology consulting",
        "technology consultant",
        "digital consulting",
    ),
    "TRANSFORMATION_CONSULTING": ("transformation consulting", "transformation consultant"),
    "BUSINESS_CONSULTING": ("business consulting", "business consultant"),
    "MANAGEMENT_CONSULTING": (
        "management consulting",
        "case team",
        "client-facing",
        "client engagement",
    ),
    "STRATEGY_OPERATIONS": ("strategy and operations", "strategy & operations"),
    "STRATEGIC_INITIATIVES": ("strategic initiatives", "strategic planning"),
    "BUSINESS_TRANSFORMATION": ("business transformation", "transformation strategy"),
    "GTM_STRATEGY": ("go-to-market strategy", "gtm strategy"),
    "CORPORATE_DEVELOPMENT": (
        "corporate development",
        "acquisition targets",
        "strategic acquisitions",
    ),
    "CORPORATE_STRATEGY": ("corporate strategy", "enterprise strategy", "internal strategy"),
    "BUSINESS_STRATEGY": ("business strategy", "business unit strategy"),
    "TECHNOLOGY_STRATEGY": (
        "technology strategy",
        "tech strategy",
        "it strategy",
        "digital strategy",
        "enterprise technology strategy",
        "technology portfolio",
        "digital roadmap",
        "technology operating model",
    ),
    "PRODUCT_MARKETING": (
        "product marketing",
        "product positioning",
        "positioning and messaging",
        "go-to-market launches",
        "sales enablement",
        "competitive intelligence",
    ),
    "MARKETING_GENERAL": (
        "marketing strategy",
        "brand management",
        "brand strategy",
        "brand planning",
        "consumer marketing",
        "consumer insights",
        "campaign strategy",
        "campaign development",
        "integrated marketing",
        "marketing planning",
    ),
    "PROGRAM_MANAGEMENT": ("program management", "program manager"),
    "PROJECT_MANAGEMENT": ("project management", "project manager"),
    "BUSINESS_OPERATIONS": ("business operations",),
    "CUSTOMER_SUCCESS": ("customer success",),
}

_FINANCE = (
    "investment banking",
    "private equity",
    "hedge fund",
    "pitch book",
    "coverage group",
    "sell-side",
    "equity research",
)
_INTERNAL = (
    "internal corporate strategy",
    "internal strategy",
    "company's own strategy",
    "business unit strategy",
)
_CLIENT = ("client-facing", "client engagement", "case team", "for clients", "client project")
_SALES = ("sales quota", "sales associate", "quota-carrying", "close revenue")
_TECH_STRATEGY = (
    "technology strategy",
    "tech strategy",
    "it strategy",
    "digital strategy",
    "enterprise technology strategy",
)
_OUTSIDE_TITLE = (
    "software engineer",
    "data scientist",
    "data science",
    "account executive",
    "human resources",
)

_CLASSIFY_SYSTEM = (
    "You classify what kind of role a job posting describes. "
    "Use the title and the job description. Discovery labels are context only. "
    "The job description wins when it conflicts with the discovery query. "
    "Do not use any candidate profile, resume, skills, visa, or preferences. "
    "Do not score fit. Do not rank the job. Do not invent facts. "
    "MARKETING is general marketing, not product marketing. "
    "TECHNOLOGY_STRATEGY is internal technology strategy, not technology consulting. "
    "Return only the allowed taxonomy. OTHER and UNKNOWN are allowed as the primary family. "
    "A second family is optional and only when the role itself performs that function. "
    "Do not set a secondary family to OTHER or UNKNOWN. "
    "A preferred qualification, or collaborating with another function, "
    "does not establish a secondary family. "
    "Structured responsibilities are the strongest sign of work the role performs. "
    "Confidence is how sure the role label is, not whether someone should apply. "
    'Reply with JSON {"primary_family","subfamily","confidence","evidence",'
    '"secondary_family","secondary_subfamily","secondary_confidence","secondary_evidence"}.'
)


class _ModelLabel(BaseModel):
    primary_family: str
    subfamily: str | None = None
    confidence: str
    evidence: list[str] = Field(default_factory=list)
    secondary_family: str | None = None
    secondary_subfamily: str | None = None
    secondary_confidence: str | None = None
    secondary_evidence: list[str] = Field(default_factory=list)


@dataclass(frozen=True, slots=True)
class RoleClassification:
    role_family: str
    role_subfamily: str | None
    role_confidence: str
    role_evidence: list[str]
    role_classifier_version: str
    role_content_hash: str | None
    used_llm: bool = False
    role_secondary_family: str | None = None
    role_secondary_subfamily: str | None = None
    role_secondary_confidence: str | None = None
    role_secondary_evidence: list[str] = field(default_factory=list)


def classification_is_current(
    *,
    role_family: str | None,
    role_content_hash: str | None,
    role_classifier_version: str | None,
    content_hash: str | None,
) -> bool:
    """True when the stored label was produced for this exact description."""
    return bool(
        role_family
        and content_hash
        and role_content_hash == content_hash
        and role_classifier_version == ROLE_CLASSIFIER_VERSION
    )


def _unknown(content_hash: str | None, reason: str) -> RoleClassification:
    return RoleClassification(
        role_family="UNKNOWN",
        role_subfamily=None,
        role_confidence="low",
        role_evidence=[reason],
        role_classifier_version=ROLE_CLASSIFIER_VERSION,
        role_content_hash=content_hash,
    )


def _result(
    family: str,
    subfamily: str | None,
    confidence: str,
    evidence: list[str],
    content_hash: str | None,
    *,
    used_llm: bool = False,
) -> RoleClassification:
    if family not in PRIMARY_FAMILIES:
        return _unknown(content_hash, "Classifier returned a label outside the taxonomy.")
    if subfamily is not None and SUBFAMILY_FAMILY.get(subfamily) != family:
        return _unknown(content_hash, "Classifier returned a subfamily outside its family.")
    if confidence not in {"high", "medium", "low"}:
        return _unknown(content_hash, "Classifier returned a label outside the taxonomy.")
    cleaned = [line.strip() for line in evidence if line and line.strip()][:4]
    if not cleaned:
        cleaned = [_EVIDENCE.get(subfamily or family, _EVIDENCE["UNKNOWN"])]
    return RoleClassification(
        role_family=family,
        role_subfamily=subfamily,
        role_confidence=confidence,
        role_evidence=cleaned,
        role_classifier_version=ROLE_CLASSIFIER_VERSION,
        role_content_hash=content_hash,
        used_llm=used_llm,
    )


def _separate_technology_and_marketing(jd: str, title_l: str, scores: dict[str, int]) -> None:
    """Keep technology strategy, technology consulting, and product marketing apart."""
    blob = f"{title_l}\n{jd}"
    consulting = "technology consulting" in blob or "it consulting" in blob
    strategy = any(phrase in blob for phrase in _TECH_STRATEGY)
    client = any(phrase in blob for phrase in _CLIENT)
    if consulting:
        scores.pop("MANAGEMENT_CONSULTING", None)
        scores["TECHNOLOGY_CONSULTING"] = max(scores.get("TECHNOLOGY_CONSULTING", 0), 5)
        scores.pop("TECHNOLOGY_STRATEGY", None)
    elif strategy and not client:
        scores.pop("TECHNOLOGY_CONSULTING", None)
        scores.pop("MANAGEMENT_CONSULTING", None)
        scores["TECHNOLOGY_STRATEGY"] = max(scores.get("TECHNOLOGY_STRATEGY", 0), 5)
    if "product marketing" in blob or "sales enablement" in jd or "competitive intelligence" in jd:
        scores.pop("MARKETING_GENERAL", None)


def _score_blob(blob: str, weight: int, scores: dict[str, int]) -> None:
    for subfamily, phrases in _PHRASES.items():
        if any(phrase in blob for phrase in phrases):
            scores[subfamily] = scores.get(subfamily, 0) + weight


_INTERACTION_RE = re.compile(
    r"\b(?:collaborat\w*|work(?:s|ing)?(?:\s+closely)?\s+with|partner(?:s|ing)?\s+with|"
    r"support(?:s|ing)?\s+the)\b",
    re.IGNORECASE,
)
_PERFORM_RE = re.compile(
    r"\b(?:own|owns|lead|leads|develop|develops|define|defines|drive|drives|manage|manages|"
    r"responsible|build|builds)\b",
    re.IGNORECASE,
)
_NO_SECONDARY = frozenset({"OTHER", "UNKNOWN"})


def _clause_containing(text: str, phrase: str) -> str:
    match = re.search(re.escape(phrase), text, re.IGNORECASE)
    if match is None:
        return ""
    start = max(
        text.rfind(".", 0, match.start()),
        text.rfind("\n", 0, match.start()),
        text.rfind(";", 0, match.start()),
    )
    ends = [
        pos
        for pos in (
            text.find(".", match.end()),
            text.find("\n", match.end()),
            text.find(";", match.end()),
        )
        if pos != -1
    ]
    end = min(ends) if ends else len(text)
    return text[start + 1 : end].strip()


def _is_interaction(clause: str) -> bool:
    """True when the clause only says the role works beside another function."""
    if not clause or _INTERACTION_RE.search(clause) is None:
        return False
    return _PERFORM_RE.search(clause) is None


def _phrase_hits(description: str) -> dict[str, dict[str, list[str]]]:
    """Family → subfamily → phrases the role itself performs."""
    found: dict[str, dict[str, list[str]]] = {}
    for subfamily, phrases in _PHRASES.items():
        family = SUBFAMILY_FAMILY[subfamily]
        for phrase in phrases:
            if phrase not in description.lower():
                continue
            if _is_interaction(_clause_containing(description, phrase)):
                continue
            found.setdefault(family, {}).setdefault(subfamily, [])
            if phrase not in found[family][subfamily]:
                found[family][subfamily].append(phrase)
    return found


def _item_text(item: Any) -> str:
    raw = str(getattr(item, "text", "") or getattr(item, "snippet", "") or "")
    return " ".join(raw.split())


def _structured_support(structured: Any, family: str) -> str | None:
    """Responsibility text showing this family is work the role performs."""
    if structured is None or getattr(structured, "availability", None) == "unavailable":
        return None
    items = getattr(getattr(structured, "responsibilities", None), "items", None) or []
    for item in items:
        text = _item_text(item)
        if not text or _is_interaction(text):
            continue
        for subfamily, phrases in _PHRASES.items():
            if SUBFAMILY_FAMILY.get(subfamily) != family:
                continue
            if any(phrase in text.lower() for phrase in phrases):
                return text[:120]
    return None


def _clip_items(items: Any, limit: int = 6) -> list[str]:
    lines: list[str] = []
    for item in list(items or [])[:limit]:
        text = _item_text(item)
        if text:
            lines.append(text[:160])
    return lines


def _structured_prompt(structured: Any) -> str:
    """Compact structured evidence for the model. Not a candidate profile."""
    if structured is None or getattr(structured, "availability", None) == "unavailable":
        return ""
    parts = ["Structured reading of the same description:"]
    responsibilities = _clip_items(
        getattr(getattr(structured, "responsibilities", None), "items", None)
    )
    if responsibilities:
        parts.append("Responsibilities: " + "; ".join(responsibilities))
    qualifications = getattr(structured, "qualifications", None)
    required = _clip_items(getattr(qualifications, "required", None))
    preferred = _clip_items(getattr(qualifications, "preferred", None))
    if required:
        parts.append("Required qualifications: " + "; ".join(required))
    if preferred:
        parts.append("Preferred qualifications: " + "; ".join(preferred))
    experience = getattr(getattr(structured, "experience", None), "snippet", None)
    if experience:
        parts.append(f"Experience: {experience}")
    education = getattr(getattr(structured, "education", None), "snippet", None)
    if education:
        parts.append(f"Education: {education}")
    areas = _clip_items(getattr(getattr(structured, "functional", None), "areas", None))
    if areas:
        parts.append("Functional mentions: " + "; ".join(areas))
    program = getattr(getattr(structured, "program", None), "snippets", None) or []
    if program:
        parts.append("Program: " + "; ".join(str(item) for item in list(program)[:4]))
    work = getattr(getattr(structured, "work_model", None), "snippets", None) or []
    if work:
        parts.append("Work model: " + "; ".join(str(item) for item in list(work)[:3]))
    domains = _clip_items(getattr(getattr(structured, "domain", None), "domains", None))
    if domains:
        parts.append("Domain: " + "; ".join(domains))
    authorization = getattr(structured, "authorization", None)
    if getattr(authorization, "state", None) == "explicit":
        parts.append("Authorization language is present and is not role-family evidence.")
    parts.append(
        "Judge the role by work it performs. A qualification or a collaboration mention "
        "does not by itself create a secondary family."
    )
    return "\n".join(parts)


def _secondary_choice(
    description: str,
    primary_family: str,
    structured: Any,
    *,
    truncated: bool,
) -> tuple[str, str | None, str, list[str]] | None:
    """A second canonical family, or None when the overlap is thin or absent."""
    if truncated or primary_family in _NO_SECONDARY:
        return None
    hits = _phrase_hits(description)
    ranked: list[tuple[str, str | None, list[str], str | None]] = []
    for family, by_sub in hits.items():
        if family == primary_family or family in _NO_SECONDARY:
            continue
        phrases = [phrase for group in by_sub.values() for phrase in group]
        support = _structured_support(structured, family)
        if len(phrases) < 2 and not (phrases and support):
            continue
        best_sub = sorted(by_sub, key=lambda name: (-len(by_sub[name]), name))[0]
        ranked.append((family, best_sub, phrases, support))
    if not ranked:
        return None
    family, subfamily, phrases, support = sorted(
        ranked,
        key=lambda item: (-len(item[2]), item[0]),
    )[0]
    if len(phrases) >= 3:
        confidence = "high"
    elif len(phrases) >= 2:
        confidence = "medium"
    else:
        confidence = "low"
    evidence = list(phrases[:3])
    if support and support not in evidence:
        evidence.append(support)
    return family, subfamily, confidence, evidence[:4]


def _with_secondary(
    result: RoleClassification,
    description: str,
    structured: Any,
    *,
    truncated: bool,
) -> RoleClassification:
    chosen = _secondary_choice(
        description,
        result.role_family,
        structured,
        truncated=truncated,
    )
    if chosen is None:
        return result
    family, subfamily, confidence, evidence = chosen
    return replace(
        result,
        role_secondary_family=family,
        role_secondary_subfamily=subfamily,
        role_secondary_confidence=confidence,
        role_secondary_evidence=evidence,
    )


def _validated_secondary(label: _ModelLabel) -> tuple[str, str | None, str, list[str]] | None:
    raw = (label.secondary_family or "").strip().upper()
    if raw in {"", * _NO_SECONDARY}:
        return None
    if raw not in PRIMARY_FAMILIES:
        return None
    subfamily = (label.secondary_subfamily or "").strip().upper() or None
    if subfamily is not None and SUBFAMILY_FAMILY.get(subfamily) != raw:
        subfamily = None
    confidence = (label.secondary_confidence or "").strip().lower()
    if confidence not in {"high", "medium", "low"}:
        confidence = "low"
    provided = [
        line.strip()
        for line in label.secondary_evidence
        if line and line.strip()
        and not re.search(r"\b(candidate|vikash|fit score|resume)\b", line, re.IGNORECASE)
    ]
    if provided and all(_is_interaction(line) for line in provided):
        return None
    evidence = [line for line in provided if not _is_interaction(line)][:4]
    if not evidence:
        evidence = [_EVIDENCE.get(subfamily or raw, _EVIDENCE["UNKNOWN"])]
    return raw, subfamily, confidence, evidence


def _deterministic(
    title: str,
    description: str,
    content_hash: str | None,
    structured: Any = None,
    *,
    truncated: bool = False,
) -> tuple[RoleClassification | None, bool]:
    """Return (classification, needs_llm). needs_llm is unused when classification is set."""
    if len(description.strip()) < 80:
        return (
            _unknown(
                content_hash,
                "Description is missing or too short to classify the role.",
            ),
            False,
        )
    jd = description.lower()
    title_l = title.lower()
    scores: dict[str, int] = {}
    _score_blob(jd, 3, scores)
    _score_blob(title_l, 2, scores)

    if any(phrase in jd for phrase in _FINANCE) or any(phrase in title_l for phrase in _FINANCE):
        for subfamily in list(scores):
            if SUBFAMILY_FAMILY.get(subfamily) == "STRATEGY_TRANSFORMATION":
                scores.pop(subfamily, None)
        scores["OTHER"] = scores.get("OTHER", 0) + 6
    if any(phrase in title_l for phrase in _OUTSIDE_TITLE) or "write production software" in jd:
        scores["OTHER"] = scores.get("OTHER", 0) + 6
    if any(phrase in title_l or phrase in jd for phrase in _SALES):
        scores["OTHER"] = scores.get("OTHER", 0) + 6
    if any(phrase in jd for phrase in _INTERNAL) and not any(phrase in jd for phrase in _CLIENT):
        for subfamily in list(scores):
            if SUBFAMILY_FAMILY.get(subfamily) == "CONSULTING":
                scores.pop(subfamily, None)
    _separate_technology_and_marketing(jd, title_l, scores)

    if not scores:
        if len(description.strip()) < 80:
            return (
                _unknown(
                    content_hash,
                    "Description is missing or too short to classify the role.",
                ),
                False,
            )
        return None, True

    ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    winner, top = ranked[0]
    second = ranked[1][1] if len(ranked) > 1 else 0
    if top < 2 or top == second:
        return None, True
    if winner == "OTHER":
        family, subfamily = "OTHER", None
        evidence = [_EVIDENCE["OTHER"]]
    else:
        family = SUBFAMILY_FAMILY[winner]
        subfamily = winner
        evidence = [_EVIDENCE[winner]]
    margin = top - second
    if top >= 6 and margin >= 3:
        confidence = "high"
    elif top >= 4 and margin >= 2:
        confidence = "medium"
    else:
        confidence = "low"
    decided = _result(family, subfamily, confidence, evidence, content_hash)
    return _with_secondary(decided, description, structured, truncated=truncated), False


def _parse_model(payload: str, content_hash: str | None) -> RoleClassification:
    text = payload.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE).strip()
    try:
        data: Any = json.loads(text)
        label = _ModelLabel.model_validate(data)
    except (json.JSONDecodeError, ValidationError):
        return _unknown(content_hash, "Classifier returned a label outside the taxonomy.")
    family = label.primary_family.strip().upper()
    subfamily = label.subfamily.strip().upper() if label.subfamily else None
    if subfamily == "":
        subfamily = None
    evidence = [
        line
        for line in label.evidence
        if not re.search(r"\b(candidate|vikash|fit score|resume)\b", line, re.IGNORECASE)
    ]
    decided = _result(
        family,
        subfamily,
        label.confidence.strip().lower(),
        evidence,
        content_hash,
        used_llm=True,
    )
    if decided.role_family == "UNKNOWN":
        return decided
    secondary = _validated_secondary(label)
    if secondary is None or secondary[0] == decided.role_family:
        return decided
    family_name, subfamily_name, confidence, secondary_evidence = secondary
    return replace(
        decided,
        role_secondary_family=family_name,
        role_secondary_subfamily=subfamily_name,
        role_secondary_confidence=confidence,
        role_secondary_evidence=secondary_evidence,
    )


async def classify_role(
    *,
    title: str,
    description: str,
    content_hash: str | None,
    discovery_family: str | None = None,
    discovery_bucket: str | None = None,
    discovery_query: str | None = None,
    client: LLMClient | None = None,
    model: str | None = None,
    truncated: bool = False,
    structured: Any = None,
) -> RoleClassification:
    """Classify the role from the posting. Discovery labels are not copied across."""
    del discovery_family, discovery_bucket, discovery_query
    decided, needs_llm = _deterministic(
        title,
        description,
        content_hash,
        structured,
        truncated=truncated,
    )
    if truncated and needs_llm:
        return _unknown(
            content_hash,
            "Description is truncated and does not identify the role.",
        )
    if decided is not None and not needs_llm:
        return decided
    if client is None or len(description.strip()) < 80:
        return _unknown(
            content_hash,
            "Description is missing or too short to classify the role.",
        )
    structured_text = _structured_prompt(structured)
    user = (
        f"Title: {title}\n"
        f"Description:\n{description[:8000]}\n"
        "Discovery labels are context only and must not override the description."
    )
    if structured_text:
        user = f"{user}\n{structured_text}"
    try:
        raw = await client.complete(
            model=model or "role-classifier",
            system_blocks=[{"type": "text", "text": _CLASSIFY_SYSTEM}],
            user=user,
            max_tokens=512,
            temperature=0,
            json_mode=True,
        )
    except Exception:
        return _unknown(content_hash, "Classifier returned a label outside the taxonomy.")
    parsed = _parse_model(raw, content_hash)
    if parsed.role_family == "UNKNOWN" and "outside the taxonomy" in parsed.role_evidence[0]:
        return parsed
    return parsed

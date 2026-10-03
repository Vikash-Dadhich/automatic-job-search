"""Decide whether a vector-gate reject may enter the normal scorer.

This does not score fit, rank priority, or change the cosine threshold.
A job comes back only when several independent pieces of evidence agree.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from config.profile import Profile
from core.db import Job
from scraper.filters import evaluate_job

RECOVERY_VERSION = "phase10-v2"
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "vector_recovery.yaml"
_ROLE_GROUPS = ("primary_role", "secondary_role", "responsibility_function")
_CONFIDENCE = frozenset({"high", "medium", "low"})
_NOT_TARGETS = frozenset({"UNKNOWN", "OTHER"})
_KNOWN_FAMILIES = frozenset(
    {
        "PRODUCT_MANAGEMENT",
        "CONSULTING",
        "STRATEGY_TRANSFORMATION",
        "PRODUCT_MARKETING",
        "MARKETING",
        "PROGRAM_PROJECT_OPERATIONS",
    }
)


@dataclass(frozen=True, slots=True)
class RecoveryDecision:
    recovered: bool
    decision: str
    reason: str
    input_hash: str


def _require_int(name: str, value: object, *, lower: int, upper: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < lower or value > upper:
        raise ValueError(f"{name} must be an integer from {lower} through {upper}")
    return value


def _phrases(value: object) -> tuple[str, ...]:
    if not isinstance(value, list) or not value or not all(isinstance(item, str) for item in value):
        raise ValueError("responsibility_phrases must be a non-empty list of phrases")
    phrases: list[str] = []
    for item in value:
        text = " ".join(item.split())
        if " " not in text:
            raise ValueError(f"responsibility phrase must contain more than one word: {text}")
        phrases.append(text)
    return tuple(phrases)


def _names(value: object, *, allowed: frozenset[str], label: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{label} must be a non-empty list of names")
    names = tuple(item.strip() for item in value)
    unknown = [item for item in names if item not in allowed]
    if unknown:
        raise ValueError(f"{label} has unknown names: {', '.join(unknown)}")
    return names


def _validate(raw: object) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ValueError("vector recovery config must be a mapping")
    if raw.get("version") != RECOVERY_VERSION:
        raise ValueError(f"vector recovery version must be {RECOVERY_VERSION}")
    block = raw.get("recovery")
    if not isinstance(block, dict):
        raise ValueError("vector recovery config must set a recovery block")
    expected = {
        "enabled",
        "min_groups",
        "role_confidences",
        "target_families",
        "responsibility_phrases",
    }
    if set(block) != expected:
        raise ValueError("vector recovery config has unexpected or missing keys")
    if not isinstance(block["enabled"], bool):
        raise ValueError("recovery.enabled must be true or false")
    families = _names(block["target_families"], allowed=_KNOWN_FAMILIES, label="target_families")
    if any(item in _NOT_TARGETS for item in families):
        raise ValueError("UNKNOWN and OTHER are not recovery targets")
    confidences = _names(
        block["role_confidences"],
        allowed=_CONFIDENCE,
        label="role_confidences",
    )
    return {
        "version": RECOVERY_VERSION,
        "recovery": {
            "enabled": block["enabled"],
            "min_groups": _require_int("min_groups", block["min_groups"], lower=1, upper=4),
            "role_confidences": confidences,
            "target_families": families,
            "responsibility_phrases": _phrases(block["responsibility_phrases"]),
        },
    }


@lru_cache
def load_recovery_config(path: str | None = None) -> dict[str, Any]:
    target = Path(path) if path else CONFIG_PATH
    with target.open(encoding="utf-8") as handle:
        raw: Any = yaml.safe_load(handle)
    return _validate(raw)


def config_hash(config: dict[str, Any] | None = None) -> str:
    payload = config if config is not None else load_recovery_config()
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def _compiled(phrases: tuple[str, ...]) -> tuple[re.Pattern[str], ...]:
    return tuple(re.compile(rf"\b{re.escape(phrase)}\b", re.IGNORECASE) for phrase in phrases)


def recovery_input_hash(
    job: Job,
    *,
    structured_hash: str | None,
    structured_version: str | None,
    config: dict[str, Any] | None = None,
) -> str:
    """Identity of the recovery rule and the inputs it reads."""
    active = config if config is not None else load_recovery_config()
    payload = {
        "version": RECOVERY_VERSION,
        "config": config_hash(active),
        "role_family": job.role_family,
        "role_confidence": job.role_confidence,
        "role_evidence": job.role_evidence,
        "role_secondary_family": job.role_secondary_family,
        "role_secondary_confidence": job.role_secondary_confidence,
        "role_secondary_evidence": job.role_secondary_evidence,
        "role_classifier_version": job.role_classifier_version,
        "eligibility_state": job.eligibility_state,
        "structured_hash": structured_hash,
        "structured_version": structured_version,
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode()).hexdigest()


def _confidence(value: str | None, allowed: tuple[str, ...]) -> bool:
    return (value or "").strip().lower() in allowed


def _family_group(
    family: str | None,
    confidence: str | None,
    evidence: list[str] | None,
    *,
    targets: tuple[str, ...],
    allowed: tuple[str, ...],
) -> bool:
    name = (family or "").strip()
    if name not in targets or name in _NOT_TARGETS:
        return False
    if not _confidence(confidence, allowed):
        return False
    return bool(evidence)


def _responsibility_group(
    document: dict[str, Any] | None,
    patterns: tuple[re.Pattern[str], ...],
) -> bool:
    if not document:
        return False
    block = document.get("responsibilities")
    if not isinstance(block, dict):
        return False
    items = block.get("items")
    if not isinstance(items, list):
        return False
    for item in items:
        if not isinstance(item, dict):
            continue
        text = item.get("text")
        if isinstance(text, str) and any(pattern.search(text) for pattern in patterns):
            return True
    return False


def _mba_program(document: dict[str, Any] | None) -> bool:
    if not document:
        return False
    program = document.get("program")
    if not isinstance(program, dict):
        return False
    return program.get("mba_internship") is True


def _reason(fired: list[str], *, recovered: bool) -> str:
    if recovered:
        return "+".join(fired)
    if not fired:
        return "insufficient_evidence"
    return "insufficient_evidence:" + "+".join(fired)


def evaluate_recovery(
    job: Job,
    profile: Profile,
    *,
    document: dict[str, Any] | None = None,
    structured_hash: str | None = None,
    structured_version: str | None = None,
    config: dict[str, Any] | None = None,
) -> RecoveryDecision:
    """Return whether this vector reject may be scored. Never raises for job data."""
    active = config if config is not None else load_recovery_config()
    digest = recovery_input_hash(
        job,
        structured_hash=structured_hash,
        structured_version=structured_version,
        config=active,
    )
    rules = active["recovery"]
    if not rules["enabled"]:
        return RecoveryDecision(False, "rejected", "disabled", digest)
    if not evaluate_job(job, profile).passed:
        return RecoveryDecision(False, "rejected", "hard_filter", digest)
    if job.eligibility_state == "CLEARLY_INELIGIBLE":
        return RecoveryDecision(False, "rejected", "clearly_ineligible", digest)

    targets = tuple(rules["target_families"])
    allowed = tuple(rules["role_confidences"])
    groups = {
        "primary_role": _family_group(
            job.role_family,
            job.role_confidence,
            job.role_evidence,
            targets=targets,
            allowed=allowed,
        ),
        "secondary_role": _family_group(
            job.role_secondary_family,
            job.role_secondary_confidence,
            job.role_secondary_evidence,
            targets=targets,
            allowed=allowed,
        ),
        "responsibility_function": _responsibility_group(
            document,
            _compiled(tuple(rules["responsibility_phrases"])),
        ),
        "mba_program": _mba_program(document),
    }
    fired = sorted(name for name, present in groups.items() if present)
    role_support = any(name in fired for name in _ROLE_GROUPS)
    recovered = role_support and len(fired) >= int(rules["min_groups"])
    decision = "recovered" if recovered else "rejected"
    return RecoveryDecision(recovered, decision, _reason(fired, recovered=recovered), digest)

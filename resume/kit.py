"""Application kit for a queued job: which resume, a deadline, and two drafted answers.

Only queued jobs get a kit, so the model cost stays tied to the daily cap. Answers
reuse the grounded resolver: facts come from the profile, never from the model.
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Any

import structlog
import yaml

from automation.answers import AnswerResolver, AnswerSource, answers_to_payload
from config.profile import load_profile
from config.settings import get_settings
from core.db import Job

log = structlog.get_logger(__name__)

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "resume_versions.yaml"
KIT_QUESTIONS = (
    "Why are you interested in this role and company?",
    "Describe your most relevant experience for this role.",
)

_MONTH = (
    r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|"
    r"aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
)
_DEADLINE = re.compile(
    rf"(?:apply\s+by|applications?\s+(?:close|due)(?:\s+on)?|deadline(?:\s+is|\s+to\s+apply)?|"
    rf"closing\s+date|close\s+date)[:\s-]*"
    rf"(?:on\s+)?({_MONTH}\.?\s+\d{{1,2}}(?:st|nd|rd|th)?(?:,?\s+\d{{4}})?)",
    re.IGNORECASE,
)


@lru_cache
def _load(path: str | None = None) -> dict[str, Any]:
    with Path(path or CONFIG_PATH).open(encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)
    if not isinstance(raw, dict) or not isinstance(raw.get("versions"), dict):
        raise ValueError("resume_versions.yaml must set default and versions")
    default = raw.get("default")
    if not isinstance(default, str) or not default.strip():
        raise ValueError("resume_versions.yaml must set a default name")
    versions = {str(key): str(value) for key, value in raw["versions"].items()}
    return {"default": default.strip(), "versions": versions}


def resume_label(role_family: str | None, *, path: str | None = None) -> str:
    config = _load(path)
    return config["versions"].get((role_family or "").strip(), config["default"])


def find_deadline(text: str | None) -> str | None:
    """A deadline only when the posting states one in plain words. Otherwise None."""
    if not text:
        return None
    match = _DEADLINE.search(text)
    return match.group(1).strip() if match else None


def has_kit(job: Job) -> bool:
    payload = job.application_answers
    return bool(isinstance(payload, dict) and payload.get("items"))


async def build_answers(job: Job, resolver: AnswerResolver | None = None) -> dict[str, Any] | None:
    """Draft the kit answers. Returns None when the model is unavailable or says nothing."""
    if resolver is None:
        if not get_settings().openai_api_key:
            return None
        resolver = AnswerResolver(load_profile())
    answers = [
        await resolver.resolve(question, job=job, force_llm=True) for question in KIT_QUESTIONS
    ]
    usable = [item for item in answers if item.source == AnswerSource.llm and item.answer]
    if not usable:
        return None
    return answers_to_payload(usable)


def kit_lines(job: Job) -> list[str]:
    """Lines for the queue card. The answers themselves follow in a second message."""
    lines = [f"Resume: {resume_label(job.role_family)}"]
    deadline = find_deadline(job.description_clean)
    if deadline:
        lines.append(f"Deadline: {deadline}")
    return lines

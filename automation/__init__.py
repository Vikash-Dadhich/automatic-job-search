"""Workday application automation (Step 5)."""

from __future__ import annotations

from automation.answers import AnswerResolver, AnswerSource, ResolvedAnswer, answers_to_payload
from automation.login import save_session
from automation.runner import ApplySummary, apply_pending
from automation.workday import Applicator, ApplyResult, BlockerError, WorkdayApplicator

__all__ = [
    "AnswerResolver",
    "AnswerSource",
    "Applicator",
    "ApplyResult",
    "ApplySummary",
    "BlockerError",
    "ResolvedAnswer",
    "WorkdayApplicator",
    "answers_to_payload",
    "apply_pending",
    "save_session",
]

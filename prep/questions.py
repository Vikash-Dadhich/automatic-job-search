"""Standard question bank for LinkedIn/Indeed application prep packs."""

from __future__ import annotations

# Answered deterministically from profile.yaml via AnswerResolver.
IDENTITY_QUESTIONS: tuple[str, ...] = (
    "First name",
    "Last name",
    "Email",
    "Phone",
    "City",
    "LinkedIn URL",
    "Are you legally authorized to work in the US?",
    "Will you now or in the future require visa sponsorship?",
    "Are you willing to relocate?",
    "Are you open to remote work?",
    "School",
    "Degree",
)

# Routed to the writer LLM (open-ended), grounded in profile + JD.
ESSAY_QUESTIONS: tuple[str, ...] = (
    "Why are you interested in this role?",
    "Why do you want to work at this company?",
    "Describe your relevant experience for this role.",
    "Tell us about what makes you a strong fit for this role.",
    "Write a short cover letter for this role.",
)

# Reminders the agent cannot ground — fill manually when applying.
MANUAL_FILL: tuple[str, ...] = (
    "Desired / expected salary (or range)",
    "Years of relevant experience (exact number if asked)",
    "Earliest start date / notice period",
    "Any employer-specific custom questions not listed above",
)

ALL_RESOLVED_QUESTIONS: tuple[str, ...] = IDENTITY_QUESTIONS + ESSAY_QUESTIONS

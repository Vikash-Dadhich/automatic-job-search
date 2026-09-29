"""Pydantic schemas for LLM scoring output."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from core.db import Tier

# Gemini structured-output contract; keeps the model from emitting prose.
SCORE_JSON_SCHEMA: dict[str, object] = {
    "type": "OBJECT",
    "properties": {
        "s": {"type": "INTEGER", "description": "Fit score 0-100"},
        "t": {"type": "INTEGER", "description": "Tier hint: 1, 2, or 3"},
        "r": {
            "type": "ARRAY",
            "items": {"type": "STRING"},
            "description": "2-4 concise reasons",
        },
    },
    "required": ["s", "r"],
}


class ScoreRaw(BaseModel):
    """Tolerant raw score payload from the model: {"s","t","r"}."""

    s: int = Field(description="Fit score 0-100")
    t: int | None = Field(default=None, description="Model's tier hint 1|2|3")
    r: list[str] = Field(default_factory=list, description="Concise reasons")

    @field_validator("s", mode="before")
    @classmethod
    def clamp_score(cls, value: object) -> int:
        # A non-numeric score means the model misbehaved; surfacing it as an error
        # beats silently scoring 0 and filing a good job under Tier 3.
        try:
            score = int(value)  # type: ignore[arg-type]
        except (TypeError, ValueError) as exc:
            raise ValueError(f"score 's' is not an integer: {value!r}") from exc
        return max(0, min(100, score))

    @field_validator("t", mode="before")
    @classmethod
    def normalize_tier_hint(cls, value: object) -> int | None:
        if value is None or value == "":
            return None
        try:
            hint = int(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return None
        if hint in (1, 2, 3):
            return hint
        return None

    @field_validator("r", mode="before")
    @classmethod
    def normalize_reasons(cls, value: object) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            text = value.strip()
            return [text] if text else []
        if isinstance(value, list):
            out: list[str] = []
            for item in value:
                text = str(item).strip()
                if text:
                    out.append(text[:240])
            return out[:5]
        return [str(value).strip()[:240]]


class Evaluation(BaseModel):
    """Normalized evaluation ready to persist on a Job row."""

    score: int = Field(ge=0, le=100)
    tier: Tier
    reasons: list[str] = Field(default_factory=list)
    outreach: str | None = None
    cover_letter: str | None = None
    # False when the JD is too thin or the fit payload is unusable. Score is not a fit.
    fit_available: bool = True
    fit_confidence: str | None = None
    fit_strengths: list[str] = Field(default_factory=list)
    fit_gaps: list[str] = Field(default_factory=list)
    fit_evidence: list[str] = Field(default_factory=list)
    fit_dimensions: dict[str, object] = Field(default_factory=dict)
    fit_content_hash: str | None = None
    fit_profile_hash: str | None = None

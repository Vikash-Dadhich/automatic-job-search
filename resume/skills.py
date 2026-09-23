"""JD skill extraction and cross-JD aggregation for the two-tier resume flow.

Per-JD extraction prefers the LLM but always degrades to a deterministic
frequency ranker, so baseline building never depends on a live API key.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from enum import StrEnum
from typing import TYPE_CHECKING, Any

import structlog
from pydantic import BaseModel, Field, field_validator

from config.settings import get_settings
from core.db import Job
from core.token_optimizer import minify_job

if TYPE_CHECKING:
    from scorer.clients import LLMClient
else:  # Runtime alias keeps `from resume.skills import LLMClient` working.
    LLMClient = Any

log = structlog.get_logger(__name__)

_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)```", re.IGNORECASE)
_TOKEN_RE = re.compile(r"[a-z][a-z0-9+#.\-]{1,}", re.IGNORECASE)
_MAX_SKILLS = 15

SKILLS_SYSTEM = """\
You extract the concrete skills a job description actually screens for.
Return ONLY a JSON array, no prose, no markdown fence.
Each element: {"name": str, "category": "hard"|"soft"|"tool"|"domain", "importance": 1-5}
Rules: at most 15 items, no duplicates, prefer nouns as written in the posting,
skip generic filler ("team player", "fast-paced"), and never invent technologies
the posting does not mention.
"""

# Terms that look frequent but carry no signal about what the role screens for.
_STOPWORDS = frozenset(
    """
    the and for with you our are will that this from have has had not but any all can
    who your their its they them was were been being able about into over under more
    most other such than then there these those what when where which while who's
    work working works experience experiences year years job jobs role roles position
    positions team teams company companies business businesses candidate candidates
    applicant applicants employee employees employer employers opportunity benefits
    required require requires requirement requirements responsibility responsibilities
    qualification qualifications preferred preferences skill skills ability abilities
    strong excellent good great new high highly well also may must should would could
    per via etc including include includes included using use used uses need needs
    plus bonus nice want wants looking look seeking seek join joining help helps
    across within through during before after between each every both some many few
    how why one two three four five ability environment environments culture mission
    apply application applications please contact email phone resume cover letter
    equal opportunity employer diversity inclusion veteran disability status race
    gender sexual orientation religion national origin compensation salary range
    full time part remote hybrid onsite office location locations day days week weeks
    month months hour hours support supporting supports provide providing provides
    ensure ensuring ensures drive driving drives lead leading leads manage managing
    manages build building builds create creating creates develop developing develops
    partner partners partnering deliver delivering delivers own owns owning
    degree degrees bachelor bachelors masters phd advanced relevant demonstrated
    detail details detail-oriented preferred qualifications basic minimum must
    years yrs employment information content video prime platform customer
    """.split()
)

# Boost known skill vocabulary so it outranks incidental repetition.
_SKILL_LEXICON = frozenset(
    """
    python java javascript typescript golang rust ruby scala kotlin swift php sql
    nosql postgres postgresql mysql mongodb redis snowflake databricks bigquery
    kafka spark airflow dbt hadoop kubernetes docker terraform ansible jenkins
    aws azure gcp lambda serverless microservices api apis rest graphql grpc
    react angular vue node django flask fastapi rails spring express
    tableau looker powerbi excel figma jira confluence amplitude mixpanel segment
    analytics experimentation roadmap roadmapping prioritization discovery
    stakeholder stakeholders agile scrum kanban okrs kpis metrics forecasting
    machine-learning ml ai llm nlp pytorch tensorflow pandas numpy
    git ci cd devops observability datadog splunk
    pricing monetization retention acquisition onboarding segmentation
    product-management product-strategy go-to-market gtm a/b-testing ab-testing
    user-research wireframing prototyping payments ecommerce oauth postman swagger
    """.split()
)


class SkillCategory(StrEnum):
    hard = "hard"
    soft = "soft"
    tool = "tool"
    domain = "domain"


class JdSkill(BaseModel):
    """One skill demanded by a single job description."""

    name: str
    category: SkillCategory = SkillCategory.hard
    importance: int = Field(default=3, ge=1, le=5)

    @field_validator("name", mode="before")
    @classmethod
    def clean_name(cls, value: object) -> str:
        return re.sub(r"\s+", " ", str(value or "").strip())

    @field_validator("category", mode="before")
    @classmethod
    def coerce_category(cls, value: object) -> SkillCategory:
        text = str(value or "").strip().lower()
        try:
            return SkillCategory(text)
        except ValueError:
            return SkillCategory.hard

    @field_validator("importance", mode="before")
    @classmethod
    def clamp_importance(cls, value: object) -> int:
        try:
            score = int(float(str(value)))
        except (TypeError, ValueError):
            return 3
        return max(1, min(5, score))


class AggregatedSkill(BaseModel):
    """A skill summarized across many JDs for one target role."""

    name: str
    category: SkillCategory = SkillCategory.hard
    prevalence_pct: float = Field(ge=0, le=100)
    avg_importance: float = Field(ge=0, le=5)
    mention_count: int = Field(ge=0)

    @property
    def weight(self) -> float:
        return self.prevalence_pct * self.avg_importance


class RoleSkillProfile(BaseModel):
    """Aggregated skill demand for a role, used to build the baseline resume."""

    role: str
    jd_count: int = Field(default=0, ge=0)
    skills: list[AggregatedSkill] = Field(default_factory=list)


def _repair_truncated_json_array(text: str) -> str:
    """Close a truncated JSON array so partial skill lists still parse."""
    cleaned = text.strip()
    if not cleaned.startswith("["):
        return cleaned
    if cleaned.endswith("]"):
        return cleaned
    # Drop a trailing incomplete object / string, then close the array.
    last_brace = cleaned.rfind("}")
    if last_brace == -1:
        return "[]"
    return cleaned[: last_brace + 1] + "]"


def parse_skills_json(raw: str) -> list[JdSkill]:
    """Parse a JSON skill array from model output; tolerant of fences and dupes."""
    if not raw or not raw.strip():
        return []
    text = raw.strip()
    fence = _FENCE_RE.search(text)
    if fence:
        text = fence.group(1).strip()
    if not text.startswith("["):
        start = text.find("[")
        end = text.rfind("]")
        if start == -1:
            return []
        text = text[start:] if end <= start else text[start : end + 1]

    candidates = [text, _repair_truncated_json_array(text)]
    data: list[Any] | None = None
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, list):
            data = parsed
            break
    if data is None:
        return []

    out: list[JdSkill] = []
    seen: set[str] = set()
    for item in data:
        if isinstance(item, str):
            item = {"name": item}
        if not isinstance(item, dict):
            continue
        try:
            skill = JdSkill.model_validate(item)
        except ValueError:
            continue
        key = skill.name.lower()
        if not key or key in seen:
            continue
        # Drop single-token filler that slipped past the model ("degree", "relevant").
        if " " not in skill.name and key in _STOPWORDS and key not in _SKILL_LEXICON:
            continue
        seen.add(key)
        out.append(skill)
    return out[:_MAX_SKILLS]


def _categorize(term: str) -> SkillCategory:
    if term in _SKILL_LEXICON:
        return SkillCategory.tool if not term.isalpha() or len(term) <= 12 else SkillCategory.hard
    return SkillCategory.hard


def extract_top_skills_deterministic(job: Job, *, top_n: int = 12) -> list[JdSkill]:
    """Offline fallback: rank repeated, non-filler terms from the posting."""
    text = f"{job.title or ''}\n{job.description_clean or ''}"
    tokens = [t.lower() for t in _TOKEN_RE.findall(text)]
    counts = Counter(
        token for token in tokens if len(token) > 2 and token not in _STOPWORDS
    )
    if not counts:
        return []

    def rank(pair: tuple[str, int]) -> tuple[float, str]:
        term, freq = pair
        boost = 2.0 if term in _SKILL_LEXICON else 0.0
        return (-(freq + boost), term)

    ranked = sorted(counts.items(), key=rank)[: max(1, top_n)]
    top_freq = max(freq for _, freq in ranked)

    skills: list[JdSkill] = []
    for term, freq in ranked:
        # Scale raw frequency into the 1-5 importance band.
        importance = 1 + round(4 * (freq / top_freq)) if top_freq else 3
        skills.append(
            JdSkill(
                name=term,
                category=_categorize(term),
                importance=max(1, min(5, importance)),
            )
        )
    return skills


async def extract_top_skills(
    job: Job,
    *,
    client: LLMClient | None = None,
    model: str | None = None,
    top_n: int = 12,
) -> list[JdSkill]:
    """Extract per-JD skills via LLM, falling back to the deterministic ranker."""
    if client is None:
        return extract_top_skills_deterministic(job, top_n=top_n)

    settings = get_settings()
    # Skill arrays are longer than score JSON; give thinking headroom so the
    # array is not truncated mid-object (which previously forced the noisy
    # deterministic fallback on every live Gemini call).
    skill_max_tokens = max(settings.score_max_tokens, 2048)
    try:
        raw = await client.complete(
            model=model or settings.active_scorer_model,
            system_blocks=[{"type": "text", "text": SKILLS_SYSTEM}],
            user=minify_job(job),
            max_tokens=skill_max_tokens,
            temperature=0.0,
            json_mode=True,
            thinking_level=settings.gemini_scorer_thinking_level,
        )
        skills = parse_skills_json(raw)
    except Exception as exc:
        log.warning("skill_extract_failed", job_id=job.id, error=str(exc)[:200])
        skills = []

    if not skills:
        log.warning("skill_extract_empty_fallback", job_id=job.id)
        return extract_top_skills_deterministic(job, top_n=top_n)
    return skills[:top_n]


def aggregate_role_skills(
    per_jd: list[list[JdSkill]],
    *,
    role: str,
    top_n: int = 15,
) -> RoleSkillProfile:
    """Roll per-JD skills into prevalence-weighted role demand."""
    jd_count = len(per_jd)
    if jd_count == 0:
        return RoleSkillProfile(role=role, jd_count=0, skills=[])

    mentions: dict[str, int] = Counter()
    importances: dict[str, list[int]] = {}
    spellings: dict[str, Counter[str]] = {}
    categories: dict[str, Counter[SkillCategory]] = {}

    for jd_skills in per_jd:
        # Count each skill once per JD so a repeated mention cannot inflate prevalence.
        seen_in_jd: set[str] = set()
        for skill in jd_skills:
            key = skill.name.strip().lower()
            if not key or key in seen_in_jd:
                continue
            seen_in_jd.add(key)
            mentions[key] += 1
            importances.setdefault(key, []).append(skill.importance)
            spellings.setdefault(key, Counter())[skill.name.strip()] += 1
            categories.setdefault(key, Counter())[skill.category] += 1

    aggregated: list[AggregatedSkill] = []
    for key, count in mentions.items():
        scores = importances.get(key) or [3]
        aggregated.append(
            AggregatedSkill(
                name=spellings[key].most_common(1)[0][0],
                category=categories[key].most_common(1)[0][0],
                prevalence_pct=round(100.0 * count / jd_count, 1),
                avg_importance=round(sum(scores) / len(scores), 2),
                mention_count=count,
            )
        )

    aggregated.sort(key=lambda s: (-s.weight, -s.mention_count, s.name.lower()))
    return RoleSkillProfile(role=role, jd_count=jd_count, skills=aggregated[:top_n])

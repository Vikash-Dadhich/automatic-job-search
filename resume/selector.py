"""Deterministic JD-aware bullet and skill selection for resume tailoring."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from config.profile import Profile
from core.db import Job

_STOPWORDS = frozenset(
    {
        "a",
        "an",
        "the",
        "and",
        "or",
        "of",
        "to",
        "in",
        "for",
        "on",
        "with",
        "at",
        "by",
        "from",
        "as",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "must",
        "can",
        "this",
        "that",
        "these",
        "those",
        "it",
        "its",
        "you",
        "your",
        "we",
        "our",
        "they",
        "their",
        "i",
        "me",
        "my",
        "not",
        "no",
        "yes",
        "if",
        "than",
        "then",
        "so",
        "such",
        "into",
        "over",
        "under",
        "about",
        "across",
        "between",
        "through",
        "during",
        "before",
        "after",
        "above",
        "below",
        "up",
        "down",
        "out",
        "off",
        "again",
        "further",
        "once",
        "here",
        "there",
        "when",
        "where",
        "why",
        "how",
        "all",
        "each",
        "few",
        "more",
        "most",
        "other",
        "some",
        "any",
        "both",
        "own",
        "same",
        "too",
        "very",
        "just",
        "also",
        "only",
        "job",
        "role",
        "team",
        "work",
        "working",
        "experience",
        "years",
        "year",
        "including",
        "using",
        "used",
        "use",
        "well",
        "strong",
        "preferred",
        "required",
        "requirements",
        "responsibilities",
        "qualifications",
        "ability",
        "able",
        "etc",
    }
)

# Tokens may include tech punctuation: c++, c#, node.js, .net
_TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9+#.]*(?:\+\+|#)?", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class RankedBullet:
    exp_index: int
    bullet_index: int
    text: str
    score: float


@dataclass
class SelectedExperience:
    title: str
    company: str
    location: str
    start_date: str
    end_date: str
    bullets: list[str] = field(default_factory=list)


def extract_job_terms(job: Job) -> set[str]:
    """Lowercase tokens + bigrams from title and cleaned description."""
    text = f"{job.title or ''}\n{job.description_clean or ''}".lower()
    tokens = [t.lower() for t in _TOKEN_RE.findall(text) if len(t) > 1]
    unigrams = {t for t in tokens if t not in _STOPWORDS}
    bigrams: set[str] = set()
    for i in range(len(tokens) - 1):
        a, b = tokens[i], tokens[i + 1]
        if a in _STOPWORDS or b in _STOPWORDS:
            continue
        bigrams.add(f"{a} {b}")
    return unigrams | bigrams


def _skill_terms(profile: Profile) -> set[str]:
    terms: set[str] = set()
    for skill in profile.skills:
        s = skill.lower().strip()
        if not s:
            continue
        terms.add(s)
        for tok in _TOKEN_RE.findall(s):
            if tok.lower() not in _STOPWORDS and len(tok) > 1:
                terms.add(tok.lower())
    return terms


def score_bullet(bullet: str, terms: set[str], skill_terms: set[str]) -> float:
    """Overlap score; matches that are also candidate skills weigh more."""
    if not bullet or not terms:
        return 0.0
    lower = bullet.lower()
    bullet_tokens = {
        t.lower() for t in _TOKEN_RE.findall(lower) if t.lower() not in _STOPWORDS
    }
    score = 0.0
    for term in terms:
        if " " in term:
            if term in lower:
                score += 2.0
                if term in skill_terms:
                    score += 1.5
        elif term in bullet_tokens or term in lower:
            score += 1.0
            if term in skill_terms:
                score += 1.0
    return score


def select_bullets(
    profile: Profile,
    job: Job,
    *,
    min_n: int = 4,
    max_n: int = 6,
) -> list[SelectedExperience]:
    """Pick top 4–6 verified bullets matching the job; regroup under experiences."""
    terms = extract_job_terms(job)
    skills = _skill_terms(profile)

    ranked: list[RankedBullet] = []
    for ei, exp in enumerate(profile.experience):
        for bi, bullet in enumerate(exp.bullets):
            ranked.append(
                RankedBullet(
                    exp_index=ei,
                    bullet_index=bi,
                    text=bullet,
                    score=score_bullet(bullet, terms, skills),
                )
            )

    if not ranked:
        return []

    available = len(ranked)
    target = min(max_n, max(min(min_n, available), 1))
    # Prefer high scores; break ties by experience order then bullet order
    ranked.sort(key=lambda r: (-r.score, r.exp_index, r.bullet_index))

    selected = ranked[:target]
    # If sparse high scores leave us short of min_n, pad with most-recent-first
    if len(selected) < min(min_n, available):
        chosen_keys = {(r.exp_index, r.bullet_index) for r in selected}
        # Most recent first: reverse experience index (later entries assumed newer)
        chronological: list[RankedBullet] = sorted(
            ranked, key=lambda r: (-r.exp_index, r.bullet_index)
        )
        for r in chronological:
            if (r.exp_index, r.bullet_index) in chosen_keys:
                continue
            selected.append(r)
            chosen_keys.add((r.exp_index, r.bullet_index))
            if len(selected) >= min(min_n, available):
                break

    # Cap at max_n
    selected = selected[: min(max_n, available)]

    # Regroup under experiences, preserving original bullet order within each
    by_exp: dict[int, list[RankedBullet]] = {}
    for r in selected:
        by_exp.setdefault(r.exp_index, []).append(r)

    out: list[SelectedExperience] = []
    for ei, exp in enumerate(profile.experience):
        if ei not in by_exp:
            continue
        bullets = sorted(by_exp[ei], key=lambda r: r.bullet_index)
        out.append(
            SelectedExperience(
                title=exp.title,
                company=exp.company,
                location=exp.location,
                start_date=exp.start_date,
                end_date=exp.end_date,
                bullets=[b.text for b in bullets],
            )
        )
    return out


def reorder_skills(profile: Profile, terms: set[str]) -> list[str]:
    """JD-present skills first, then remaining profile skills."""
    matched: list[str] = []
    rest: list[str] = []
    for skill in profile.skills:
        s = skill.strip()
        if not s:
            continue
        lower = s.lower()
        tokens = {t.lower() for t in _TOKEN_RE.findall(lower)}
        if lower in terms or tokens & terms:
            matched.append(s)
        else:
            rest.append(s)
    return matched + rest


def _grounded_summary(profile: Profile, job: Job) -> str | None:
    """Short grounded summary from profile facts only (never invented)."""
    titles = [e.title for e in profile.experience[:2] if e.title]
    skills = profile.skills[:4]
    if not titles and not skills:
        return None
    parts: list[str] = []
    if titles:
        parts.append(f"{profile.identity.full_name} — {' / '.join(titles)}")
    if skills:
        parts.append(f"Skills: {', '.join(skills)}")
    target = job.title.strip() if job.title else ""
    if target:
        parts.append(f"Targeting: {target}")
    return ". ".join(parts) + "."


def build_resume_data(profile: Profile, job: Job) -> dict[str, Any]:
    """Assemble JSON payload for the Typst template."""
    terms = extract_job_terms(job)
    selected = select_bullets(profile, job)
    skills = reorder_skills(profile, terms)
    identity = profile.identity

    experience = [
        {
            "title": exp.title,
            "company": exp.company,
            "location": exp.location,
            "start": exp.start_date,
            "end": exp.end_date,
            "bullets": exp.bullets,
        }
        for exp in selected
    ]

    education = [
        {
            "degree": edu.degree,
            "field": edu.field,
            "school": edu.school,
            "location": edu.location,
            "graduation": edu.graduation_date,
            "gpa": edu.gpa,
        }
        for edu in profile.education
    ]

    return {
        "name": identity.full_name,
        "email": identity.email,
        "phone": identity.phone,
        "location": identity.location,
        "linkedin": identity.linkedin_url or "",
        "github": identity.github_url or "",
        "portfolio": identity.portfolio_url or "",
        "summary": _grounded_summary(profile, job),
        "skills": skills,
        "experience": experience,
        "education": education,
    }


# Re-export for type hints / tests
__all__ = [
    "SelectedExperience",
    "build_resume_data",
    "extract_job_terms",
    "reorder_skills",
    "score_bullet",
    "select_bullets",
]

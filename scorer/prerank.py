"""Deterministic, LLM-free pre-rank to order jobs before scoring.

Recall/cost lever: with a wide discovery funnel (many sites, deep fetch), the
scorer can face hundreds of `discovered` jobs. Scoring them in arbitrary DB
order risks spending the LLM budget on weak matches while strong ones wait.

`prerank_score` assigns a cheap heuristic score from the title/company/location
so the scoring queue is processed best-first. Combined with an optional
`SCORE_BUDGET`, this guarantees the most promising jobs are always scored even
when a per-run cap is applied — the least-promising tail is what gets deferred.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime

from config.profile import Profile
from core.db import Job, Source
from core.textmatch import company_matches

_INTERN_WORD_RE = re.compile(r"\bintern(ship)?\b", re.IGNORECASE)
_SUMMER_RE = re.compile(r"\bsummer\s*20\d{2}\b", re.IGNORECASE)

# Role families we actively target (matches the 8 search-term groups).
_ROLE_KEYWORDS = (
    "product manager",
    "product management",
    "associate product",
    "program manager",
    "project manager",
    "project management",
    "product marketing",
    "strategy",
    "consultant",
    "consulting",
    "product operations",
    "customer success",
    "go-to-market",
    "gtm",
)

# Sources whose listings tend to carry richer, first-party detail rank higher
# when all else is equal (Google is an aggregator; dedupe favors the original).
_SOURCE_WEIGHT = {
    Source.workday: 6.0,
    Source.linkedin: 4.0,
    Source.indeed: 3.0,
    Source.zip_recruiter: 2.0,
    Source.google: 1.0,
}


def prerank_score(job: Job, profile: Profile) -> float:
    """Cheap 0..~100 heuristic; higher = score sooner. No network, no LLM."""
    title = job.title or ""
    title_lower = title.lower()
    prefs = profile.preferences
    score = 0.0

    # Strongest signal: an explicit intern/internship word in the title.
    if _INTERN_WORD_RE.search(title):
        score += 40.0
    elif _SUMMER_RE.search(title) or "new grad" in title_lower or "new graduate" in title_lower:
        score += 22.0

    # Role relevance to what we actually target.
    if any(kw in title_lower for kw in _ROLE_KEYWORDS):
        score += 14.0

    # Preference-title alignment (substring either direction).
    for pref in prefs.titles:
        p = pref.lower()
        if p and (p in title_lower or title_lower in p):
            score += 16.0
            break

    # Dream-company boost (normalizes legal suffixes via company_matches).
    for dream in prefs.dream_companies:
        if company_matches(job.company, dream):
            score += 30.0
            break

    # Location preference.
    location = (job.location or "").lower()
    if location:
        on_site_prefs = [p for p in prefs.locations if p.strip().lower() != "remote"]
        if any(p.lower() in location for p in on_site_prefs):
            score += 8.0
        if prefs.remote_ok and "remote" in location:
            score += 5.0

    # Source weight.
    src = job.source if isinstance(job.source, Source) else Source(job.source)
    score += _SOURCE_WEIGHT.get(src, 1.0)

    # Recency: fresher postings first.
    posted = job.posted_at or job.discovered_at
    if posted is not None:
        posted = posted if posted.tzinfo else posted.replace(tzinfo=UTC)
        age_hours = (datetime.now(UTC) - posted).total_seconds() / 3600.0
        if age_hours <= 12:
            score += 10.0
        elif age_hours <= 24:
            score += 6.0
        elif age_hours <= 48:
            score += 3.0

    return score


def prerank_jobs(jobs: list[Job], profile: Profile) -> list[Job]:
    """Return jobs ordered best-first by ``prerank_score`` (stable on ties)."""
    return sorted(
        jobs,
        key=lambda j: (prerank_score(j, profile), -(j.id or 0)),
        reverse=True,
    )

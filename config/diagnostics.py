"""Secret-free snapshot of the candidate profile version and effective config.

The hashes identify which profile and which settings produced a run.
Raw profile text, API keys, tokens, and database URLs are not included.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from config.profile import PROFILE_PATH, Profile, load_profile
from config.settings import PROJECT_ROOT, Settings, get_settings

_DIAGNOSTIC_PATH = PROJECT_ROOT / "storage" / "diagnostics" / "effective_config.json"


def fingerprint_profile(profile: Profile) -> str:
    """SHA-256 of canonical profile facts. The raw profile is not returned."""
    payload = json.dumps(profile.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def profile_hash(path: Path | None = None) -> str:
    """SHA-256 of the parsed profile facts. Comments and key order do not matter."""
    profile_path = path or PROFILE_PATH
    return fingerprint_profile(load_profile(str(profile_path)))


def public_config(settings: Settings | None = None) -> dict[str, Any]:
    """Settings that change discovery, scoring, or delivery. No secrets."""
    settings = settings or get_settings()
    return {
        "internship_only": settings.internship_only,
        "enable_apply": settings.enable_apply,
        "enable_reviews": settings.enable_reviews,
        "enable_prep_pack": settings.enable_prep_pack,
        "prep_pack_brief": settings.prep_pack_brief,
        "prep_pack_limit": settings.prep_pack_limit,
        "enable_suggestions": settings.enable_suggestions,
        "enable_benchmark": settings.enable_benchmark,
        "enable_linkedin_scrape": settings.enable_linkedin_scrape,
        "llm_provider": settings.llm_provider,
        "scorer_model": settings.active_scorer_model,
        "writer_model": settings.active_writer_model,
        "tier_one_drafts_enabled": settings.tier_one_drafts_enabled,
        "score_budget": settings.score_budget,
        "vector_gate_enabled": settings.vector_gate_enabled,
        "embedding_model": settings.openai_embedding_model,
        "embedding_threshold": settings.vector_threshold,
        "embedding_dimensions": settings.vector_dimensions,
        "embedding_max_chars": settings.vector_max_chars,
        "max_jd_chars": settings.max_jd_chars,
        "tier_one_min_score": settings.tier_one_min_score,
        "tier_two_min_score": settings.tier_two_min_score,
        "years_experience_slack": settings.years_experience_slack,
        "max_required_years_experience": settings.max_required_years_experience,
        "enable_seniority_filter": settings.enable_seniority_filter,
        "timezone": settings.timezone,
        "schedule_times": list(settings.schedule_times),
    }


def effective_config_hash(settings: Settings | None = None) -> str:
    """SHA-256 of ``public_config``. Changes when an effective setting changes."""
    payload = json.dumps(public_config(settings), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def effective_baseline(settings: Settings | None = None) -> dict[str, Any]:
    """Profile version plus the public config used for this process."""
    config = public_config(settings)
    return {
        "profile_hash": profile_hash(),
        "effective_config_hash": effective_config_hash(settings),
        **config,
    }


def write_effective_baseline(path: Path | None = None) -> Path:
    """Write the baseline JSON. The file is gitignored runtime output."""
    target = path or _DIAGNOSTIC_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(effective_baseline(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return target

"""Per-JD skill diff against a role baseline + suggestion persistence."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import structlog

from config.profile import Profile, load_profile
from config.settings import get_settings
from core.db import (
    Job,
    RoleBaseline,
    SkillPlacement,
    SkillProvenance,
    SkillSuggestion,
    SuggestionStatus,
    get_job_by_id,
    get_role_baseline_by_role,
    get_suggestions_for_job,
    init_db,
    session_scope,
)
from resume.skills import JdSkill, LLMClient, extract_top_skills

log = structlog.get_logger(__name__)

_TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9+#.]*(?:\+\+|#)?", re.IGNORECASE)


def _norm(name: str) -> str:
    return re.sub(r"\s+", " ", name.strip().lower())


def _profile_skill_keys(profile: Profile) -> set[str]:
    keys: set[str] = set()
    for skill in profile.skills:
        s = skill.strip()
        if not s:
            continue
        keys.add(_norm(s))
        for tok in _TOKEN_RE.findall(s.lower()):
            if len(tok) > 1:
                keys.add(tok.lower())
    for exp in profile.experience:
        for bullet in exp.bullets:
            for tok in _TOKEN_RE.findall(bullet.lower()):
                if len(tok) > 1:
                    keys.add(tok.lower())
    return keys


def _baseline_skill_keys(baseline: RoleBaseline) -> set[str]:
    keys: set[str] = set()
    for entry in baseline.skills or []:
        if isinstance(entry, dict):
            name = str(entry.get("name") or "")
        else:
            name = str(entry)
        if name.strip():
            keys.add(_norm(name))
            for tok in _TOKEN_RE.findall(name.lower()):
                if len(tok) > 1:
                    keys.add(tok.lower())
    # Also cover skills already on the compiled baseline resume
    resume_skills = (baseline.resume_data or {}).get("skills") or []
    for name in resume_skills:
        if str(name).strip():
            keys.add(_norm(str(name)))
    return keys


def _skill_covered(skill: JdSkill, covered: set[str]) -> bool:
    key = _norm(skill.name)
    if key in covered:
        return True
    tokens = {t.lower() for t in _TOKEN_RE.findall(skill.name.lower()) if len(t) > 1}
    return bool(tokens & covered)


def classify_provenance(skill: JdSkill, profile: Profile) -> SkillProvenance:
    """grounded if the skill is in profile.skills or provable from bullets."""
    keys = _profile_skill_keys(profile)
    return (
        SkillProvenance.grounded
        if _skill_covered(skill, keys)
        else SkillProvenance.inferred
    )


def draft_proposed_text(
    skill: JdSkill,
    *,
    placement: SkillPlacement,
    profile: Profile,
) -> str:
    """Deterministic proposed wording for skill placement.

    For experience bullets we find the best related bullet first.
    The LLM-woven variant is generated asynchronously in `draft_proposed_text_llm`.
    """
    if placement == SkillPlacement.skills:
        return skill.name
    # Experience weave: attach to the first bullet that looks related, else a note
    key = _norm(skill.name)
    for exp in profile.experience:
        for bullet in exp.bullets:
            if key in bullet.lower() or any(
                t in bullet.lower() for t in key.split() if len(t) > 2
            ):
                return f"{bullet.rstrip('.')} (incl. {skill.name})."
    exp0 = profile.experience[0]
    return f"Applied {skill.name} in {exp0.title} work at {exp0.company}."


async def draft_proposed_text_llm(
    skill: JdSkill,
    *,
    placement: SkillPlacement,
    profile: Profile,
    client: LLMClient | None = None,
) -> str:
    """LLM-woven experience bullet that naturally incorporates the missing skill.

    Falls back to the deterministic version on any error so the caller always
    gets a usable string.
    """
    if placement == SkillPlacement.skills:
        return skill.name

    # Find the best candidate bullet to rewrite.
    key = _norm(skill.name)
    best_bullet: str | None = None
    best_role: str = ""
    best_company: str = ""
    for exp in profile.experience:
        for bullet in exp.bullets:
            if key in bullet.lower() or any(
                t in bullet.lower() for t in key.split() if len(t) > 2
            ):
                best_bullet = bullet
                best_role = exp.title
                best_company = exp.company
                break
        if best_bullet:
            break

    if best_bullet is None and profile.experience:
        exp0 = profile.experience[0]
        best_role = exp0.title
        best_company = exp0.company

    try:
        from scorer.clients import build_llm_client
        from scorer.prompts import BANNED_WORDS

        settings = get_settings()
        llm = client or build_llm_client()

        if best_bullet:
            prompt = (
                f"Rewrite this resume bullet to naturally incorporate '{skill.name}'. "
                "Keep it one sentence (≤18 words), start with a strong past-tense verb, "
                "no buzzwords or AI clichés, preserve original metrics if any.\n\n"
                f"Original bullet: {best_bullet}"
            )
        else:
            prompt = (
                f"Write a single resume bullet for a {best_role} at {best_company} "
                f"that demonstrates '{skill.name}'. "
                "One sentence (≤18 words), strong past-tense verb, "
                "no buzzwords, no AI clichés."
            )

        forbidden = ", ".join(sorted(BANNED_WORDS)[:20])
        text = await llm.complete(
            model=settings.active_scorer_model,
            system_blocks=[
                {
                    "type": "text",
                    "text": (
                        "You write terse, factual resume bullets. "
                        f"Forbidden words: {forbidden}."
                    ),
                }
            ],
            user=prompt,
            max_tokens=80,
            temperature=0.3,
            thinking_level=settings.gemini_scorer_thinking_level,
        )
        text = text.strip().strip('"').strip()
        if not text or len(text) > 200 or text[0] in "[{":
            raise ValueError("Bad LLM output")
        return text
    except Exception as exc:
        log.warning("draft_bullet_llm_failed", skill=skill.name, error=str(exc))
        return draft_proposed_text(skill, placement=placement, profile=profile)


async def diff_against_baseline_async(
    baseline: RoleBaseline,
    jd_skills: list[JdSkill],
    profile: Profile,
    *,
    job_id: int,
    placement: SkillPlacement = SkillPlacement.skills,
    client: LLMClient | None = None,
) -> list[dict[str, Any]]:
    """Async version of diff_against_baseline with optional LLM bullet weaving."""
    import asyncio

    covered = _baseline_skill_keys(baseline)
    candidates: list[tuple[JdSkill, Any]] = []
    seen: set[str] = set()
    for skill in jd_skills:
        key = _norm(skill.name)
        if key in seen:
            continue
        seen.add(key)
        if not _skill_covered(skill, covered):
            candidates.append((skill, classify_provenance(skill, profile)))

    async def _row(skill: JdSkill, provenance: Any) -> dict[str, Any]:
        proposed = await draft_proposed_text_llm(
            skill, placement=placement, profile=profile, client=client
        ) if placement == SkillPlacement.experience else draft_proposed_text(
            skill, placement=placement, profile=profile
        )
        return {
            "job_id": job_id,
            "baseline_id": baseline.id,
            "skill": skill.name,
            "category": skill.category.value,
            "placement": placement,
            "proposed_text": proposed,
            "provenance": provenance,
        }

    rows = await asyncio.gather(*[_row(s, p) for s, p in candidates])
    return list(rows)


def diff_against_baseline(
    baseline: RoleBaseline,
    jd_skills: list[JdSkill],
    profile: Profile,
    *,
    job_id: int,
    placement: SkillPlacement = SkillPlacement.skills,
) -> list[dict[str, Any]]:
    """Return suggestion dicts for JD skills missing from the baseline resume."""
    covered = _baseline_skill_keys(baseline)
    suggestions: list[dict[str, Any]] = []
    seen: set[str] = set()
    for skill in jd_skills:
        key = _norm(skill.name)
        if key in seen:
            continue
        seen.add(key)
        if _skill_covered(skill, covered):
            continue
        provenance = classify_provenance(skill, profile)
        suggestions.append(
            {
                "job_id": job_id,
                "baseline_id": baseline.id,
                "skill": skill.name,
                "category": skill.category.value,
                "placement": placement,
                "proposed_text": draft_proposed_text(
                    skill, placement=placement, profile=profile
                ),
                "provenance": provenance,
                "status": SuggestionStatus.pending,
            }
        )
    return suggestions


def write_tailoring_report(
    job: Job,
    *,
    baseline: RoleBaseline,
    jd_skills: list[JdSkill],
    suggestions: list[SkillSuggestion],
    out_dir: Path,
) -> Path:
    """Write JSON + Markdown tailoring report under the job resume folder."""
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "job_id": job.id,
        "job_title": job.title,
        "company": job.company,
        "baseline_id": baseline.id,
        "baseline_role": baseline.role,
        "jd_skills": [s.model_dump(mode="json") for s in jd_skills],
        "suggestions": [
            {
                "id": s.id,
                "skill": s.skill,
                "category": s.category,
                "placement": s.placement.value if hasattr(s.placement, "value") else s.placement,
                "proposed_text": s.proposed_text,
                "provenance": (
                    s.provenance.value if hasattr(s.provenance, "value") else s.provenance
                ),
                "status": s.status.value if hasattr(s.status, "value") else s.status,
            }
            for s in suggestions
        ],
    }
    json_path = out_dir / "tailoring_report.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        f"# Tailoring report — {job.title} @ {job.company}",
        "",
        f"Baseline role: **{baseline.role}** (id={baseline.id})",
        "",
        "## JD top skills",
    ]
    for s in jd_skills:
        lines.append(f"- {s.name} ({s.category.value}, importance={s.importance})")
    lines.append("")
    lines.append("## Proposed additions (missing from baseline)")
    if not suggestions:
        lines.append("- None — baseline already covers JD skills.")
    for s in suggestions:
        prov = s.provenance.value if hasattr(s.provenance, "value") else s.provenance
        lines.append(f"- **{s.skill}** [{prov}] → `{s.proposed_text}`")
    md_path = out_dir / "tailoring_report.md"
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path


async def generate_suggestions_for_job(
    job_id: int,
    *,
    role: str | None = None,
    profile: Profile | None = None,
    client: LLMClient | None = None,
    replace_pending: bool = True,
) -> list[SkillSuggestion]:
    """Extract JD skills, diff vs role baseline, persist SkillSuggestion rows."""
    await init_db()
    profile = profile or load_profile()
    settings = get_settings()

    async with session_scope() as session:
        job = await get_job_by_id(session, job_id)
    if job is None:
        raise ValueError(f"Job {job_id} not found")

    # Resolve role: explicit > first preference title that matches job title > first preference
    role_name = role
    if not role_name:
        title_l = (job.title or "").lower()
        for pref in profile.preferences.titles:
            if pref.lower() in title_l or title_l in pref.lower():
                role_name = pref
                break
        if not role_name and profile.preferences.titles:
            role_name = profile.preferences.titles[0]
    if not role_name:
        role_name = job.title or "General"

    async with session_scope() as session:
        baseline = await get_role_baseline_by_role(session, role_name)

    if baseline is None:
        from resume.baseline import build_role_baseline

        baseline = await build_role_baseline(
            role_name,
            title_terms=[role_name],
            profile=profile,
            client=client,
        )

    use_llm = settings.resume_use_llm_tailoring
    llm = client
    if use_llm and llm is None:
        try:
            from scorer.engine import build_llm_client

            llm = build_llm_client()
        except Exception:
            llm = None

    jd_skills = await extract_top_skills(job, client=llm)
    placement = (
        SkillPlacement.experience
        if settings.resume_skill_placement == "skills_and_experience"
        else SkillPlacement.skills
    )
    drafts = diff_against_baseline(
        baseline,
        jd_skills,
        profile,
        job_id=job_id,
        placement=placement,
    )

    now = datetime.now(UTC)
    saved: list[SkillSuggestion] = []
    async with session_scope() as session:
        if replace_pending:
            existing = await get_suggestions_for_job(session, job_id)
            for row in existing:
                if row.status == SuggestionStatus.pending:
                    await session.delete(row)

        for draft in drafts:
            row = SkillSuggestion(
                job_id=draft["job_id"],
                baseline_id=draft["baseline_id"],
                skill=draft["skill"],
                category=draft["category"],
                placement=draft["placement"],
                proposed_text=draft["proposed_text"],
                provenance=draft["provenance"],
                status=SuggestionStatus.pending,
                created_at=now,
                updated_at=now,
            )
            session.add(row)
            saved.append(row)
        await session.flush()
        for row in saved:
            await session.refresh(row)

    out_dir = settings.resumes_path / str(job_id)
    write_tailoring_report(
        job,
        baseline=baseline,
        jd_skills=jd_skills,
        suggestions=saved,
        out_dir=out_dir,
    )
    log.info(
        "suggestions_generated",
        job_id=job_id,
        role=role_name,
        count=len(saved),
        baseline_id=baseline.id,
    )
    return saved


def apply_approved_suggestions_to_resume_data(
    resume_data: dict[str, Any],
    suggestions: list[SkillSuggestion],
) -> dict[str, Any]:
    """Merge approved/edited suggestions into resume_data (skills section)."""
    data = dict(resume_data)
    skills = list(data.get("skills") or [])
    seen = {_norm(str(s)) for s in skills}
    for sug in suggestions:
        status = sug.status.value if hasattr(sug.status, "value") else sug.status
        if status not in {
            SuggestionStatus.approved.value,
            SuggestionStatus.edited.value,
        }:
            continue
        text = (sug.proposed_text or sug.skill or "").strip()
        if not text:
            continue
        placement = (
            sug.placement.value if hasattr(sug.placement, "value") else sug.placement
        )
        if placement == SkillPlacement.experience.value:
            # Append as a bullet under the first experience entry
            experience = list(data.get("experience") or [])
            if experience:
                exp0 = dict(experience[0])
                bullets = list(exp0.get("bullets") or [])
                bullets.append(text)
                exp0["bullets"] = bullets
                experience[0] = exp0
                data["experience"] = experience
            # Also ensure the skill name is listed
            if _norm(sug.skill) not in seen:
                skills.append(sug.skill)
                seen.add(_norm(sug.skill))
        else:
            if _norm(text) not in seen and _norm(sug.skill) not in seen:
                skills.append(sug.skill if placement == SkillPlacement.skills.value else text)
                seen.add(_norm(sug.skill))
    data["skills"] = skills
    return data


__all__ = [
    "apply_approved_suggestions_to_resume_data",
    "classify_provenance",
    "diff_against_baseline",
    "generate_suggestions_for_job",
    "write_tailoring_report",
]

"""Role baseline builder: aggregate ~15-20 JDs into a role-optimized resume."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from typing import Any

import structlog

from config.profile import Profile, load_profile
from config.settings import get_settings
from core.db import (
    Job,
    RoleBaseline,
    get_jobs_for_role,
    get_role_baseline_by_role,
    init_db,
    session_scope,
)
from resume.compiler import clean_name, compile_resume_data
from resume.selector import build_resume_data, select_bullets
from resume.skills import (
    LLMClient,
    RoleSkillProfile,
    aggregate_role_skills,
    extract_top_skills,
)

log = structlog.get_logger(__name__)


def _slugify_role(role: str) -> str:
    text = re.sub(r"[^\w\s-]", "", (role or "").strip().lower())
    text = re.sub(r"[\s\-]+", "_", text).strip("_")
    return text or "role"


def _synthetic_job_for_role(role: str, skill_names: list[str]) -> Job:
    """Build a lightweight Job so existing selector APIs can rank bullets."""
    from core.db import Source

    desc = (
        f"Role: {role}\n"
        f"Required skills: {', '.join(skill_names)}\n"
        + "\n".join(f"- Experience with {s}" for s in skill_names[:15])
    )
    return Job(
        source=Source.linkedin,
        external_id=f"baseline-{_slugify_role(role)}",
        title=role,
        company="Role Baseline",
        url="https://example.com/baseline",
        description_clean=desc,
    )


def build_baseline_resume_data(
    profile: Profile,
    skill_profile: RoleSkillProfile,
) -> dict[str, Any]:
    """Assemble Typst resume JSON from an aggregated role skill profile."""
    skill_names = [s.name for s in skill_profile.skills]
    synthetic = _synthetic_job_for_role(skill_profile.role, skill_names)
    data = build_resume_data(profile, synthetic)

    # Prefer aggregated role skills (JD-prevalent first), then remaining profile skills
    profile_skills = [s.strip() for s in profile.skills if s.strip()]
    seen = {_normalize(s) for s in skill_names}
    rest = [s for s in profile_skills if _normalize(s) not in seen]
    data["skills"] = skill_names + rest
    data["summary"] = (
        f"{profile.identity.full_name} — targeting {skill_profile.role}. "
        f"Core skills: {', '.join(skill_names[:6])}."
    )
    # Ensure experience still has selected bullets (selector already ran)
    if not data.get("experience"):
        selected = select_bullets(profile, synthetic)
        data["experience"] = [
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
    return data


def _normalize(name: str) -> str:
    return re.sub(r"\s+", " ", name.strip().lower())


async def build_role_baseline(
    role: str,
    *,
    title_terms: list[str] | None = None,
    profile: Profile | None = None,
    client: LLMClient | None = None,
    limit: int | None = None,
    refresh: bool = False,
) -> RoleBaseline:
    """Pull role JDs from the DB, aggregate skills, compile a baseline PDF, persist."""
    await init_db()
    profile = profile or load_profile()
    settings = get_settings()
    jd_limit = limit if limit is not None else settings.resume_baseline_jd_limit
    terms = title_terms if title_terms is not None else [role]
    terms = [t.strip() for t in terms if t and t.strip()] or [role]

    if not refresh:
        async with session_scope() as session:
            existing = await get_role_baseline_by_role(session, role)
            if existing is not None:
                log.info("role_baseline_reuse", role=role, baseline_id=existing.id)
                return existing

    async with session_scope() as session:
        jobs = await get_jobs_for_role(session, terms, limit=jd_limit)

    if len(jobs) < 3:
        log.warning(
            "role_baseline_few_jobs",
            role=role,
            count=len(jobs),
            terms=terms,
        )

    use_llm = settings.resume_use_llm_tailoring
    llm = client
    if use_llm and llm is None:
        try:
            from scorer.engine import build_llm_client

            llm = build_llm_client()
        except Exception as exc:
            log.warning("role_baseline_no_llm", error=str(exc))
            llm = None

    per_jd: list[list[Any]] = []
    for job in jobs:
        skills = await extract_top_skills(job, client=llm)
        per_jd.append(skills)

    # If the DB is empty, still produce a baseline from the profile alone
    if not per_jd:
        from resume.skills import JdSkill, SkillCategory

        per_jd = [
            [
                JdSkill(name=s, category=SkillCategory.hard, importance=4)
                for s in profile.skills[:15]
            ]
        ]

    skill_profile = aggregate_role_skills(per_jd, role=role, top_n=15)
    resume_data = build_baseline_resume_data(profile, skill_profile)

    out_dir = settings.baselines_path / _slugify_role(role)
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = out_dir / f"{clean_name(profile.identity.full_name)}_Baseline.pdf"
    fit = compile_resume_data(resume_data, pdf_path, autofit=True)

    skills_json = [s.model_dump(mode="json") for s in skill_profile.skills]
    job_ids = [j.id for j in jobs if j.id is not None]
    now = datetime.now(UTC)

    # Persist fit + skill profile artifacts
    (out_dir / "skills.json").write_text(
        json.dumps(
            {
                "role": role,
                "jd_count": skill_profile.jd_count,
                "skills": skills_json,
                "job_ids": job_ids,
                "fit": {
                    "pages": fit.pages,
                    "levers": fit.levers,
                    "attempts": fit.attempts,
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (out_dir / "resume_data.json").write_text(
        json.dumps(resume_data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    async with session_scope() as session:
        if refresh:
            existing = await get_role_baseline_by_role(session, role)
            if existing is not None:
                existing.title_terms = terms
                existing.skills = skills_json
                existing.resume_data = resume_data
                existing.pdf_path = str(pdf_path.resolve())
                existing.job_ids = job_ids
                existing.updated_at = now
                session.add(existing)
                await session.flush()
                await session.refresh(existing)
                log.info(
                    "role_baseline_refreshed",
                    role=role,
                    baseline_id=existing.id,
                    jd_count=len(job_ids),
                    pages=fit.pages,
                )
                return existing

        row = RoleBaseline(
            role=role,
            title_terms=terms,
            skills=skills_json,
            resume_data=resume_data,
            pdf_path=str(pdf_path.resolve()),
            job_ids=job_ids,
            created_at=now,
            updated_at=now,
        )
        session.add(row)
        await session.flush()
        await session.refresh(row)
        log.info(
            "role_baseline_built",
            role=role,
            baseline_id=row.id,
            jd_count=len(job_ids),
            pages=fit.pages,
            skills=len(skills_json),
        )
        return row


__all__ = [
    "build_baseline_resume_data",
    "build_role_baseline",
]

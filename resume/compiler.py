"""Typst resume compiler + static base resume + one-page auto-fit + pikepdf sanitize."""

from __future__ import annotations

import copy
import json
import re
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pikepdf
import structlog
import typst

from config.profile import Profile, load_profile
from config.settings import PROJECT_ROOT, get_settings
from core.db import Job, Status, get_job_by_id, get_jobs_by_status, init_db, session_scope
from resume.selector import build_resume_data

log = structlog.get_logger(__name__)

TEMPLATE_PATH = Path(__file__).resolve().parent / "templates" / "resume.typ"

_DEFAULT_CREATOR = "Microsoft Word"
_DEFAULT_PRODUCER = "Microsoft: Print To PDF"

# Auto-fit defaults and floors
_DEFAULT_FONT = 10.0
_DEFAULT_LEADING = 0.65
_DEFAULT_SECTION_GAP = 0.55
_MIN_FONT = 9.0
_MIN_LEADING = 0.5
_MIN_SECTION_GAP = 0.35
_DEFAULT_MAX_BULLETS = 12
_MIN_BULLETS = 4
_DEFAULT_SKILLS_CAP = 40
_MIN_SKILLS_CAP = 8


@dataclass
class ResumeSummary:
    generated: int = 0
    skipped: int = 0
    errors: int = 0
    error_details: list[str] = field(default_factory=list)


@dataclass
class FitReport:
    """Levers pulled to keep the resume on one page."""

    pages: int = 1
    font_size: float = _DEFAULT_FONT
    leading: float = _DEFAULT_LEADING
    section_gap: float = _DEFAULT_SECTION_GAP
    max_bullets: int = _DEFAULT_MAX_BULLETS
    skills_cap: int = _DEFAULT_SKILLS_CAP
    levers: list[str] = field(default_factory=list)
    attempts: int = 0


def clean_name(full_name: str) -> str:
    """Normalize a person's name for filenames: 'Jane Q. Doe' -> 'Jane_Q_Doe'."""
    text = (full_name or "").strip()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s\-]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "Resume"


def sanitize_pdf(
    path: Path,
    *,
    creator: str = _DEFAULT_CREATOR,
    producer: str = _DEFAULT_PRODUCER,
) -> None:
    """Overwrite Creator/Producer and strip author-ish metadata."""
    with pikepdf.open(path, allow_overwriting_input=True) as pdf:
        with pdf.open_metadata(set_pikepdf_as_editor=False) as meta:
            meta["xmp:CreatorTool"] = creator
            meta["pdf:Producer"] = producer
            for key in ("dc:creator", "dc:publisher", "xmp:Author"):
                if key in meta:
                    del meta[key]

        # Mirror into classic DocumentInfo
        info = pdf.docinfo
        info["/Creator"] = creator
        info["/Producer"] = producer
        for key in ("/Author", "/Keywords", "/Subject", "/Title"):
            if key in info:
                del info[key]

        pdf.save(path, fix_metadata_version=False)


def pdf_page_count(path: Path) -> int:
    """Return the number of pages in a PDF."""
    with pikepdf.open(path) as pdf:
        return len(pdf.pages)


def apply_fit_caps(
    data: dict[str, Any],
    *,
    max_bullets: int,
    skills_cap: int,
    font_size: float,
    leading: float,
    section_gap: float,
) -> dict[str, Any]:
    """Return a copy of resume data with content caps and typography knobs applied."""
    out = copy.deepcopy(data)
    skills = list(out.get("skills") or [])
    if len(skills) > skills_cap:
        out["skills"] = skills[:skills_cap]

    remaining = max_bullets
    capped_exp: list[dict[str, Any]] = []
    for exp in out.get("experience") or []:
        exp_copy = dict(exp)
        bullets = list(exp_copy.get("bullets") or [])
        if remaining <= 0:
            exp_copy["bullets"] = []
        elif len(bullets) > remaining:
            exp_copy["bullets"] = bullets[:remaining]
            remaining = 0
        else:
            remaining -= len(bullets)
        capped_exp.append(exp_copy)
    out["experience"] = capped_exp

    out["font_size"] = font_size
    out["leading"] = leading
    out["section_gap"] = section_gap
    return out


def _next_fit_state(report: FitReport) -> FitReport | None:
    """Advance to the next least-destructive fit lever; None if floors reached."""
    # 1) Tighten spacing
    if report.section_gap > _MIN_SECTION_GAP + 0.01:
        report.section_gap = max(_MIN_SECTION_GAP, round(report.section_gap - 0.1, 2))
        report.levers.append(f"section_gap={report.section_gap}")
        return report
    if report.leading > _MIN_LEADING + 0.01:
        report.leading = max(_MIN_LEADING, round(report.leading - 0.05, 2))
        report.levers.append(f"leading={report.leading}")
        return report
    # 2) Shrink font
    if report.font_size > _MIN_FONT + 0.01:
        report.font_size = max(_MIN_FONT, round(report.font_size - 0.5, 1))
        report.levers.append(f"font_size={report.font_size}")
        return report
    # 3) Drop bullets
    if report.max_bullets > _MIN_BULLETS:
        report.max_bullets = max(_MIN_BULLETS, report.max_bullets - 2)
        report.levers.append(f"max_bullets={report.max_bullets}")
        return report
    # 4) Cap skills
    if report.skills_cap > _MIN_SKILLS_CAP:
        report.skills_cap = max(_MIN_SKILLS_CAP, report.skills_cap - 4)
        report.levers.append(f"skills_cap={report.skills_cap}")
        return report
    return None


def compile_resume_data(
    data: dict[str, Any],
    output: Path,
    *,
    autofit: bool = True,
) -> FitReport:
    """Compile resume JSON to PDF; optionally iterate until one page."""
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"Typst template missing: {TEMPLATE_PATH}")

    output.parent.mkdir(parents=True, exist_ok=True)
    report = FitReport(
        font_size=float(data.get("font_size", _DEFAULT_FONT)),
        leading=float(data.get("leading", _DEFAULT_LEADING)),
        section_gap=float(data.get("section_gap", _DEFAULT_SECTION_GAP)),
        max_bullets=int(data.get("max_bullets", _DEFAULT_MAX_BULLETS)),
        skills_cap=int(data.get("skills_cap", _DEFAULT_SKILLS_CAP)),
    )

    while True:
        report.attempts += 1
        capped = apply_fit_caps(
            data,
            max_bullets=report.max_bullets,
            skills_cap=report.skills_cap,
            font_size=report.font_size,
            leading=report.leading,
            section_gap=report.section_gap,
        )
        payload = json.dumps(capped, ensure_ascii=False)
        typst.compile(
            input=str(TEMPLATE_PATH),
            output=str(output),
            root=str(PROJECT_ROOT),
            sys_inputs={"data": payload},
        )
        sanitize_pdf(output)
        pages = pdf_page_count(output)
        report.pages = pages
        if not autofit or pages <= 1:
            break
        nxt = _next_fit_state(report)
        if nxt is None:
            log.warning(
                "resume_autofit_floor",
                path=str(output),
                pages=pages,
                levers=report.levers,
            )
            break

    log.info(
        "resume_compiled_data",
        path=str(output),
        pages=report.pages,
        attempts=report.attempts,
        levers=report.levers,
    )
    return report


def compile_resume(
    profile: Profile,
    job: Job,
    *,
    out_dir: Path | None = None,
    resume_data: dict[str, Any] | None = None,
    autofit: bool = True,
) -> Path:
    """Compile a tailored resume PDF for one job; return absolute path."""
    if job.id is None:
        raise ValueError("Job must have an id before compiling a resume")
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"Typst template missing: {TEMPLATE_PATH}")

    settings = get_settings()
    base = Path(out_dir) if out_dir is not None else settings.resumes_path
    job_dir = base / str(job.id)
    job_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{clean_name(profile.identity.full_name)}_Resume.pdf"
    output = (job_dir / filename).resolve()

    data = resume_data if resume_data is not None else build_resume_data(profile, job)
    started = time.perf_counter()
    fit = compile_resume_data(data, output, autofit=autofit)
    duration_ms = int((time.perf_counter() - started) * 1000)

    # Persist fit report next to the PDF
    report_path = job_dir / "fit_report.json"
    report_path.write_text(
        json.dumps(
            {
                "pages": fit.pages,
                "attempts": fit.attempts,
                "levers": fit.levers,
                "font_size": fit.font_size,
                "leading": fit.leading,
                "section_gap": fit.section_gap,
                "max_bullets": fit.max_bullets,
                "skills_cap": fit.skills_cap,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    log.info(
        "resume_compiled",
        job_id=job.id,
        path=str(output),
        duration_ms=duration_ms,
        pages=fit.pages,
        bullets=sum(len(e.get("bullets", [])) for e in data.get("experience", [])),
        levers=fit.levers,
    )
    return output


async def compile_pending(
    *,
    profile: Profile | None = None,
    limit: int | None = None,
    force: bool = False,
    out_dir: Path | None = None,
) -> ResumeSummary:
    """Compile resumes for staged jobs missing resume_path (unless force)."""
    await init_db()
    profile = profile or load_profile()
    summary = ResumeSummary()

    async with session_scope() as session:
        jobs = await get_jobs_by_status(session, Status.staged, limit=limit)

    if not jobs:
        log.info("compile_pending_empty")
        return summary

    for job in jobs:
        if job.resume_path and not force:
            summary.skipped += 1
            continue
        try:
            path = compile_resume(profile, job, out_dir=out_dir)
            async with session_scope() as session:
                if job.id is None:
                    raise ValueError("job missing id")
                target = await get_job_by_id(session, job.id)
                if target is None:
                    raise ValueError(f"job {job.id} missing")
                target.resume_path = str(path)
                session.add(target)
            summary.generated += 1
        except Exception as exc:
            log.warning("resume_compile_failed", job_id=job.id, error=str(exc))
            summary.errors += 1
            summary.error_details.append(f"job {job.id}: {exc}")

    log.info(
        "compile_pending_complete",
        generated=summary.generated,
        skipped=summary.skipped,
        errors=summary.errors,
    )
    return summary


def _job_resume_output(
    profile: Profile,
    job: Job,
    *,
    out_dir: Path | None = None,
) -> Path:
    """Resolve the per-job resume PDF path (create parent dirs)."""
    if job.id is None:
        raise ValueError("Job must have an id before preparing a resume")
    settings = get_settings()
    base = Path(out_dir) if out_dir is not None else settings.resumes_path
    job_dir = base / str(job.id)
    job_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{clean_name(profile.identity.full_name)}_Resume.pdf"
    return (job_dir / filename).resolve()


def prepare_base_resume(
    profile: Profile,
    job: Job,
    *,
    out_dir: Path | None = None,
    base_resume: Path | None = None,
) -> Path:
    """Copy the candidate's base PDF for one job, sanitize metadata, return path."""
    settings = get_settings()
    source = Path(base_resume) if base_resume is not None else settings.base_resume_file
    if not source.is_file():
        raise FileNotFoundError(
            f"Base resume not found: {source}. "
            "Save your PDF as config/base_resume.pdf before applying."
        )

    output = _job_resume_output(profile, job, out_dir=out_dir)
    shutil.copy2(source, output)
    sanitize_pdf(output)

    log.info(
        "resume_prepared_from_base",
        job_id=job.id,
        path=str(output),
        source=str(source),
    )
    return output


async def _baseline_pdf_for_job(job: Job, profile: Profile) -> Path | None:
    """Return the role baseline PDF for this job when one exists, else None."""
    from core.db import get_role_baseline_by_role

    title = (job.title or "").strip()
    if not title:
        return None
    # Resolve from preferences titles: find first pref that appears in the job title.
    prefs_titles = list(profile.preferences.titles)
    role = None
    title_lower = title.lower()
    for pref in prefs_titles:
        if pref.strip().lower() in title_lower:
            role = pref.strip()
            break
    if role is None and prefs_titles:
        role = prefs_titles[0]
    if not role:
        return None

    try:
        async with session_scope() as session:
            baseline = await get_role_baseline_by_role(session, role)
        if baseline is None or not baseline.pdf_path:
            return None
        pdf = Path(baseline.pdf_path)
        return pdf if pdf.is_file() else None
    except Exception:
        return None


async def prepare_pending(
    *,
    profile: Profile | None = None,
    limit: int | None = None,
    force: bool = False,
    out_dir: Path | None = None,
    base_resume: Path | None = None,
    status: Status = Status.staged,
) -> ResumeSummary:
    """Attach the best available resume to jobs in one status that are missing resume_path.

    The default remains staged. The pipeline passes pending_review after shortlist
    so only the review queue is prepared on a normal run.

    Priority:
    1. Role baseline PDF (Typst-compiled from aggregated JDs) when one exists.
    2. Candidate's static base PDF (config/base_resume.pdf).

    Falls back to the static PDF if the baseline is missing or the file has gone stale.
    """
    await init_db()
    profile = profile or load_profile()
    summary = ResumeSummary()

    settings = get_settings()
    source = Path(base_resume) if base_resume is not None else settings.base_resume_file
    base_available = source.is_file()
    if not base_available:
        log.warning("prepare_pending_missing_base", path=str(source))

    async with session_scope() as session:
        jobs = await get_jobs_by_status(session, status, limit=limit)

    if not jobs:
        log.info("prepare_pending_empty")
        return summary

    for job in jobs:
        if job.resume_path and not force:
            summary.skipped += 1
            continue
        try:
            # Prefer the role-specific baseline PDF over the static base.
            baseline_pdf = await _baseline_pdf_for_job(job, profile)
            resume_source = baseline_pdf if baseline_pdf is not None else (
                source if base_available else None
            )
            if resume_source is None:
                raise FileNotFoundError(
                    "No base resume and no role baseline found. "
                    "Save config/base_resume.pdf or run build-baseline first."
                )
            output = _job_resume_output(profile, job, out_dir=out_dir)
            shutil.copy2(resume_source, output)
            sanitize_pdf(output)
            log.info(
                "resume_prepared",
                job_id=job.id,
                path=str(output),
                source=str(resume_source),
                from_baseline=baseline_pdf is not None,
            )
            async with session_scope() as session:
                if job.id is None:
                    raise ValueError("job missing id")
                target = await get_job_by_id(session, job.id)
                if target is None:
                    raise ValueError(f"job {job.id} missing")
                target.resume_path = str(output)
                session.add(target)
            summary.generated += 1
        except Exception as exc:
            log.warning("resume_prepare_failed", job_id=job.id, error=str(exc))
            summary.errors += 1
            summary.error_details.append(f"job {job.id}: {exc}")

    log.info(
        "prepare_pending_complete",
        generated=summary.generated,
        skipped=summary.skipped,
        errors=summary.errors,
    )
    return summary


async def compile_for_job(
    job_id: int,
    *,
    profile: Profile | None = None,
    out_dir: Path | None = None,
    resume_data: dict[str, Any] | None = None,
) -> Path:
    """Generate a Typst-tailored resume for one job and persist resume_path."""
    await init_db()
    profile = profile or load_profile()

    async with session_scope() as session:
        job = await get_job_by_id(session, job_id)

    if job is None:
        raise ValueError(f"Job {job_id} not found")

    path = compile_resume(
        profile,
        job,
        out_dir=out_dir,
        resume_data=resume_data,
    )

    async with session_scope() as session:
        target = await get_job_by_id(session, job_id)
        if target is None:
            raise ValueError(f"Job {job_id} missing")
        target.resume_path = str(path)
        session.add(target)

    log.info("resume_tailored_for_job", job_id=job_id, path=str(path))
    return path

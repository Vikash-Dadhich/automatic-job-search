"""Build combined Markdown + Typst PDF application prep packs."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import structlog
import typst

from automation.answers import AnswerResolver, ResolvedAnswer
from config.profile import Profile, load_profile
from config.settings import PROJECT_ROOT, get_settings
from core.db import Job
from prep.questions import ALL_RESOLVED_QUESTIONS, MANUAL_FILL
from scorer.engine import LLMClient, build_llm_client

log = structlog.get_logger(__name__)

TEMPLATE_PATH = Path(__file__).resolve().parent / "templates" / "prep_pack.typ"


@dataclass
class PrepPackResult:
    markdown_path: Path | None = None
    pdf_path: Path | None = None
    job_ids: list[int] = field(default_factory=list)
    job_count: int = 0
    errors: list[str] = field(default_factory=list)


def _answer_item(answer: ResolvedAnswer) -> dict[str, str]:
    return {
        "question": answer.question,
        "answer": answer.answer,
        "source": answer.source.value,
    }


async def build_job_section(
    job: Job,
    profile: Profile,
    client: LLMClient,
) -> dict[str, Any]:
    """Resolve standard + essay questions for one job into a serializable section."""
    resolver = AnswerResolver(profile, client=client)
    answers = await resolver.resolve_many(list(ALL_RESOLVED_QUESTIONS), job=job)
    tier = job.tier.value if job.tier else None
    return {
        "job_id": job.id,
        "title": job.title,
        "company": job.company,
        "location": job.location or "N/A",
        "url": job.url,
        "source": job.source.value if job.source else "",
        "score": job.score,
        "tier": tier,
        "outreach_draft": job.outreach_draft or "",
        "cover_letter": job.cover_letter or "",
        "answers": [_answer_item(a) for a in answers],
        "manual_fill": list(MANUAL_FILL),
    }


def render_markdown(sections: list[dict[str, Any]], *, generated_at: str) -> str:
    """Render a combined Markdown prep pack for all job sections."""
    lines: list[str] = [
        "# Application Prep Pack",
        "",
        f"Generated: {generated_at}",
        f"Jobs included: {len(sections)}",
        "",
        "_LinkedIn / Indeed applications are manual. Copy answers into each form. "
        "Exact employer-specific questions may differ._",
        "",
        "---",
        "",
    ]
    for idx, section in enumerate(sections, start=1):
        score = section.get("score")
        score_s = str(score) if score is not None else "?"
        tier = section.get("tier") or "?"
        lines.extend(
            [
                f"## {idx}. {section.get('title')} @ {section.get('company')}",
                "",
                f"- **Location:** {section.get('location')}",
                f"- **Score / Tier:** {score_s} / {tier}",
                f"- **Source:** {section.get('source')}",
                f"- **URL:** {section.get('url')}",
                "",
                "### Drafted answers",
                "",
            ]
        )
        for item in section.get("answers") or []:
            q = str(item.get("question") or "").strip()
            a = str(item.get("answer") or "").strip() or "_(blank — fill manually)_"
            src = str(item.get("source") or "").strip()
            lines.append(f"**Q:** {q}")
            lines.append(f"**A:** {a}  ")
            lines.append(f"_Source: {src}_")
            lines.append("")

        outreach = str(section.get("outreach_draft") or "").strip()
        if outreach:
            lines.extend(["### Outreach draft (Tier 1)", "", outreach, ""])

        letter = str(section.get("cover_letter") or "").strip()
        if letter:
            lines.extend(["### Cover letter (Tier 1)", "", letter, ""])

        lines.extend(["### Fill yourself", ""])
        for reminder in section.get("manual_fill") or list(MANUAL_FILL):
            lines.append(f"- [ ] {reminder}")
        lines.extend(["", "---", ""])

    return "\n".join(lines).rstrip() + "\n"


def compile_prep_pdf(data: dict[str, Any], out_path: Path) -> Path:
    """Compile prep-pack JSON via Typst template to PDF."""
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"Prep-pack Typst template missing: {TEMPLATE_PATH}")
    out_path = out_path.resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, ensure_ascii=False)
    typst.compile(
        input=str(TEMPLATE_PATH),
        output=str(out_path),
        root=str(PROJECT_ROOT),
        sys_inputs={"data": payload},
    )
    return out_path


async def generate_prep_pack(
    jobs: list[Job],
    *,
    profile: Profile | None = None,
    client: LLMClient | None = None,
    out_dir: Path | None = None,
) -> PrepPackResult:
    """Build Markdown + PDF prep pack for the given jobs."""
    result = PrepPackResult()
    if not jobs:
        return result

    profile = profile or load_profile()
    client = client or build_llm_client()
    settings = get_settings()
    base = Path(out_dir) if out_dir is not None else settings.prep_packs_path
    base.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    generated_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")

    sections: list[dict[str, Any]] = []
    for job in jobs:
        if job.id is None:
            result.errors.append("job missing id")
            continue
        try:
            section = await build_job_section(job, profile, client)
            sections.append(section)
            result.job_ids.append(job.id)
        except Exception as exc:
            msg = f"job {job.id}: {exc}"
            result.errors.append(msg)
            log.warning("prep_pack_job_failed", job_id=job.id, error=str(exc))

    if not sections:
        return result

    result.job_count = len(sections)
    md_path = base / f"prep_pack_{stamp}.md"
    pdf_path = base / f"prep_pack_{stamp}.pdf"

    md_path.write_text(
        render_markdown(sections, generated_at=generated_at),
        encoding="utf-8",
    )
    result.markdown_path = md_path

    pdf_data = {
        "generated_at": generated_at,
        "job_count": len(sections),
        "jobs": sections,
    }
    started = time.perf_counter()
    try:
        compile_prep_pdf(pdf_data, pdf_path)
        result.pdf_path = pdf_path
        log.info(
            "prep_pack_compiled",
            jobs=len(sections),
            markdown=str(md_path),
            pdf=str(pdf_path),
            duration_ms=int((time.perf_counter() - started) * 1000),
        )
    except Exception as exc:
        result.errors.append(f"pdf: {exc}")
        log.warning("prep_pack_pdf_failed", error=str(exc))

    return result

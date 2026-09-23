"""Peer benchmark comparator: score candidate vs LinkedIn peers for a job."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

import structlog
from pydantic import BaseModel, Field

from config.profile import Profile, load_profile
from config.settings import get_settings
from core.db import (
    Benchmark,
    Job,
    PeerProfile,
    get_job_by_id,
    init_db,
    session_scope,
)
from resume.skills import JdSkill
from scraper.linkedin_people import PeerProfileData

log = structlog.get_logger(__name__)


class DimensionScore(BaseModel):
    name: str
    mine: float
    peer_median: float
    percentile: float
    note: str = ""


class BenchmarkReport(BaseModel):
    job_id: int
    overall_score: int = Field(ge=0, le=100)
    percentile: float
    dimensions: list[DimensionScore] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    peer_count: int = 0


@dataclass
class BenchmarkSummary:
    report: BenchmarkReport | None = None
    peer_ids: list[int] = field(default_factory=list)
    report_path: str | None = None


def _norm(s: str) -> str:
    return " ".join(s.strip().lower().split())


def _skill_coverage(skills: list[str], jd_skills: list[JdSkill]) -> float:
    if not jd_skills:
        return 0.0
    mine = {_norm(s) for s in skills}
    hits = 0
    for sk in jd_skills:
        key = _norm(sk.name)
        tokens = set(key.split())
        if key in mine or tokens & mine:
            hits += 1
    return 100.0 * hits / len(jd_skills)


def _education_rank(level: str | None) -> float:
    mapping = {
        None: 0.0,
        "other": 1.0,
        "bachelor": 2.0,
        "master": 3.0,
        "mba": 3.5,
        "phd": 4.0,
    }
    if not level:
        return 0.0
    return mapping.get(level.strip().lower(), 1.0)


def _seniority_rank(level: str | None) -> float:
    mapping = {
        None: 0.0,
        "intern": 1.0,
        "junior": 2.0,
        "mid": 3.0,
        "senior": 4.0,
        "staff": 5.0,
        "principal": 5.5,
        "manager": 5.0,
        "director": 6.0,
        "vp": 7.0,
        "other": 2.5,
    }
    if not level:
        return 0.0
    return mapping.get(level.strip().lower(), 2.5)


def _percentile(value: float, peers: list[float]) -> float:
    if not peers:
        return 50.0
    below = sum(1 for p in peers if p < value)
    equal = sum(1 for p in peers if p == value)
    return 100.0 * (below + 0.5 * equal) / len(peers)


def _median(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


def _derive_seniority(profile: Profile, *, years: float) -> str:
    """Map years + current title into a seniority band for peer comparison."""
    title = (profile.experience[0].title if profile.experience else "").lower()
    if any(k in title for k in ("intern", "trainee")):
        return "intern"
    if any(k in title for k in ("director", "head of")):
        return "director"
    if any(k in title for k in ("vp", "vice president")):
        return "vp"
    if any(k in title for k in ("principal", "staff")):
        return "staff" if "staff" in title else "principal"
    if any(k in title for k in ("senior", "sr.", "sr ")):
        return "senior"
    if any(k in title for k in ("manager", "lead")) and "product manager" not in title:
        return "manager"
    if years < 2:
        return "junior"
    if years < 5:
        return "mid"
    if years < 8:
        return "senior"
    return "staff"


def profile_to_peer_data(profile: Profile, *, url: str = "") -> PeerProfileData:
    """Map grounded profile.yaml into PeerProfileData for self comparison."""
    skills = list(profile.skills)
    companies = [e.company for e in profile.experience]
    # Prefer the profile helper (deduped career span) when available.
    if hasattr(profile, "total_years_experience"):
        years = float(profile.total_years_experience())
    else:
        years = 0.0
        for exp in profile.experience:
            try:
                start_y = int(exp.start_date.split("-")[0])
                end = exp.end_date.strip().lower()
                end_y = (
                    datetime.now(UTC).year
                    if end in {"present", "current", ""}
                    else int(end.split("-")[0])
                )
                years += max(0, end_y - start_y)
            except Exception:
                continue
    edu_level = "other"
    for edu in profile.education:
        deg = (edu.degree or "").lower()
        if "mba" in deg:
            edu_level = "mba"
            break
        if "ph.d" in deg or "phd" in deg:
            edu_level = "phd"
            break
        if "m." in deg or "master" in deg:
            edu_level = "master"
        elif "b." in deg or "bachelor" in deg:
            edu_level = "bachelor"
    title = profile.experience[0].title if profile.experience else None
    return PeerProfileData(
        url=url or profile.identity.linkedin_url,
        full_name=profile.identity.full_name,
        headline=title,
        current_title=title,
        years_experience=float(years) if years else None,
        companies=companies,
        education_level=edu_level,
        skills=skills,
        seniority=_derive_seniority(profile, years=years),
    )


def build_benchmark(
    job: Job,
    me: PeerProfileData,
    peers: list[PeerProfileData],
    jd_skills: list[JdSkill],
) -> BenchmarkReport:
    """Deterministic comparator across YOE, skill coverage, education, seniority."""
    if job.id is None:
        raise ValueError("job must have an id")

    my_yoe = float(me.years_experience or 0)
    peer_yoe = [float(p.years_experience or 0) for p in peers]
    my_skills = _skill_coverage(me.skills, jd_skills)
    peer_skills = [_skill_coverage(p.skills, jd_skills) for p in peers]
    my_edu = _education_rank(me.education_level)
    peer_edu = [_education_rank(p.education_level) for p in peers]
    my_sen = _seniority_rank(me.seniority)
    peer_sen = [_seniority_rank(p.seniority) for p in peers]

    dims = [
        DimensionScore(
            name="years_experience",
            mine=my_yoe,
            peer_median=_median(peer_yoe),
            percentile=_percentile(my_yoe, peer_yoe),
            note="Total years across roles",
        ),
        DimensionScore(
            name="jd_skill_coverage",
            mine=round(my_skills, 1),
            peer_median=round(_median(peer_skills), 1),
            percentile=_percentile(my_skills, peer_skills),
            note="% of JD top skills present on profile",
        ),
        DimensionScore(
            name="education",
            mine=my_edu,
            peer_median=_median(peer_edu),
            percentile=_percentile(my_edu, peer_edu),
            note="Degree level rank",
        ),
        DimensionScore(
            name="seniority",
            mine=my_sen,
            peer_median=_median(peer_sen),
            percentile=_percentile(my_sen, peer_sen),
            note="Seniority band",
        ),
    ]

    # Weighted overall: skills dominate for fit
    weights = {
        "years_experience": 0.2,
        "jd_skill_coverage": 0.45,
        "education": 0.15,
        "seniority": 0.2,
    }
    overall_pct = sum(d.percentile * weights[d.name] for d in dims)
    overall_score = int(round(max(0, min(100, overall_pct))))

    strengths: list[str] = []
    gaps: list[str] = []
    recs: list[str] = []
    for d in dims:
        if d.percentile >= 60:
            strengths.append(f"{d.name}: {d.percentile:.0f}th percentile vs peers")
        elif d.percentile <= 40:
            gaps.append(f"{d.name}: {d.percentile:.0f}th percentile vs peers")

    # Skill-level gaps vs JD
    mine_keys = {_norm(s) for s in me.skills}
    for sk in jd_skills:
        key = _norm(sk.name)
        if key not in mine_keys and not (set(key.split()) & mine_keys):
            gaps.append(f"Missing JD skill: {sk.name}")
            if len(recs) < 5:
                recs.append(f"Add or demonstrate {sk.name} on resume/profile")

    if not recs and gaps:
        recs.append("Review gap list and prioritize high-importance JD skills")
    if not strengths:
        strengths.append("Keep applying — peer set may be senior-skewed")

    return BenchmarkReport(
        job_id=job.id,
        overall_score=overall_score,
        percentile=round(overall_pct, 1),
        dimensions=dims,
        strengths=strengths[:8],
        gaps=gaps[:12],
        recommendations=recs[:6],
        peer_count=len(peers),
    )


async def persist_peer_profile(
    data: PeerProfileData,
    *,
    is_self: bool = False,
    raw_text: str | None = None,
) -> PeerProfile:
    await init_db()
    now = datetime.now(UTC)
    async with session_scope() as session:
        row = PeerProfile(
            url=data.url,
            is_self=is_self,
            full_name=data.full_name,
            headline=data.headline,
            current_title=data.current_title,
            years_experience=data.years_experience,
            companies=list(data.companies),
            education_level=data.education_level,
            skills=list(data.skills),
            seniority=data.seniority,
            raw_text=raw_text,
            created_at=now,
            updated_at=now,
        )
        session.add(row)
        await session.flush()
        await session.refresh(row)
        return row


async def run_benchmark(
    job_id: int,
    *,
    peer_urls: list[str] | None = None,
    search_url: str | None = None,
    profile: Profile | None = None,
    peers: list[PeerProfileData] | None = None,
    jd_skills: list[JdSkill] | None = None,
    scrape: bool = False,
    auto_discover: bool = False,
) -> BenchmarkSummary:
    """Build and persist a benchmark for one job.

    When scrape=False (default in tests), supply `peers` and `jd_skills` directly.
    When scrape=True, requires ENABLE_LINKEDIN_SCRAPE and a saved LinkedIn session.
    When auto_discover=True, crawls LinkedIn People Search for peer /in/ URLs
    (implies scrape=True for those URLs).
    """
    await init_db()
    profile = profile or load_profile()
    settings = get_settings()

    async with session_scope() as session:
        job = await get_job_by_id(session, job_id)
    if job is None:
        raise ValueError(f"Job {job_id} not found")

    me = profile_to_peer_data(profile)

    if peers is None:
        peers = []
        from scraper.linkedin_people import (
            auto_discover_peers,
            discover_peers,
            parse_profile,
            scrape_profile,
        )

        urls = list(discover_peers(urls=peer_urls, search_url=search_url))
        do_scrape = scrape or auto_discover
        if auto_discover and not urls:
            urls = await auto_discover_peers(job, profile)
            do_scrape = True
        elif auto_discover and urls:
            log.info(
                "benchmark_auto_discover_skipped",
                reason="explicit urls already provided",
                count=len(urls),
            )

        if do_scrape and urls:
            for url in urls:
                try:
                    raw = await scrape_profile(url)
                    peers.append(await parse_profile(raw))
                except Exception as exc:
                    log.warning("benchmark_peer_scrape_failed", url=url, error=str(exc)[:200])
        elif urls and not do_scrape:
            log.warning(
                "benchmark_urls_without_scrape",
                count=len(urls),
                hint="Pass --scrape / scrape=True, or --auto",
            )

    if jd_skills is None:
        from resume.skills import extract_top_skills
        from scorer.clients import build_llm_client

        client = None
        if settings.resume_use_llm_tailoring:
            try:
                client = build_llm_client()
            except Exception:
                client = None
        jd_skills = await extract_top_skills(job, client=client)

    report = build_benchmark(job, me, peers, jd_skills)

    peer_ids: list[int] = []
    me_row = await persist_peer_profile(me, is_self=True)
    peer_ids.append(me_row.id or 0)
    for p in peers:
        row = await persist_peer_profile(p, is_self=False)
        if row.id is not None:
            peer_ids.append(row.id)

    out_dir = settings.benchmarks_path / str(job_id)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "benchmark.json"
    report_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    md_path = out_dir / "benchmark.md"
    md_lines = [
        f"# Benchmark — {job.title} @ {job.company}",
        "",
        f"Overall: **{report.overall_score}/100** ({report.percentile:.0f}th percentile)",
        f"Peers compared: {report.peer_count}",
        "",
        "## Dimensions",
    ]
    for d in report.dimensions:
        md_lines.append(
            f"- {d.name}: mine={d.mine}, peer_median={d.peer_median}, "
            f"percentile={d.percentile:.0f}"
        )
    md_lines += ["", "## Strengths", *[f"- {s}" for s in report.strengths]]
    md_lines += ["", "## Gaps", *[f"- {g}" for g in report.gaps]]
    md_lines += ["", "## Recommendations", *[f"- {r}" for r in report.recommendations]]
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    async with session_scope() as session:
        row = Benchmark(
            job_id=job_id,
            overall_score=report.overall_score,
            percentile=report.percentile,
            dimensions={d.name: d.model_dump() for d in report.dimensions},
            strengths=list(report.strengths),
            gaps=list(report.gaps),
            recommendations=list(report.recommendations),
            peer_ids=peer_ids,
            report_path=str(report_path),
            created_at=datetime.now(UTC),
        )
        session.add(row)

    log.info(
        "benchmark_complete",
        job_id=job_id,
        score=report.overall_score,
        peers=report.peer_count,
        path=str(report_path),
    )
    return BenchmarkSummary(
        report=report,
        peer_ids=peer_ids,
        report_path=str(report_path),
    )


__all__ = [
    "BenchmarkReport",
    "BenchmarkSummary",
    "DimensionScore",
    "build_benchmark",
    "profile_to_peer_data",
    "run_benchmark",
]

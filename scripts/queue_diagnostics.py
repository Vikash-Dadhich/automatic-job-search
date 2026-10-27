"""Read-only picture of the job pool: where jobs come from and what kind they are.

Prints GitHub annotations (at most 10 per step, so lines are grouped). Never writes.
"""

from __future__ import annotations

import asyncio
from collections import Counter
from datetime import UTC, datetime, timedelta

from sqlmodel import col, select

from core.db import Job, Status, session_scope
from scraper.title_family import title_family


def _note(title: str, lines: list[str]) -> None:
    text = " | ".join(lines)[:3500].replace("\n", " ")
    print(f"::notice title={title}::{text}", flush=True)


async def main(days: int = 30) -> None:
    since = datetime.now(UTC) - timedelta(days=days)
    async with session_scope() as session:
        jobs = list(
            (await session.exec(select(Job).where(col(Job.discovered_at) >= since))).all()
        )
    _note(f"pool last {days} days", [f"{len(jobs)} jobs"])
    by_source = Counter(str(job.source.value if job.source else "?") for job in jobs)
    _note("by source", [f"{k}: {v}" for k, v in by_source.most_common()])
    by_status = Counter(job.status.value for job in jobs)
    _note("by status", [f"{k}: {v}" for k, v in by_status.most_common()])
    fam = Counter((job.status.value, title_family(job.title) or "NOT_TARGET") for job in jobs)
    _note("status x title family", [f"{s}/{f}: {n}" for (s, f), n in sorted(fam.items())])
    llm = Counter(
        (title_family(job.title) or "NOT_TARGET", job.role_family or "NONE")
        for job in jobs
        if job.score is not None
    )
    _note(
        "scored: title family vs model family",
        [f"{a}->{b}: {n}" for (a, b), n in llm.most_common(25)],
    )
    reasons = Counter(
        (job.justification or ["?"])[0][:60]
        for job in jobs
        if job.status == Status.filtered_out and job.score is None
    )
    _note("filter reasons", [f"{r}: {n}" for r, n in reasons.most_common(15)])
    for family in ("PRODUCT_MANAGEMENT", "CONSULTING"):
        pool = sorted(
            (job for job in jobs if title_family(job.title) == family),
            key=lambda job: -(job.score or -1),
        )
        _note(
            f"{family} titles",
            [
                f"{job.status.value} s={job.score} v={job.vector_decision} "
                f"{job.title[:50]} @ {job.company[:20]}"
                for job in pool[:25]
            ],
        )
    unscored = Counter(
        title_family(job.title) or "NOT_TARGET"
        for job in jobs
        if job.status == Status.discovered
    )
    _note("waiting to be scored", [f"{k}: {v}" for k, v in unscored.most_common()])


if __name__ == "__main__":
    asyncio.run(main())

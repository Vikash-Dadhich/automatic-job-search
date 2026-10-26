"""Print the stage timings of the latest pipeline run as GitHub annotations.

Runs after the pipeline step even when that step timed out. A stage still marked
running is the one that was stuck. Reads only; never writes.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from sqlmodel import col, select

from core.db import PipelineRun, PipelineStageRun, session_scope


def _utc(moment: datetime) -> datetime:
    return moment if moment.tzinfo else moment.replace(tzinfo=UTC)


def describe(stage: PipelineStageRun, now: datetime) -> str:
    if stage.status == "running":
        waited = int((now - _utc(stage.started_at)).total_seconds())
        return f"STILL RUNNING after {waited}s"
    seconds = (stage.duration_ms or 0) // 1000
    note = f" ({stage.error[:80]})" if stage.error else ""
    return f"{stage.status} in {seconds}s{note}"


async def main() -> None:
    now = datetime.now(UTC)
    async with session_scope() as session:
        run = (
            await session.exec(select(PipelineRun).order_by(col(PipelineRun.id).desc()).limit(1))
        ).first()
        if run is None:
            print("::notice title=stage report::no pipeline run found")
            return
        stages = (
            await session.exec(
                select(PipelineStageRun)
                .where(col(PipelineStageRun.pipeline_run_id) == run.id)
                .order_by(col(PipelineStageRun.id))
            )
        ).all()
    print(f"::notice title=run {run.id}::status {run.status}, {len(stages)} stages")
    for stage in stages:
        print(f"::notice title=stage {stage.stage}::{describe(stage, now)}")


if __name__ == "__main__":
    asyncio.run(main())

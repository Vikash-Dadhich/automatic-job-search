"""Approve path: reopen Workday session and click Submit (only from Telegram)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import structlog

from automation.browser import SessionMissingError, launch_context, new_page
from automation.telemetry import human_delay
from automation.workday import (
    BlockerError,
    click_by_role,
    click_next,
    detect_blocker,
    is_review_page,
    screenshot,
)
from config.settings import get_settings
from core.db import Job

log = structlog.get_logger(__name__)

_MAX_PAGES = 12


@dataclass
class SubmitResult:
    submitted: bool
    screenshot_path: str | None = None
    reason: str | None = None


class Submitter(Protocol):
    """Injectable submitter used by handlers (mockable offline)."""

    async def submit(self, job: Job) -> SubmitResult: ...


class WorkdaySubmitter:
    """Reopen saved session, reach review, click Submit once."""

    def __init__(
        self,
        *,
        headless: bool | None = None,
        sessions_dir: Path | None = None,
    ) -> None:
        self._headless = headless
        self._sessions_dir = sessions_dir

    async def submit(self, job: Job) -> SubmitResult:
        if not job.url:
            return SubmitResult(submitted=False, reason="Job missing url")
        tenant = (job.tenant or "").strip()
        if not tenant:
            from config.targets import parse_workday_url

            try:
                tenant = parse_workday_url(job.url).tenant
            except ValueError as exc:
                return SubmitResult(
                    submitted=False,
                    reason=f"No tenant and URL not parseable: {exc}",
                )

        settings = get_settings()
        headless = settings.browser_headless if self._headless is None else self._headless

        try:
            async with launch_context(
                tenant,
                headless=headless,
                require_session=True,
                sessions_dir=self._sessions_dir,
            ) as (_pw, _browser, context):
                page = await new_page(context)
                await page.goto(job.url, wait_until="domcontentloaded")
                await human_delay(min_ms=400, max_ms=900)

                blocker = await detect_blocker(page)
                if blocker:
                    shot = await screenshot(page, job, suffix="submit_blocker")
                    raise BlockerError(
                        f"Blocker detected ({blocker})",
                        screenshot_path=str(shot),
                    )

                # Try to open application / resume draft
                await click_by_role(
                    page,
                    "button",
                    ["Apply", "Apply Now", "Continue Application", "Resume"],
                )
                await human_delay(min_ms=300, max_ms=700)

                reached_review = False
                for _step in range(_MAX_PAGES):
                    await human_delay(min_ms=200, max_ms=500)
                    blocker = await detect_blocker(page)
                    if blocker:
                        shot = await screenshot(page, job, suffix="submit_blocker")
                        raise BlockerError(
                            f"Blocker mid-form ({blocker})",
                            screenshot_path=str(shot),
                        )
                    try:
                        page_text = await page.locator("body").inner_text(timeout=3000)
                    except Exception:
                        page_text = ""

                    if is_review_page(page_text, page.url):
                        reached_review = True
                        break
                    advanced = await click_next(page)
                    if not advanced:
                        if is_review_page(page_text, page.url):
                            reached_review = True
                        break

                if not reached_review:
                    shot = await screenshot(page, job, suffix="submit_no_review")
                    return SubmitResult(
                        submitted=False,
                        screenshot_path=str(shot),
                        reason="Could not reach review page",
                    )

                # THE ONLY place that clicks Submit
                clicked = await click_by_role(
                    page,
                    "button",
                    ["Submit Application", "Submit", "Send Application"],
                )
                if not clicked:
                    shot = await screenshot(page, job, suffix="submit_missing")
                    return SubmitResult(
                        submitted=False,
                        screenshot_path=str(shot),
                        reason="Submit button not found",
                    )

                await human_delay(min_ms=500, max_ms=1200)
                blocker = await detect_blocker(page)
                if blocker:
                    shot = await screenshot(page, job, suffix="submit_blocker")
                    raise BlockerError(
                        f"Blocker after Submit ({blocker})",
                        screenshot_path=str(shot),
                    )

                shot = await screenshot(page, job, suffix="submitted")
                log.info("workday_submitted", job_id=job.id, screenshot=str(shot))
                return SubmitResult(
                    submitted=True,
                    screenshot_path=str(shot),
                    reason="submitted",
                )
        except BlockerError as exc:
            return SubmitResult(
                submitted=False,
                screenshot_path=exc.screenshot_path,
                reason=str(exc),
            )
        except SessionMissingError as exc:
            return SubmitResult(submitted=False, reason=str(exc))
        except Exception as exc:
            log.warning("workday_submit_failed", job_id=job.id, error=str(exc))
            return SubmitResult(submitted=False, reason=str(exc))

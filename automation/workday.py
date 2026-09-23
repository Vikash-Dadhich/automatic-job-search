"""Workday application pre-fill: stop at review, never submit."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol, cast

import structlog
from playwright.async_api import Locator, Page

from automation.answers import AnswerResolver, ResolvedAnswer, answers_to_payload
from automation.browser import SessionMissingError, launch_context, new_page
from automation.telemetry import human_delay, type_like_human
from config.profile import Profile, load_profile
from config.settings import get_settings
from core.db import Job

log = structlog.get_logger(__name__)

_MAX_PAGES = 12
_BLOCKER_HINTS = (
    "cf-challenge",
    "challenge-platform",
    "just a moment",
    "attention required",
    "verify you are human",
    "cloudflare",
    "access denied",
    "multi-factor",
    "two-factor",
    "enter the code",
    "verification code",
    "captcha",
)


class BlockerError(RuntimeError):
    """Cloudflare / MFA / unknown hard stop — yield to manual review."""

    def __init__(self, message: str, *, screenshot_path: str | None = None) -> None:
        super().__init__(message)
        self.screenshot_path = screenshot_path


@dataclass
class ApplyResult:
    """Outcome of a single Workday pre-fill attempt."""

    screenshot_path: str | None = None
    application_answers: dict[str, Any] | None = None
    answers: list[ResolvedAnswer] = field(default_factory=list)
    reached_review: bool = False


class Applicator(Protocol):
    """Injectable applicator used by the runner (mockable offline)."""

    async def apply(self, job: Job) -> ApplyResult: ...


async def screenshot(page: Page, job: Job, *, suffix: str = "review") -> Path:
    settings = get_settings()
    out_dir = settings.screenshots_path / str(job.id or "unknown")
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{suffix}.png"
    await page.screenshot(path=str(path), full_page=True)
    return path


async def detect_blocker(page: Page) -> str | None:
    """Return a short reason if the page looks like a bot/MFA wall."""
    try:
        title = (await page.title() or "").lower()
        url = (page.url or "").lower()
        body = ""
        try:
            body = (await page.locator("body").inner_text(timeout=2000) or "")[:2000].lower()
        except Exception:
            body = ""
        blob = f"{title}\n{url}\n{body}"
        for hint in _BLOCKER_HINTS:
            if hint in blob:
                return hint
    except Exception as exc:
        log.warning("blocker_detect_failed", error=str(exc))
    return None


async def safe_click(locator: Locator) -> bool:
    try:
        if await locator.count() == 0:
            return False
        target = locator.first
        if not await target.is_visible():
            return False
        await human_delay()
        await target.click()
        return True
    except Exception:
        return False


async def click_by_role(page: Page, role: str, name: str | list[str]) -> bool:
    names = [name] if isinstance(name, str) else name
    for n in names:
        # Playwright types role as a Literal; callers pass ergonomic strings.
        loc = page.get_by_role(cast(Any, role), name=n, exact=False)
        if await safe_click(loc):
            return True
    return False


async def _upload_resume(page: Page, resume_path: Path) -> bool:
    """Attach resume via file input (accessibility-friendly when labeled)."""
    if not resume_path.is_file():
        raise FileNotFoundError(f"Resume not found: {resume_path}")

    # Prefer labeled file inputs
    for label in ("Resume", "Upload Resume", "CV", "Attach Resume", "Select file"):
        try:
            loc = page.get_by_label(label, exact=False)
            if await loc.count() > 0:
                await loc.first.set_input_files(str(resume_path))
                await human_delay()
                return True
        except Exception:
            continue

    # Fallback: any file input
    try:
        file_inputs = page.locator('input[type="file"]')
        if await file_inputs.count() > 0:
            await file_inputs.first.set_input_files(str(resume_path))
            await human_delay()
            return True
    except Exception as exc:
        log.warning("resume_upload_failed", error=str(exc))
    return False


async def _collect_labeled_fields(page: Page) -> list[tuple[str, Locator]]:
    """Discover fillable controls via accessible names (get_by_label / roles)."""
    fields: list[tuple[str, Locator]] = []
    seen: set[str] = set()

    # Textboxes / comboboxes with accessible names
    for role in ("textbox", "combobox", "searchbox"):
        loc = page.get_by_role(role)
        count = await loc.count()
        for i in range(count):
            item = loc.nth(i)
            try:
                if not await item.is_visible():
                    continue
                name = (await item.get_attribute("aria-label")) or ""
                if not name:
                    # Try associated label via accessible name
                    name = await item.evaluate(
                        """el => {
                          const id = el.getAttribute('id');
                          if (id) {
                            const lab = document.querySelector(`label[for="${id}"]`);
                            if (lab) return lab.textContent || '';
                          }
                          const wrapped = el.closest('label');
                          if (wrapped) return wrapped.textContent || '';
                          return el.getAttribute('placeholder') || el.getAttribute('name') || '';
                        }"""
                    )
                label = " ".join((name or "").split())
                if not label or label.lower() in seen:
                    continue
                seen.add(label.lower())
                fields.append((label, item))
            except Exception:
                continue
    return fields


async def _fill_field(locator: Locator, value: str) -> None:
    if not value:
        return
    try:
        tag = await locator.evaluate("el => (el.tagName || '').toLowerCase()")
        role = await locator.get_attribute("role")
        if tag == "select" or role == "combobox":
            try:
                await locator.select_option(label=value)
            except Exception:
                try:
                    await locator.select_option(value=value)
                except Exception:
                    await type_like_human(locator, value)
        else:
            await type_like_human(locator, value)
        await human_delay()
    except Exception as exc:
        log.warning("fill_field_failed", error=str(exc))


def is_review_page(page_text: str, url: str) -> bool:
    blob = f"{page_text}\n{url}".lower()
    review_hints = (
        "review your application",
        "review application",
        "please review",
        "submit application",
        "ready to submit",
        "/review",
    )
    return any(h in blob for h in review_hints)


async def click_next(page: Page) -> bool:
    """Advance a multi-step form without submitting the final application."""
    # Never click Submit / Submit Application
    for name in ("Next", "Continue", "Save and Continue", "Save & Continue"):
        if await click_by_role(page, "button", name):
            return True
    return False


class WorkdayApplicator:
    """Pre-fill a Workday application and pause at the review screen."""

    def __init__(
        self,
        *,
        profile: Profile | None = None,
        answer_resolver: AnswerResolver | None = None,
        headless: bool | None = None,
        sessions_dir: Path | None = None,
    ) -> None:
        self._profile = profile
        self._answer_resolver = answer_resolver
        self._headless = headless
        self._sessions_dir = sessions_dir

    def _resolve_profile(self) -> Profile:
        return self._profile or load_profile()

    def _resolve_answers(self) -> AnswerResolver:
        if self._answer_resolver is not None:
            return self._answer_resolver
        return AnswerResolver(self._resolve_profile())

    async def apply(self, job: Job) -> ApplyResult:
        if not job.url:
            raise ValueError("Job missing url")
        if not job.resume_path:
            raise ValueError("Job missing resume_path")
        tenant = (job.tenant or "").strip()
        if not tenant:
            # Best-effort: parse from URL host
            from config.targets import parse_workday_url

            try:
                tenant = parse_workday_url(job.url).tenant
            except ValueError as exc:
                raise ValueError(
                    f"Job {job.id} has no tenant and URL is not parseable: {exc}"
                ) from exc

        resume_path = Path(job.resume_path)
        resolver = self._resolve_answers()
        collected: list[ResolvedAnswer] = []

        try:
            async with launch_context(
                tenant,
                headless=self._headless,
                require_session=True,
                sessions_dir=self._sessions_dir,
            ) as (_pw, _browser, context):
                page = await new_page(context)
                await page.goto(job.url, wait_until="domcontentloaded")
                await human_delay(min_ms=400, max_ms=900)

                blocker = await detect_blocker(page)
                if blocker:
                    shot = await screenshot(page, job, suffix="blocker")
                    raise BlockerError(
                        f"Blocker detected ({blocker})",
                        screenshot_path=str(shot),
                    )

                # Start application
                started = await click_by_role(
                    page,
                    "button",
                    ["Apply", "Apply Now", "Start Your Application", "Autofill with Resume"],
                )
                if not started:
                    started = await click_by_role(
                        page,
                        "link",
                        ["Apply", "Apply Now"],
                    )
                await human_delay(min_ms=300, max_ms=700)

                blocker = await detect_blocker(page)
                if blocker:
                    shot = await screenshot(page, job, suffix="blocker")
                    raise BlockerError(
                        f"Blocker detected after Apply ({blocker})",
                        screenshot_path=str(shot),
                    )

                # Resume upload (best-effort)
                await _upload_resume(page, resume_path)

                reached_review = False
                for _step in range(_MAX_PAGES):
                    await human_delay(min_ms=200, max_ms=500)
                    blocker = await detect_blocker(page)
                    if blocker:
                        shot = await screenshot(page, job, suffix="blocker")
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

                    fields = await _collect_labeled_fields(page)
                    for label, locator in fields:
                        resolved = await resolver.resolve(label, job=job)
                        collected.append(resolved)
                        if resolved.answer:
                            await _fill_field(locator, resolved.answer)

                    # Prefer Autofill with Resume if still offered
                    await click_by_role(
                        page,
                        "button",
                        ["Autofill with Resume", "Use My Last Application"],
                    )

                    advanced = await click_next(page)
                    if not advanced:
                        # Maybe already on review without clear wording
                        if is_review_page(page_text, page.url):
                            reached_review = True
                        break

                shot = await screenshot(
                    page,
                    job,
                    suffix="review" if reached_review else "paused",
                )
                # Safety: never click Submit
                payload = answers_to_payload(collected)
                return ApplyResult(
                    screenshot_path=str(shot),
                    application_answers=payload,
                    answers=collected,
                    reached_review=reached_review,
                )
        except BlockerError:
            raise
        except SessionMissingError as exc:
            raise BlockerError(str(exc), screenshot_path=None) from exc
        except Exception:
            raise

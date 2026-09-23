"""Stealth Playwright browser context using saved Workday sessions."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import structlog
from playwright.async_api import Browser, BrowserContext, Page, Playwright, async_playwright

from automation.vault import has_saved_session, session_state_path
from config.settings import get_settings

log = structlog.get_logger(__name__)

# Lightweight in-repo stealth patches (avoid brittle third-party packages).
_STEALTH_INIT_SCRIPT = """
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
window.chrome = window.chrome || { runtime: {} };
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) => (
  parameters.name === 'notifications'
    ? Promise.resolve({ state: Notification.permission })
    : originalQuery(parameters)
);
"""


class SessionMissingError(RuntimeError):
    """Raised when no reusable storage_state exists for a tenant."""


async def _new_context(
    browser: Browser,
    *,
    storage_state: Path | None,
    headless: bool,  # noqa: ARG001 — recorded for logging only; launch owns headless
) -> BrowserContext:
    kwargs: dict[str, Any] = {
        "viewport": {"width": 1280, "height": 900},
        "locale": "en-US",
        "timezone_id": get_settings().timezone,
        "user_agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
    }
    if storage_state is not None and storage_state.is_file():
        kwargs["storage_state"] = str(storage_state)

    context = await browser.new_context(**kwargs)
    await context.add_init_script(_STEALTH_INIT_SCRIPT)
    return context


@asynccontextmanager
async def launch_context(
    tenant: str,
    *,
    headless: bool | None = None,
    require_session: bool = True,
    sessions_dir: Path | None = None,
) -> AsyncIterator[tuple[Playwright, Browser, BrowserContext]]:
    """Launch Chromium with stealth patches and optional saved storage_state.

    Yields (playwright, browser, context). Caller must not use after exit.
    """
    settings = get_settings()
    use_headless = settings.browser_headless if headless is None else headless
    state_path = session_state_path(tenant, sessions_dir=sessions_dir)

    if require_session and not has_saved_session(tenant, sessions_dir=sessions_dir):
        raise SessionMissingError(
            f"No saved session for tenant {tenant!r}. "
            "Run automation.login.save_session(...) once (manual placeholder)."
        )

    storage = state_path if state_path.is_file() else None
    log.info(
        "browser_launch",
        tenant=tenant,
        headless=use_headless,
        session=str(storage) if storage else None,
    )

    async with async_playwright() as playwright:
        launch_kwargs: dict[str, Any] = {"headless": use_headless}
        if settings.browser_channel:
            launch_kwargs["channel"] = settings.browser_channel
        browser = await playwright.chromium.launch(**launch_kwargs)
        try:
            context = await _new_context(
                browser,
                storage_state=storage,
                headless=use_headless,
            )
            try:
                yield playwright, browser, context
            finally:
                await context.close()
        finally:
            await browser.close()


async def new_page(context: BrowserContext) -> Page:
    return await context.new_page()


async def save_storage_state(context: BrowserContext, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    await context.storage_state(path=str(path))
    log.info("storage_state_saved", path=str(path))
    return path

"""One-time interactive LinkedIn login helper (manual MFA).

Opens a headful browser on linkedin.com, waits for you to finish login / MFA,
then writes Playwright storage_state for reuse by the people scraper.

Usage:
  uv run python -c "import asyncio; from scraper.linkedin_session import save_linkedin_session; \\
    print(asyncio.run(save_linkedin_session()))"
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import structlog

from automation.browser import launch_context, new_page, save_storage_state
from automation.vault import session_state_path
from config.settings import get_settings

log = structlog.get_logger(__name__)

LINKEDIN_TENANT = "linkedin"
DEFAULT_LOGIN_TIMEOUT_S = 10 * 60
LINKEDIN_HOME = "https://www.linkedin.com/login"


async def save_linkedin_session(
    *,
    timeout_s: float = DEFAULT_LOGIN_TIMEOUT_S,
    sessions_dir: Path | None = None,
    wait_for_enter: bool = True,
) -> Path:
    """Open headful browser; after manual LinkedIn login, persist storage_state."""
    out = session_state_path(LINKEDIN_TENANT, sessions_dir=sessions_dir)
    settings = get_settings()
    out.parent.mkdir(parents=True, exist_ok=True)

    log.info(
        "save_linkedin_session_start",
        out=str(out),
        headless=False,
        timezone=settings.timezone,
    )

    async with launch_context(
        LINKEDIN_TENANT,
        headless=False,
        require_session=False,
        sessions_dir=sessions_dir,
    ) as (_pw, _browser, context):
        page = await new_page(context)
        await page.goto(LINKEDIN_HOME, wait_until="domcontentloaded")
        print(
            "\n=== Manual LinkedIn login required ===\n"
            "1. Complete login / MFA in the opened browser.\n"
            "2. Confirm you can see your LinkedIn feed while signed in.\n"
            "3. Return here and press Enter to save the session to:\n"
            f"   {out}\n"
            f"(Timeout: {int(timeout_s)}s)\n"
        )
        if wait_for_enter:
            await asyncio.wait_for(
                asyncio.to_thread(input, "Press Enter after login... "),
                timeout=timeout_s,
            )
        await save_storage_state(context, out)

    log.info("save_linkedin_session_complete", path=str(out))
    return out

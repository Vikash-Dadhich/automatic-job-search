"""One-time interactive Workday login helper (manual placeholder).

Opens a headful browser on the tenant careers site, waits for you to finish
login / MFA, then writes Playwright storage_state for reuse by the applicator.

Usage (manual, do last):
  uv run python -c "import asyncio; from automation import save_session; \\
    print(asyncio.run(save_session('https://TENANT.wd5.myworkdayjobs.com/en-US/External')))"
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import structlog

from automation.browser import launch_context, new_page, save_storage_state
from automation.vault import session_state_path
from config.settings import get_settings
from config.targets import parse_workday_url

log = structlog.get_logger(__name__)

# How long to wait for the human to finish login/MFA before giving up.
DEFAULT_LOGIN_TIMEOUT_S = 10 * 60


async def save_session(
    tenant_url: str,
    *,
    timeout_s: float = DEFAULT_LOGIN_TIMEOUT_S,
    sessions_dir: Path | None = None,
    wait_for_enter: bool = True,
) -> Path:
    """Open headful browser; after manual login, persist storage_state.

    Parameters
    ----------
    tenant_url:
        Any Workday careers / job URL for the tenant (parsed for tenant slug).
    timeout_s:
        Max seconds to wait for manual login confirmation.
    sessions_dir:
        Override for where to write ``{tenant}.json``.
    wait_for_enter:
        If True (default), wait until stdin Enter is pressed after login.
        Set False in automated tests that inject cookies another way.
    """
    parts = parse_workday_url(tenant_url)
    tenant = parts.tenant
    out = session_state_path(tenant, sessions_dir=sessions_dir)
    settings = get_settings()
    out.parent.mkdir(parents=True, exist_ok=True)

    log.info(
        "save_session_start",
        tenant=tenant,
        url=parts.public_base,
        out=str(out),
        headless=False,
        timezone=settings.timezone,
    )

    async with launch_context(
        tenant,
        headless=False,
        require_session=False,
        sessions_dir=sessions_dir,
    ) as (_pw, _browser, context):
        page = await new_page(context)
        await page.goto(parts.public_base, wait_until="domcontentloaded")
        print(
            f"\n=== Manual login required for tenant '{tenant}' ===\n"
            f"1. Complete login / MFA in the opened browser.\n"
            f"2. Confirm you can see the careers site while signed in.\n"
            f"3. Return here and press Enter to save the session to:\n"
            f"   {out}\n"
            f"(Timeout: {int(timeout_s)}s)\n"
        )
        if wait_for_enter:
            await asyncio.wait_for(
                asyncio.to_thread(input, "Press Enter after login... "),
                timeout=timeout_s,
            )
        await save_storage_state(context, out)

    log.info("save_session_complete", tenant=tenant, path=str(out))
    return out

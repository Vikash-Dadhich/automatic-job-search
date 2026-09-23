"""Optional Playwright locator smoke test against a local HTML fixture.

Skipped automatically when Chromium is not installed so CI stays offline-green.
"""

from __future__ import annotations

from pathlib import Path

import pytest

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "workday_form.html"


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            browser.close()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _chromium_available(),
    reason="Chromium not installed (run: uv run playwright install chromium)",
)


@pytest.mark.asyncio
async def test_accessibility_locators_on_fixture() -> None:
    from playwright.async_api import async_playwright

    assert FIXTURE.is_file()
    url = FIXTURE.as_uri()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)

        email = page.get_by_label("Email Address", exact=False)
        assert await email.count() == 1
        await email.fill("you@example.com")
        assert await email.input_value() == "you@example.com"

        phone = page.get_by_role("textbox", name="Phone Number")
        assert await phone.count() == 1

        next_btn = page.get_by_role("button", name="Next")
        submit_btn = page.get_by_role("button", name="Submit Application")
        assert await next_btn.count() == 1
        assert await submit_btn.count() == 1
        # Safety posture: tests never click Submit
        await next_btn.click()

        await browser.close()

"""LinkedIn people profile scrape + parse (authenticated session).

Default posture is conservative: headful, long jitter, semi-automated peer URLs,
and blocker abort. Enable via ENABLE_LINKEDIN_SCRAPE=true.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol

import structlog
from pydantic import BaseModel, Field

from automation.browser import SessionMissingError, launch_context, new_page
from automation.telemetry import human_delay
from config.settings import get_settings
from scraper.linkedin_session import LINKEDIN_TENANT

log = structlog.get_logger(__name__)

_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)```", re.IGNORECASE)


class BlockerError(RuntimeError):
    """LinkedIn checkpoint / login wall / Cloudflare detected."""

    def __init__(self, message: str, *, screenshot_path: str | None = None) -> None:
        super().__init__(message)
        self.screenshot_path = screenshot_path


class RawProfile(BaseModel):
    """Raw text extracted from a LinkedIn profile page."""

    url: str
    headline: str = ""
    about: str = ""
    experience_text: str = ""
    education_text: str = ""
    skills_text: str = ""
    full_text: str = ""


class PeerProfileData(BaseModel):
    """Normalized peer profile for benchmarking."""

    url: str
    full_name: str | None = None
    headline: str | None = None
    current_title: str | None = None
    years_experience: float | None = None
    companies: list[str] = Field(default_factory=list)
    education_level: str | None = None
    skills: list[str] = Field(default_factory=list)
    seniority: str | None = None


class LLMClient(Protocol):
    async def complete(
        self,
        *,
        model: str,
        system_blocks: list[dict[str, Any]],
        user: str,
        max_tokens: int,
        temperature: float,
        json_mode: bool = False,
    ) -> str: ...


PROFILE_PARSE_SYSTEM = """\
You parse a LinkedIn profile text dump into structured JSON.
Return ONLY JSON (no markdown):
{
  "full_name": "...",
  "headline": "...",
  "current_title": "...",
  "years_experience": <number or null>,
  "companies": ["..."],
  "education_level": "bachelor|master|mba|phd|other|null",
  "skills": ["..."],
  "seniority": "intern|junior|mid|senior|staff|principal|manager|director|vp|other"
}
Invent nothing beyond the text. If unknown, use null or [].
"""


@dataclass
class ScrapeSummary:
    scraped: int = 0
    errors: int = 0
    error_details: list[str] = field(default_factory=list)


def _require_enabled() -> None:
    settings = get_settings()
    if not settings.enable_linkedin_scrape:
        raise RuntimeError(
            "LinkedIn scrape is disabled. Set ENABLE_LINKEDIN_SCRAPE=true to proceed."
        )


async def _detect_blocker(page: Any, *, screenshots_dir: Path) -> None:
    url = (page.url or "").lower()
    title = ""
    try:
        title = (await page.title() or "").lower()
    except Exception:
        title = ""
    body = ""
    try:
        body = (await page.inner_text("body") or "")[:2000].lower()
    except Exception:
        body = ""

    blocked = any(
        needle in url or needle in title or needle in body
        for needle in (
            "checkpoint",
            "challenge",
            "authwall",
            "login",
            "captcha",
            "unusual activity",
            "security verification",
            "cloudflare",
        )
    )
    # Feed/profile pages contain "login" in footer links — require stronger signal
    strong = any(
        needle in url or needle in title
        for needle in ("checkpoint", "challenge", "authwall", "/login", "captcha")
    ) or "unusual activity" in body or "security verification" in body
    if strong or (blocked and "feed" not in url and "/in/" not in url):
        shot = screenshots_dir / f"linkedin_blocker_{int(datetime.now(UTC).timestamp())}.png"
        shot.parent.mkdir(parents=True, exist_ok=True)
        try:
            await page.screenshot(path=str(shot), full_page=True)
        except Exception:
            shot = None
        raise BlockerError(
            f"LinkedIn blocker detected at {page.url}",
            screenshot_path=str(shot) if shot else None,
        )


def parse_profile_html(html: str, url: str) -> RawProfile:
    """Offline-friendly extraction from saved HTML (tests / fixtures)."""
    from selectolax.parser import HTMLParser

    tree = HTMLParser(html or "")
    text = tree.body.text(separator="\n") if tree.body else ""
    # Heuristic section splits
    headline = ""
    h1 = tree.css_first("h1")
    if h1:
        headline = h1.text(strip=True)

    def _section(label: str) -> str:
        pattern = re.compile(
            rf"{label}\s*\n([\s\S]*?)(?=\n(?:About|Experience|Education|Skills|Licenses)\b|$)",
            re.IGNORECASE,
        )
        m = pattern.search(text)
        return (m.group(1).strip() if m else "")[:4000]

    return RawProfile(
        url=url,
        headline=headline,
        about=_section("About"),
        experience_text=_section("Experience"),
        education_text=_section("Education"),
        skills_text=_section("Skills"),
        full_text=text[:12000],
    )


async def scrape_profile(
    url: str,
    *,
    context: Any | None = None,
    sessions_dir: Path | None = None,
) -> RawProfile:
    """Navigate to a LinkedIn profile URL and extract visible text sections."""
    _require_enabled()
    settings = get_settings()
    screenshots = settings.screenshots_path

    async def _extract(page: Any) -> RawProfile:
        await human_delay(min_ms=800, max_ms=2000)
        await page.goto(url, wait_until="domcontentloaded")
        await human_delay(min_ms=1200, max_ms=2800)
        await _detect_blocker(page, screenshots_dir=screenshots)
        # Expand common "see more" buttons when present
        for role_name in ("See more", "Show more", "see more"):
            try:
                btn = page.get_by_role("button", name=re.compile(role_name, re.I))
                count = await btn.count()
                for i in range(min(count, 5)):
                    await btn.nth(i).click(timeout=1500)
                    await human_delay(min_ms=200, max_ms=600)
            except Exception:
                continue
        html = await page.content()
        return parse_profile_html(html, url)

    if context is not None:
        page = await new_page(context)
        try:
            return await _extract(page)
        finally:
            await page.close()

    headless = settings.linkedin_headless
    try:
        async with launch_context(
            LINKEDIN_TENANT,
            headless=headless,
            require_session=True,
            sessions_dir=sessions_dir,
        ) as (_pw, _browser, ctx):
            page = await new_page(ctx)
            try:
                return await _extract(page)
            finally:
                await page.close()
    except SessionMissingError as exc:
        raise RuntimeError(
            "No LinkedIn session. Run scraper.linkedin_session.save_linkedin_session() first."
        ) from exc


def parse_profile_json(text: str, url: str) -> PeerProfileData:
    cleaned = (text or "").strip()
    fence = _FENCE_RE.search(cleaned)
    if fence:
        cleaned = fence.group(1).strip()
    data = json.loads(cleaned)
    if not isinstance(data, dict):
        raise ValueError("Expected JSON object for peer profile")
    data["url"] = url
    return PeerProfileData.model_validate(data)


async def parse_profile(
    raw: RawProfile,
    *,
    client: LLMClient | None = None,
) -> PeerProfileData:
    """Parse RawProfile into PeerProfileData via LLM, with heuristic fallback."""
    if client is None:
        return _heuristic_parse(raw)

    from config.settings import get_settings

    settings = get_settings()
    user = (
        f"URL: {raw.url}\nHeadline: {raw.headline}\n\n"
        f"About:\n{raw.about}\n\nExperience:\n{raw.experience_text}\n\n"
        f"Education:\n{raw.education_text}\n\nSkills:\n{raw.skills_text}\n\n"
        f"Full text (truncated):\n{raw.full_text[:6000]}"
    )
    try:
        text = await client.complete(
            model=settings.active_writer_model,
            system_blocks=[{"type": "text", "text": PROFILE_PARSE_SYSTEM}],
            user=user,
            max_tokens=1024,
            temperature=0.0,
            json_mode=True,
        )
        return parse_profile_json(text, raw.url)
    except Exception as exc:
        log.warning("peer_parse_fallback", url=raw.url, error=str(exc))
        return _heuristic_parse(raw)


def _heuristic_parse(raw: RawProfile) -> PeerProfileData:
    skills = [
        s.strip()
        for s in re.split(r"[,•|\n]", raw.skills_text)
        if s.strip() and len(s.strip()) < 40
    ][:30]
    companies: list[str] = []
    for line in raw.experience_text.splitlines():
        line = line.strip()
        if line and len(line) < 80 and not line.startswith("·"):
            companies.append(line)
            if len(companies) >= 5:
                break
    return PeerProfileData(
        url=raw.url,
        full_name=None,
        headline=raw.headline or None,
        current_title=raw.headline or None,
        years_experience=None,
        companies=companies,
        education_level=None,
        skills=skills,
        seniority=None,
    )


def discover_peers(
    *,
    urls: list[str] | None = None,
    search_url: str | None = None,
) -> list[str]:
    """Return peer profile URLs.

    Semi-automated by default: caller supplies explicit profile URLs and/or one
    search URL (search URL itself is returned for the caller to open; full
    auto-search is behind linkedin_auto_search / auto_discover_peers).
    """
    settings = get_settings()
    found: list[str] = []
    for url in urls or []:
        u = (url or "").strip()
        if u and u not in found:
            found.append(u)
    if search_url and settings.linkedin_auto_search:
        log.info(
            "linkedin_auto_search_use_auto_discover",
            search_url=search_url,
            hint="Prefer auto_discover_peers() which crawls the search page",
        )
    elif search_url and not urls:
        log.info(
            "linkedin_search_url_received",
            search_url=search_url,
            hint="Open the search, copy /in/ URLs, re-run with --urls — or use --auto",
        )
    return found[: settings.linkedin_max_peers]


_PROFILE_URL_RE = re.compile(
    r"https?://(?:www\.)?linkedin\.com/in/[A-Za-z0-9\-_%]+/?",
    re.IGNORECASE,
)


def build_people_search_url(
    *,
    title: str,
    location: str | None = None,
    company: str | None = None,
) -> str:
    """Build a LinkedIn People Search URL from role keywords."""
    from urllib.parse import quote_plus

    parts = [title.strip()]
    if company and company.strip():
        parts.append(company.strip())
    if location and location.strip() and location.strip().lower() != "remote":
        # Use city only — full "Seattle, WA, United States" confuses the search.
        city = location.split(",")[0].strip()
        if city:
            parts.append(city)
    keywords = " ".join(p for p in parts if p)
    return (
        "https://www.linkedin.com/search/results/people/"
        f"?keywords={quote_plus(keywords)}&origin=GLOBAL_SEARCH_HEADER"
    )


def extract_profile_urls(html: str, *, max_peers: int) -> list[str]:
    """Pull unique /in/ profile URLs from a search-results HTML dump."""
    found: list[str] = []
    seen: set[str] = set()
    for match in _PROFILE_URL_RE.finditer(html or ""):
        url = match.group(0).split("?")[0].rstrip("/")
        # Normalize to https://www.linkedin.com/in/slug
        key = url.lower()
        if key in seen:
            continue
        # Skip LinkedIn's own vanity pages that aren't people.
        slug = key.rsplit("/in/", 1)[-1]
        if slug in {"", "unavailable", "sales", "talent"}:
            continue
        seen.add(key)
        found.append(url)
        if len(found) >= max_peers:
            break
    return found


async def auto_discover_peers(
    job: Any,
    profile: Any,
    *,
    max_peers: int | None = None,
    context: Any | None = None,
    sessions_dir: Path | None = None,
) -> list[str]:
    """Crawl LinkedIn People Search for peers matching this job's title.

    Requires ENABLE_LINKEDIN_SCRAPE=true and a saved LinkedIn session.
    Returns concrete /in/ URLs (never scrapes the profiles themselves).
    """
    _require_enabled()
    settings = get_settings()
    limit = max_peers if max_peers is not None else settings.linkedin_max_peers
    title = (getattr(job, "title", None) or "").strip() or "Product Manager"
    location = None
    prefs = getattr(profile, "preferences", None)
    if prefs is not None:
        locs = getattr(prefs, "locations", None) or []
        for loc in locs:
            if str(loc).strip().lower() != "remote":
                location = str(loc).strip()
                break
    if not location:
        identity = getattr(profile, "identity", None)
        location = getattr(identity, "location", None) if identity else None

    search_url = build_people_search_url(
        title=title, location=location, company=None
    )
    # Prefer title+location over title+company — company-filtered search often
    # returns only current employees of that one employer.
    log.info(
        "linkedin_auto_discover_start",
        title=title,
        location=location,
        search_url=search_url,
        max_peers=limit,
    )

    screenshots = settings.screenshots_path

    async def _crawl(page: Any) -> list[str]:
        await human_delay(min_ms=800, max_ms=1800)
        await page.goto(search_url, wait_until="domcontentloaded")
        await human_delay(min_ms=1500, max_ms=3200)
        await _detect_blocker(page, screenshots_dir=screenshots)
        # Scroll to load more result cards
        for _ in range(3):
            try:
                await page.mouse.wheel(0, 2400)
            except Exception:
                break
            await human_delay(min_ms=600, max_ms=1400)
        html = await page.content()
        urls = extract_profile_urls(html, max_peers=limit)
        if not urls:
            # Fallback: collect hrefs from anchors when the SPA embeds relative paths.
            try:
                hrefs = await page.eval_on_selector_all(
                    "a[href*='/in/']",
                    "els => els.map(e => e.href)",
                )
            except Exception:
                hrefs = []
            urls = extract_profile_urls("\n".join(hrefs or []), max_peers=limit)
        return urls

    if context is not None:
        page = await new_page(context)
        try:
            urls = await _crawl(page)
        finally:
            await page.close()
    else:
        headless = settings.linkedin_headless
        try:
            async with launch_context(
                LINKEDIN_TENANT,
                headless=headless,
                require_session=True,
                sessions_dir=sessions_dir,
            ) as (_pw, _browser, ctx):
                page = await new_page(ctx)
                try:
                    urls = await _crawl(page)
                finally:
                    await page.close()
        except SessionMissingError as exc:
            raise RuntimeError(
                "No LinkedIn session. Run scraper.linkedin_session.save_linkedin_session() first."
            ) from exc

    log.info("linkedin_auto_discover_done", count=len(urls), urls=urls[:5])
    return urls


__all__ = [
    "BlockerError",
    "PeerProfileData",
    "RawProfile",
    "ScrapeSummary",
    "auto_discover_peers",
    "build_people_search_url",
    "discover_peers",
    "extract_profile_urls",
    "parse_profile",
    "parse_profile_html",
    "parse_profile_json",
    "scrape_profile",
]

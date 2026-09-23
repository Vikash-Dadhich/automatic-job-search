"""Regression test: Workday detail responses must attach to the right listing."""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

from config.targets import WorkdayTenant, parse_workday_url
from scraper import workday_rest

_CAREERS_URL = "https://acme.wd1.myworkdayjobs.com/en-US/careers"


@pytest.mark.asyncio
async def test_details_pair_with_correct_listing(monkeypatch: pytest.MonkeyPatch) -> None:
    """A listing without externalPath used to shift details onto the wrong jobs."""
    parts = parse_workday_url(_CAREERS_URL)

    listings = [
        {"title": "Alpha PM", "postedOn": "Posted Today"},  # no externalPath
        {"title": "Beta PM", "postedOn": "Posted Today", "externalPath": "/job/beta"},
        {"title": "Gamma PM", "postedOn": "Posted Today", "externalPath": "/job/gamma"},
    ]

    async def fake_listing(
        client: Any, p: Any, *, search_text: str, offset: int
    ) -> dict[str, Any]:
        if offset:
            return {"jobPostings": [], "total": len(listings)}
        return {"jobPostings": listings, "total": len(listings)}

    async def fake_detail(
        client: Any, p: Any, external_path: str, sem: asyncio.Semaphore
    ) -> dict[str, Any]:
        slug = external_path.rsplit("/", 1)[-1]
        return {
            "jobReqId": f"REQ-{slug}",
            "title": slug.title(),
            "jobDescription": f"<p>Description for {slug}</p>",
            "startDate": None,
        }

    monkeypatch.setattr(workday_rest, "_fetch_listing_page", fake_listing)
    monkeypatch.setattr(workday_rest, "_fetch_detail", fake_detail)

    tenant = WorkdayTenant(name="Acme", url=_CAREERS_URL, search_terms=["pm"])
    postings = await workday_rest.fetch_workday(tenant, hours_old=24)

    by_id = {p.external_id: p for p in postings}
    assert len(postings) == 2, "only listings with externalPath are fetchable"
    for slug in ("beta", "gamma"):
        posting = by_id[f"{parts.tenant}:REQ-{slug}"]
        # URL comes from the listing, description from the detail response.
        # Under the old zip they came from different jobs.
        assert posting.url.endswith(f"/job/{slug}")
        assert slug in (posting.description_html or ""), "detail attached to wrong job"

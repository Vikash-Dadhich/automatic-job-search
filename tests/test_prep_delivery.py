"""Offline tests for prep-pack Telegram delivery + dedupe."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from bot.prep import send_prep_pack
from bot.telegram import TelegramClient
from config.profile import (
    Address,
    Education,
    Exclusions,
    Experience,
    Identity,
    Preferences,
    Profile,
    WorkAuthorization,
)
from core.db import Job, Source, Status, Tier, get_job_by_id, session_scope, upsert_job
from tests.test_telegram import FakeTransport


class FakeClient:
    async def complete(
        self,
        *,
        model: str,
        system_blocks: list[dict[str, Any]],
        user: str,
        max_tokens: int,
        temperature: float,
        json_mode: bool = False,
        **_kwargs: Any,
    ) -> str:
        del json_mode
        return "Grounded essay answer for this role."


def _profile() -> Profile:
    return Profile(
        identity=Identity(
            full_name="Vikash Dadhich",
            email="vikash98@uw.edu",
            phone="+91-8094110701",
            location="Seattle, WA",
            linkedin_url="https://www.linkedin.com/in/vikash-dadhich/",
            github_url="",
            portfolio_url=None,
            address=Address(
                street="1 Main St",
                city="Seattle",
                state="WA",
                zip="98105",
            ),
        ),
        work_authorization=WorkAuthorization(
            status="F-1 student visa",
            sponsorship_required=True,
            authorized_to_work_us=True,
            needs_visa_sponsorship=True,
        ),
        education=[
            Education(
                degree="MBA",
                field="Business Administration",
                school="Foster School of Business, University of Washington",
                location="Seattle, WA",
                graduation_date="2028-06",
            )
        ],
        experience=[
            Experience(
                title="Product Lead",
                company="Acme",
                location="Seattle, WA",
                start_date="2025-01",
                end_date="present",
                bullets=["Led product delivery."],
            )
        ],
        skills=["Product Strategy"],
        preferences=Preferences(
            titles=["Product Manager"],
            locations=["Remote"],
            remote_ok=True,
            relocation_ok=True,
        ),
        exclusions=Exclusions(),
    )


async def test_send_prep_pack_marks_jobs(
    db_ready: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PREP_PACKS_DIR", str(tmp_path / "prep_packs"))
    monkeypatch.setenv("PREP_PACK_BRIEF", "false")
    from config.settings import get_settings

    get_settings.cache_clear()

    async with session_scope() as session:
        job = await upsert_job(
            session,
            Job(
                source=Source.linkedin,
                external_id="li-prep-1",
                title="Product Manager",
                company="GoodCo",
                location="Remote",
                url="https://example.com/1",
                description_clean="PM role requiring product strategy.",
                status=Status.pending_review,
                score=90,
                tier=Tier.one,
                shortlist_rank=1,
                shortlist_version="phase13-v2",
            ),
        )
        job_id = job.id
    assert job_id is not None

    # Workday staged job should be ignored by prep-pack query
    async with session_scope() as session:
        await upsert_job(
            session,
            Job(
                source=Source.workday,
                external_id="wd-1",
                title="PM",
                company="WDCo",
                location="Remote",
                url="https://example.com/wd",
                description_clean="Workday role",
                status=Status.staged,
                score=95,
                tier=Tier.one,
            ),
        )

    transport = FakeTransport()
    client = TelegramClient(transport=transport, chat_id="999")
    summary = await send_prep_pack(
        client,
        profile=_profile(),
        llm_client=FakeClient(),
    )
    assert summary.jobs == 1
    assert summary.sent >= 1
    methods = [c["method"] for c in transport.calls]
    assert "sendDocument" in methods

    async with session_scope() as session:
        target = await get_job_by_id(session, job_id)
        assert target is not None
        assert target.prep_pack_sent_at is not None

    # Second run: dedupe — nothing new to send
    transport2 = FakeTransport()
    client2 = TelegramClient(transport=transport2, chat_id="999")
    summary2 = await send_prep_pack(
        client2,
        profile=_profile(),
        llm_client=FakeClient(),
    )
    assert summary2.jobs == 0
    assert transport2.calls == []

    get_settings.cache_clear()


async def test_send_prep_pack_empty(db_ready: Path) -> None:
    transport = FakeTransport()
    client = TelegramClient(transport=transport, chat_id="999")
    summary = await send_prep_pack(
        client,
        profile=_profile(),
        llm_client=FakeClient(),
    )
    assert summary.jobs == 0
    assert summary.skipped == 1
    assert transport.calls
    assert transport.calls[0]["method"] == "sendMessage"
    assert "No jobs are currently selected for review." in transport.calls[0]["payload"]["text"]

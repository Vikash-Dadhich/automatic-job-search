"""Offline tests for Tier-1 cover letter drafting."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from config.profile import Profile
from core.db import Job, Source, Status, Tier, get_job_by_source_id, session_scope, upsert_job
from scorer.cover_letter import cap_cover_letter, generate_cover_letter
from scorer.engine import score_pending


class _ScriptedClient:
    def __init__(self, replies: list[str]) -> None:
        self.replies = replies
        self.calls: list[str] = []

    async def complete(self, *, user: str, **_kwargs: Any) -> str:
        self.calls.append(user)
        idx = min(len(self.calls) - 1, len(self.replies) - 1)
        return self.replies[idx]


def _job() -> Job:
    return Job(
        source=Source.linkedin,
        external_id="letter-1",
        title="Product Manager",
        company="GoodCo",
        location="Remote",
        url="https://example.com/letter",
        description_clean="Own the roadmap.",
        status=Status.discovered,
    )


def test_cap_cover_letter_cuts_on_sentence_boundary() -> None:
    text = ("A" * 1400) + ". " + ("B" * 400)
    capped = cap_cover_letter(text)
    assert len(capped) <= 1500
    assert capped.endswith(".")
    assert "B" not in capped


def test_cap_cover_letter_hard_slice_without_punctuation() -> None:
    capped = cap_cover_letter("x" * 2000)
    assert len(capped) == 1500


async def test_generate_cover_letter_retries_banned_words(profile: Profile) -> None:
    client = _ScriptedClient(
        [
            "I am thrilled to apply for this role at GoodCo.",
            "I am applying for the Product Manager role at GoodCo. "
            "The roadmap work matches what I have shipped. "
            "One result is a launch that cut time-to-market.",
        ]
    )
    letter = await generate_cover_letter(_job(), profile, client)  # type: ignore[arg-type]
    assert len(client.calls) == 2
    assert "thrilled" not in letter.lower()
    assert "GoodCo" in letter


async def test_generate_cover_letter_falls_back_when_strip_empties(profile: Profile) -> None:
    client = _ScriptedClient(
        [
            "I am thrilled to apply.",
            "I am thrilled to apply.",
        ]
    )
    letter = await generate_cover_letter(_job(), profile, client)  # type: ignore[arg-type]
    assert "thrilled" not in letter.lower()
    assert "GoodCo" in letter
    assert "Product Manager" in letter


async def test_score_pending_persists_tier_one_letter_only(
    db_ready: Path,
    profile: Profile,
) -> None:
    async with session_scope() as session:
        await upsert_job(
            session,
            Job(
                source=Source.linkedin,
                external_id="tier-one",
                title="Product Manager",
                company="LetterCo",
                location="Remote",
                url="https://example.com/one",
                description_clean="Python product role with 3 years experience.",
                status=Status.discovered,
            ),
        )
        await upsert_job(
            session,
            Job(
                source=Source.linkedin,
                external_id="tier-two",
                title="Product Manager",
                company="OtherCo",
                location="Remote",
                url="https://example.com/two",
                description_clean="Python product role with 3 years experience.",
                status=Status.discovered,
            ),
        )

    class Routing:
        def __init__(self) -> None:
            self.letter_calls = 0

        async def complete(self, *, user: str, **_kwargs: Any) -> str:
            if "Write a 3-5 sentence cover letter" in user:
                self.letter_calls += 1
                return (
                    "I am applying for the Product Manager role at LetterCo. "
                    "The roadmap matches work I have done. "
                    "One result is a launch I already shipped."
                )
            if "LetterCo" in user:
                return '{"s":90,"t":1,"r":["strong match"]}'
            return '{"s":70,"t":2,"r":["partial match"]}'

    client = Routing()
    summary = await score_pending(
        client=client,  # type: ignore[arg-type]
        profile=profile,
        generate_outreach=False,
        generate_cover_letter=True,
    )
    assert summary.staged == 2
    assert summary.errors == 0
    assert client.letter_calls == 1

    async with session_scope() as session:
        high = await get_job_by_source_id(session, Source.linkedin, "tier-one")
        mid = await get_job_by_source_id(session, Source.linkedin, "tier-two")
        assert high is not None and high.tier == Tier.one
        assert high.cover_letter is not None
        assert "LetterCo" in high.cover_letter
        assert mid is not None and mid.tier == Tier.two
        assert mid.cover_letter is None


async def test_tier_one_drafts_stay_off_unless_enabled(
    db_ready: Path,
    profile: Profile,
) -> None:
    async with session_scope() as session:
        await upsert_job(
            session,
            Job(
                source=Source.linkedin,
                external_id="drafts-off",
                title="Product Manager",
                company="QuietCo",
                location="Remote",
                url="https://example.com/quiet",
                description_clean="Python product role with 3 years experience.",
                status=Status.discovered,
            ),
        )

    class Counting:
        def __init__(self) -> None:
            self.extra = 0

        async def complete(self, *, user: str, **_kwargs: Any) -> str:
            if "cover letter" in user.lower() or "outreach" in user.lower():
                self.extra += 1
            return '{"s":92,"t":1,"r":["fit"]}'

    client = Counting()
    summary = await score_pending(client=client, profile=profile)  # type: ignore[arg-type]
    assert summary.staged == 1
    assert client.extra == 0
    async with session_scope() as session:
        saved = await get_job_by_source_id(session, Source.linkedin, "drafts-off")
        assert saved is not None
        assert saved.score == 92
        assert saved.outreach_draft is None
        assert saved.cover_letter is None


async def test_cover_letter_failure_still_stages(
    db_ready: Path,
    profile: Profile,
) -> None:
    async with session_scope() as session:
        await upsert_job(
            session,
            Job(
                source=Source.linkedin,
                external_id="letter-boom",
                title="Product Manager",
                company="BoomCo",
                location="Remote",
                url="https://example.com/boom-letter",
                description_clean="Python product role with 3 years experience.",
                status=Status.discovered,
            ),
        )

    class BoomLetter:
        async def complete(self, *, user: str, **_kwargs: Any) -> str:
            if "cover letter" in user.lower():
                raise RuntimeError("writer down")
            return '{"s":92,"t":1,"r":["fit"]}'

    summary = await score_pending(
        client=BoomLetter(),  # type: ignore[arg-type]
        profile=profile,
        generate_outreach=False,
        generate_cover_letter=True,
    )
    assert summary.errors == 0
    assert summary.staged == 1
    async with session_scope() as session:
        saved = await get_job_by_source_id(session, Source.linkedin, "letter-boom")
        assert saved is not None
        assert saved.status == Status.staged
        assert saved.score == 92
        assert saved.cover_letter is None

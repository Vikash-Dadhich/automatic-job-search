"""Offline tests for the LLM scorer (mock client — no network)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from config.profile import Profile, load_profile
from core.db import Job, Source, Status, Tier, get_job_by_id, session_scope, upsert_job
from core.token_optimizer import approx_tokens, cache_block, compact_json_dumps, minify_job
from scorer.engine import Scorer, compute_tier, parse_score, score_pending
from scorer.outreach import contains_banned, generate_outreach
from scorer.prompts import (
    BANNED_WORDS,
    build_outreach_user,
    build_scoring_system_blocks,
    build_scoring_user,
)


class FakeClient:
    """Deterministic LLM stand-in for offline tests."""

    def __init__(
        self,
        *,
        score_payload: str = '{"s":72,"t":2,"r":["skills match","title fit"]}',
        outreach_payloads: list[str] | None = None,
        fail_once: bool = False,
    ) -> None:
        self.score_payload = score_payload
        self.outreach_payloads = outreach_payloads or [
            "I noticed the Backend role at GoodCo. "
            "My Python and SQL work maps well to the posting. "
            "Would you be open to a short referral chat?"
        ]
        self._outreach_i = 0
        self.fail_once = fail_once
        self._failed = False
        self.calls: list[dict[str, Any]] = []

    async def complete(
        self,
        *,
        model: str,
        system_blocks: list[dict[str, Any]],
        user: str,
        max_tokens: int,
        temperature: float,
        json_mode: bool = False,
        json_schema: dict[str, Any] | None = None,
        thinking_level: str | None = None,
    ) -> str:
        self.calls.append(
            {
                "model": model,
                "system_blocks": system_blocks,
                "user": user,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "json_mode": json_mode,
                "json_schema": json_schema,
                "thinking_level": thinking_level,
            }
        )
        if self.fail_once and not self._failed:
            self._failed = True
            raise RuntimeError("simulated API failure")

        # Outreach prompts ask for a message; scoring asks to evaluate
        if "Write a 3-sentence outreach" in user or "Rewrite without" in user:
            idx = min(self._outreach_i, len(self.outreach_payloads) - 1)
            text = self.outreach_payloads[idx]
            self._outreach_i += 1
            return text
        return self.score_payload


def test_parse_score_plain_json() -> None:
    raw = parse_score('{"s":84,"t":1,"r":["strong Python","remote ok"]}')
    assert raw.s == 84
    assert raw.t == 1
    assert raw.r == ["strong Python", "remote ok"]


def test_parse_score_code_fenced() -> None:
    text = 'Here you go:\n```json\n{"s":50,"t":3,"r":["weak match"]}\n```\n'
    raw = parse_score(text)
    assert raw.s == 50
    assert raw.t == 3


def test_parse_score_with_prose() -> None:
    text = 'Result: {"s":90,"t":1,"r":["dream company"]} thanks'
    raw = parse_score(text)
    assert raw.s == 90
    assert raw.t == 1


def test_parse_score_clamps() -> None:
    raw = parse_score('{"s":150,"t":9,"r":"single reason"}')
    assert raw.s == 100
    assert raw.t is None
    assert raw.r == ["single reason"]


def test_compute_tier_thresholds(profile: Profile) -> None:
    assert compute_tier(90, "GoodCo", profile) == Tier.one
    assert compute_tier(70, "GoodCo", profile) == Tier.two
    assert compute_tier(40, "GoodCo", profile) == Tier.three


def test_compute_tier_dream_company(profile: Profile) -> None:
    dream_profile = profile.model_copy(
        update={
            "preferences": profile.preferences.model_copy(
                update={"dream_companies": ["DreamCo"]}
            )
        }
    )
    assert compute_tier(50, "DreamCo", dream_profile) == Tier.one


def test_prompt_builders_cache_and_content(profile: Profile) -> None:
    blocks = build_scoring_system_blocks(profile)
    assert len(blocks) == 1
    assert blocks[0]["cache_control"] == {"type": "ephemeral"}
    assert profile.identity.full_name in blocks[0]["text"]

    job = Job(
        source=Source.linkedin,
        external_id="p1",
        title="Backend Engineer",
        company="GoodCo",
        location="Remote",
        url="https://example.com/1",
        description_clean="Requirements\nPython",
    )
    user = build_scoring_user(job)
    assert "Backend Engineer" in user
    assert "GoodCo" in user

    outreach_user = build_outreach_user(job, profile)
    assert "Backend Engineer" in outreach_user
    assert "3-sentence" in outreach_user


def test_token_optimizer_helpers() -> None:
    block = cache_block("hello")
    assert block["cache_control"]["type"] == "ephemeral"
    assert approx_tokens("abcd") == 1
    assert compact_json_dumps({"s": 1, "r": ["a"]}) == '{"s":1,"r":["a"]}'

    job = Job(
        source=Source.linkedin,
        external_id="m1",
        title="SE",
        company="Co",
        url="https://example.com",
        description_clean="x" * 7000,
    )
    mini = minify_job(job, max_chars=2000)
    assert "trimmed" in mini
    assert len(mini) < 2000 + 200


def test_minify_job_keeps_head_and_tail() -> None:
    """Sponsorship / YOE lines live at the bottom of a JD and must survive."""
    body = "HEAD-MARKER\n" + ("filler line\n" * 2000) + "TAIL-MARKER"
    job = Job(
        source=Source.linkedin,
        external_id="m2",
        title="SE",
        company="Co",
        url="https://example.com",
        description_clean=body,
    )
    mini = minify_job(job, max_chars=1500)
    assert "HEAD-MARKER" in mini
    assert "TAIL-MARKER" in mini


def test_contains_banned() -> None:
    assert "delve" in contains_banned("I would delve into this role.")
    assert contains_banned("Plain professional note.") == []
    assert "thrilled to apply" in BANNED_WORDS


async def test_generate_outreach_retries_on_banned(profile: Profile) -> None:
    job = Job(
        source=Source.linkedin,
        external_id="o1",
        title="Engineer",
        company="GoodCo",
        url="https://example.com/o1",
        description_clean="Python",
    )
    client = FakeClient(
        outreach_payloads=[
            "I am thrilled to apply and delve into this opportunity at GoodCo. More. More.",
            "I saw the Engineer role at GoodCo. My Python background fits the needs. "
            "Could we chat about a referral?",
        ]
    )
    draft = await generate_outreach(job, profile, client)
    assert contains_banned(draft) == []
    assert "GoodCo" in draft
    assert len(client.calls) >= 2


async def test_score_pending_tiers_and_outreach(
    db_ready: Path,
    profile: Profile,
) -> None:
    # Seed three discovered jobs with canned scores via score map in FakeClient
    async with session_scope() as session:
        await upsert_job(
            session,
            Job(
                source=Source.linkedin,
                external_id="high",
                title="Senior Engineer",
                company="GoodCo",
                location="Remote",
                url="https://example.com/high",
                description_clean="Requirements\nPython SQL",
                status=Status.discovered,
            ),
        )
        await upsert_job(
            session,
            Job(
                source=Source.linkedin,
                external_id="mid",
                title="Engineer",
                company="MidCo",
                location="Remote",
                url="https://example.com/mid",
                description_clean="Requirements\nPython",
                status=Status.discovered,
            ),
        )
        await upsert_job(
            session,
            Job(
                source=Source.indeed,
                external_id="low",
                title="Intern",
                company="LowCo",
                location="Remote",
                url="https://example.com/low",
                description_clean="Requirements\nExcel",
                status=Status.discovered,
            ),
        )

    # Client returns score based on company in the user prompt
    class RoutingClient(FakeClient):
        async def complete(self, **kwargs: Any) -> str:
            user = kwargs["user"]
            self.calls.append(kwargs)
            if "Write a 3-sentence outreach" in user or "Rewrite without" in user:
                return (
                    "I noticed the Senior Engineer role at GoodCo. "
                    "My Python work aligns with the posting. "
                    "Would you have time for a brief referral chat?"
                )
            if "GoodCo" in user:
                return '{"s":90,"t":1,"r":["strong match"]}'
            if "MidCo" in user:
                return '{"s":70,"t":2,"r":["partial match"]}'
            return '{"s":40,"t":3,"r":["weak match"]}'

    client = RoutingClient()
    summary = await score_pending(
        client=client,
        profile=profile,
        generate_outreach=True,
    )
    assert summary.scored == 3
    assert summary.staged == 2
    assert summary.filtered_out == 1
    assert summary.errors == 0
    assert summary.by_tier.get("one") == 1
    assert summary.by_tier.get("two") == 1
    assert summary.by_tier.get("three") == 1

    async with session_scope() as session:
        high = await session.get(Job, 1)
        # Prefer lookup by external_id for stability
        from core.db import get_job_by_source_id

        high = await get_job_by_source_id(session, Source.linkedin, "high")
        mid = await get_job_by_source_id(session, Source.linkedin, "mid")
        low = await get_job_by_source_id(session, Source.indeed, "low")

        assert high is not None
        assert high.score == 90
        assert high.tier == Tier.one
        assert high.status == Status.staged
        assert high.outreach_draft is not None
        assert "GoodCo" in high.outreach_draft
        assert high.scored_at is not None

        assert mid is not None
        assert mid.score == 70
        assert mid.tier == Tier.two
        assert mid.status == Status.staged
        assert mid.outreach_draft is None

        assert low is not None
        assert low.score == 40
        assert low.tier == Tier.three
        assert low.status == Status.filtered_out


async def test_score_pending_marks_error(
    db_ready: Path,
    profile: Profile,
) -> None:
    async with session_scope() as session:
        job = await upsert_job(
            session,
            Job(
                source=Source.linkedin,
                external_id="boom",
                title="Engineer",
                company="BoomCo",
                url="https://example.com/boom",
                description_clean="Python",
                status=Status.discovered,
            ),
        )
        job_id = job.id

    client = FakeClient(fail_once=True)
    summary = await Scorer(client=client, profile=profile).score_pending(
        client=client,
        profile=profile,
        generate_outreach=False,
        concurrency=1,
    )
    assert summary.errors == 1
    assert summary.scored == 0

    async with session_scope() as session:
        assert job_id is not None
        saved = await get_job_by_id(session, job_id)
        assert saved is not None
        assert saved.status == Status.error


async def test_score_pending_stop_after_staged(
    db_ready: Path,
    profile: Profile,
) -> None:
    async with session_scope() as session:
        for i in range(6):
            await upsert_job(
                session,
                Job(
                    source=Source.linkedin,
                    external_id=f"stop-{i}",
                    title="Product Manager",
                    company=f"Co{i}",
                    location="Remote",
                    url=f"https://example.com/stop-{i}",
                    description_clean="Python product role with 3 years experience",
                    status=Status.discovered,
                ),
            )

    class AlwaysStageClient(FakeClient):
        async def complete(self, **kwargs: Any) -> str:
            self.calls.append(kwargs)
            user = kwargs["user"]
            if "Write a 3-sentence outreach" in user or "Rewrite without" in user:
                return "Note one. Note two. Note three."
            return '{"s":70,"t":2,"r":["fit"]}'

    client = AlwaysStageClient()
    summary = await score_pending(
        client=client,
        profile=profile,
        generate_outreach=False,
        concurrency=2,
        stop_after_staged=2,
    )
    assert summary.staged >= 2
    # Wave size is 2: early-stop after a wave that reaches the target.
    assert summary.scored <= 4
    score_calls = [c for c in client.calls if c.get("json_mode") is True]
    assert len(score_calls) == summary.scored
    assert all(c.get("json_mode") is True for c in score_calls)


async def test_score_job_prefilter_skips_llm(profile: Profile) -> None:
    job = Job(
        source=Source.linkedin,
        external_id="vp1",
        title="VP of Product",
        company="BigCo",
        url="https://example.com/vp",
        description_clean="Lead the product org.",
        status=Status.discovered,
    )
    client = FakeClient()
    evaluation = await Scorer(client=client, profile=profile).score_job(
        job,
        client=client,
        profile=profile,
        generate_outreach=False,
    )
    assert evaluation.tier == Tier.three
    assert evaluation.score == 0
    assert client.calls == []
    assert evaluation.reasons
    assert "seniority" in evaluation.reasons[0].lower()


def test_load_profile_for_scorer() -> None:
    # Sanity: scorer imports don't break profile load
    p = load_profile()
    assert p.identity.full_name

"""Telegram presents the persisted shortlist and does not choose another one."""

from __future__ import annotations

from pathlib import Path

import pytest

from bot.prep import render_shortlist, select_shortlist, send_prep_pack
from bot.telegram import TelegramClient
from config.settings import get_settings
from core.db import Job, Source, Status, get_job_by_id, session_scope, upsert_job
from scorer.shortlist import apply_shortlist
from tests.test_telegram import FakeTransport


class _RaisingClient:
    def __init__(self) -> None:
        self.calls = 0

    async def complete(self, **_kwargs: object) -> str:
        self.calls += 1
        raise AssertionError("telegram rendering must not call the model")


def _enable_brief(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("PREP_PACK_BRIEF", "true")
    monkeypatch.setenv("PREP_PACKS_DIR", str(tmp_path / "prep"))
    get_settings.cache_clear()


async def _insert(job: Job) -> int:
    async with session_scope() as session:
        saved = await upsert_job(session, job)
        assert saved.id is not None
        return saved.id


def _row(
    external_id: str,
    *,
    score: int,
    priority: int | None = None,
    rank: int | None = None,
    company: str = "Acme",
    title: str = "Product Manager Intern",
    source: Source = Source.linkedin,
    url: str = "https://example.com/job",
    eligibility: str | None = None,
    role: str | None = None,
    confidence: str | None = None,
    secondary: str | None = None,
    evidence: list[str] | None = None,
    visa: str | None = None,
) -> Job:
    dimensions = None
    if visa is not None:
        dimensions = {"VISA_SPONSORSHIP": {"state": visa}}
    return Job(
        source=source,
        external_id=external_id,
        title=title,
        company=company,
        location="Seattle, WA",
        url=url,
        description_clean="Stored posting",
        status=Status.pending_review if rank is not None else Status.staged,
        score=score,
        priority_score=priority,
        shortlist_rank=rank,
        shortlist_version="phase13-v2" if rank is not None else None,
        shortlist_reason="selected_by_priority" if rank is not None else None,
        eligibility_state=eligibility,
        role_family=role,
        role_confidence=confidence,
        role_secondary_family=secondary,
        fit_evidence=evidence,
        eligibility_dimensions=dimensions,
    )


async def test_output_matches_the_canonical_shortlist(
    db_ready: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    _enable_brief(monkeypatch, tmp_path)
    await _insert(
        _row("high", score=96, priority=None, title="Unselected", url="https://example.com/no")
    )
    for index, priority in enumerate((90, 80, 70), start=1):
        await _insert(
            Job(
                source=Source.linkedin,
                external_id=f"pick-{index}",
                title=f"Selected {index}",
                company=f"Co {index}",
                location="Remote",
                url=f"https://example.com/yes/{index}",
                description_clean="Stored posting",
                status=Status.staged,
                score=60 + index,
                priority_score=priority,
            )
        )
    result = await apply_shortlist()
    assert result.selected == 3

    transport = FakeTransport()
    summary = await send_prep_pack(
        TelegramClient(transport=transport, chat_id="1"),
        llm_client=_RaisingClient(),  # type: ignore[arg-type]
    )
    assert summary.jobs == 3
    assert summary.markdown_path is not None
    text = Path(summary.markdown_path).read_text(encoding="utf-8")
    assert text.index("Selected 1") < text.index("Selected 2") < text.index("Selected 3")
    assert "Unselected" not in text
    assert "https://example.com/no" not in text
    get_settings.cache_clear()


async def test_three_selected_jobs_are_not_filled_out(
    db_ready: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    _enable_brief(monkeypatch, tmp_path)
    for rank, score in ((1, 90), (2, 70), (3, 55)):
        await _insert(_row(f"yes-{rank}", score=score, rank=rank, title=f"Kept {rank}"))
    await _insert(_row("extra", score=88, title="Filler", url="https://example.com/filler"))
    summary = await send_prep_pack(TelegramClient(transport=FakeTransport(), chat_id="1"))
    assert summary.jobs == 3
    text = Path(summary.markdown_path or "").read_text(encoding="utf-8")
    assert text.count("Kept ") == 3
    assert "Filler" not in text
    get_settings.cache_clear()


async def test_empty_shortlist_sends_no_cards(
    db_ready: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    _enable_brief(monkeypatch, tmp_path)
    await _insert(_row("loud", score=99, title="Not Selected", url="https://example.com/loud"))
    transport = FakeTransport()
    summary = await send_prep_pack(TelegramClient(transport=transport, chat_id="1"))
    assert summary.jobs == 0
    assert summary.sent == 0
    assert transport.calls[0]["method"] == "sendMessage"
    assert "sendDocument" not in [call["method"] for call in transport.calls]
    assert "Not Selected" not in transport.calls[0]["payload"]["text"]
    get_settings.cache_clear()


async def test_selected_job_below_old_thresholds_is_shown(
    db_ready: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    _enable_brief(monkeypatch, tmp_path)
    await _insert(_row("low", score=50, rank=1, title="Below Old Cutoff"))
    await _insert(_row("high", score=99, title="High But Unselected", url="https://example.com/high"))
    summary = await send_prep_pack(TelegramClient(transport=FakeTransport(), chat_id="1"))
    text = Path(summary.markdown_path or "").read_text(encoding="utf-8")
    assert "Below Old Cutoff" in text
    assert "Fit: 50" in text
    assert "High But Unselected" not in text
    get_settings.cache_clear()


async def test_order_follows_shortlist_rank_not_fit(
    db_ready: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    _enable_brief(monkeypatch, tmp_path)
    await _insert(_row("second", score=99, rank=2, title="Second"))
    await _insert(_row("first", score=40, rank=1, title="First"))
    summary = await send_prep_pack(TelegramClient(transport=FakeTransport(), chat_id="1"))
    text = Path(summary.markdown_path or "").read_text(encoding="utf-8")
    assert text.index("First") < text.index("Second")
    get_settings.cache_clear()


def test_duplicate_job_id_is_rendered_once() -> None:
    job = _row("dup", score=80, rank=1, title="Once")
    job.id = 7
    text = render_shortlist([job, job])
    assert text.count("Once") == 1


async def test_card_shows_stored_fields_without_changing_them(
    db_ready: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    _enable_brief(monkeypatch, tmp_path)

    def _boom(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("rendering must not classify or embed")

    monkeypatch.setattr("scorer.embeddings.build_embedder", _boom)
    monkeypatch.setattr("scorer.role_classify.classify_role", _boom, raising=False)
    job_id = await _insert(
        _row(
            "card",
            score=87,
            priority=81,
            rank=1,
            title="Product Manager Intern",
            company="Northwind",
            source=Source.indeed,
            url="https://jobs.example/apply/42",
            eligibility="UNKNOWN",
            role="PRODUCT_MANAGEMENT",
            confidence="high",
            secondary="CONSULTING",
            evidence=["Product ownership"],
            visa="UNKNOWN",
        )
    )
    confirmed = await _insert(
        _row(
            "confirmed",
            score=70,
            rank=2,
            eligibility="CONFIRMED_ELIGIBLE",
            title="Confirmed Role",
            url="https://jobs.example/confirmed",
        )
    )
    blocked = await _insert(
        _row(
            "blocked",
            score=70,
            rank=3,
            eligibility="CLEARLY_INELIGIBLE",
            title="Blocked Role",
            url="https://jobs.example/blocked",
        )
    )
    llm = _RaisingClient()
    summary = await send_prep_pack(
        TelegramClient(transport=FakeTransport(), chat_id="1"),
        llm_client=llm,  # type: ignore[arg-type]
    )
    assert llm.calls == 0
    text = Path(summary.markdown_path or "").read_text(encoding="utf-8")
    assert "Fit: 87" in text
    assert "Priority: 81" in text
    assert "Eligibility: UNKNOWN" in text
    assert "Eligibility: CONFIRMED_ELIGIBLE" in text
    assert "Eligibility: CLEARLY_INELIGIBLE" in text
    assert "Role: PRODUCT_MANAGEMENT" in text
    assert "Secondary role: CONSULTING" in text
    assert "Confidence: high" in text
    assert "Product ownership" in text
    assert "Visa: UNKNOWN" in text
    assert "Source: indeed" in text
    assert "https://jobs.example/apply/42" in text
    async with session_scope() as session:
        saved = await get_job_by_id(session, job_id)
        assert saved is not None
        assert saved.shortlist_rank == 1
        assert saved.shortlist_reason == "selected_by_priority"
        assert saved.status == Status.pending_review
        assert saved.role_family == "PRODUCT_MANAGEMENT"
        assert saved.eligibility_state == "UNKNOWN"
        assert saved.priority_score == 81
        assert saved.score == 87
        for other_id, state in (
            (confirmed, "CONFIRMED_ELIGIBLE"),
            (blocked, "CLEARLY_INELIGIBLE"),
        ):
            other = await get_job_by_id(session, other_id)
            assert other is not None
            assert other.eligibility_state == state
            assert other.shortlist_rank is not None
    get_settings.cache_clear()


async def test_production_send_does_not_call_legacy_select_shortlist(
    db_ready: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    _enable_brief(monkeypatch, tmp_path)
    await _insert(_row("kept", score=40, rank=1, title="Canonical"))

    def _legacy(_jobs: list[Job]) -> list[Job]:
        raise AssertionError("production send called the legacy selector")

    monkeypatch.setattr("bot.prep.select_shortlist", _legacy)
    summary = await send_prep_pack(TelegramClient(transport=FakeTransport(), chat_id="1"))
    assert summary.jobs == 1
    text = Path(summary.markdown_path or "").read_text(encoding="utf-8")
    assert "Canonical" in text
    assert select_shortlist is not _legacy
    get_settings.cache_clear()

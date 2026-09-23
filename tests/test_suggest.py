"""Tests for Telegram skill-suggestion callbacks and apply-on-approve."""

from __future__ import annotations

from typing import Any

import pytest

from bot.suggest import decide_suggestion, send_pending_suggestions
from bot.telegram import (
    SuggestAction,
    decode_suggest_callback,
    encode_suggest_callback,
    is_suggest_callback,
)
from config.profile import (
    Address,
    Education,
    Experience,
    Identity,
    Preferences,
    Profile,
    WorkAuthorization,
)
from core.db import (
    Job,
    RoleBaseline,
    SkillPlacement,
    SkillProvenance,
    SkillSuggestion,
    Source,
    Status,
    SuggestionStatus,
    get_skill_suggestion_by_id,
    get_suggestions_for_job,
    session_scope,
    upsert_job,
)


def test_suggest_callback_roundtrip() -> None:
    data = encode_suggest_callback(SuggestAction.approve, 42)
    assert is_suggest_callback(data)
    action, sid = decode_suggest_callback(data)
    assert action == SuggestAction.approve
    assert sid == 42
    assert len(data.encode()) <= 64


def test_suggest_callback_rejects_review_namespace() -> None:
    with pytest.raises(ValueError):
        decode_suggest_callback("v1|ok|1")


class FakeTransport:
    def __init__(self) -> None:
        self.posts: list[tuple[str, dict[str, Any]]] = []

    async def post(
        self,
        method: str,
        payload: dict[str, Any] | None = None,
        *,
        files: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        self.posts.append((method, dict(payload or {})))
        if method == "sendMessage":
            return {
                "ok": True,
                "result": {
                    "message_id": 99,
                    "chat": {"id": 12345},
                    "text": payload.get("text") if payload else "",
                },
            }
        return {"ok": True, "result": True}


def _profile() -> Profile:
    return Profile(
        identity=Identity(
            full_name="Jane Q. Doe",
            email="jane@example.com",
            phone="+1-555-111-2222",
            location="Seattle, WA",
            linkedin_url="https://www.linkedin.com/in/janedoe",
            github_url="https://github.com/janedoe",
            portfolio_url=None,
            address=Address(street="1 Main", city="Seattle", state="WA", zip="98101"),
        ),
        work_authorization=WorkAuthorization(
            status="US Citizen",
            sponsorship_required=False,
            authorized_to_work_us=True,
            needs_visa_sponsorship=False,
        ),
        education=[
            Education(
                degree="M.S.",
                field="CS",
                school="Example U",
                location="Seattle, WA",
                graduation_date="2024-05",
            )
        ],
        experience=[
            Experience(
                title="Software Engineer",
                company="Acme",
                location="Seattle, WA",
                start_date="2022-01",
                end_date="2024-01",
                bullets=["Built Python APIs."],
            )
        ],
        skills=["Python", "SQL"],
        preferences=Preferences(
            titles=["Software Engineer"],
            locations=["Seattle, WA"],
            remote_ok=True,
            relocation_ok=False,
        ),
    )


@pytest.mark.asyncio
async def test_send_and_decide_suggestions(db_ready, tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("RESUMES_DIR", str(tmp_path / "resumes"))
    monkeypatch.setenv("BASELINES_DIR", str(tmp_path / "baselines"))
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "12345")
    from config.settings import get_settings

    get_settings.cache_clear()

    async with session_scope() as session:
        job = await upsert_job(
            session,
            Job(
                source=Source.linkedin,
                external_id="t1",
                title="Software Engineer",
                company="Acme",
                url="https://example.com/t1",
                description_clean="Python Kafka",
                status=Status.staged,
            ),
        )
        baseline = RoleBaseline(
            role="Software Engineer",
            title_terms=["Software Engineer"],
            skills=[{"name": "Python"}],
            resume_data={
                "name": "Jane Q. Doe",
                "email": "jane@example.com",
                "phone": "+1-555-111-2222",
                "location": "Seattle, WA",
                "linkedin": "",
                "github": "",
                "portfolio": "",
                "summary": "SE",
                "skills": ["Python"],
                "experience": [
                    {
                        "title": "Software Engineer",
                        "company": "Acme",
                        "location": "Seattle, WA",
                        "start": "2022-01",
                        "end": "2024-01",
                        "bullets": ["Built Python APIs."],
                    }
                ],
                "education": [
                    {
                        "degree": "M.S.",
                        "field": "CS",
                        "school": "Example U",
                        "location": "Seattle, WA",
                        "graduation": "2024-05",
                        "gpa": None,
                    }
                ],
            },
            pdf_path=None,
            job_ids=[job.id] if job.id else [],
        )
        session.add(baseline)
        await session.flush()
        await session.refresh(baseline)
        sug = SkillSuggestion(
            job_id=job.id or 0,
            baseline_id=baseline.id,
            skill="Kafka",
            category="tool",
            placement=SkillPlacement.skills,
            proposed_text="Kafka",
            provenance=SkillProvenance.inferred,
            status=SuggestionStatus.pending,
        )
        session.add(sug)
        await session.flush()
        await session.refresh(sug)
        suggestion_id = sug.id
        job_id = job.id

    assert suggestion_id is not None and job_id is not None

    from bot.telegram import TelegramClient

    transport = FakeTransport()
    client = TelegramClient(transport=transport, chat_id="12345")
    summary = await send_pending_suggestions(client=client)
    assert summary.sent == 1
    assert any(m == "sendMessage" for m, _ in transport.posts)

    async with session_scope() as session:
        loaded = await get_skill_suggestion_by_id(session, suggestion_id)
        assert loaded is not None
        assert loaded.review_message_id == 99

    # Approve then reject would leave one pending — approve the only one
    status = await decide_suggestion(suggestion_id, SuggestAction.approve)
    assert status == SuggestionStatus.approved

    async with session_scope() as session:
        all_sugs = await get_suggestions_for_job(session, job_id)
        assert all(s.status != SuggestionStatus.pending for s in all_sugs)
        from core.db import get_job_by_id

        job_row = await get_job_by_id(session, job_id)
        assert job_row is not None
        assert job_row.resume_path

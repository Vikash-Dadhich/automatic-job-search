"""Offline tests for AnswerResolver (deterministic + mock LLM)."""

from __future__ import annotations

from typing import Any

from automation.answers import (
    AnswerResolver,
    AnswerSource,
    ResolvedAnswer,
    answers_to_payload,
    is_open_ended,
    resolve_deterministic,
)
from config.profile import load_profile
from core.db import Job, Source


class FakeAnswerClient:
    def __init__(self, payloads: list[str] | None = None) -> None:
        self.payloads = payloads or [
            "I have built Python APIs and data pipelines that match this role."
        ]
        self._i = 0
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
        **_kwargs: Any,
    ) -> str:
        self.calls.append({"model": model, "user": user, "json_mode": json_mode})
        idx = min(self._i, len(self.payloads) - 1)
        text = self.payloads[idx]
        self._i += 1
        return text


def test_deterministic_identity_and_auth(profile) -> None:
    assert resolve_deterministic("Email Address", profile) == profile.identity.email
    assert resolve_deterministic("Phone Number", profile) == profile.identity.phone
    assert resolve_deterministic("First Name", profile)
    assert resolve_deterministic("Last Name", profile)
    assert resolve_deterministic("Street Address", profile) == profile.identity.address.street
    assert resolve_deterministic("City", profile) == profile.identity.address.city
    assert resolve_deterministic("Zip Code", profile) == profile.identity.address.zip

    auth_yes = resolve_deterministic(
        "Are you legally authorized to work in the United States?",
        profile,
    )
    assert auth_yes == ("Yes" if profile.work_authorization.authorized_to_work_us else "No")

    sponsor = resolve_deterministic(
        "Will you now or in the future require visa sponsorship?",
        profile,
    )
    expect_sponsor = (
        "Yes"
        if (
            profile.work_authorization.needs_visa_sponsorship
            or profile.work_authorization.sponsorship_required
        )
        else "No"
    )
    assert sponsor == expect_sponsor


def test_deterministic_eeo_decline(profile) -> None:
    ans = resolve_deterministic("Race / Ethnicity (voluntary EEO)", profile)
    assert ans == "Decline to self-identify"
    ans2 = resolve_deterministic("Do you have a disability? (voluntary)", profile)
    assert ans2 == "Decline to self-identify"
    ans3 = resolve_deterministic("Veteran status", profile)
    assert ans3 == "Decline to self-identify"


def test_deterministic_source_and_unknown(profile) -> None:
    assert resolve_deterministic("How did you hear about this position?", profile) == (
        "Company career site"
    )
    assert resolve_deterministic("Favorite color of stapler?", profile) is None


def test_is_open_ended() -> None:
    assert is_open_ended("Why are you interested in this role?")
    assert is_open_ended("Please describe your relevant experience")
    assert not is_open_ended("Email Address")


async def test_resolver_deterministic_path(profile) -> None:
    client = FakeAnswerClient()
    resolver = AnswerResolver(profile, client=client)
    result = await resolver.resolve("Email Address")
    assert result.source == AnswerSource.deterministic
    assert result.answer == profile.identity.email
    assert client.calls == []


async def test_resolver_open_ended_llm(profile) -> None:
    client = FakeAnswerClient(
        payloads=["I match this Backend role through Python and SQL work."]
    )
    resolver = AnswerResolver(profile, client=client)
    job = Job(
        source=Source.workday,
        external_id="wd-1",
        title="Backend Engineer",
        company="Acme",
        url="https://acme.wd5.myworkdayjobs.com/en-US/External/job/1",
        tenant="acme",
    )
    result = await resolver.resolve(
        "Why are you interested in this role?",
        job=job,
    )
    assert result.source == AnswerSource.llm
    assert "Python" in result.answer
    assert len(client.calls) == 1


async def test_resolver_blank_for_unknown_closed(profile) -> None:
    client = FakeAnswerClient()
    resolver = AnswerResolver(profile, client=client)
    result = await resolver.resolve("Favorite color of stapler?")
    assert result.source == AnswerSource.blank
    assert result.answer == ""
    assert client.calls == []


async def test_resolver_banned_word_retry(profile) -> None:
    client = FakeAnswerClient(
        payloads=[
            "I am thrilled to apply and delve into this role.",
            "My Python experience maps well to the posting requirements.",
        ]
    )
    resolver = AnswerResolver(profile, client=client)
    result = await resolver.resolve(
        "Why do you want this job?",
        job=Job(
            source=Source.workday,
            external_id="wd-2",
            title="Engineer",
            company="Co",
            url="https://co.wd1.myworkdayjobs.com/en-US/External/job/2",
            tenant="co",
        ),
    )
    assert result.source == AnswerSource.llm
    assert "thrilled to apply" not in result.answer.lower()
    assert "delve" not in result.answer.lower()
    assert len(client.calls) == 2


async def test_cover_letter_field_uses_stored_text(profile) -> None:
    client = FakeAnswerClient()
    job = Job(
        source=Source.workday,
        external_id="wd-letter",
        title="Engineer",
        company="Co",
        url="https://co.wd1.myworkdayjobs.com/en-US/External/job/9",
        cover_letter="Stored letter about the Engineer role at Co.",
    )
    resolver = AnswerResolver(profile, client=client)
    stored = await resolver.resolve("Cover letter", job=job)
    assert stored.source == AnswerSource.stored
    assert stored.answer.startswith("Stored letter")
    assert client.calls == []

    essay = await resolver.resolve("Why are you interested in this role?", job=job)
    assert essay.source == AnswerSource.llm
    assert len(client.calls) == 1


def test_answers_to_payload(profile) -> None:
    ans = resolve_deterministic("Email Address", profile)
    payload = answers_to_payload(
        [ResolvedAnswer("Email", ans or "", AnswerSource.deterministic)]
    )
    assert payload["count"] == 1
    assert payload["items"][0]["source"] == "deterministic"


def test_load_profile_fixture() -> None:
    p = load_profile()
    assert p.identity.email

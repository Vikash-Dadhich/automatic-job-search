"""Offline tests for LinkedIn/Indeed prep-pack builder."""

from __future__ import annotations

from pathlib import Path
from typing import Any

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
from core.db import Job, Source, Status, Tier
from prep.builder import (
    build_job_section,
    compile_prep_pdf,
    generate_prep_pack,
    render_markdown,
)
from prep.questions import ESSAY_QUESTIONS, IDENTITY_QUESTIONS, MANUAL_FILL


class FakeClient:
    def __init__(self, text: str = "I am a strong fit for this role.") -> None:
        self.text = text
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
        return self.text


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
                title="Co-founder and Technical Product Lead",
                company="Saarthi Manosetu Wellness",
                location="Jodhpur, India",
                start_date="2025-04",
                end_date="present",
                bullets=["Built a digital wellness platform."],
            )
        ],
        skills=["Product Strategy", "Python"],
        preferences=Preferences(
            titles=["Product Manager"],
            locations=["Seattle, WA", "Remote"],
            remote_ok=True,
            relocation_ok=True,
            dream_companies=[],
        ),
        exclusions=Exclusions(),
    )


def _job(**kwargs: Any) -> Job:
    defaults: dict[str, Any] = {
        "id": 11,
        "source": Source.linkedin,
        "external_id": "prep-1",
        "title": "Product Manager",
        "company": "GoodCo",
        "location": "Remote",
        "url": "https://example.com/jobs/1",
        "description_clean": "Looking for a PM with product strategy experience.",
        "status": Status.staged,
        "score": 88,
        "tier": Tier.one,
        "outreach_draft": "Hi — interested in the PM role.",
    }
    defaults.update(kwargs)
    return Job(**defaults)


async def test_build_job_section_identity_and_essays() -> None:
    client = FakeClient("Clear essay answer about the role.")
    section = await build_job_section(_job(), _profile(), client)
    assert section["title"] == "Product Manager"
    assert section["outreach_draft"]
    by_q = {a["question"]: a for a in section["answers"]}
    assert by_q["Email"]["answer"] == "vikash98@uw.edu"
    assert by_q["Email"]["source"] == "deterministic"
    assert by_q["First name"]["answer"] == "Vikash"
    assert "Yes" in by_q["Will you now or in the future require visa sponsorship?"]["answer"]
    essay_q = ESSAY_QUESTIONS[0]
    assert by_q[essay_q]["source"] == "llm"
    assert "Clear essay" in by_q[essay_q]["answer"]
    assert client.calls  # LLM used for essays
    assert len(section["answers"]) == len(IDENTITY_QUESTIONS) + len(ESSAY_QUESTIONS)


async def test_build_job_section_filters_banned_words() -> None:
    client = FakeClient("I am thrilled to apply and delve into this role.")
    section = await build_job_section(_job(), _profile(), client)
    essay = next(a for a in section["answers"] if a["question"] == ESSAY_QUESTIONS[0])
    # Banned-word gate retries then strips; FakeClient always returns banned text,
    # so the final answer is blank after stripping.
    assert len(client.calls) >= 2
    assert essay["source"] in {"llm", "blank"}
    lower = (essay["answer"] or "").lower()
    assert "thrilled to apply" not in lower
    assert "delve" not in lower


def test_render_markdown_includes_jobs_and_manual() -> None:
    sections = [
        {
            "job_id": 1,
            "title": "PM",
            "company": "Co",
            "location": "Remote",
            "url": "https://x.com",
            "source": "linkedin",
            "score": 90,
            "tier": "one",
            "outreach_draft": "Hello",
            "answers": [
                {"question": "Email", "answer": "a@b.com", "source": "deterministic"}
            ],
            "manual_fill": list(MANUAL_FILL),
        }
    ]
    md = render_markdown(sections, generated_at="2026-01-01")
    assert "# Application Prep Pack" in md
    assert "PM @ Co" in md
    assert "a@b.com" in md
    assert "Hello" in md
    assert MANUAL_FILL[0] in md


def test_compile_prep_pdf(tmp_path: Path) -> None:
    data = {
        "generated_at": "2026-01-01 00:00 UTC",
        "job_count": 1,
        "jobs": [
            {
                "title": "Product Manager",
                "company": "GoodCo",
                "location": "Remote",
                "url": "https://example.com/1",
                "source": "linkedin",
                "score": 88,
                "tier": "one",
                "outreach_draft": "",
                "answers": [
                    {
                        "question": "Email",
                        "answer": "vikash98@uw.edu",
                        "source": "deterministic",
                    }
                ],
                "manual_fill": list(MANUAL_FILL),
            }
        ],
    }
    out = tmp_path / "pack.pdf"
    path = compile_prep_pdf(data, out)
    assert path.exists()
    assert path.read_bytes().startswith(b"%PDF")


async def test_generate_prep_pack_writes_files(tmp_path: Path) -> None:
    result = await generate_prep_pack(
        [_job()],
        profile=_profile(),
        client=FakeClient(),
        out_dir=tmp_path,
    )
    assert result.job_count == 1
    assert result.job_ids == [11]
    assert result.markdown_path is not None and result.markdown_path.is_file()
    assert result.pdf_path is not None and result.pdf_path.is_file()
    text = result.markdown_path.read_text(encoding="utf-8")
    assert "Product Manager @ GoodCo" in text

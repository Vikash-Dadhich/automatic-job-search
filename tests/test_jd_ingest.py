"""Phase 4 JD normalization, hashing, and upsert protection."""

from __future__ import annotations

from pathlib import Path

from core.db import Source, get_job_by_source_id, session_scope, upsert_job
from scraper.models import RawPosting, to_job
from scraper.textclean import (
    SUSPICIOUS_BELOW,
    content_hash,
    extract_sections,
    html_to_text,
    normalize_description,
)

_LONG = (
    "The internship owns a product area with engineers and designers. "
    "You will write requirements, talk to customers, and ship a summer release. "
)


def test_plain_text_and_whitespace() -> None:
    messy = f"  Hello   \n\n\n\tWorld  {_LONG}"
    normalized = normalize_description(messy)
    assert normalized.text.startswith("Hello\n\nWorld")
    assert "internship owns" in normalized.text
    assert normalized.status == "present"
    assert normalized.extraction_path == "plain"
    assert content_hash(messy) == content_hash(normalized.text)


def test_html_strips_script_style_and_nav() -> None:
    html = (
        "<html><body><nav>Menu</nav><script>bad()</script><style>.x{}</style>"
        f"<p>{_LONG}</p><footer>copyright 2026</footer></body></html>"
    )
    text = html_to_text(html)
    assert "bad()" not in text
    assert "Menu" not in text
    assert "copyright" not in text
    assert "internship owns" in text
    broken = html_to_text("<div><p>Own the roadmap for the summer internship.</p>")
    assert "Own the roadmap" in broken
    assert normalize_description(html, from_html=True).extraction_path == "html"


def test_markdown_and_unknown_sections_are_kept() -> None:
    text = (
        "Equal Opportunity Employer statement that should not lead the posting.\n\n"
        f"{_LONG}\n\n"
        "## Responsibilities\n"
        "Ship the internship roadmap.\n\n"
        "Team culture\n"
        "Work with design and engineering.\n\n"
        "## Compensation\n"
        "Paid hourly for the summer.\n"
    )
    sections = extract_sections(text)
    assert "internship owns" in sections
    assert "Ship the internship roadmap" in sections
    assert "Team culture" in sections
    assert "Paid hourly" in sections
    assert "Equal Opportunity" not in sections
    normalized = normalize_description(text)
    assert normalized.extraction_path == "sections"
    assert normalized.status == "present"
    assert len(normalized.text) >= SUSPICIOUS_BELOW


def test_missing_short_and_truncated_descriptions() -> None:
    assert normalize_description("").status == "missing"
    assert normalize_description("  \n\t").status == "missing"
    short = normalize_description("Intern.")
    assert short.status == "suspicious"
    assert short.truncated is False
    long = "Responsibilities\n" + ("Ship the internship project. " * 2000)
    truncated = normalize_description(long)
    assert truncated.truncated is True
    assert truncated.status == "truncated"
    assert "[... trimmed ...]" in truncated.text
    assert truncated.char_count == len(truncated.text)
    again = normalize_description(truncated.text)
    assert again.truncated is True
    assert again.text == truncated.text


def test_content_hash_ignores_formatting_and_tracks_meaning() -> None:
    html = f"<p>{_LONG}</p>"
    plain = html_to_text(html)
    assert content_hash(plain) == content_hash(normalize_description(html, from_html=True).text)
    assert content_hash("") == content_hash("   \n ")
    assert content_hash(plain) != content_hash(plain + " Extra duty.")
    assert content_hash(normalize_description(plain).text) == content_hash(plain)


def test_jobsy_and_workday_descriptions_and_provenance() -> None:
    jobspy = RawPosting(
        source=Source.linkedin,
        external_id="js-1",
        title="Product Manager Intern",
        company="GoodCo",
        url="https://example.com/js",
        description_clean=f"## Responsibilities\n{_LONG}",
        discovery_family="PRODUCT_MANAGEMENT",
        discovery_bucket="PM_CORE",
        discovery_query="Product Manager Intern",
    )
    job = to_job(jobspy)
    assert job.jd_status == "present"
    assert "internship owns" in (job.description_clean or "")
    assert job.discovery_family == "PRODUCT_MANAGEMENT"
    assert job.discovery_query == "Product Manager Intern"
    assert job.content_hash == content_hash(job.description_clean or "")

    workday = RawPosting(
        source=Source.workday,
        external_id="wd-1",
        title="Consulting Intern",
        company="BigCo",
        url="https://example.com/wd",
        description_html=f"<h2>Responsibilities</h2><p>{_LONG}</p>",
        tenant="nvidia",
        discovery_family="CONSULTING",
        discovery_bucket="MANAGEMENT_CONSULTING",
        discovery_query="Consulting Intern",
    )
    stored = to_job(workday)
    assert stored.jd_extraction_path == "html" or stored.jd_status == "present"
    assert "internship owns" in (stored.description_clean or "")
    assert stored.tenant == "nvidia"
    assert stored.discovery_bucket == "MANAGEMENT_CONSULTING"

    missing = to_job(
        RawPosting(
            source=Source.workday,
            external_id="wd-2",
            title="Consulting Intern",
            company="BigCo",
            url="https://example.com/wd2",
            tenant="nvidia",
        )
    )
    assert missing.description_clean is None
    assert missing.jd_status == "missing"


async def test_upsert_keeps_good_jd_and_clears_stale_embedding(db_ready: Path) -> None:
    del db_ready
    good = (
        "Responsibilities\n"
        "Own an internship product area with engineers, write requirements, and ship."
    )
    async with session_scope() as session:
        saved = await upsert_job(
            session,
            to_job(
                RawPosting(
                    source=Source.indeed,
                    external_id="keep-1",
                    title="Strategy Intern",
                    company="GoodCo",
                    url="https://example.com/keep",
                    description_clean=good,
                    discovery_family="STRATEGY_TRANSFORMATION",
                    discovery_bucket="CORPORATE_STRATEGY",
                    discovery_query="Strategy Intern",
                )
            ),
        )
        saved.embedding = [0.1, 0.2]
        saved.vector_decision = "pass"
        session.add(saved)
        kept_text = saved.description_clean
        kept_hash = saved.content_hash

    async with session_scope() as session:
        await upsert_job(
            session,
            to_job(
                RawPosting(
                    source=Source.indeed,
                    external_id="keep-1",
                    title="Strategy Intern",
                    company="GoodCo",
                    url="https://example.com/keep",
                    description_clean="   ",
                    discovery_family="STRATEGY_TRANSFORMATION",
                    discovery_bucket="CORPORATE_STRATEGY",
                    discovery_query="Strategy Intern",
                )
            ),
        )
        kept = await get_job_by_source_id(session, Source.indeed, "keep-1")
        assert kept is not None
        assert kept.description_clean == kept_text
        assert kept.content_hash == kept_hash
        assert kept.embedding == [0.1, 0.2]
        assert kept.discovery_query == "Strategy Intern"

    rewritten = good + " The employer added a new customer research requirement."
    async with session_scope() as session:
        await upsert_job(
            session,
            to_job(
                RawPosting(
                    source=Source.indeed,
                    external_id="keep-1",
                    title="Strategy Intern",
                    company="GoodCo",
                    url="https://example.com/keep",
                    description_clean=rewritten,
                )
            ),
        )
        changed = await get_job_by_source_id(session, Source.indeed, "keep-1")
        assert changed is not None
        assert "customer research" in (changed.description_clean or "")
        assert changed.content_hash != kept_hash
        assert changed.embedding is None
        assert changed.vector_decision is None

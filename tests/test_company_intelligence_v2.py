"""Factual company signals. They do not score employers or change job decisions."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import pytest
from sqlalchemy import Table, text
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable
from sqlmodel import SQLModel

import scorer.company_intelligence as company_intelligence
from core.db import (
    Source,
    Status,
    get_engine,
    init_db,
    reset_engine,
    session_scope,
    upsert_job,
)
from scorer.company_intelligence import (
    INTELLIGENCE_VERSION,
    CompanyLookupResult,
    CompanySourceDocument,
    attach_company_intelligence,
    extract_company_signals,
    merge_company_signals,
    normalize_company_name,
    refresh_company_intelligence,
)
from scorer.eligibility import attach_eligibility
from scraper.models import RawPosting, to_job

RETRIEVED_TEXT = (
    "Northwind is a payments and banking company with U.S. operations. "
    "It offers an MBA internship program and an internship program. "
    "Northwind is a publicly traded company. Annual revenue of $4 billion. "
    "Listed on the NYSE. Operates in 12 countries. 40 offices. "
    "Approximately 8,000 employees."
)


class _Provider:
    def __init__(self, text: str) -> None:
        self.text = text
        self.calls = 0

    async def lookup(
        self,
        company_name: str,
        source_url: str,
        source_type: str = "official_website",
    ) -> CompanyLookupResult:
        del company_name
        self.calls += 1
        return CompanyLookupResult(
            document=CompanySourceDocument(
                source_type=source_type,
                url=source_url,
                text=self.text,
                retrieved_at=datetime(2026, 10, 2, 12, 0, tzinfo=UTC),
            )
        )


def _signals(record: object) -> list[dict[str, object]]:
    context = getattr(record, "context", None)
    assert isinstance(context, dict)
    raw = context.get("signals")
    assert isinstance(raw, list)
    return raw


def _one(record: object, name: str) -> dict[str, object]:
    matches = [item for item in _signals(record) if item["signal"] == name]
    assert len(matches) == 1
    return matches[0]


def test_version_and_normalization_stay_explicit() -> None:
    assert INTELLIGENCE_VERSION == "phase8-v2"
    assert normalize_company_name("AT&T") == "at&t"
    assert normalize_company_name("  Microsoft Corporation ") == "microsoft"
    source = Path(company_intelligence.__file__ or "").read_text(encoding="utf-8")
    assert "build_llm_client" not in source
    forbidden = {
        "company_score",
        "prestige_score",
        "brand_score",
        "culture_score",
        "company_quality",
        "employer_quality",
    }
    assert forbidden.isdisjoint(source)


def test_signals_are_explicit_and_multi_valued() -> None:
    signals = extract_company_signals(RETRIEVED_TEXT)
    names = {item["signal"] for item in signals}
    assert {"domain:payments", "domain:banking"} <= names
    assert "mba_internship_program" in names
    assert "internship_program" in names
    assert "us_operations" in names
    assert "public_private" in names
    assert "revenue" in names
    assert "exchange" in names
    assert "country_count" in names
    assert "office_count" in names
    assert "employee_count" in names
    plain = extract_company_signals("We run an internship program for undergraduates.")
    assert "internship_program" in {item["signal"] for item in plain}
    assert "mba_internship_program" not in {item["signal"] for item in plain}
    assert extract_company_signals("Acme is a prestigious employer with a great culture.") == []
    assert extract_company_signals("Headquartered in Seattle.") == []


def test_authoritative_source_wins_a_contradiction() -> None:
    official = {
        "signal": "us_operations",
        "value": True,
        "snippet": "U.S. operations",
        "basis": "explicit",
        "source_type": "official_website",
        "source_url": "https://acme.example/about",
        "observed_at": "2026-10-01T00:00:00+00:00",
    }
    careers = {**official, "value": False, "source_type": "careers", "source_url": "https://careers.example"}
    merged = merge_company_signals([official], [careers], source_url=careers["source_url"])
    assert len(merged) == 1
    assert merged[0]["value"] is True
    assert merged[0]["source_type"] == "official_website"


def test_context_column_compiles_for_postgres() -> None:
    table = SQLModel.metadata.tables["company_intelligence"]
    assert isinstance(table, Table)
    sql = str(CreateTable(table).compile(dialect=postgresql.dialect()))
    assert "context" in sql


async def test_context_column_is_added_to_an_existing_table(tmp_db: object) -> None:
    del tmp_db
    from pathlib import Path

    from config.settings import get_settings

    url = get_settings().database_url
    path = Path(url.removeprefix("sqlite+aiosqlite:///"))
    raw = sqlite3.connect(path)
    raw.execute(
        "CREATE TABLE company_intelligence (id INTEGER PRIMARY KEY, lookup_key TEXT)"
    )
    raw.commit()
    raw.close()
    await reset_engine()
    await init_db()
    engine = get_engine()
    async with engine.connect() as conn:
        rows = (await conn.execute(text("PRAGMA table_info(company_intelligence)"))).fetchall()
    assert "context" in {row[1] for row in rows}


async def test_profile_signals_persist_with_evidence(db_ready: object) -> None:
    del db_ready
    provider = _Provider(RETRIEVED_TEXT)
    async with session_scope() as session:
        record = await refresh_company_intelligence(
            session,
            "Northwind",
            source_url="https://northwind.example/about",
            source_type="official_website",
            provider=provider,
        )
    assert record.intelligence_version == "phase8-v2"
    assert record.context is not None
    assert record.context["version"] == "phase8-v2"
    payments = _one(record, "domain:payments")
    assert payments["value"] == "payments"
    assert payments["source_type"] == "official_website"
    assert payments["source_url"] == "https://northwind.example/about"
    assert "payments" in str(payments["snippet"])
    assert str(payments["observed_at"]).startswith("2026-10-02")
    assert _one(record, "mba_internship_program")["value"] is True
    assert _one(record, "us_operations")["value"] is True
    assert _one(record, "exchange")["value"] == "NYSE"
    assert _one(record, "revenue")["basis"] == "explicit"
    assert provider.calls == 1
    async with session_scope() as session:
        again = await refresh_company_intelligence(
            session,
            "Northwind",
            source_url="https://northwind.example/about",
            provider=provider,
        )
    assert provider.calls == 2
    assert len(_signals(again)) == len(_signals(record))
    again_names = [item["signal"] for item in _signals(again)]
    record_names = [item["signal"] for item in _signals(record)]
    assert again_names == record_names


async def test_changed_page_replaces_that_source_and_keeps_another(db_ready: object) -> None:
    del db_ready
    async with session_scope() as session:
        first = await refresh_company_intelligence(
            session,
            "Northwind",
            source_url="https://northwind.example/about",
            source_type="official_website",
            provider=_Provider("Northwind has U.S. operations in payments."),
        )
        assert _one(first, "us_operations")["value"] is True
        second = await refresh_company_intelligence(
            session,
            "Northwind",
            source_url="https://careers.northwind.example/students",
            source_type="careers",
            provider=_Provider("Students may join the internship program."),
        )
        names = {item["signal"] for item in _signals(second)}
        assert "us_operations" in names
        assert "internship_program" in names
        assert "mba_internship_program" not in names
        replaced = await refresh_company_intelligence(
            session,
            "Northwind",
            source_url="https://northwind.example/about",
            source_type="official_website",
            provider=_Provider("Northwind is a healthcare company."),
        )
    names = {item["signal"] for item in _signals(replaced)}
    assert "domain:healthcare" in names
    assert "domain:payments" not in names
    assert "us_operations" not in names
    assert "internship_program" in names


async def test_company_facts_do_not_change_job_decisions(db_ready: object, profile: object) -> None:
    del db_ready
    posting = RawPosting(
        source=Source.linkedin,
        external_id="co-decision",
        title="Intern",
        company="Northwind",
        location="Seattle, WA",
        url="https://example.com/co-decision",
        description_clean=(
            "Join the product internship and own a roadmap with the team this summer. "
            "The posting does not mention visa sponsorship."
        ),
    )
    async with session_scope() as session:
        job = await upsert_job(session, to_job(posting, status=Status.staged))
        job.score = 80
        job.priority_score = 70
        job.role_family = "PRODUCT_MANAGEMENT"
        job.role_family_weight = 40
        job.shortlist_rank = 1
        await attach_eligibility(job, profile)  # type: ignore[arg-type]
        eligibility = job.eligibility_state
        priority = job.priority_score
        await attach_company_intelligence(
            session,
            job,
            source_url="https://northwind.example/about",
            provider=_Provider(
                "We do not sponsor visas. "
                "Northwind has U.S. operations and an MBA internship program."
            ),
        )
    assert job.eligibility_state == eligibility
    assert job.score == 80
    assert job.priority_score == priority
    assert job.role_family_weight == 40
    assert job.shortlist_rank == 1
    assert job.status == Status.staged


async def test_company_enrichment_failure_does_not_stop_ingestion(
    db_ready: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del db_ready
    from scraper.ingest import run_ingestion

    async def boom(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("company lookup down")

    async def one_posting(*_args: object, **_kwargs: object) -> list[RawPosting]:
        return [
            RawPosting(
                source=Source.linkedin,
                external_id="co-ingest",
                title="Intern",
                company="Northwind",
                location="Remote",
                url="https://example.com/co-ingest",
                description_clean=(
                    "A summer product internship with a written description of the work."
                ),
            )
        ]

    monkeypatch.setattr("scraper.ingest.fetch_linkedin_indeed", one_posting)
    monkeypatch.setattr("scraper.ingest.attach_company_intelligence", boom)
    summary = await run_ingestion(include_workday=False)
    assert summary.errors == []
    assert summary.upserted == 1

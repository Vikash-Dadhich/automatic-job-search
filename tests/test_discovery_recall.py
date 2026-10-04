"""Offline recall against a frozen posting list. Synthetic rows are not the sample."""

from __future__ import annotations

from pathlib import Path

import pytest

from scraper.discovery_recall import (
    BenchmarkCase,
    Observation,
    ObservedJob,
    load_benchmark,
    measure_recall,
)

FIXTURE = (
    Path(__file__).resolve().parent / "fixtures" / "discovery_recall_benchmark.yaml"
)


def _case(*observations: Observation, **kwargs: object) -> BenchmarkCase:
    data: dict[str, object] = {
        "case_id": "synthetic-1",
        "relevant": True,
        "internship": True,
        "summer_2027": True,
        "verified_on": "2026-10-04",
        "provenance": "synthetic test row, not a verified posting",
        "role_family": "PRODUCT_MANAGEMENT",
        "observations": observations,
    }
    data.update(kwargs)
    return BenchmarkCase(**data)  # type: ignore[arg-type]


def _job(**kwargs: object) -> ObservedJob:
    data: dict[str, object] = {
        "source": "linkedin",
        "external_id": "ext-1",
        "url": "https://www.linkedin.com/jobs/view/100",
        "company": "Acme",
        "title": "Product Manager Intern",
        "location": "Seattle, WA",
        "content_hash": None,
    }
    data.update(kwargs)
    return ObservedJob(**data)  # type: ignore[arg-type]


def test_source_id_matches_and_title_alone_does_not() -> None:
    case = _case(Observation(source="linkedin", external_id="ext-1", title="Other title"))
    same_title = _job(external_id="different", title="Product Manager Intern", url=None)
    assert measure_recall([case], [same_title]).matched == 0
    stored = _job(external_id="ext-1", title="Unrelated title", url=None)
    report = measure_recall([case], [stored])
    assert report.status == "measured"
    assert report.relevant == 1
    assert report.matched == 1
    assert report.recall == 100.0
    assert report.unmatched_ids == ()


def test_unmatched_case_is_named() -> None:
    case = _case(
        Observation(
            source="indeed",
            external_id="miss-9",
            url="https://www.indeed.com/viewjob?jk=miss-9",
        ),
        case_id="missing-posting",
    )
    report = measure_recall([case], [_job()])
    assert report.matched == 0
    assert report.unmatched == 1
    assert report.recall == 0.0
    assert report.unmatched_ids == ("missing-posting",)


def test_two_boards_count_as_one_expected_job() -> None:
    case = _case(
        Observation(
            source="linkedin",
            external_id="li-1",
            url="https://jobs.example.com/postings/42?utm_source=li",
            company="Acme",
            title="Product Manager Intern",
            location="Seattle, WA",
        ),
        Observation(
            source="indeed",
            external_id="in-9",
            url="https://jobs.example.com/postings/42?utm_source=indeed",
            company="Acme",
            title="Product Manager Intern",
            location="Seattle, WA",
        ),
        case_id="one-posting",
    )
    stored = _job(
        source="google",
        external_id="g-1",
        url="https://jobs.example.com/postings/42",
        company="Acme",
        title="Product Manager Intern",
        location="Seattle, WA",
    )
    report = measure_recall([case], [stored])
    assert report.relevant == 1
    assert report.matched == 1
    assert report.by_source["linkedin"] == {"relevant": 1, "matched": 1}
    assert report.by_source["indeed"] == {"relevant": 1, "matched": 1}
    assert sum(row["relevant"] for row in report.by_source.values()) == 2


def test_invalid_records_are_rejected(tmp_path: Path) -> None:
    path = tmp_path / "benchmark.yaml"
    path.write_text(
        "version: discovery-recall-v1\n"
        "cases:\n"
        "  - case_id: broken\n"
        "    relevant: true\n"
        "    internship: true\n"
        "    summer_2027: true\n"
        "    verified_on: '2026-10-04'\n"
        "    provenance: noted\n"
        "    observations:\n"
        "      - source: greenhouse\n"
        "        external_id: x\n"
    )
    with pytest.raises(ValueError, match="V1 board"):
        load_benchmark(path)
    path.write_text("version: other\ncases: []\n")
    with pytest.raises(ValueError, match="version"):
        load_benchmark(path)


def test_empty_sample_is_unavailable_not_perfect() -> None:
    report = measure_recall([], [])
    assert report.status == "unavailable"
    assert report.relevant == 0
    assert report.recall is None
    assert report.unmatched_ids == ()


def test_repeated_measurement_is_identical() -> None:
    case = _case(
        Observation(
            source="workday",
            external_id="R1",
            url="https://acme.wd5.myworkdayjobs.com/job/1",
        ),
        case_id="wd-1",
        role_family="CONSULTING",
    )
    jobs = [_job(source="indeed", external_id="other")]
    assert measure_recall([case], jobs) == measure_recall([case], jobs)


def test_irrelevant_rows_are_not_in_the_denominator() -> None:
    skipped = _case(
        Observation(source="linkedin", external_id="full-time"),
        case_id="not-intern",
        internship=False,
    )
    kept = _case(
        Observation(source="linkedin", external_id="ext-1"),
        case_id="kept",
        role_family="CONSULTING",
    )
    report = measure_recall([skipped, kept], [_job()])
    assert report.relevant == 1
    assert report.matched == 1
    assert report.by_family["CONSULTING"]["matched"] == 1
    assert "PRODUCT_MANAGEMENT" not in report.by_family


def test_checked_in_sample_does_not_claim_recall() -> None:
    cases = load_benchmark(FIXTURE)
    report = measure_recall(cases, [])
    if not cases:
        assert report.status == "unavailable"
        assert report.recall is None
        assert report.relevant == 0
    else:
        assert report.status == "measured"
        assert report.relevant == len([case for case in cases if case.relevant])
        assert report.recall is not None

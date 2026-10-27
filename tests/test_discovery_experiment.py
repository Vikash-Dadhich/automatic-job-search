"""Offline checks for the frozen catalog experiment. No job boards."""

from __future__ import annotations

from pathlib import Path

import pytest

from scraper.coverage import SearchStatus, observe_search
from scraper.discovery import enabled_query_texts, load_discovery
from scraper.discovery_experiment import (
    ARM_BASELINE,
    ARM_TREATMENT,
    ExperimentRefusal,
    FrozenPhrase,
    QueryExecution,
    _execute_phrase,
    _from_observation,
    account_executions,
    build_schedule,
    compare_arms,
    load_arms,
    plan_request_volume,
    run_discovery_experiment,
    scheduled_slots,
    treatment_only_phrases,
)

_NEW = (
    "Product Growth Intern",
    "AI Consulting Intern",
    "New Ventures Intern",
    "Customer Strategy Intern",
    "Strategic Analytics Intern",
    "Innovation Strategy Intern",
    "Digital Transformation Intern",
    "AI Transformation Intern",
    "AI Strategy Intern",
    "Data Strategy MBA Intern",
    "General Management Intern",
    "General Management MBA Intern",
)

_ROOT = Path(__file__).resolve().parent.parent


def test_frozen_catalogs_have_unique_counts() -> None:
    baseline, treatment = load_arms()
    assert len(baseline) == 111
    assert len(treatment) == 123
    assert len({item.query.casefold() for item in baseline}) == 111
    assert len({item.query.casefold() for item in treatment}) == 123
    assert {item.arm for item in baseline} == {ARM_BASELINE}
    assert {item.arm for item in treatment} == {ARM_TREATMENT}
    assert treatment_only_phrases(baseline, treatment) == _NEW


# SHA-256 of the baseline queries joined by newlines, frozen from HEAD 2b5e462.
_FROZEN_BASELINE_SHA256 = "5a765f969025ff227a2c27ede6db9ae59be5703e57ff2470be4c147f4a556410"


def test_baseline_fixture_stays_the_pre_fix9_list() -> None:
    import hashlib

    baseline, _treatment = load_arms()
    assert len(baseline) == 111
    assert len({item.query.casefold() for item in baseline}) == 111
    digest = hashlib.sha256("\n".join(item.query for item in baseline).encode()).hexdigest()
    assert digest == _FROZEN_BASELINE_SHA256


def test_treatment_matches_the_production_catalog() -> None:
    _baseline, treatment = load_arms()
    assert [item.query for item in treatment] == enabled_query_texts()


def test_schedule_is_deterministic_and_uses_both_arm_orders() -> None:
    baseline, treatment = load_arms()
    first = build_schedule(baseline, treatment, seed=0)
    second = build_schedule(baseline, treatment, seed=0)
    assert first == second
    assert len(first) == 234
    baseline_queries = [item.query for item in first if item.arm == ARM_BASELINE]
    treatment_queries = [item.query for item in first if item.arm == ARM_TREATMENT]
    assert baseline_queries == [item.query for item in baseline]
    assert treatment_queries != [item.query for item in treatment]
    assert sorted(treatment_queries) == sorted(item.query for item in treatment)
    orders: set[tuple[str, str]] = set()
    shared = {item.query.casefold() for item in baseline}
    for query in shared:
        arms = tuple(item.arm for item in first if item.query.casefold() == query)
        assert len(arms) == 2
        orders.add((arms[0], arms[1]))
    assert orders == {(ARM_BASELINE, ARM_TREATMENT), (ARM_TREATMENT, ARM_BASELINE)}


@pytest.mark.asyncio
async def test_dry_run_does_not_fetch_or_write(tmp_path: Path) -> None:
    catalog = Path("config/discovery.yaml").read_text(encoding="utf-8")
    before = enabled_query_texts()

    async def forbidden(*_args: object, **_kwargs: object) -> list[object]:
        raise AssertionError("dry-run contacted a source")

    report = await run_discovery_experiment(
        live=False,
        seed=1,
        experiment_id="dry",
        persist_dir=tmp_path,
        jobspy_fetch=forbidden,
        workday_fetch=forbidden,
    )
    assert report["mode"] == "dry_run"
    assert report["status"] == "planned"
    assert report["measured"] is False
    assert report["external_requests"] is False
    assert report["database_writes"] is False
    assert report["telegram"] is False
    assert report["persisted_path"] is None
    assert report["executions"] == []
    assert report["arms"][ARM_BASELINE]["phrases"] == 111
    assert report["arms"][ARM_TREATMENT]["phrases"] == 123
    assert report["schedule_length"] == 234
    assert list(tmp_path.iterdir()) == []
    assert Path("config/discovery.yaml").read_text(encoding="utf-8") == catalog
    assert enabled_query_texts() == before
    weights = {family.id: str(family.weight) for family in load_discovery().families}
    assert weights == {
        "PRODUCT_MANAGEMENT": "0.40",
        "CONSULTING": "0.40",
        "STRATEGY_TRANSFORMATION": "0.15",
        "OTHER": "0.05",
    }


@pytest.mark.asyncio
async def test_persist_without_live_is_refused() -> None:
    with pytest.raises(ExperimentRefusal):
        await run_discovery_experiment(live=False, persist=True, seed=1)


def _execution(
    arm: str,
    query: str,
    source: str,
    identities: tuple[str, ...] = (),
    status: str = "results",
    *,
    possible_cap: bool = False,
    result_count: int | None = None,
) -> QueryExecution:
    count = result_count
    if count is None:
        count = len(identities) if status == "results" else (0 if status == "empty" else None)
    return QueryExecution(
        experiment_id="math",
        arm=arm,
        family_id="FAMILY",
        bucket_id="BUCKET",
        query=query,
        source=source,
        detail="",
        started_at="t",
        finished_at="t",
        status=status,
        result_count=count,
        unidentified=0,
        identities=identities if status == "results" else (),
        possible_cap=possible_cap,
        error=None,
    )


def test_comparison_math_keeps_failures_out_of_yield() -> None:
    rows = [
        _execution(
            ARM_BASELINE,
            "Consulting Intern",
            "linkedin",
            ("linkedin:li-a", "linkedin:li-a"),
        ),
        _execution(ARM_BASELINE, "Strategy Intern", "linkedin", ("linkedin:li-b",)),
        _execution(ARM_TREATMENT, "Consulting Intern", "linkedin", ("linkedin:li-a",)),
        _execution(ARM_TREATMENT, "Product Growth Intern", "linkedin", ("linkedin:li-4471167170",)),
        _execution(ARM_TREATMENT, "AI Strategy Intern", "linkedin", ("linkedin:li-a",)),
        _execution(ARM_BASELINE, "Strategy Intern", "indeed", status="failed", result_count=None),
        _execution(ARM_TREATMENT, "AI Consulting Intern", "indeed", status="empty"),
        _execution(
            ARM_TREATMENT,
            "General Management Intern",
            "google",
            status="incomplete",
            result_count=None,
        ),
        _execution(
            ARM_BASELINE,
            "Consulting Intern",
            "zip_recruiter",
            ("zip_recruiter:capped",),
            possible_cap=True,
        ),
        _execution(ARM_BASELINE, "Consulting Intern", "workday", status="not_executed"),
    ]
    report = compare_arms(
        rows,
        new_phrases=_NEW,
        baseline_slots={
            ("consulting intern", "linkedin", ""),
            ("strategy intern", "linkedin", ""),
        },
    )
    baseline = report["overall"]["baseline"]
    treatment = report["overall"]["treatment"]
    assert baseline["failed"] == 1
    assert baseline["empty"] == 0
    assert baseline["capped"] == 1
    assert baseline["skipped"] == 1
    assert treatment["empty"] == 1
    assert treatment["incomplete"] == 1
    assert treatment["failed"] == 0
    assert baseline["raw_results"] == 4
    assert baseline["unique_identities"] == 3
    assert baseline["duplicate_identities"] == 1
    assert report["in_both_arms"] == ["linkedin:li-a"]
    assert report["baseline_only"] == ["linkedin:li-b", "zip_recruiter:capped"]
    assert "linkedin:li-4471167170" in report["treatment_only"]
    assert report["incremental"]["vocabulary_only"] == ["linkedin:li-4471167170"]
    assert report["incremental"]["mixed_with_shared_phrases"] == []
    assert report["verified_summer_2027_mba_in_vocabulary_increment"] == [
        {"identity": "linkedin:li-4471167170", "case_id": "li-4471167170"}
    ]
    indeed = report["by_source"]["indeed"]["baseline"]
    assert indeed["failed"] == 1
    assert indeed["empty"] == 0
    assert indeed["raw_results"] == 0


def test_failed_hits_are_not_attributed() -> None:
    failed = observe_search(
        family_id="CONSULTING",
        bucket_id="MANAGEMENT_CONSULTING",
        query="Consulting Intern",
        source="indeed",
        hits=("indeed:should-not-count",),
        error="api_key=supersecret",
        failed=True,
    )
    assert failed.status.value == "partial"
    assert failed.identities == ("indeed:should-not-count",)
    row = _execution(
        ARM_BASELINE,
        "Consulting Intern",
        "indeed",
        ("indeed:should-not-count",),
        status="failed",
        result_count=None,
    )
    report = compare_arms([row], new_phrases=_NEW)
    assert report["overall"]["baseline"]["failed"] == 1
    assert report["overall"]["baseline"]["empty"] == 0
    assert report["overall"]["baseline"]["unique_identities"] == 0
    assert report["in_both_arms"] == []
    assert "supersecret" not in (failed.error or "")


def test_production_paths_do_not_launch_the_experiment() -> None:
    for relative in (
        "orchestrator/pipeline.py",
        "orchestrator/scheduler.py",
        "scraper/ingest.py",
        ".github/workflows/ci.yml",
        ".github/workflows/pipeline.yml",
    ):
        text = (_ROOT / relative).read_text(encoding="utf-8")
        assert "discovery_experiment" not in text
        assert "discovery-experiment" not in text
    module = (_ROOT / "scraper" / "discovery_experiment.py").read_text(encoding="utf-8")
    assert "run_ingestion" not in module
    assert "upsert_job" not in module
    assert "Telegram" not in module
    runner = (_ROOT / "main.py").read_text(encoding="utf-8")
    assert 'command == "discovery-experiment"' in runner
    assert "run_pipeline" in runner
    serve = runner.split("async def _cmd_serve", 1)[1].split("async def _cmd_run_once", 1)[0]
    once = runner.split("async def _cmd_run_once", 1)[1].split("async def _cmd_poll", 1)[0]
    assert "discovery-experiment" not in serve
    assert "discovery-experiment" not in once


def test_cli_defaults_to_dry_run() -> None:
    from main import build_parser

    args = build_parser().parse_args(["discovery-experiment"])
    assert args.live is False
    assert args.persist is False
    assert args.seed is None


@pytest.mark.asyncio
async def test_live_fake_attributes_only_the_requested_phrase(tmp_path: Path) -> None:
    from config.targets import SearchConfig, Targets, WorkdayTenant

    targets = Targets(
        search=SearchConfig(
            sites=["linkedin"],
            location="United States",
            hours_old=36,
            results_wanted=50,
            terms=["not-the-experiment-list"],
        ),
        workday_tenants=[
            WorkdayTenant(
                name="Example",
                url="https://example.wd1.myworkdayjobs.com/ExampleSite",
            )
        ],
    )

    async def jobspy(_targets: object, plan: object, observations: list[object]) -> list[object]:
        search = plan.searches[0]  # type: ignore[attr-defined]
        for site in plan.jobspy_sites:  # type: ignore[attr-defined]
            hits: tuple[str, ...] = ()
            if site == "linkedin" and search.query == "Product Growth Intern":
                hits = ("linkedin:li-4471167170",)
            observations.append(
                observe_search(
                    family_id=search.family_id,
                    bucket_id=search.bucket_id,
                    query=search.query,
                    source=site,
                    hits=hits,
                )
            )
        return []

    async def workday(
        tenant: object,
        *,
        search_terms: list[str],
        hours_old: int,
        provenance: dict[str, tuple[str, str]],
        observations: list[object],
    ) -> list[object]:
        del hours_old
        term = search_terms[0]
        family_id, bucket_id = provenance[term]
        observations.append(
            observe_search(
                family_id=family_id,
                bucket_id=bucket_id,
                query=term,
                source="workday",
                detail=tenant.name,  # type: ignore[attr-defined]
                hits=(),
            )
        )
        return []

    report = await run_discovery_experiment(
        live=True,
        persist=True,
        seed=2,
        experiment_id="live-fake",
        persist_dir=tmp_path,
        targets=targets,
        jobspy_fetch=jobspy,
        workday_fetch=workday,
    )
    assert report["mode"] == "live"
    assert report["status"] == "complete"
    assert report["database_writes"] is False
    assert report["external_requests"] is True
    saved = tmp_path / "live-fake.json"
    assert saved.exists()
    assert report["persisted_path"] == str(saved)
    assert "not-the-experiment-list" not in saved.read_text(encoding="utf-8")
    comparison = report["comparison"]
    assert comparison["treatment_only"] == ["linkedin:li-4471167170"]
    assert comparison["baseline_only"] == []
    assert comparison["incremental"]["vocabulary_only"] == ["linkedin:li-4471167170"]
    assert comparison["incremental"]["shared_phrase_only"] == []
    assert comparison["verified_summer_2027_mba_in_vocabulary_increment"] == [
        {"identity": "linkedin:li-4471167170", "case_id": "li-4471167170"}
    ]
    growth = [
        row
        for row in report["executions"]
        if row["query"] == "Product Growth Intern" and row["source"] == "linkedin"
    ]
    assert len(growth) == 1
    assert growth[0]["arm"] == ARM_TREATMENT
    assert growth[0]["identities"] == ["linkedin:li-4471167170"]
    failed_as_empty = [
        row for row in report["executions"] if row["status"] == "empty" and row["result_count"] != 0
    ]
    assert failed_as_empty == []
    withheld = comparison["incremental"]["vocabulary_withheld"]
    confirmed = set(comparison["incremental"]["vocabulary_only"])
    mixed = set(comparison["incremental"]["mixed_with_shared_phrases"])
    shared = set(comparison["incremental"]["shared_phrase_only"])
    assert confirmed | {item["identity"] for item in withheld} | mixed | shared == set(
        comparison["treatment_only"]
    )


def _yield_pair(baseline_status: str) -> list[QueryExecution]:
    if baseline_status == "results":
        baseline = _execution(
            ARM_BASELINE,
            "Consulting Intern",
            "linkedin",
            ("linkedin:li-old",),
        )
    elif baseline_status == "empty":
        baseline = _execution(ARM_BASELINE, "Consulting Intern", "linkedin", status="empty")
    else:
        baseline = _execution(
            ARM_BASELINE,
            "Consulting Intern",
            "linkedin",
            status=baseline_status,
            result_count=None,
        )
    treatment = _execution(
        ARM_TREATMENT,
        "Product Growth Intern",
        "linkedin",
        ("linkedin:li-new",),
    )
    return [baseline, treatment]


def test_baseline_failure_blocks_confirmed_vocabulary() -> None:
    report = compare_arms(
        _yield_pair("failed"),
        new_phrases=_NEW,
        baseline_slots={("consulting intern", "linkedin", "")},
    )
    assert report["incremental"]["vocabulary_only"] == []
    assert report["incremental"]["vocabulary_withheld"] == [
        {"identity": "linkedin:li-new", "reason": "baseline_failed"}
    ]


def test_missing_baseline_slot_blocks_confirmed_vocabulary() -> None:
    treatment = _execution(
        ARM_TREATMENT,
        "Product Growth Intern",
        "linkedin",
        ("linkedin:li-new",),
    )
    report = compare_arms(
        [treatment],
        new_phrases=_NEW,
        baseline_slots={("consulting intern", "linkedin", "")},
    )
    assert report["incremental"]["vocabulary_only"] == []
    assert report["incremental"]["vocabulary_withheld"] == [
        {"identity": "linkedin:li-new", "reason": "missing_baseline"}
    ]


def test_incomplete_run_has_no_confirmed_vocabulary() -> None:
    report = compare_arms(
        _yield_pair("empty"),
        new_phrases=_NEW,
        baseline_slots={("consulting intern", "linkedin", "")},
        run_complete=False,
    )
    assert report["incremental"]["vocabulary_only"] == []
    assert report["incremental"]["vocabulary_withheld"] == [
        {"identity": "linkedin:li-new", "reason": "run_incomplete"}
    ]


def test_complete_baseline_confirms_treatment_only_candidate() -> None:
    report = compare_arms(
        _yield_pair("empty"),
        new_phrases=_NEW,
        baseline_slots={("consulting intern", "linkedin", "")},
        run_complete=True,
    )
    assert report["incremental"]["vocabulary_only"] == ["linkedin:li-new"]
    assert report["incremental"]["vocabulary_withheld"] == []
    withheld = report["incremental"]["vocabulary_withheld"]
    pieces = (
        set(report["incremental"]["vocabulary_only"])
        | {item["identity"] for item in withheld}
        | set(report["incremental"]["mixed_with_shared_phrases"])
        | set(report["incremental"]["shared_phrase_only"])
    )
    assert pieces == set(report["treatment_only"])


def test_partial_workday_keeps_the_error_and_blocks_completeness() -> None:
    from config.targets import WorkdayTenant
    from scraper.workday_rest import _workday_observation

    tenant = WorkdayTenant(
        name="Example",
        url="https://example.wd1.myworkdayjobs.com/ExampleSite",
    )
    observation = _workday_observation(
        tenant,
        "Consulting Intern",
        ("workday:example:JR1",),
        provenance={"Consulting Intern": ("CONSULTING", "MANAGEMENT_CONSULTING")},
        error="HTTP 500 after the first page",
    )
    assert observation.status is SearchStatus.partial
    assert observation.identities == ("workday:example:JR1",)
    assert observation.error is not None
    assert "HTTP 500" in observation.error
    assert observation.status is not SearchStatus.empty
    baseline = _execution(
        ARM_BASELINE,
        "Consulting Intern",
        "workday",
        ("workday:example:JR1",),
        status="partial",
    )
    treatment = _execution(
        ARM_TREATMENT,
        "Product Growth Intern",
        "workday",
        ("workday:example:JR9",),
    )
    report = compare_arms(
        [baseline, treatment],
        new_phrases=_NEW,
        baseline_slots={("consulting intern", "workday", "")},
    )
    assert report["incremental"]["vocabulary_only"] == []
    assert report["incremental"]["vocabulary_withheld"] == [
        {"identity": "workday:example:JR9", "reason": "baseline_incomplete"}
    ]


@pytest.mark.asyncio
async def test_jobspy_exception_keeps_earlier_observations() -> None:
    from config.targets import SearchConfig, Targets, WorkdayTenant

    targets = Targets(
        search=SearchConfig(sites=["linkedin"], location="United States", hours_old=36),
        workday_tenants=[
            WorkdayTenant(name="Example", url="https://example.wd1.myworkdayjobs.com/ExampleSite")
        ],
    )
    settings = {
        "jobspy_sites": ["linkedin"],
        "workday_enabled": True,
        "active_workday_tenants": ["Example"],
    }
    phrase = FrozenPhrase(ARM_BASELINE, "CONSULTING", "MANAGEMENT_CONSULTING", "Consulting Intern")

    async def jobspy(_targets: object, plan: object, observations: list[object]) -> list[object]:
        search = plan.searches[0]  # type: ignore[attr-defined]
        observations.append(
            observe_search(
                family_id=search.family_id,
                bucket_id=search.bucket_id,
                query=search.query,
                source="linkedin",
                hits=("linkedin:li-kept",),
            )
        )
        return []

    async def workday(*_args: object, **_kwargs: object) -> list[object]:
        raise RuntimeError("api_key=supersecret")

    rows = await _execute_phrase(
        phrase,
        experiment_id="partial-exc",
        targets=targets,
        settings=settings,
        jobspy_fetch=jobspy,
        workday_fetch=workday,
    )
    linkedin = next(row for row in rows if row.source == "linkedin")
    workday_row = next(row for row in rows if row.source == "workday")
    assert linkedin.status == "results"
    assert linkedin.identities == ("linkedin:li-kept",)
    assert workday_row.status == "failed"
    assert workday_row.result_count is None
    assert workday_row.identities == ()
    assert "supersecret" not in (workday_row.error or "")
    assert all(row.status != "empty" for row in rows)


def test_unrecognized_jobspy_site_is_unidentified_not_empty() -> None:
    from scraper.discovery import PlannedSearch
    from scraper.linkedin_jobspy import _dataframe_to_postings, _jobspy_observations

    class _Frame:
        def __init__(self, rows: list[dict[str, str]]) -> None:
            self._rows = rows
            self.empty = False

        def to_dict(self, orient: str) -> list[dict[str, str]]:
            assert orient == "records"
            return self._rows

    rows = [
        {
            "site": "",
            "title": "Hidden Intern",
            "company": "Secret Co",
            "job_url": "https://example.test/hidden",
            "id": "mystery-1",
        },
        {
            "site": "linkedin",
            "title": "Known Intern",
            "company": "Acme",
            "job_url": "https://www.linkedin.com/jobs/view/9",
            "id": "li-9",
        },
    ]
    _kept, stats = _dataframe_to_postings(_Frame(rows), profile=None, search=None)
    assert stats["unidentified"]["count"] == 1
    assert all(posting.source.value != "" for posting in _kept)
    notes = _jobspy_observations(
        PlannedSearch("CONSULTING", "MANAGEMENT_CONSULTING", "Consulting Intern"),
        ["linkedin"],
        _kept,
        stats=stats,
    )
    by_source = {note.source: note for note in notes}
    assert by_source["unidentified"].unidentified_count == 1
    assert by_source["unidentified"].identities == ()
    assert by_source["unidentified"].status is SearchStatus.partial
    assert by_source["linkedin"].status is SearchStatus.partial
    assert by_source["linkedin"].status is not SearchStatus.empty
    assert by_source["linkedin"].identities == ("linkedin:li-9",)
    identity_blob = " ".join(identity for note in notes for identity in note.identities)
    hit_blob = " ".join(str(hit) for note in notes for hit in note.hits)
    blob = identity_blob + " " + hit_blob
    assert "mystery-1" not in blob
    assert "Hidden Intern" not in blob
    treatment = _execution(
        ARM_TREATMENT,
        "Product Growth Intern",
        "linkedin",
        ("linkedin:li-new",),
    )
    report = compare_arms(
        [
            QueryExecution(
                experiment_id="u",
                arm=ARM_BASELINE,
                family_id="F",
                bucket_id="B",
                query="Consulting Intern",
                source="linkedin",
                detail="",
                started_at="t",
                finished_at="t",
                status="partial",
                result_count=1,
                unidentified=1,
                identities=("linkedin:li-9",),
                possible_cap=False,
                error="jobspy rows had no recognized site and were not attributed",
                ambiguous=True,
            ),
            treatment,
        ],
        new_phrases=_NEW,
        baseline_slots={("consulting intern", "linkedin", "")},
    )
    assert report["incremental"]["vocabulary_only"] == []
    assert report["incremental"]["vocabulary_withheld"][0]["reason"] == "ambiguous_attribution"


def test_google_rewrite_is_visible_and_yield_is_withheld() -> None:
    from scraper.linkedin_jobspy import _google_search_term, google_executed_query

    assert google_executed_query("AI Strategy Intern") == "AI Strategy Intern internship"
    assert _google_search_term(None, "AI Strategy Intern") == "AI Strategy Intern internship"  # type: ignore[arg-type]
    phrase = FrozenPhrase(
        ARM_TREATMENT, "STRATEGY_TRANSFORMATION", "TECHNOLOGY_STRATEGY", "AI Strategy Intern"
    )
    observation = observe_search(
        family_id=phrase.family_id,
        bucket_id=phrase.bucket_id,
        query=phrase.query,
        source="google",
        hits=("google:g-1",),
    )
    recorded = _from_observation(observation, phrase, "g", "t", "t")
    assert recorded.query == "AI Strategy Intern"
    assert recorded.executed_query == "AI Strategy Intern internship"
    assert recorded.executed_query != recorded.query
    baseline = _execution(ARM_BASELINE, "Strategy Intern", "google", status="empty")
    report = compare_arms(
        [baseline, recorded],
        new_phrases=_NEW,
        baseline_slots={("strategy intern", "google", "")},
        run_complete=True,
    )
    assert report["incremental"]["vocabulary_only"] == []
    assert report["incremental"]["vocabulary_withheld"] == [
        {"identity": "google:g-1", "reason": "ambiguous_attribution"}
    ]


def test_slot_accounting_reconciles() -> None:
    phrase = FrozenPhrase(ARM_BASELINE, "CONSULTING", "MANAGEMENT_CONSULTING", "Consulting Intern")
    settings = {"jobspy_sites": ["linkedin"], "workday_enabled": False}
    slots = scheduled_slots((phrase,), settings)
    assert slots == {(ARM_BASELINE, "consulting intern", "linkedin", "")}

    empty_incremental: dict[str, list[object]] = {
        "vocabulary_only": [],
        "vocabulary_withheld": [],
    }

    def check(rows: list[QueryExecution], field: str) -> None:
        account = account_executions(rows, slots, empty_incremental)
        assert account["scheduled_slots"] == 1
        total = (
            account["completed_slots"]
            + account["partial_slots"]
            + account["failed_slots"]
            + account["skipped_slots"]
            + account["incomplete_slots"]
        )
        assert total == account["scheduled_slots"]
        assert account[field] == 1

    hit = _execution(ARM_BASELINE, "Consulting Intern", "linkedin", ("linkedin:li-1",))
    check([hit], "completed_slots")
    assert account_executions([hit], slots, empty_incremental)["raw_attributed_hits"] == 1
    partial = _execution(
        ARM_BASELINE,
        "Consulting Intern",
        "linkedin",
        status="partial",
        result_count=0,
    )
    check([partial], "partial_slots")
    check(
        [
            _execution(
                ARM_BASELINE,
                "Consulting Intern",
                "linkedin",
                status="failed",
                result_count=None,
            )
        ],
        "failed_slots",
    )
    check([], "incomplete_slots")
    unidentified = QueryExecution(
        experiment_id="u",
        arm=ARM_BASELINE,
        family_id="F",
        bucket_id="B",
        query="Consulting Intern",
        source="unidentified",
        detail="",
        started_at="t",
        finished_at="t",
        status="partial",
        result_count=0,
        unidentified=2,
        identities=(),
        possible_cap=False,
        error=None,
        ambiguous=True,
    )
    partial_hit = QueryExecution(
        experiment_id="u",
        arm=ARM_BASELINE,
        family_id="F",
        bucket_id="B",
        query="Consulting Intern",
        source="linkedin",
        detail="",
        started_at="t",
        finished_at="t",
        status="partial",
        result_count=1,
        unidentified=0,
        identities=("linkedin:li-9",),
        possible_cap=False,
        error=None,
        ambiguous=True,
    )
    account = account_executions([partial_hit, unidentified], slots, empty_incremental)
    assert account["observation_rows"] == 2
    assert account["scheduled_slots"] == 1
    assert account["partial_slots"] == 1
    assert account["completed_slots"] == 0
    assert account["unidentified_rows"] == 2
    assert account["raw_attributed_hits"] == 1
    assert account["distinct_identities"] == 1


def test_finished_runner_is_not_the_same_as_every_slot_succeeding() -> None:
    phrase = FrozenPhrase(ARM_BASELINE, "CONSULTING", "MANAGEMENT_CONSULTING", "Consulting Intern")
    settings = {"jobspy_sites": ["linkedin"], "workday_enabled": False}
    failed = _execution(
        ARM_BASELINE,
        "Consulting Intern",
        "linkedin",
        status="failed",
        result_count=None,
    )
    account = account_executions(
        [failed],
        scheduled_slots((phrase,), settings),
        {"vocabulary_only": [], "vocabulary_withheld": []},
    )
    assert account["failed_slots"] == 1
    assert account["completed_slots"] == 0
    assert failed.status != "empty"


@pytest.mark.asyncio
async def test_keyboard_interrupt_is_not_a_complete_report() -> None:
    from config.targets import SearchConfig, Targets

    targets = Targets(
        search=SearchConfig(sites=["linkedin"], location="United States", hours_old=36),
    )

    async def jobspy(*_args: object, **_kwargs: object) -> list[object]:
        raise KeyboardInterrupt

    async def workday(*_args: object, **_kwargs: object) -> list[object]:
        raise AssertionError("workday should not run")

    with pytest.raises(KeyboardInterrupt):
        await run_discovery_experiment(
            live=True,
            seed=1,
            experiment_id="interrupt",
            targets=targets,
            jobspy_fetch=jobspy,
            workday_fetch=workday,
        )


def test_request_volume_separates_jobspy_workday_and_slots() -> None:
    shared = FrozenPhrase(ARM_BASELINE, "CONSULTING", "MANAGEMENT_CONSULTING", "Consulting Intern")
    shared_again = FrozenPhrase(
        ARM_TREATMENT, "CONSULTING", "MANAGEMENT_CONSULTING", "Consulting Intern"
    )
    extra = FrozenPhrase(
        ARM_TREATMENT, "CONSULTING", "TECHNOLOGY_CONSULTING", "AI Consulting Intern"
    )
    schedule = (shared, shared_again, extra)
    baseline = (shared,)
    treatment = (shared_again, extra)
    settings = {
        "jobspy_sites": ["linkedin", "indeed"],
        "workday_enabled": True,
        "active_workday_tenants": ["Example", "Other"],
    }
    volume = plan_request_volume(schedule, baseline, treatment, settings)
    assert volume["shared_phrases"] == 1
    assert volume["shared_phrase_executions"] == 2
    assert volume["treatment_only_phrases"] == 1
    assert volume["treatment_only_executions"] == 1
    assert volume["schedule_length"] == 3
    assert volume["jobspy_phrase_calls"] == 3
    assert volume["jobspy_sites_per_call"] == 2
    assert volume["workday_tenant_calls"] == 6
    assert volume["workday_tenants"] == 2
    assert volume["planned_adapter_calls"] == 9
    assert volume["scheduled_observation_slots"] == 12
    assert volume["scheduled_observation_slots"] != volume["jobspy_phrase_calls"]
    assert volume["scheduled_observation_slots"] != volume["workday_tenant_calls"]
    assert "not an HTTP request count" in volume["note"]
    executions = (
        volume["shared_phrase_executions"]
        + volume["treatment_only_executions"]
        + volume["baseline_only_executions"]
    )
    assert executions == volume["schedule_length"]


@pytest.mark.asyncio
async def test_current_config_dry_run_states_adapter_call_counts() -> None:
    report = await run_discovery_experiment(live=False, seed=1, experiment_id="volume")
    volume = report["request_volume"]
    assert report["external_requests"] is False
    assert report["persisted_path"] is None
    assert volume["shared_phrases"] == 111
    assert volume["treatment_only_phrases"] == 12
    assert volume["shared_phrase_executions"] == 222
    assert volume["treatment_only_executions"] == 12
    assert volume["schedule_length"] == 234
    sites = len(report["settings"]["jobspy_sites"])
    tenants = len(report["settings"]["active_workday_tenants"])
    assert sites == 4
    assert tenants == 23
    assert volume["jobspy_phrase_calls"] == 234
    assert volume["jobspy_sites_per_call"] == 4
    assert volume["workday_tenant_calls"] == 234 * tenants
    assert volume["planned_adapter_calls"] == 234 + (234 * tenants)
    assert volume["scheduled_observation_slots"] == 234 * (4 + tenants)
    assert volume["jobspy_phrase_calls"] != volume["workday_tenant_calls"]
    assert volume["scheduled_observation_slots"] != volume["planned_adapter_calls"]
    assert "HTTP" in volume["note"]

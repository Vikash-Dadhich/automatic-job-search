# Discovery run observability

This records what a discovery run actually did. It does not change which queries run, how recent a posting must be, or which jobs are kept. It is not market recall. See [the recall benchmark](discovery-recall-benchmark.md) for that separate list.

## Where it is stored

Each pipeline run has a row in `pipeline_runs` (`run_key`, UTC `started_at`, UTC `finished_at`, status). The ingestion stage row in `pipeline_stage_runs` may also hold `evidence`, a nullable JSON document. A missing `evidence` value means that stage was recorded before this field existed, or the optional write failed. Job rows are unchanged either way.

`storage/diagnostics/discovery_coverage.json` is still overwritten each local run. The stage JSON is the copy that stays with that run. GitHub Actions logs keep aggregate lines only. They are not a substitute for `evidence`.

## What a query row means

`evidence.queries[]` uses the coverage statuses:

- `results` — at least one `source:external_id` hit remained after the filters that already ran.
- `empty` — the search finished and no hit remained. For LinkedIn and Indeed that is after the source recency parameter and the location filter. It is not proof the board had nothing.
- `failed` — the fetcher raised or the source blocked the request. The `error` string is redacted and at most 200 characters.
- `not_executed` — a planned search never ran, or a placeholder Workday tenant was skipped. A skip is not an empty result.

`fetched_count` is rows the fetcher returned for that source before the location filter (JobSpy) or before Workday recency (Workday). `retained_count` is the hits kept after those filters. `location_dropped` and `recency_dropped` are the rows removed at those boundaries. A missing Workday date is still kept.

`possible_cap_hit` is a warning. It is true when a JobSpy source returned at least `results_wanted` rows, or a Workday search stopped at `max_pages` with more listings reported. It does not prove later pages contained a missed posting.

`within_run_duplicates_removed` counts repeated `(source, external_id)` pairs inside one ingest, before the database upsert. `hard_filtered_out` is the existing negative-filter count. `persisted` is the existing upsert count. `upsert_job` does not say whether that was an insert or an update, so the payload does not invent that split.

## Recency

`hours_old` is the configured value, currently 36. The semantics differ by source and are stored on `recency_semantics`:

- LinkedIn: JobSpy sends `f_TPR` seconds equal to `hours_old * 3600` at request time.
- Indeed: JobSpy sends a `dateOnIndeed` window of `hours_old` hours.
- Google: `hours_old` is ignored because `google_search_term` replaces the time phrase.
- ZipRecruiter: `hours_old` is rounded up to the next full day.
- Workday: after the list returns, `postedOn` and `startDate` are filtered. A missing date is kept.

## What this cannot reconstruct

Runs before this field, including the September 2026 snapshot, have no per-query evidence. Actions logs from 2026-09-23 onward show that searches ran. They do not keep each query's hits. Nothing in this record can show that a source omitted a posting it never returned.

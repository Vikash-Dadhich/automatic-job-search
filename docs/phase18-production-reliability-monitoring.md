# Phase 18 — Production reliability and monitoring

Monitoring records what a pipeline run did. It does not decide which jobs are
fit, eligible, prioritized, shortlisted, allocated, or applied to.

## Purpose

The pipeline already isolates stage failures, retries transient model calls,
and keeps application state restart-safe. Phase 18 adds a small operational
history so an operator can see whether a run started, whether it finished,
which stages failed or were skipped, and whether the process looks healthy.

## Architecture

Two tables sit beside the job and application tables:

- `pipeline_runs` — one row per `run_pipeline()` invocation
- `pipeline_stage_runs` — one row per executed or skipped stage

`orchestrator/monitoring.py` writes those rows. `orchestrator/health.py` reads
them, plus existing job status counts, and returns `healthy`, `degraded`, or
`unhealthy`. Neither module changes scoring, ranking, shortlist, portfolio,
feedback, calibration, or the application tracker.

Configuration lives in `config/monitoring.yaml` and is versioned
`phase18-v1`. Each run stores that version and a hash of the effective
configuration plus the monitoring file. The hash is not a secret.

## Pipeline run lifecycle

A run is inserted as `running` before the first stage.

When `run_pipeline()` returns:

- `succeeded` — every executed stage returned
- `partial` — at least one stage raised, and later stages still ran
- `failed` — an exception escaped the pipeline itself

`partial` is not `failed`. A stage error stays in `PipelineSummary.stage_errors`
and the function still returns. `failed` means the process did not finish the
function. `duration_ms` is the time from `started_at` to `finished_at`.

## Stage telemetry

Each stage is inserted as `running` and closed as `succeeded`, `failed`, or
`skipped`. A failed row stores a short error string. Counters are the integers
the stage already returned, such as `discovered`, `scored`, `selected`,
`allocated`, and `applied`. Descriptions, answers, and full summaries are not
stored.

Skipped stages are the ones the existing flags already skip.

## Health states

`get_health_report()` is deterministic for a database, a clock, and the
configuration.

`healthy` means the database answers, configuration checks pass, no recent run
was interrupted, and the latest completed run succeeded with no recent stage
failures, no stale workflow backlog, and a manual-review queue under the
configured cap. No runs yet is healthy when the database and configuration
are fine.

`degraded` means the process can still be inspected, but the latest completed
run was `partial`, `failed`, or `interrupted`, a stage failed inside the
recent window, the manual-review queue is at the cap, or jobs are sitting in
`error` or past a stale-age threshold.

`unhealthy` means the database cannot be reached, configuration is invalid,
recent interrupted runs have reached `critical_stale_runs`, or the last
`critical_repeated_failures` completed runs are all `failed`.

A degraded or unhealthy report does not change job decisions.

## Stale runs

A run left at `running` is compared with `stale_run_minutes` (default 180).
The check runs at the start of the next pipeline and whenever health is
requested. A run younger than the threshold stays `running`. An older one
becomes `interrupted`. Nothing about the jobs in that run is replayed.

## Backlog diagnostics

Health counts existing statuses only: `discovered`, `staged`,
`pending_review`, `manual_review`, `submitted`, `error`, `filtered_out`, and
`ignored`.

It also counts jobs whose `updated_at` is older than:

- `stale_pending_review_days` (14)
- `stale_manual_review_days` (7)
- `stale_staged_days` (21)

These counts are diagnostic. Jobs are not moved, deleted, or retried.

## Configuration

`config/monitoring.yaml`:

| Setting | Default | Meaning |
| --- | --- | --- |
| `stale_run_minutes` | 180 | Age before a `running` row is `interrupted` |
| `recent_error_hours` | 24 | Window for recent stage failures and interrupted runs |
| `stale_pending_review_days` | 14 | Age before a pending review looks stale |
| `stale_manual_review_days` | 7 | Age before a manual review looks stale |
| `stale_staged_days` | 21 | Age before a staged job looks stale |
| `critical_stale_runs` | 1 | Interrupted runs in the window that make health `unhealthy` |
| `critical_repeated_failures` | 3 | Consecutive completed `failed` runs that make health `unhealthy` |
| `manual_review_backlog` | 25 | Manual-review count that makes health `degraded` |

Timezone, schedule times, and a non-empty database URL are checked with the
existing settings. Optional tokens are not required. Disabled features do not
need credentials.

## CLI

```bash
uv run python main.py health
```

Prints status, the latest run, the latest completed run, duration, stage
failures, interrupted runs, workflow counts, and database/config status. It
does not start the scheduler. `doctor` remains the separate pipeline report.
The webhook `/health` route remains a process liveness check.

## Failure isolation

Stage exceptions still land in `stage_errors` and later stages still run.
If writing a run or stage row fails, the failure is logged as
`monitoring_run_record_failed` or `monitoring_stage_record_failed` and the
pipeline continues. A health query that cannot read an optional diagnostic
returns an explicit unavailable database state instead of raising into the
scheduler.

## Restart behavior

A new process creates a new pipeline run. It does not rebuild the previous
process's memory. Interrupted history is only a label on the old operational
row. Job status, application rows, and submissions are unchanged.

## Logging

New events: `monitoring_run_started`, `monitoring_run_completed`,
`monitoring_run_interrupted`, `monitoring_stage_started`,
`monitoring_stage_completed`, `monitoring_stage_failed`,
`monitoring_health_completed`, `monitoring_config_invalid`.

They carry `run_id`, stage, status, `duration_ms`, and a short error.
They do not carry API keys, tokens, passwords, cookies, credentials, resumes,
application answers, or job descriptions. Existing `pipeline_*` events stay.

## What this phase does not change

Fit, priority, eligibility, shortlist, portfolio, feedback, calibration,
discovery, and application submission are untouched. There is no new retry
around apply, submit, Telegram approval, or resume generation. There is no
phase after this one in the plan.

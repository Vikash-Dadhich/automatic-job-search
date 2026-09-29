# Phase 3 discovery coverage

Phase 3 measures what the existing search plan actually returned. It does not change which phrases run, and it does not score jobs.

High internal discovery coverage does not prove complete market recall. There is no list of every Summer 2027 internship in the United States, so these numbers are not a share of the market.

## What a number means

A search is one planned phrase on one source. JobSpy still runs the phrase once across its sites. Each site gets its own row. Workday gets one row per tenant. Finish order does not matter. Counts follow the plan: phrase order, then site order, then tenant order.

| Status | Meaning |
|---|---|
| results | The search ran and returned postings. |
| empty | The search ran and returned nothing. |
| failed | The search did not run to a result. This is not an empty market. |
| not executed | The plan included it, but this run did not report it. |

Identity is `source` plus `external_id`, the same key already stored on a job. A posting with no external id counts as raw and unidentified. It is not treated as a new unique job. The same external id on LinkedIn and Indeed stays two discoveries. Cross-board identity is a later phase.

Incremental discovery is how many identities in that search had not already appeared in an earlier search in plan order. Repeats inside one search count once. Family, bucket, and source incremental numbers add up to the run's unique count.

Duplicate rate uses identifiable results only. Zero-result rate uses searches that ran (results plus empty) and leaves failures out of that rate.

## How to read it

A phrase with status `empty` is a weak search for that source on this run. A phrase with status `failed` says nothing about whether internships exist. A phrase whose raw count is high and whose incremental count is zero mostly repeated jobs earlier searches already found.

The run log `discovery_coverage` has the totals and family rollups. The query rows are in `storage/diagnostics/discovery_coverage.json` after a non-test ingestion. Nothing is deleted or rewritten because a search returned zero.

## Limits

These metrics describe this system's searches. They do not estimate the unseen market, rank queries by candidate fit, or merge the same job across boards.

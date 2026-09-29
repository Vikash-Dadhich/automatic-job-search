# Phase 1 discovery architecture

Recorded 29 September 2026.

The family weights represent discovery/search priority and are not candidate-to-job fit scores.

Phase 2 will expand and refine the search taxonomy and vocabulary. This phase only builds the structure those phrases plug into.

## Purpose

Search broadly, then let later phases understand, filter, and prioritize. Phase 1 stops discovery from being one flat list of queries, without changing how a job is scored.

## Current problem

Discovery ran every phrase in `config/targets.yaml` the same way. About ten internship titles were searched on LinkedIn, Indeed, Google, and ZipRecruiter, and the same list was sent to Workday. A Product Strategy internship or a Strategy Consulting internship had no home unless the title happened to match one of those ten strings.

Fit scores did not choose the queries, and they still must not.

## New architecture

```text
config/discovery.yaml          what to search
        |
        v
scraper/discovery.py           one-pass plan and capacity allocation
        |
        +--> JobSpy executor     scraper/linkedin_jobspy.py
        |
        +--> Workday executor    scraper/workday_rest.py
        |
        v
clean, hard filters, database  unchanged
```

Three concerns stay separate:

- Role taxonomy: family, bucket, query, optional title variants.
- Discovery allocation: how many query executions each family receives.
- Source execution: JobSpy sites and Workday tenants, with their existing parameters in `config/targets.yaml`.

`load_targets()` copies the enabled queries onto `search.terms` so older callers still see a flat list. The ingestion path uses the plan, not that list, to decide what runs.

## Role families

| Id | Name | Weight |
|---|---|---|
| `PRODUCT_MANAGEMENT` | Product Management | 0.40 |
| `CONSULTING` | Consulting | 0.40 |
| `STRATEGY_TRANSFORMATION` | Strategy / Transformation | 0.15 |
| `OTHER` | Other | 0.05 |

Enabled weights must sum to 1.00. All four are enabled.

## 40/40/15/5 priority model

These weights divide search capacity. They are not added to the 0–100 fit score, the embedding cosine, or the tier.

A high-fit job in Other is still a high-fit job. A medium-fit Product Management job is not boosted because its family weight is 0.40. That combination belongs to a later phase.

## Search buckets

Each family has enabled buckets. Each enabled bucket has at least one query. The ten queries that already ran are kept:

| Query | Bucket | Family |
|---|---|---|
| Product Manager Intern | `PM_CORE` | Product Management |
| MBA Product Manager Intern | `APM_MBA_PM` | Product Management |
| Product Operations Intern | `PRODUCT_OPERATIONS` | Product Management |
| Management Consultant Intern | `MANAGEMENT_CONSULTING` | Consulting |
| Strategy Intern | `CORPORATE_STRATEGY` | Strategy / Transformation |
| Go-to-Market Intern | `GTM_STRATEGY` | Strategy / Transformation |
| Product Marketing Intern | `PRODUCT_MARKETING` | Other |
| Program Manager Intern | `PROGRAM_MANAGEMENT` | Other |
| Project Manager Intern | `PROJECT_MANAGEMENT` | Other |
| Customer Success Intern | `OTHER_ADJACENT_MBA_ROLES` | Other |

Buckets that had no migrated query have one starter phrase so the plan can execute them. Examples: `Technical Product Manager Intern`, `Product Strategy Intern`, `Strategy Consulting Intern`. Title variants are an empty slot for later vocabulary. They are not searched.

`Strategy Intern` sits under corporate strategy. That is a placement choice, not a claim that every strategy internship is corporate strategy. Phase 2 can split the phrase.

## Search allocation

`run_ingestion(search_capacity=N)` asks for N query executions. `N is None` means every enabled query, once.

`allocate_units` is deterministic:

1. Usable capacity is the request, capped by how many queries actually exist.
2. Each enabled family gets a share proportional to its weight.
3. A family cannot receive more queries than it has.
4. Units left over because a family was capped are given to families that still have room, again by relative weight.
5. The same inputs always return the same counts.

With a request of 100 and enough queries in every family, the split is 40 / 40 / 15 / 5.

## Spillover behavior

Spillover is search capacity a family could not use, which was then given to other families. It is not unused fit, a weak embedding, or a low tier.

A request larger than the whole query catalog is unavailable capacity. The current catalog has 19 queries. A request of 100 still runs those 19 searches. The other 81 units are not spillover. The plan records requested 100, usable 19, allocated 19, spillover 0.

Spillover is the other case: the catalog can fill the request, but one family has fewer queries than its share. Request 100, Other has only 2 queries, and the other families have room. Other's unused 3 units move to Product Management, Consulting, and Strategy / Transformation. The result is 41 / 41 / 16 / 2, and the plan records spillover 3.

The default production plan requests one execution per enabled query, so every configured query runs once.

Inside a family, the same rule splits that family's units across its buckets in proportion to how many queries each bucket has. Queries are then taken in file order. There is no second pass that searches again because the first results looked weak.

## Source separation

Families do not name LinkedIn. The plan's `jobspy_sites` are the enabled discovery sources that also appear in `config/targets.yaml` `search.sites`, in that file's order. Today that is LinkedIn, Indeed, Google, and ZipRecruiter. Workday stays a separate enabled source and still uses the tenant list in `targets.yaml`.

One JobSpy call still covers the selected sites for one query. Location, distance, `results_wanted` (50), and `hours_old` (36) are unchanged.

Disabling a source in `discovery.yaml` drops it from the plan without editing a role family.

## Provenance

Each new or refreshed job can store:

- `source` (already on the job)
- `discovery_family`
- `discovery_bucket`
- `discovery_query`

JobSpy stamps the query that returned the row. Workday stamps the same fields when the tenant search used a planned query. The first query to see a `(source, external id)` pair keeps the provenance. `discovered_at` is still the run timestamp.

A production run logs `discovery_plan` with requested capacity, usable capacity, per-family ideal and assigned counts, genuine spillover, per-bucket counts, search count, and sources. The log has no secrets and no profile text.

## What Phase 1 does not do

- It does not change the fit rubric, embedding model, embedding threshold, tier cutoffs, or shortlist.
- It does not add family weight to the fit score.
- It does not change the internship filter, sponsorship classifier, or seniority filter.
- It does not change the candidate profile or location rules.
- It does not add job boards.
- It does not deduplicate across sources by company and title.
- It does not search again when results look thin.

## What Phase 2 will do

Phase 2 will expand and refine the search taxonomy and vocabulary: more phrases per bucket, title variants that should actually be searched, and a review of whether starter queries and the `Strategy Intern` placement are the right recall set. The discovery engine should not need to be rewritten to add those phrases.

# Phase 13 shortlist

The shortlist decides which staged jobs enter the human review queue. It does not score them again and it does not remove the ones it skips.

Priority 2.0 `priority_score` is the order. Shortlist does not calculate it again. `sort_by_priority` breaks ties by fit, then posted or discovered time, then job id. A staged job with no priority score is left staged and is not given a substitute score. A missing fit sorts after a fit of 0. Telegram reads this persisted result and does not choose its own list. `bot.prep.select_shortlist` is a legacy score-fill helper and is not the production shortlist.

## Configuration

`config/shortlist.yaml`, version `phase13-v2`:

- `max_size` is 20. This is the size of the pending-review queue, not a score cutoff.
- `max_per_company` is 2. Legal suffixes are ignored through the existing company-token helper, so "Acme, Inc." and "Acme LLC" share a cap. "Meta" and "MetLife" do not. A blank company name is not grouped with other blank names.
- `diversity_margin` is 5. A different target family can take a crowded seat only when its priority is within 5 points. A larger gap keeps the higher-priority job.
- `role_diversity.target_families` lists the families that may take that seat: product management, consulting, strategy and transformation, product marketing, marketing, and program or project operations. UNKNOWN and OTHER are not targets. The primary `role_family` is the seat. A secondary family does not count as its own family.

Jobs already in `pending_review` count toward `max_size`. A second run does not add more while the queue is full, and it does not rewrite jobs already waiting.

## Selection

1. Keep jobs whose status is `staged`.
2. Skip staged jobs whose `priority_score` is missing. Their status is not changed.
3. Walk the rest in priority order and take jobs until the open seats are full, skipping a company that already has `max_per_company` seats. Legal suffixes use the existing company-token helper.
4. If one role family then holds more than half the seats, look for a staged job whose primary family is a configured target and is not that crowded family. The replacement must be within `diversity_margin` of the lowest selected job in the crowded family, and the company cap still applies. If no such job exists, the list stays as priority left it.
5. Sort the chosen jobs again with `sort_by_priority` and number them from 1.

There is no family quota and no portfolio seat split. A list can still be mostly one family when the other jobs are farther than the margin, or when no other target family is available.

A selected job moves from `staged` to `pending_review`. Its fit, tier, eligibility, role, company intelligence, vectors, discovery fields, description fields, and priority are left as they were. The row stores `shortlist_version`, `shortlist_rank`, `shortlist_reason`, and `shortlist_config_hash` so a later run can see why it was chosen. Reasons are `selected_by_priority` or `selected_for_role_diversity`. Portfolio allocation is a later step and is not changed here.

A job that is not chosen stays `staged`. It is not deleted, filtered out, or marked ineligible. `pending_review`, `submitted`, `ignored`, `manual_review`, `filtered_out`, and `error` are not candidates and are not rewritten.

## Pipeline

`staged` means the job is scored and still waiting. It is not in the human review queue. `pending_review` means the shortlist chose it, or an earlier Workday pre-fill parked it there. The shortlist does not pull a job back out of `pending_review`.

The run order is ingest, score, shortlist, resume, suggestions, benchmark, prep, apply, then reviews.

- Shortlist reads `staged` and returns the ids it moved to `pending_review`.
- Resume preparation on that run attaches a resume to `pending_review` jobs. A direct `prepare_pending()` call still uses `staged`.
- Skill suggestions and Tier-1 benchmarking use those shortlist ids. They do not scan every staged job, and they do not scan the whole review queue from earlier runs.
- The Telegram file reads jobs that already have `shortlist_rank`, in that order. It does not score them again, fill the file to a count, or add a job that this shortlist did not select. An empty selection sends a notice and no job cards.
- Workday pre-fill still reads `staged`. A job in `pending_review` is not an application candidate. Shortlist does not start an application.
- Telegram review reads `pending_review`. Approve, discard, and submit are unchanged.

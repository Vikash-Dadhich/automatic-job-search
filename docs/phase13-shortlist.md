# Phase 13 shortlist

The shortlist decides which staged jobs enter the human review queue. It does not score them again and it does not remove the ones it skips.

Phase 12 `priority_score` is the order. `sort_by_priority` breaks ties by fit, then posted or discovered time, then job id. A missing priority sorts after every numeric priority, including 0. A missing fit sorts after a fit of 0.

## Configuration

`config/shortlist.yaml`, version `phase13-v1`:

- `max_size` is 20. This is the size of the pending-review queue, not a score cutoff.
- `max_per_company` is 2. Legal suffixes are ignored through the existing company-token helper, so "Acme, Inc." and "Acme LLC" share a cap. "Meta" and "MetLife" do not. A blank company name is not grouped with other blank names.
- `diversity_margin` is 5. It exists so a different family can take the last seat only when its priority is close. A larger gap keeps the higher-priority job.

Jobs already in `pending_review` count toward `max_size`. A second run does not add more while the queue is full, and it does not rewrite jobs already waiting.

## Selection

1. Keep jobs whose status is `staged`.
2. Walk them in Phase 12 order and take jobs until the open seats are full, skipping a company that already has `max_per_company` seats.
3. If one role family then holds more than half the seats, look for a staged job from another family whose Phase 7 weight is above UNKNOWN. Product Management, Consulting, and Strategy/Transformation qualify. Other families and UNKNOWN do not take a diversity seat. The replacement must be within `diversity_margin` of the lowest selected job in the crowded family, and it must still respect the company cap. If no such job exists, the list stays as priority left it.
4. Sort the chosen jobs again with `sort_by_priority` and number them from 1.

There is no family quota. A list can still be mostly one family when the other jobs are farther than the margin, or when no other targeted family is available.

A selected job moves from `staged` to `pending_review`. Its fit, tier, eligibility, role, company intelligence, vectors, discovery fields, description fields, and priority are left as they were. The row stores `shortlist_version`, `shortlist_rank`, `shortlist_reason`, and `shortlist_config_hash` so a later run can see why it was chosen. Reasons are `selected_by_priority` or `selected_for_portfolio_diversity`.

A job that is not chosen stays `staged`. It is not deleted, filtered out, or marked ineligible. `pending_review`, `submitted`, `ignored`, `manual_review`, `filtered_out`, and `error` are not candidates and are not rewritten.

## Pipeline

The run order is ingest, score, shortlist, resume, suggestions, benchmark, prep, apply, then reviews. Resume preparation in that run attaches a resume to `pending_review` jobs. Calling `prepare_pending` directly still uses `staged`, which is what the existing resume tests do.

Suggestions, benchmark, the prep-pack file, and Workday pre-fill still read `staged`. They do not see jobs the shortlist has already moved into review. Telegram review already reads `pending_review`, so it sends the jobs this phase selected. Approve, discard, and submit are unchanged.

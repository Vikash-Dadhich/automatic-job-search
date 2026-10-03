# Phase 14 application portfolio

Priority says which job deserves attention. The shortlist says which jobs enter human review. The portfolio says which staged application candidates may use the limited number of application attempts in this run.

It does not compute a new score. It does not change fit, tier, priority, eligibility, role family, or status.

## Capacity

`Settings.apply_limit` is the cap (default 10). That is the most jobs one run may allocate. It does not require 10 applications. `Settings.company_cooldown_days` is the window (default 30). Phase 14 does not keep a second copy of either number.

`config/application_portfolio.yaml`, version `phase14-v2`, sets whether the layer is on, how many jobs from one company this run may allocate (`max_applications_per_company`, default 2), and `balance_margin` (default 5). The margin is how far below the next priority-ordered job a different role family may sit and still take that seat because its target share is still open. A wider gap keeps the higher-priority job. The 40/40/15/5 shares are not quotas.

## Who can be allocated

Only jobs the existing apply runner would already consider: status `staged`, a resume on file, and a Workday application URL. `pending_review` is the human-review queue and is not an application candidate. `filtered_out`, `ignored`, `submitted`, `error`, and `manual_review` are not candidates. A staged job whose eligibility is `CLEARLY_INELIGIBLE` is not allocated. Unknown eligibility is not treated as ineligible.

## What counts as a recent application

The existing `get_recently_applied_companies` helper is the record. A company is in that set when a job is `submitted`, `pending_review`, or `manual_review`, and `decided_at` falls inside `company_cooldown_days`. `ignored` is not included. A row with no `decided_at` is not included, so a review card or a discovery row does not consume the company. Matching uses the existing company-token helper, so `Acme, Inc.` and `Acme LLC` are the same employer.

That cooldown blocks the company outright. It is stricter than the per-run cap of 2. The cap of 2 only limits how many not-yet-committed jobs at the same employer can be allocated together in this run. A blank company name is not grouped with other blank names.

## Role-family mix

Buckets use the Phase 7 weights: Product Management 40, Consulting 40, Strategy/Transformation 15, and every other family, including UNKNOWN, shares the OTHER weight of 5. Those four numbers are shares of 100, not a second weight table.

Seats are the largest whole number that fits each share. Any leftover seat goes to the bucket with the largest remainder. If two remainders tie, the bucket that currently has fewer seats gets it. For 10 seats that is 4, 4, 1, and 1.

The allocator walks jobs in stored priority order. It does not calculate priority again. A job with no `priority_score` is deferred and stays staged. The primary role family is the bucket. A secondary family does not take a second seat.

While a bucket is still under its share, its own highest-priority jobs are taken normally. Once a bucket has reached its share, a job from a bucket that is still open can take the next seat only when its priority is within `balance_margin` of the job that would otherwise be next, and only when the company cap still holds. A larger gap keeps the higher-priority job. Seats that a bucket cannot fill, or will not fill because the gap is too wide, go to the highest-priority jobs that remain. A bucket with extra jobs is not rejected. Those jobs stay staged and can be chosen on a later run. Nothing is multiplied by the weight.

## Decisions

`ALLOCATED` uses a seat this run. `DEFERRED` is eligible but the run is full. It is not a bad job and it is not filtered. `BLOCKED_COMPANY` is the cooldown or the per-run company cap. `BLOCKED_CAPACITY` is a capacity of zero. The row stores `portfolio_version`, `portfolio_decision`, `portfolio_reason`, and `portfolio_config_hash`. The next run recomputes from current jobs. The stored decision is the last result, not a permanent block.

## Pipeline

When apply is enabled, portfolio runs immediately before apply and passes the ids it actually saved as `ALLOCATED` into the existing runner. A job that was only planned, then skipped because it was no longer staged or eligible, is not in that list. The runner still refuses anything that is not `staged`. On that explicit id list it also requires the current row to still say `ALLOCATED` and to stay Workday-eligible. After pacing and tenant setup, and immediately before pre-fill, the runner reloads that row and applies the same checks again. A decision that changes before the applicator is called is skipped, not applied. An unrestricted `apply_pending()` call with no id list keeps the older staged lookup. When apply is disabled, portfolio does not run, so turning the code on does not start applications. Workday pacing is unchanged. This layer does not submit, does not learn from interviews or offers, and does not score companies.

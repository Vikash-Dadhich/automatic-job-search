---
source_file: "scorer/application_portfolio.py"
type: "code"
community: "test_application_portfolio.py"
location: "L174"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_application_portfoliopy
---

# allocate_portfolio()

## Connections
- [[Choose staged candidates. Does not write status, fit, or priority.]] - `rationale_for` [EXTRACTED]
- [[Job]] - `uses` [INFERRED]
- [[PortfolioDecision]] - `calls` [EXTRACTED]
- [[_bucket()_1]] - `calls` [EXTRACTED]
- [[_is_candidate()]] - `calls` [EXTRACTED]
- [[_on_cooldown()]] - `calls` [EXTRACTED]
- [[_seat_targets()]] - `calls` [EXTRACTED]
- [[application_portfolio.py]] - `contains` [EXTRACTED]
- [[apply_portfolio()]] - `calls` [EXTRACTED]
- [[bucket_weights()]] - `calls` [EXTRACTED]
- [[can_take()]] - `contains` [EXTRACTED]
- [[identity()]] - `contains` [EXTRACTED]
- [[sort_by_priority()]] - `calls` [EXTRACTED]
- [[take()]] - `contains` [EXTRACTED]
- [[test_allocation_does_not_rescore()]] - `calls` [EXTRACTED]
- [[test_application_portfolio.py]] - `imports` [EXTRACTED]
- [[test_blank_companies_do_not_share_a_cap()]] - `calls` [EXTRACTED]
- [[test_company_cap_is_per_run_and_suffix_aware()]] - `calls` [EXTRACTED]
- [[test_cooldown_blocks_the_company_and_leaves_scores()]] - `calls` [EXTRACTED]
- [[test_daily_capacity_defers_the_rest()]] - `calls` [EXTRACTED]
- [[test_ignored_job_does_not_consume_a_slot()]] - `calls` [EXTRACTED]
- [[test_ineligible_and_review_jobs_are_not_candidates()]] - `calls` [EXTRACTED]
- [[test_priority_order_and_zero_capacity()]] - `calls` [EXTRACTED]
- [[test_role_family_targets_are_soft()]] - `calls` [EXTRACTED]
- [[test_unknown_eligibility_can_still_be_allocated()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_application_portfoliopy
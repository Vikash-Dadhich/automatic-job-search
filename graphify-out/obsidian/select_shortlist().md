---
source_file: "scorer/shortlist.py"
type: "code"
community: "test_phase13_shortlist.py"
location: "L224"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_phase13_shortlistpy
---

# select_shortlist()

## Connections
- [[Any_24]] - `references` [EXTRACTED]
- [[Job]] - `uses` [INFERRED]
- [[Pick staged jobs that already have a priority score. Does not write or rescore.]] - `rationale_for` [EXTRACTED]
- [[ShortlistPick]] - `calls` [EXTRACTED]
- [[Status]] - `uses` [INFERRED]
- [[_company_key()]] - `calls` [EXTRACTED]
- [[_diversify()]] - `calls` [EXTRACTED]
- [[_identity()]] - `calls` [EXTRACTED]
- [[_targets()]] - `calls` [EXTRACTED]
- [[apply_shortlist()]] - `calls` [EXTRACTED]
- [[load_shortlist_config()]] - `calls` [EXTRACTED]
- [[shortlist.py]] - `contains` [EXTRACTED]
- [[sort_by_priority()]] - `calls` [EXTRACTED]
- [[test_diversity_respects_company_cap_and_ignores_secondary_family()]] - `calls` [EXTRACTED]
- [[test_family_diversity_is_a_soft_swap()]] - `calls` [EXTRACTED]
- [[test_low_priority_still_takes_an_open_seat()]] - `calls` [EXTRACTED]
- [[test_missing_dates_still_select()]] - `calls` [EXTRACTED]
- [[test_non_staged_jobs_are_ignored()]] - `calls` [EXTRACTED]
- [[test_phase13_shortlist.py]] - `imports` [EXTRACTED]
- [[test_priority_order_and_phase12_ties()]] - `calls` [EXTRACTED]
- [[test_selection_does_not_score()]] - `calls` [EXTRACTED]
- [[test_selection_ignores_discovery_and_vector()]] - `calls` [EXTRACTED]
- [[test_size_and_company_cap()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_phase13_shortlistpy
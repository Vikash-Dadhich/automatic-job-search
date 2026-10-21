---
source_file: "tests/test_priority_v2.py"
type: "code"
community: "calculate_priority"
location: "L17"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/calculate_priority
---

# _job()

## Connections
- [[Job]] - `calls` [EXTRACTED]
- [[Source]] - `uses` [INFERRED]
- [[Status]] - `uses` [INFERRED]
- [[score()]] - `calls` [EXTRACTED]
- [[test_confidence_and_structured_evidence()]] - `calls` [EXTRACTED]
- [[test_domains_are_capped_and_irrelevant_domains_add_nothing()]] - `calls` [EXTRACTED]
- [[test_eligibility_order_and_unknown()]] - `calls` [EXTRACTED]
- [[test_missing_jd_is_omitted_and_truncated_stays_lower()]] - `calls` [EXTRACTED]
- [[test_priority_does_not_call_a_model()]] - `calls` [EXTRACTED]
- [[test_priority_stays_bounded_and_fit_is_only_an_input()]] - `calls` [EXTRACTED]
- [[test_priority_v2.py]] - `contains` [EXTRACTED]
- [[test_program_evidence_is_capped_and_not_mba_by_default()]] - `calls` [EXTRACTED]
- [[test_role_alignment_and_bounded_secondary()]] - `calls` [EXTRACTED]
- [[test_role_evidence_changes_the_priority_hash()]] - `calls` [EXTRACTED]
- [[test_secondary_role_must_be_a_different_target_family()]] - `calls` [EXTRACTED]
- [[test_us_presence_does_not_change_eligibility()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/calculate_priority
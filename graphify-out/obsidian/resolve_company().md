---
source_file: "scorer/company_intelligence.py"
type: "code"
community: "test_company_intelligence.py"
location: "L553"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_company_intelligencepy
---

# resolve_company()

## Connections
- [[AsyncSession]] - `references` [EXTRACTED]
- [[CompanyIntelProvider]] - `references` [EXTRACTED]
- [[CompanyIntelligence]] - `uses` [INFERRED]
- [[Find or create factual intelligence. Provider errors stay on the company row.]] - `rationale_for` [EXTRACTED]
- [[_accumulate_sources()]] - `calls` [EXTRACTED]
- [[_apply_context()]] - `calls` [EXTRACTED]
- [[_apply_facts()]] - `calls` [EXTRACTED]
- [[_by_key()]] - `calls` [EXTRACTED]
- [[_clear_facts()]] - `calls` [EXTRACTED]
- [[_confidence_for()]] - `calls` [EXTRACTED]
- [[_new_row()]] - `calls` [EXTRACTED]
- [[_reliable_source_url()]] - `calls` [EXTRACTED]
- [[_source_type()]] - `calls` [EXTRACTED]
- [[_status_for()]] - `calls` [EXTRACTED]
- [[_store_failure()]] - `calls` [EXTRACTED]
- [[attach_company_intelligence()]] - `calls` [EXTRACTED]
- [[company_intelligence.py]] - `contains` [EXTRACTED]
- [[empty_company_context()]] - `calls` [EXTRACTED]
- [[extract_company_facts()]] - `calls` [EXTRACTED]
- [[merge_company_facts()]] - `calls` [EXTRACTED]
- [[normalize_company_name()]] - `calls` [EXTRACTED]
- [[refresh_company_intelligence()]] - `calls` [EXTRACTED]
- [[test_ambiguous_names_stay_separate()]] - `calls` [EXTRACTED]
- [[test_company_intelligence.py]] - `imports` [EXTRACTED]
- [[test_company_sources_accumulate_and_a_failed_refresh_keeps_them()]] - `calls` [EXTRACTED]
- [[test_complete_record_and_ignored_claims()]] - `calls` [EXTRACTED]
- [[test_cooldown_set_is_unchanged()]] - `calls` [EXTRACTED]
- [[test_persisted_source_type_matches_the_caller()]] - `calls` [EXTRACTED]
- [[test_source_grounded_partial_record()]] - `calls` [EXTRACTED]
- [[test_sparse_refresh_does_not_erase_known_facts()]] - `calls` [EXTRACTED]
- [[test_unknown_without_a_source_stays_null()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_company_intelligencepy
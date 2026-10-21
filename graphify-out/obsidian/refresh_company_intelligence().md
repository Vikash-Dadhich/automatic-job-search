---
source_file: "scorer/company_intelligence.py"
type: "code"
community: "test_company_intelligence_v2.py"
location: "L660"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_company_intelligence_v2py
---

# refresh_company_intelligence()

## Connections
- [[AsyncSession]] - `references` [EXTRACTED]
- [[CompanyIntelProvider]] - `references` [EXTRACTED]
- [[CompanyIntelligence]] - `uses` [INFERRED]
- [[Look up the company again. Does not recompute fit or role-family weight.]] - `rationale_for` [EXTRACTED]
- [[company_intelligence.py]] - `contains` [EXTRACTED]
- [[resolve_company()]] - `calls` [EXTRACTED]
- [[test_changed_page_replaces_that_source_and_keeps_another()]] - `calls` [EXTRACTED]
- [[test_company_intelligence.py]] - `imports` [EXTRACTED]
- [[test_company_intelligence_v2.py]] - `imports` [EXTRACTED]
- [[test_company_sources_accumulate_and_a_failed_refresh_keeps_them()]] - `calls` [EXTRACTED]
- [[test_profile_signals_persist_with_evidence()]] - `calls` [EXTRACTED]
- [[test_sparse_refresh_does_not_erase_known_facts()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_company_intelligence_v2py
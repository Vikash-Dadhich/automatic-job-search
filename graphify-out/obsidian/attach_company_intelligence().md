---
source_file: "scorer/company_intelligence.py"
type: "code"
community: "test_company_intelligence.py"
location: "L679"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_company_intelligencepy
---

# attach_company_intelligence()

## Connections
- [[AsyncSession]] - `references` [EXTRACTED]
- [[CompanyIntelProvider]] - `references` [EXTRACTED]
- [[CompanyIntelligence]] - `uses` [INFERRED]
- [[Job]] - `uses` [INFERRED]
- [[Point the job at a company record without changing score, weight, or status.]] - `rationale_for` [EXTRACTED]
- [[company_intelligence.py]] - `contains` [EXTRACTED]
- [[ingest.py]] - `imports` [EXTRACTED]
- [[resolve_company()]] - `calls` [EXTRACTED]
- [[run_ingestion()]] - `calls` [EXTRACTED]
- [[test_company_facts_do_not_change_job_decisions()]] - `calls` [EXTRACTED]
- [[test_company_facts_do_not_change_scoring_signals()]] - `calls` [EXTRACTED]
- [[test_company_intelligence.py]] - `imports` [EXTRACTED]
- [[test_company_intelligence_v2.py]] - `imports` [EXTRACTED]
- [[test_company_sources_accumulate_and_a_failed_refresh_keeps_them()]] - `calls` [EXTRACTED]
- [[test_explicit_refresh_calls_the_provider_again()]] - `calls` [EXTRACTED]
- [[test_provider_failures_do_not_change_the_job()]] - `calls` [EXTRACTED]
- [[test_same_company_is_reused_without_merging_jobs()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_company_intelligencepy
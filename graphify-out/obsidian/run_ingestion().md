---
source_file: "scraper/ingest.py"
type: "code"
community: "Source"
location: "L193"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Source
---

# run_ingestion()

## Connections
- [[HttpCompanyIntelProvider]] - `calls` [EXTRACTED]
- [[IngestSummary]] - `calls` [EXTRACTED]
- [[Profile]] - `uses` [INFERRED]
- [[RawPosting]] - `uses` [INFERRED]
- [[Run one full discovery cycle and persist results. ``search_capacity`` is how…]] - `rationale_for` [EXTRACTED]
- [[SearchObservation]] - `uses` [INFERRED]
- [[Status]] - `uses` [INFERRED]
- [[Targets]] - `uses` [INFERRED]
- [[_apply_role_classification()]] - `calls` [EXTRACTED]
- [[_attach_coverage()]] - `calls` [EXTRACTED]
- [[_dedupe()]] - `calls` [EXTRACTED]
- [[_load_role_client()]] - `calls` [EXTRACTED]
- [[_mark_source_failed()]] - `calls` [EXTRACTED]
- [[_stamp_role_family_weight()]] - `calls` [EXTRACTED]
- [[asyncio_11]] - `calls` [EXTRACTED]
- [[attach_company_intelligence()]] - `calls` [EXTRACTED]
- [[attach_eligibility()]] - `calls` [EXTRACTED]
- [[attach_structured_jd()]] - `calls` [EXTRACTED]
- [[build_discovery_plan()]] - `calls` [EXTRACTED]
- [[evaluate()]] - `calls` [EXTRACTED]
- [[fetch_all_workday()]] - `calls` [EXTRACTED]
- [[fetch_linkedin_indeed()]] - `calls` [EXTRACTED]
- [[ingest.py]] - `contains` [EXTRACTED]
- [[init_db()]] - `calls` [EXTRACTED]
- [[load_profile()]] - `calls` [EXTRACTED]
- [[load_targets()]] - `calls` [EXTRACTED]
- [[log_discovery_plan()]] - `calls` [EXTRACTED]
- [[pipeline.py]] - `indirect_call` [INFERRED]
- [[scraper__init__.py]] - `imports` [EXTRACTED]
- [[session_scope()]] - `calls` [EXTRACTED]
- [[test_company_enrichment_failure_does_not_stop_ingestion()]] - `calls` [EXTRACTED]
- [[test_company_intelligence_v2.py]] - `imports` [EXTRACTED]
- [[test_db_ingest.py]] - `imports` [EXTRACTED]
- [[test_eligibility.py]] - `imports` [EXTRACTED]
- [[test_provider_failure_does_not_break_ingestion()]] - `calls` [EXTRACTED]
- [[test_run_ingestion_noop()]] - `calls` [EXTRACTED]
- [[test_structured_jd.py]] - `imports` [EXTRACTED]
- [[test_structured_jd_failure_does_not_stop_ingestion()]] - `calls` [EXTRACTED]
- [[to_job()]] - `calls` [EXTRACTED]
- [[trustworthy_company_source()]] - `calls` [EXTRACTED]
- [[upsert_job()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Source
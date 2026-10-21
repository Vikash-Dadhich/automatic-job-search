---
source_file: "orchestrator/monitoring.py"
type: "code"
community: "test_monitoring.py"
location: "L1"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_monitoringpy
---

# monitoring.py

## Connections
- [[Durable pipeline history. A failure here must not stop the pipeline.]] - `rationale_for` [EXTRACTED]
- [[Job]] - `imports` [EXTRACTED]
- [[PipelineRun]] - `imports` [EXTRACTED]
- [[PipelineStageRun]] - `imports` [EXTRACTED]
- [[Status]] - `imports` [EXTRACTED]
- [[_as_utc()_1]] - `imports` [EXTRACTED]
- [[_moment()]] - `contains` [EXTRACTED]
- [[_require_int()_5]] - `contains` [EXTRACTED]
- [[_utcnow()]] - `imports` [EXTRACTED]
- [[_validate()_6]] - `contains` [EXTRACTED]
- [[close_pipeline_run()]] - `contains` [EXTRACTED]
- [[close_stage_run()]] - `contains` [EXTRACTED]
- [[count_jobs_by_status()]] - `contains` [EXTRACTED]
- [[count_stale_jobs()]] - `contains` [EXTRACTED]
- [[database_reachable()]] - `contains` [EXTRACTED]
- [[datetime_10]] - `imports_from` [EXTRACTED]
- [[db.py]] - `imports_from` [EXTRACTED]
- [[diagnostics.py]] - `imports_from` [EXTRACTED]
- [[effective_config_hash()]] - `imports` [EXTRACTED]
- [[functools]] - `imports_from` [EXTRACTED]
- [[get_engine()]] - `imports` [EXTRACTED]
- [[get_settings()]] - `imports` [EXTRACTED]
- [[hashlib]] - `imports` [EXTRACTED]
- [[health.py]] - `imports_from` [EXTRACTED]
- [[init_db()]] - `imports` [EXTRACTED]
- [[interrupt_stale_runs()]] - `contains` [EXTRACTED]
- [[json]] - `imports` [EXTRACTED]
- [[list_pipeline_runs()]] - `contains` [EXTRACTED]
- [[list_stage_runs()]] - `contains` [EXTRACTED]
- [[load_monitoring_config()]] - `contains` [EXTRACTED]
- [[monitoring_config_hash()]] - `contains` [EXTRACTED]
- [[open_pipeline_run()]] - `contains` [EXTRACTED]
- [[open_stage_run()]] - `contains` [EXTRACTED]
- [[operational_config_hash()]] - `contains` [EXTRACTED]
- [[parse_hhmm()]] - `imports` [EXTRACTED]
- [[pathlib]] - `imports_from` [EXTRACTED]
- [[record_skipped_stage()]] - `contains` [EXTRACTED]
- [[scheduler.py]] - `imports_from` [EXTRACTED]
- [[session_scope()]] - `imports` [EXTRACTED]
- [[settings.py]] - `imports_from` [EXTRACTED]
- [[sqlmodel_2]] - `imports_from` [EXTRACTED]
- [[stage_counters()]] - `contains` [EXTRACTED]
- [[test_monitoring.py]] - `imports_from` [EXTRACTED]
- [[typing]] - `imports_from` [EXTRACTED]
- [[uuid]] - `imports` [EXTRACTED]
- [[validate_operational_config()]] - `contains` [EXTRACTED]
- [[yaml]] - `imports` [EXTRACTED]
- [[zoneinfo]] - `imports_from` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_monitoringpy
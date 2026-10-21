---
type: community
cohesion: 0.11
members: 34
---

# pipeline.py

**Cohesion:** 0.11 - loosely connected
**Members:** 34 nodes

## Members
- [[dot-ok()]] - code - orchestrator/pipeline.py
- [[Aggregated results from one full pipeline run.]] - rationale - orchestrator/pipeline.py
- [[Allocate apply capacity among staged candidates. Does not change status.]] - rationale - orchestrator/pipeline.py
- [[Any_16]] - code
- [[Benchmark Tier-1 jobs from this run's shortlist. Not the leftover staged pool.]] - rationale - orchestrator/pipeline.py
- [[Full pipeline ingest, score, shortlist, resume, suggest, prep, apply, reviews.]] - rationale - orchestrator/pipeline.py
- [[Job ids the shortlist just moved into review. Empty when that stage did not run.]] - rationale - orchestrator/pipeline.py
- [[Move the current staged selection into pending_review.]] - rationale - orchestrator/pipeline.py
- [[PipelineSummary]] - code - orchestrator/pipeline.py
- [[Prepare resumes for the review queue, not for every staged job.]] - rationale - orchestrator/pipeline.py
- [[Run all pipeline stages sequentially with per-stage isolation. A failure in one…]] - rationale - orchestrator/pipeline.py
- [[Staged ids the portfolio layer just allocated. Empty when that stage did not…]] - rationale - orchestrator/pipeline.py
- [[_allocated_ids()]] - code - orchestrator/pipeline.py
- [[_apply_allocated()]] - code - orchestrator/pipeline.py
- [[_benchmark_stage()]] - code - orchestrator/pipeline.py
- [[_benchmark_tier_one_stage()]] - code - orchestrator/pipeline.py
- [[_note_skipped()]] - code - orchestrator/pipeline.py
- [[_portfolio_stage()]] - code - orchestrator/pipeline.py
- [[_prep_stage()]] - code - orchestrator/pipeline.py
- [[_prepare_shortlisted_resumes()]] - code - orchestrator/pipeline.py
- [[_run_opened_pipeline()]] - code - orchestrator/pipeline.py
- [[_run_stage()]] - code - orchestrator/pipeline.py
- [[_safe_close_run()]] - code - orchestrator/pipeline.py
- [[_safe_close_stage()]] - code - orchestrator/pipeline.py
- [[_safe_open_run()]] - code - orchestrator/pipeline.py
- [[_safe_open_stage()]] - code - orchestrator/pipeline.py
- [[_selected_ids()]] - code - orchestrator/pipeline.py
- [[_shortlist_stage()]] - code - orchestrator/pipeline.py
- [[_suggest_stage()]] - code - orchestrator/pipeline.py
- [[contextvars]] - concept
- [[os]] - concept
- [[pipeline.py]] - code - orchestrator/pipeline.py
- [[run_pipeline()]] - code - orchestrator/pipeline.py
- [[time]] - concept

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/pipelinepy
SORT file.name ASC
```

## Connections to other communities
- 16 edges to [[_COMMUNITY_test_monitoring.py]]
- 7 edges to [[_COMMUNITY_session_scope]]
- 7 edges to [[_COMMUNITY_get_settings]]
- 6 edges to [[_COMMUNITY_suggest.py]]
- 6 edges to [[_COMMUNITY_test_application_portfolio.py]]
- 6 edges to [[_COMMUNITY_test_pipeline_order_and_aggregation]]
- 5 edges to [[_COMMUNITY_scheduler.py]]
- 5 edges to [[_COMMUNITY_json]]
- 5 edges to [[_COMMUNITY_test_phase13_shortlist.py]]
- 4 edges to [[_COMMUNITY_MonkeyPatch]]
- 3 edges to [[_COMMUNITY_test_resume.py]]
- 3 edges to [[_COMMUNITY_main.py]]
- 3 edges to [[_COMMUNITY_ingest.py]]
- 2 edges to [[_COMMUNITY_Tier]]
- 2 edges to [[_COMMUNITY_handlers.py]]
- 2 edges to [[_COMMUNITY_alerts.py]]
- 2 edges to [[_COMMUNITY_db.py]]
- 2 edges to [[_COMMUNITY_benchmarkengine.py]]
- 2 edges to [[_COMMUNITY_Phase 18 — Production reliability and monitoring]]
- 2 edges to [[_COMMUNITY_builder.py]]
- 2 edges to [[_COMMUNITY_review.py]]
- 2 edges to [[_COMMUNITY_typing]]
- 1 edge to [[_COMMUNITY_conftest.py]]
- 1 edge to [[_COMMUNITY_test_vector_recovery.py]]
- 1 edge to [[_COMMUNITY_send_prep_pack]]
- 1 edge to [[_COMMUNITY_Source]]
- 1 edge to [[_COMMUNITY_runner.py]]
- 1 edge to [[_COMMUNITY_Job]]
- 1 edge to [[_COMMUNITY_diff.py]]
- 1 edge to [[_COMMUNITY_scorerengine.py]]

## Top bridge nodes
- [[pipeline.py]] - degree 71, connects to 26 communities
- [[run_pipeline()]] - degree 29, connects to 10 communities
- [[_benchmark_tier_one_stage()]] - degree 9, connects to 5 communities
- [[time]] - degree 10, connects to 3 communities
- [[_prepare_shortlisted_resumes()]] - degree 6, connects to 2 communities
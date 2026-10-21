---
type: community
cohesion: 0.08
members: 46
---

# db.py

**Cohesion:** 0.08 - loosely connected
**Members:** 46 nodes

## Members
- [[Add Phase 2 columns to an existing jobs table. No-op when already present.]] - rationale - core/db.py
- [[Add the phase8-v2 context column. No-op when the table or column is already…]] - rationale - core/db.py
- [[Any_26]] - code
- [[Async SQLModel persistence for jobs, scoring, and workflow state. Supports…]] - rationale - core/db.py
- [[Column names on jobs, or empty when the table does not exist yet.]] - rationale - core/db.py
- [[Create storage directories and ensure all tables exist.]] - rationale - core/db.py
- [[Data model (coredb.py)]] - document - AGENTS.md
- [[Dispose the global engine (used by tests to switch DATABASE_URL).]] - rationale - core/db.py
- [[Do not replace a usable JD with an empty or too-short refetch.]] - rationale - core/db.py
- [[Idempotent ALTER for Phase 2 columns on an existing jobs table.]] - rationale - tests/test_job_columns.py
- [[Missing or suspiciously short text. A real rewrite is still usable.]] - rationale - core/db.py
- [[Path_25]] - code
- [[Staged non-Workday (manual-apply) jobs not yet in a prep pack (score desc).]] - rationale - core/db.py
- [[Status lifecycle]] - document - AGENTS.md
- [[UTC-aware DateTime column (TIMESTAMPTZ on Postgres; works on SQLite too).]] - rationale - core/db.py
- [[Unwrap a single-column select row into a company string.]] - rationale - core/db.py
- [[_company_name()_1]] - code - core/db.py
- [[_dialect_name()]] - code - core/db.py
- [[_ensure_company_columns()]] - code - core/db.py
- [[_ensure_job_columns()]] - code - core/db.py
- [[_incoming_description_unusable()]] - code - core/db.py
- [[_is_postgres_url()]] - code - core/db.py
- [[_is_sqlite_url()]] - code - core/db.py
- [[_job_column_names()]] - code - core/db.py
- [[_keep_stored_description()]] - code - core/db.py
- [[_stored_description_usable()]] - code - core/db.py
- [[_table_column_names()]] - code - core/db.py
- [[_tz_datetime()]] - code - core/db.py
- [[async_sessionmaker]] - code
- [[datetime_6]] - code
- [[db.py]] - code - core/db.py
- [[get_engine()]] - code - core/db.py
- [[get_session_factory()]] - code - core/db.py
- [[get_unsent_alerts()]] - code - core/db.py
- [[get_unsent_pending_reviews()]] - code - core/db.py
- [[get_unsent_prep_pack_jobs()]] - code - core/db.py
- [[init_db()]] - code - core/db.py
- [[job_to_dict()]] - code - core/db.py
- [[manual_review jobs that have not yet been alerted on Telegram. Scoring failures…]] - rationale - core/db.py
- [[pending_review jobs that have not yet been sent to Telegram.]] - rationale - core/db.py
- [[reset_engine()]] - code - core/db.py
- [[sqlalchemy]] - concept
- [[sqlite3]] - concept
- [[test_context_column_is_added_to_an_existing_table()]] - code - tests/test_company_intelligence_v2.py
- [[test_ensure_job_columns_on_legacy_table()]] - code - tests/test_job_columns.py
- [[test_job_columns.py]] - code - tests/test_job_columns.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/dbpy
SORT file.name ASC
```

## Connections to other communities
- 25 edges to [[_COMMUNITY_AsyncSession]]
- 19 edges to [[_COMMUNITY_test_monitoring.py]]
- 16 edges to [[_COMMUNITY_suggest.py]]
- 12 edges to [[_COMMUNITY_handlers.py]]
- 12 edges to [[_COMMUNITY_Job]]
- 10 edges to [[_COMMUNITY_discovery_recall.py]]
- 9 edges to [[_COMMUNITY_test_feedback.py]]
- 9 edges to [[_COMMUNITY_session_scope]]
- 9 edges to [[_COMMUNITY_get_settings]]
- 9 edges to [[_COMMUNITY_migrate_to_neon.py]]
- 8 edges to [[_COMMUNITY_test_pacing.py]]
- 8 edges to [[_COMMUNITY_tracker.py]]
- 8 edges to [[_COMMUNITY_upsert_job]]
- 8 edges to [[_COMMUNITY_test_phase13_shortlist.py]]
- 7 edges to [[_COMMUNITY_conftest.py]]
- 7 edges to [[_COMMUNITY_test_company_intelligence_v2.py]]
- 6 edges to [[_COMMUNITY_diff.py]]
- 6 edges to [[_COMMUNITY_Source]]
- 6 edges to [[_COMMUNITY_alerts.py]]
- 6 edges to [[_COMMUNITY_review.py]]
- 6 edges to [[_COMMUNITY_baseline.py]]
- 5 edges to [[_COMMUNITY_benchmarkengine.py]]
- 5 edges to [[_COMMUNITY_pathlib]]
- 4 edges to [[_COMMUNITY_test_doctor.py]]
- 4 edges to [[_COMMUNITY_test_application_portfolio.py]]
- 4 edges to [[_COMMUNITY_test_application_tracker.py]]
- 4 edges to [[_COMMUNITY_test_scorer.py]]
- 3 edges to [[_COMMUNITY_test_structured_jd.py]]
- 3 edges to [[_COMMUNITY_test_career_intelligence.py]]
- 3 edges to [[_COMMUNITY_Tier]]
- 3 edges to [[_COMMUNITY_asyncio]]
- 3 edges to [[_COMMUNITY_textclean.py]]
- 3 edges to [[_COMMUNITY_runner.py]]
- 3 edges to [[_COMMUNITY_scorerengine.py]]
- 3 edges to [[_COMMUNITY_test_role_classify.py]]
- 3 edges to [[_COMMUNITY_skills.py]]
- 3 edges to [[_COMMUNITY_typing]]
- 3 edges to [[_COMMUNITY_test_vector_recovery.py]]
- 2 edges to [[_COMMUNITY_company_intelligence.py]]
- 2 edges to [[_COMMUNITY_calculate_priority]]
- 2 edges to [[_COMMUNITY_pytest]]
- 2 edges to [[_COMMUNITY_pipeline.py]]
- 2 edges to [[_COMMUNITY_handle_callback]]
- 2 edges to [[_COMMUNITY_send_prep_pack]]
- 2 edges to [[_COMMUNITY_calibration.py]]
- 2 edges to [[_COMMUNITY_feedback.py]]
- 2 edges to [[_COMMUNITY_ingest.py]]
- 2 edges to [[_COMMUNITY_filters.py]]
- 2 edges to [[_COMMUNITY_test_resume.py]]
- 2 edges to [[_COMMUNITY_re]]
- 2 edges to [[_COMMUNITY_workday.py]]
- 2 edges to [[_COMMUNITY_WorkdaySubmitter]]
- 2 edges to [[_COMMUNITY_test_fit.py]]
- 2 edges to [[_COMMUNITY_prerank.py]]
- 2 edges to [[_COMMUNITY_profile.py]]
- 1 edge to [[_COMMUNITY_MonkeyPatch]]
- 1 edge to [[_COMMUNITY_LLMClient]]
- 1 edge to [[_COMMUNITY_main.py]]
- 1 edge to [[_COMMUNITY_Structured JD intelligence]]
- 1 edge to [[_COMMUNITY_structured_jd.py]]
- 1 edge to [[_COMMUNITY_Profile]]
- 1 edge to [[_COMMUNITY_test_calibration.py]]
- 1 edge to [[_COMMUNITY_workday_rest.py]]
- 1 edge to [[_COMMUNITY_eligibility.py]]
- 1 edge to [[_COMMUNITY_classify_role]]
- 1 edge to [[_COMMUNITY_test_company_intelligence.py]]
- 1 edge to [[_COMMUNITY_test_pipeline_order_and_aggregation]]
- 1 edge to [[_COMMUNITY_test_eligibility.py]]
- 1 edge to [[_COMMUNITY_test_phase0_baseline.py]]
- 1 edge to [[_COMMUNITY_test_application_deadline.py]]
- 1 edge to [[_COMMUNITY_scheduler.py]]
- 1 edge to [[_COMMUNITY_builder.py]]
- 1 edge to [[_COMMUNITY_priority.py]]
- 1 edge to [[_COMMUNITY_scorer__init__.py]]
- 1 edge to [[_COMMUNITY_linkedin_jobspy.py]]
- 1 edge to [[_COMMUNITY_test_apply_url.py]]
- 1 edge to [[_COMMUNITY_test_cover_letter.py]]
- 1 edge to [[_COMMUNITY_test_discovery.py]]
- 1 edge to [[_COMMUNITY_test_priority.py]]
- 1 edge to [[_COMMUNITY_test_recruiting_universe.py]]

## Top bridge nodes
- [[db.py]] - degree 217, connects to 75 communities
- [[init_db()]] - degree 86, connects to 36 communities
- [[Data model (coredb.py)]] - degree 10, connects to 9 communities
- [[Status lifecycle]] - degree 12, connects to 4 communities
- [[get_engine()]] - degree 12, connects to 4 communities
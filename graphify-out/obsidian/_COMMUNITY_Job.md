---
type: community
cohesion: 0.12
members: 36
---

# Job

**Cohesion:** 0.12 - loosely connected
**Members:** 36 nodes

## Members
- [[dot-submit()_2]] - code - tests/test_handlers.py
- [[Cards in the order given. Duplicate ids are shown once.]] - rationale - bot/prep.py
- [[Core job record threaded through discovery → scoring → application.]] - rationale - core/db.py
- [[Generate and deliver LinkedInIndeed application prep packs via Telegram.]] - rationale - bot/prep.py
- [[Job]] - code - core/db.py
- [[Legacy score fill. Production Telegram does not call this. The canonical…]] - rationale - bot/prep.py
- [[MonkeyPatch_27]] - code
- [[Offline tests for the score shortlist and uncapped scoring.]] - rationale - tests/test_shortlist.py
- [[One factual card. Missing fields are omitted. Nothing is inferred.]] - rationale - bot/prep.py
- [[One text file for the run. Empty input sends nothing.]] - rationale - bot/prep.py
- [[Path_47]] - code
- [[Persisted shortlist rows, in shortlist order. Does not select jobs.]] - rationale - bot/prep.py
- [[PrepSummary]] - code - bot/prep.py
- [[_dedupe()_1]] - code - bot/prep.py
- [[_fit_lines()]] - code - bot/prep.py
- [[_job()_13]] - code - tests/test_shortlist.py
- [[_load_canonical_shortlist()]] - code - bot/prep.py
- [[_mark_sent()]] - code - bot/prep.py
- [[_notify_empty()]] - code - bot/prep.py
- [[_score()_1]] - code - bot/prep.py
- [[_seed()_2]] - code - tests/test_shortlist.py
- [[_send_shortlist_document()]] - code - bot/prep.py
- [[_visa_state()]] - code - bot/prep.py
- [[datetime_13]] - code
- [[prep.py]] - code - bot/prep.py
- [[render_job_card()]] - code - bot/prep.py
- [[render_shortlist()]] - code - bot/prep.py
- [[select_shortlist()_1]] - code - bot/prep.py
- [[shortlist_caption()]] - code - bot/prep.py
- [[test_no_score_budget_scores_every_eligible_job()]] - code - tests/test_shortlist.py
- [[test_shortlist.py]] - code - tests/test_shortlist.py
- [[test_shortlist_document_marks_sent()]] - code - tests/test_shortlist.py
- [[test_shortlist_fills_to_20_from_60()]] - code - tests/test_shortlist.py
- [[test_shortlist_leaves_slots_empty_under_60()]] - code - tests/test_shortlist.py
- [[test_shortlist_sends_every_score_above_75()]] - code - tests/test_shortlist.py
- [[test_shortlist_skips_jobs_already_sent()]] - code - tests/test_shortlist.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Job
SORT file.name ASC
```

## Connections to other communities
- 28 edges to [[_COMMUNITY_session_scope]]
- 17 edges to [[_COMMUNITY_test_vector_recovery.py]]
- 16 edges to [[_COMMUNITY_runner.py]]
- 16 edges to [[_COMMUNITY_send_prep_pack]]
- 16 edges to [[_COMMUNITY_test_scorer.py]]
- 15 edges to [[_COMMUNITY_priority.py]]
- 14 edges to [[_COMMUNITY_get_settings]]
- 14 edges to [[_COMMUNITY_upsert_job]]
- 14 edges to [[_COMMUNITY_scorerengine.py]]
- 13 edges to [[_COMMUNITY_test_phase13_shortlist.py]]
- 13 edges to [[_COMMUNITY_test_application_portfolio.py]]
- 12 edges to [[_COMMUNITY_test_fit.py]]
- 12 edges to [[_COMMUNITY_db.py]]
- 11 edges to [[_COMMUNITY_pathlib]]
- 11 edges to [[_COMMUNITY_re]]
- 10 edges to [[_COMMUNITY_handlers.py]]
- 9 edges to [[_COMMUNITY_test_career_intelligence.py]]
- 9 edges to [[_COMMUNITY_test_resume.py]]
- 9 edges to [[_COMMUNITY_review.py]]
- 7 edges to [[_COMMUNITY_baseline.py]]
- 7 edges to [[_COMMUNITY_alerts.py]]
- 7 edges to [[_COMMUNITY_test_monitoring.py]]
- 7 edges to [[_COMMUNITY_eligibility.py]]
- 6 edges to [[_COMMUNITY_Source]]
- 6 edges to [[_COMMUNITY_filters.py]]
- 6 edges to [[_COMMUNITY_skills.py]]
- 6 edges to [[_COMMUNITY_LLMClient]]
- 6 edges to [[_COMMUNITY_WorkdaySubmitter]]
- 6 edges to [[_COMMUNITY_suggest.py]]
- 6 edges to [[_COMMUNITY_test_eligibility.py]]
- 5 edges to [[_COMMUNITY_TelegramClient]]
- 5 edges to [[_COMMUNITY_test_application_tracker.py]]
- 5 edges to [[_COMMUNITY_test_feedback.py]]
- 5 edges to [[_COMMUNITY_handle_callback]]
- 5 edges to [[_COMMUNITY_profile.py]]
- 5 edges to [[_COMMUNITY_prerank.py]]
- 5 edges to [[_COMMUNITY_test_priority.py]]
- 5 edges to [[_COMMUNITY_workday.py]]
- 5 edges to [[_COMMUNITY_builder.py]]
- 5 edges to [[_COMMUNITY_Tier]]
- 4 edges to [[_COMMUNITY_bot__init__.py]]
- 4 edges to [[_COMMUNITY_test_company_intelligence.py]]
- 4 edges to [[_COMMUNITY_test_doctor.py]]
- 4 edges to [[_COMMUNITY_calculate_priority]]
- 4 edges to [[_COMMUNITY_tracker.py]]
- 3 edges to [[_COMMUNITY_test_pacing.py]]
- 3 edges to [[_COMMUNITY_benchmarkengine.py]]
- 3 edges to [[_COMMUNITY_test_structured_jd.py]]
- 3 edges to [[_COMMUNITY_diff.py]]
- 3 edges to [[_COMMUNITY_pytest]]
- 2 edges to [[_COMMUNITY_test_application_deadline.py]]
- 2 edges to [[_COMMUNITY_test_cover_letter.py]]
- 2 edges to [[_COMMUNITY_AsyncSession]]
- 2 edges to [[_COMMUNITY_ingest.py]]
- 2 edges to [[_COMMUNITY_discovery_recall.py]]
- 2 edges to [[_COMMUNITY_test_role_classify.py]]
- 2 edges to [[_COMMUNITY_sort_by_priority]]
- 2 edges to [[_COMMUNITY_typing]]
- 1 edge to [[_COMMUNITY_Profile]]
- 1 edge to [[_COMMUNITY_main.py]]
- 1 edge to [[_COMMUNITY_company_intelligence.py]]
- 1 edge to [[_COMMUNITY_feedback.py]]
- 1 edge to [[_COMMUNITY_structured_jd.py]]
- 1 edge to [[_COMMUNITY_migrate_to_neon.py]]
- 1 edge to [[_COMMUNITY_test_calibration.py]]
- 1 edge to [[_COMMUNITY_6. What is sent to you]]
- 1 edge to [[_COMMUNITY_pipeline.py]]

## Top bridge nodes
- [[Job]] - degree 374, connects to 62 communities
- [[prep.py]] - degree 39, connects to 18 communities
- [[test_shortlist.py]] - degree 34, connects to 15 communities
- [[test_no_score_budget_scores_every_eligible_job()]] - degree 11, connects to 5 communities
- [[test_shortlist_document_marks_sent()]] - degree 9, connects to 4 communities
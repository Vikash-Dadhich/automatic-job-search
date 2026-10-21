---
type: community
cohesion: 0.11
members: 27
---

# upsert_job

**Cohesion:** 0.11 - loosely connected
**Members:** 27 nodes

## Members
- [[Core persistence and shared utilities.]] - rationale - core/__init__.py
- [[Insert a job or update mutable fields when the posting is already stored. The…]] - rationale - core/db.py
- [[Path_18]] - code
- [[Path_19]] - code
- [[Path_20]] - code
- [[Set the portfolio weight from the classified family. Fit and status stay put.]] - rationale - core/db.py
- [[__init__()_3]] - code - tests/test_cover_letter.py
- [[__init__()_4]] - code - tests/test_cover_letter.py
- [[_stamp_role_family_weight()]] - code - core/db.py
- [[complete()_2]] - code - tests/test_cover_letter.py
- [[complete()_3]] - code - tests/test_cover_letter.py
- [[complete()_4]] - code - tests/test_cover_letter.py
- [[complete()_5]] - code - tests/test_scorer.py
- [[complete()_6]] - code - tests/test_scorer.py
- [[core__init__.py]] - code - core/__init__.py
- [[get_job_by_source_id()]] - code - core/db.py
- [[test_classification_persists_and_does_not_filter()]] - code - tests/test_role_classify.py
- [[test_cover_letter_failure_still_stages()]] - code - tests/test_cover_letter.py
- [[test_score_pending_persists_tier_one_letter_only()]] - code - tests/test_cover_letter.py
- [[test_score_pending_skips_cooldown_company()]] - code - tests/test_scorer.py
- [[test_score_pending_stop_after_staged()]] - code - tests/test_scorer.py
- [[test_score_pending_tiers_and_outreach()]] - code - tests/test_scorer.py
- [[test_score_pending_token_usage()]] - code - tests/test_scorer.py
- [[test_tier_one_drafts_stay_off_unless_enabled()]] - code - tests/test_cover_letter.py
- [[test_upsert_keeps_good_jd_and_clears_stale_embedding()]] - code - tests/test_jd_ingest.py
- [[upsert_job()]] - code - core/db.py
- [[usage()]] - code - tests/test_scorer.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/upsert_job
SORT file.name ASC
```

## Connections to other communities
- 32 edges to [[_COMMUNITY_Source]]
- 27 edges to [[_COMMUNITY_session_scope]]
- 14 edges to [[_COMMUNITY_Job]]
- 11 edges to [[_COMMUNITY_test_vector_recovery.py]]
- 10 edges to [[_COMMUNITY_test_role_classify.py]]
- 8 edges to [[_COMMUNITY_db.py]]
- 8 edges to [[_COMMUNITY_test_application_portfolio.py]]
- 7 edges to [[_COMMUNITY_Profile]]
- 7 edges to [[_COMMUNITY_test_application_tracker.py]]
- 6 edges to [[_COMMUNITY_classify_role]]
- 6 edges to [[_COMMUNITY_test_scorer.py]]
- 5 edges to [[_COMMUNITY_Tier]]
- 5 edges to [[_COMMUNITY_test_company_intelligence.py]]
- 5 edges to [[_COMMUNITY_test_cover_letter.py]]
- 4 edges to [[_COMMUNITY_pytest]]
- 4 edges to [[_COMMUNITY_test_resume.py]]
- 4 edges to [[_COMMUNITY_test_eligibility.py]]
- 4 edges to [[_COMMUNITY_test_recruiting_universe.py]]
- 4 edges to [[_COMMUNITY_get_settings]]
- 4 edges to [[_COMMUNITY_pathlib]]
- 3 edges to [[_COMMUNITY_handlers.py]]
- 3 edges to [[_COMMUNITY_alerts.py]]
- 3 edges to [[_COMMUNITY_test_structured_jd.py]]
- 3 edges to [[_COMMUNITY_suggest.py]]
- 3 edges to [[_COMMUNITY_ingest.py]]
- 3 edges to [[_COMMUNITY_textclean.py]]
- 3 edges to [[_COMMUNITY_AsyncSession]]
- 3 edges to [[_COMMUNITY_baseline.py]]
- 3 edges to [[_COMMUNITY_test_feedback.py]]
- 3 edges to [[_COMMUNITY_handle_callback]]
- 3 edges to [[_COMMUNITY_test_phase13_shortlist.py]]
- 3 edges to [[_COMMUNITY_test_priority.py]]
- 2 edges to [[_COMMUNITY_TokenUsage]]
- 2 edges to [[_COMMUNITY_discovery_recall.py]]
- 2 edges to [[_COMMUNITY_test_pacing.py]]
- 2 edges to [[_COMMUNITY_test_discovery.py]]
- 2 edges to [[_COMMUNITY_test_application_deadline.py]]
- 2 edges to [[_COMMUNITY_profile.py]]
- 2 edges to [[_COMMUNITY_test_career_intelligence.py]]
- 2 edges to [[_COMMUNITY_test_fit.py]]
- 2 edges to [[_COMMUNITY_review.py]]
- 2 edges to [[_COMMUNITY_send_prep_pack]]
- 1 edge to [[_COMMUNITY_test_calibration.py]]
- 1 edge to [[_COMMUNITY_test_company_intelligence_v2.py]]
- 1 edge to [[_COMMUNITY_diff.py]]

## Top bridge nodes
- [[upsert_job()]] - degree 139, connects to 43 communities
- [[get_job_by_source_id()]] - degree 33, connects to 14 communities
- [[test_score_pending_persists_tier_one_letter_only()]] - degree 13, connects to 7 communities
- [[test_score_pending_token_usage()]] - degree 13, connects to 7 communities
- [[test_score_pending_tiers_and_outreach()]] - degree 12, connects to 7 communities
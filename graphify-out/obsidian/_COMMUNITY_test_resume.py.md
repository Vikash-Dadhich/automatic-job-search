---
type: community
cohesion: 0.12
members: 32
---

# test_resume.py

**Cohesion:** 0.12 - loosely connected
**Members:** 32 nodes

## Members
- [[Any_12]] - code
- [[Assemble JSON payload for the Typst template.]] - rationale - resume/selector.py
- [[Deterministic JD-aware bullet and skill selection for resume tailoring.]] - rationale - resume/selector.py
- [[JD-present skills first, then remaining profile skills.]] - rationale - resume/selector.py
- [[Lowercase tokens + bigrams from title and cleaned description.]] - rationale - resume/selector.py
- [[MonkeyPatch_4]] - code
- [[Overlap score; matches that are also candidate skills weigh more.]] - rationale - resume/selector.py
- [[Path_13]] - code
- [[Pick top 4–6 verified bullets matching the job; regroup under experiences.]] - rationale - resume/selector.py
- [[Profile with several verified bullets for selection tests.]] - rationale - tests/test_resume.py
- [[RankedBullet]] - code - resume/selector.py
- [[SelectedExperience]] - code - resume/selector.py
- [[Short grounded summary from profile facts only (never invented).]] - rationale - resume/selector.py
- [[Tests for resume selection, Typst compile, and pikepdf sanitization.]] - rationale - tests/test_resume.py
- [[_grounded_summary()]] - code - resume/selector.py
- [[_rich_profile()]] - code - tests/test_resume.py
- [[_sample_job()]] - code - tests/test_resume.py
- [[_skill_terms()]] - code - resume/selector.py
- [[build_resume_data()]] - code - resume/selector.py
- [[dataclasses]] - concept
- [[extract_job_terms()]] - code - resume/selector.py
- [[reorder_skills()]] - code - resume/selector.py
- [[score_bullet()]] - code - resume/selector.py
- [[select_bullets()]] - code - resume/selector.py
- [[selector.py]] - code - resume/selector.py
- [[test_build_resume_data_shape()]] - code - tests/test_resume.py
- [[test_compile_pending_skips_existing()]] - code - tests/test_resume.py
- [[test_compile_resume_and_sanitize()]] - code - tests/test_resume.py
- [[test_extract_job_terms_and_selection()]] - code - tests/test_resume.py
- [[test_resume.py]] - code - tests/test_resume.py
- [[test_sanitize_pdf_idempotent()]] - code - tests/test_resume.py
- [[test_select_bullets_caps_when_sparse()]] - code - tests/test_resume.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/test_resumepy
SORT file.name ASC
```

## Connections to other communities
- 21 edges to [[_COMMUNITY_get_settings]]
- 16 edges to [[_COMMUNITY_profile.py]]
- 9 edges to [[_COMMUNITY_Job]]
- 8 edges to [[_COMMUNITY_Profile]]
- 5 edges to [[_COMMUNITY_session_scope]]
- 5 edges to [[_COMMUNITY_baseline.py]]
- 4 edges to [[_COMMUNITY_suggest.py]]
- 4 edges to [[_COMMUNITY_upsert_job]]
- 3 edges to [[_COMMUNITY_Source]]
- 3 edges to [[_COMMUNITY_pipeline.py]]
- 2 edges to [[_COMMUNITY_ingest.py]]
- 2 edges to [[_COMMUNITY_re]]
- 2 edges to [[_COMMUNITY_db.py]]
- 2 edges to [[_COMMUNITY_workday.py]]
- 1 edge to [[_COMMUNITY_main.py]]
- 1 edge to [[_COMMUNITY_handlers.py]]
- 1 edge to [[_COMMUNITY_calibration.py]]
- 1 edge to [[_COMMUNITY_linkedin_people.py]]
- 1 edge to [[_COMMUNITY_alerts.py]]
- 1 edge to [[_COMMUNITY_filters.py]]
- 1 edge to [[_COMMUNITY_role_classify.py]]
- 1 edge to [[_COMMUNITY_textclean.py]]
- 1 edge to [[_COMMUNITY_discovery_recall.py]]
- 1 edge to [[_COMMUNITY_eligibility.py]]
- 1 edge to [[_COMMUNITY_typing]]
- 1 edge to [[_COMMUNITY_pytest]]
- 1 edge to [[_COMMUNITY_pathlib]]
- 1 edge to [[_COMMUNITY_runner.py]]
- 1 edge to [[_COMMUNITY_test_pacing.py]]
- 1 edge to [[_COMMUNITY_test_pipeline_order_and_aggregation]]
- 1 edge to [[_COMMUNITY_company_intelligence.py]]
- 1 edge to [[_COMMUNITY_test_phase13_shortlist.py]]
- 1 edge to [[_COMMUNITY_builder.py]]
- 1 edge to [[_COMMUNITY_review.py]]
- 1 edge to [[_COMMUNITY_clients.py]]
- 1 edge to [[_COMMUNITY_test_application_portfolio.py]]
- 1 edge to [[_COMMUNITY_priority.py]]
- 1 edge to [[_COMMUNITY_test_vector_recovery.py]]
- 1 edge to [[_COMMUNITY_test_career_intelligence.py]]
- 1 edge to [[_COMMUNITY_feedback.py]]
- 1 edge to [[_COMMUNITY_test_fit.py]]
- 1 edge to [[_COMMUNITY_test_discovery.py]]
- 1 edge to [[_COMMUNITY_benchmarkengine.py]]
- 1 edge to [[_COMMUNITY_test_llm_provider.py]]
- 1 edge to [[_COMMUNITY_scorerengine.py]]

## Top bridge nodes
- [[dataclasses]] - degree 37, connects to 34 communities
- [[test_resume.py]] - degree 41, connects to 11 communities
- [[selector.py]] - degree 21, connects to 8 communities
- [[build_resume_data()]] - degree 20, connects to 6 communities
- [[test_compile_pending_skips_existing()]] - degree 11, connects to 5 communities
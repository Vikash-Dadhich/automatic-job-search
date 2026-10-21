---
type: community
cohesion: 0.12
members: 24
---

# LLMClient

**Cohesion:** 0.12 - loosely connected
**Members:** 24 nodes

## Members
- [[dot-__init__()_35]] - code - scorer/engine.py
- [[dot-_resolve_client()]] - code - automation/answers.py
- [[dot-_resolve_client()_1]] - code - scorer/engine.py
- [[dot-_score_and_persist()]] - code - scorer/engine.py
- [[dot-score_job()]] - code - scorer/engine.py
- [[dot-score_pending()]] - code - scorer/engine.py
- [[Advisory reading. A failure here does not change fit, priority, or status.]] - rationale - scorer/engine.py
- [[Any_50]] - code
- [[LLMClient_1]] - code - scorer/clients.py
- [[Minimal async LLM interface (mockable for offline tests).]] - rationale - scorer/clients.py
- [[Protocol_5]] - code
- [[Record attention order. A failure here does not change fit, tier, or status.]] - rationale - scorer/engine.py
- [[Score a single job and optionally draft Tier-1 outreach and a cover letter.]] - rationale - scorer/engine.py
- [[Score discovered jobs and persist tiered results.]] - rationale - scorer/engine.py
- [[Score discovered jobs with bounded concurrency; optional early-stop.]] - rationale - scorer/engine.py
- [[Score one job and persist; never raises (returns error outcome).]] - rationale - scorer/engine.py
- [[Scorer]] - code - scorer/engine.py
- [[Structured JD and company context. A lookup failure leaves priority computable.]] - rationale - scorer/engine.py
- [[_JobOutcome]] - code - scorer/engine.py
- [[_attach_priority()]] - code - scorer/engine.py
- [[_priority_evidence()]] - code - scorer/engine.py
- [[_record_career_intelligence()]] - code - scorer/engine.py
- [[_status_for_tier()]] - code - scorer/engine.py
- [[test_score_job_prefilter_skips_llm()]] - code - tests/test_scorer.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/LLMClient
SORT file.name ASC
```

## Connections to other communities
- 12 edges to [[_COMMUNITY_scorerengine.py]]
- 9 edges to [[_COMMUNITY_test_scorer.py]]
- 8 edges to [[_COMMUNITY_Profile]]
- 8 edges to [[_COMMUNITY_session_scope]]
- 6 edges to [[_COMMUNITY_Job]]
- 5 edges to [[_COMMUNITY_test_fit.py]]
- 5 edges to [[_COMMUNITY_Tier]]
- 4 edges to [[_COMMUNITY_re]]
- 4 edges to [[_COMMUNITY_test_vector_recovery.py]]
- 4 edges to [[_COMMUNITY_diff.py]]
- 3 edges to [[_COMMUNITY_scorer__init__.py]]
- 3 edges to [[_COMMUNITY_test_eligibility.py]]
- 3 edges to [[_COMMUNITY_suggest.py]]
- 2 edges to [[_COMMUNITY_skills.py]]
- 2 edges to [[_COMMUNITY_eligibility.py]]
- 2 edges to [[_COMMUNITY_get_settings]]
- 1 edge to [[_COMMUNITY_structured_jd.py]]
- 1 edge to [[_COMMUNITY_company_intelligence.py]]
- 1 edge to [[_COMMUNITY_Source]]
- 1 edge to [[_COMMUNITY_role_classify.py]]
- 1 edge to [[_COMMUNITY_ingest.py]]
- 1 edge to [[_COMMUNITY_clients.py]]
- 1 edge to [[_COMMUNITY_Any_1]]
- 1 edge to [[_COMMUNITY_classify_role]]
- 1 edge to [[_COMMUNITY_test_role_classify.py]]
- 1 edge to [[_COMMUNITY_filters.py]]
- 1 edge to [[_COMMUNITY_discovery_recall.py]]
- 1 edge to [[_COMMUNITY_test_structured_jd.py]]
- 1 edge to [[_COMMUNITY_test_phase13_shortlist.py]]
- 1 edge to [[_COMMUNITY_db.py]]
- 1 edge to [[_COMMUNITY_test_priority.py]]
- 1 edge to [[_COMMUNITY_test_career_intelligence.py]]
- 1 edge to [[_COMMUNITY_prerank.py]]
- 1 edge to [[_COMMUNITY_test_doctor.py]]

## Top bridge nodes
- [[LLMClient_1]] - degree 34, connects to 15 communities
- [[dot-score_pending()]] - degree 18, connects to 11 communities
- [[Scorer]] - degree 24, connects to 10 communities
- [[dot-score_job()]] - degree 14, connects to 9 communities
- [[test_score_job_prefilter_skips_llm()]] - degree 8, connects to 7 communities
---
type: community
cohesion: 0.15
members: 29
---

# test_eligibility.py

**Cohesion:** 0.15 - loosely connected
**Members:** 29 nodes

## Members
- [[dot-__init__()_17]] - code - tests/test_eligibility.py
- [[dot-complete()_7]] - code - tests/test_eligibility.py
- [[Copy a decision onto the job. Does not change score, tier, or status.]] - rationale - scorer/eligibility.py
- [[EligibilityDecision]] - code - scorer/eligibility.py
- [[Exception_1]] - code
- [[Hash of the profile facts this engine reads. Dream companies are excluded.]] - rationale - scorer/eligibility.py
- [[Phase 9 eligibility. Unknown sponsorship is not a rejection, and fit is…]] - rationale - tests/test_eligibility.py
- [[PostgreSQL types for the eligibility columns. Used by the schema test.]] - rationale - scorer/eligibility.py
- [[Return a cached decision, or compute one. Model failure stays UNKNOWN.]] - rationale - scorer/eligibility.py
- [[_Model]] - code - tests/test_eligibility.py
- [[_job()_5]] - code - tests/test_eligibility.py
- [[assign_eligibility()]] - code - scorer/eligibility.py
- [[attach_eligibility()]] - code - scorer/eligibility.py
- [[eligibility_column_types()]] - code - scorer/eligibility.py
- [[eligibility_is_current()]] - code - scorer/eligibility.py
- [[evaluate_eligibility()]] - code - scorer/eligibility.py
- [[profile_eligibility_hash()]] - code - scorer/eligibility.py
- [[test_cache_identity()]] - code - tests/test_eligibility.py
- [[test_citizenship_clearance_and_eeo()]] - code - tests/test_eligibility.py
- [[test_education_graduation_and_experience()]] - code - tests/test_eligibility.py
- [[test_eligibility.py]] - code - tests/test_eligibility.py
- [[test_explicit_sponsorship_paths()]] - code - tests/test_eligibility.py
- [[test_hostile_language_wins_and_false_friends_do_not()]] - code - tests/test_eligibility.py
- [[test_location_is_not_a_seattle_gate()]] - code - tests/test_eligibility.py
- [[test_malformed_model_stays_unknown()]] - code - tests/test_eligibility.py
- [[test_postgres_eligibility_columns()]] - code - tests/test_eligibility.py
- [[test_signals_do_not_change_eligibility()]] - code - tests/test_eligibility.py
- [[test_sqlite_persistence_and_upsert()]] - code - tests/test_eligibility.py
- [[test_unknown_authorization_and_dates()]] - code - tests/test_eligibility.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/test_eligibilitypy
SORT file.name ASC
```

## Connections to other communities
- 18 edges to [[_COMMUNITY_Profile]]
- 15 edges to [[_COMMUNITY_eligibility.py]]
- 14 edges to [[_COMMUNITY_Source]]
- 6 edges to [[_COMMUNITY_Job]]
- 4 edges to [[_COMMUNITY_session_scope]]
- 4 edges to [[_COMMUNITY_filters.py]]
- 4 edges to [[_COMMUNITY_upsert_job]]
- 3 edges to [[_COMMUNITY_LLMClient]]
- 2 edges to [[_COMMUNITY_ingest.py]]
- 2 edges to [[_COMMUNITY_test_recruiting_universe.py]]
- 2 edges to [[_COMMUNITY_json]]
- 1 edge to [[_COMMUNITY_scorerengine.py]]
- 1 edge to [[_COMMUNITY_test_company_intelligence_v2.py]]
- 1 edge to [[_COMMUNITY_get_settings]]
- 1 edge to [[_COMMUNITY_pytest]]
- 1 edge to [[_COMMUNITY_db.py]]
- 1 edge to [[_COMMUNITY_pathlib]]
- 1 edge to [[_COMMUNITY_profile.py]]

## Top bridge nodes
- [[test_eligibility.py]] - degree 45, connects to 13 communities
- [[attach_eligibility()]] - degree 15, connects to 8 communities
- [[evaluate_eligibility()]] - degree 26, connects to 6 communities
- [[test_sqlite_persistence_and_upsert()]] - degree 9, connects to 4 communities
- [[_job()_5]] - degree 16, connects to 3 communities
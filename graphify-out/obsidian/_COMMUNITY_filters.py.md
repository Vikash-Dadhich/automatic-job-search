---
type: community
cohesion: 0.10
members: 31
---

# filters.py

**Cohesion:** 0.10 - loosely connected
**Members:** 31 nodes

## Members
- [[Apply the same hard-negative rules to a persisted Job (scoring backlog guard).]] - rationale - scraper/filters.py
- [[Deterministic negative pre-filter before LLM scoring.]] - rationale - scraper/filters.py
- [[FilterResult]] - code - scraper/filters.py
- [[Missing or weak evidence must not become a hard rejection.]] - rationale - tests/test_false_negative.py
- [[Split so a later sentence cannot change an earlier clearance statement.]] - rationale - scraper/filters.py
- [[Title phrases that count as internships when the word 'intern' is absent.]] - rationale - scraper/filters.py
- [[True for intern titles and controlled MBA summer-associate titles. The word…]] - rationale - scraper/filters.py
- [[True when the posting explicitly limits applicants to U.S. citizens.]] - rationale - scraper/filters.py
- [[Years that are explicitly required. Preferred or unclear numbers are ignored.]] - rationale - scraper/filters.py
- [[_clearance_clauses()]] - code - scraper/filters.py
- [[_haystack()]] - code - scraper/filters.py
- [[_mandatory_years()]] - code - scraper/filters.py
- [[_matches_any()]] - code - scraper/filters.py
- [[_posting()_2]] - code - tests/test_false_negative.py
- [[_qualifier_is_mandatory()]] - code - scraper/filters.py
- [[_seniority_reason()]] - code - scraper/filters.py
- [[_soft_internship_signals()]] - code - scraper/filters.py
- [[``required``, ``preferred``, or ``none``. Required or preferred is decided from…]] - rationale - scraper/filters.py
- [[citizenship_restriction()]] - code - scraper/filters.py
- [[clearance_requirement()]] - code - scraper/filters.py
- [[datetime_2]] - code
- [[evaluate_job()]] - code - scraper/filters.py
- [[filters.py]] - code - scraper/filters.py
- [[has_internship_signal()]] - code - scraper/filters.py
- [[test_clearance_words_must_be_about_clearance()]] - code - tests/test_false_negative.py
- [[test_explicit_internship_title_survives_seniority_words()]] - code - tests/test_false_negative.py
- [[test_false_negative.py]] - code - tests/test_false_negative.py
- [[test_preferred_clearance_is_not_a_hard_rejection()]] - code - tests/test_false_negative.py
- [[test_role_uncertainty_does_not_filter()]] - code - tests/test_false_negative.py
- [[test_unknown_eligibility_is_not_a_rejection()]] - code - tests/test_false_negative.py
- [[test_unknown_fit_judgment_stays_unknown()]] - code - tests/test_false_negative.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/filterspy
SORT file.name ASC
```

## Connections to other communities
- 29 edges to [[_COMMUNITY_Profile]]
- 15 edges to [[_COMMUNITY_Source]]
- 10 edges to [[_COMMUNITY_eligibility.py]]
- 8 edges to [[_COMMUNITY_discovery_recall.py]]
- 6 edges to [[_COMMUNITY_Job]]
- 5 edges to [[_COMMUNITY_structured_jd.py]]
- 4 edges to [[_COMMUNITY_session_scope]]
- 4 edges to [[_COMMUNITY_test_eligibility.py]]
- 3 edges to [[_COMMUNITY_re]]
- 3 edges to [[_COMMUNITY_scorerengine.py]]
- 3 edges to [[_COMMUNITY_test_vector_recovery.py]]
- 3 edges to [[_COMMUNITY_test_recruiting_universe.py]]
- 3 edges to [[_COMMUNITY_test_fit.py]]
- 2 edges to [[_COMMUNITY_get_settings]]
- 2 edges to [[_COMMUNITY_json]]
- 2 edges to [[_COMMUNITY_linkedin_jobspy.py]]
- 2 edges to [[_COMMUNITY_db.py]]
- 2 edges to [[_COMMUNITY_profile.py]]
- 1 edge to [[_COMMUNITY_LLMClient]]
- 1 edge to [[_COMMUNITY_typing]]
- 1 edge to [[_COMMUNITY_test_resume.py]]
- 1 edge to [[_COMMUNITY_ingest.py]]
- 1 edge to [[_COMMUNITY_test_phase0_baseline.py]]
- 1 edge to [[_COMMUNITY_Tier]]

## Top bridge nodes
- [[filters.py]] - degree 49, connects to 20 communities
- [[test_false_negative.py]] - degree 28, connects to 10 communities
- [[evaluate_job()]] - degree 15, connects to 6 communities
- [[test_unknown_fit_judgment_stays_unknown()]] - degree 7, connects to 6 communities
- [[has_internship_signal()]] - degree 11, connects to 5 communities
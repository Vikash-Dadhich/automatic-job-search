---
type: community
cohesion: 0.14
members: 28
---

# test_structured_jd.py

**Cohesion:** 0.14 - loosely connected
**Members:** 28 nodes

## Members
- [[Any_13]] - code
- [[Derived reading of one normalized JD. Not a score and not a role label.]] - rationale - core/db.py
- [[Persist a reading for this job. A failure here must not raise.]] - rationale - scraper/structured_jd.py
- [[Read explicit structure from normalized JD text. Absence stays unknown.]] - rationale - scraper/structured_jd.py
- [[Structured JD readings. Deterministic, and independent of fit or eligibility.]] - rationale - tests/test_structured_jd.py
- [[StructuredJobDescription]] - code - core/db.py
- [[True when this row was built for this normalized text and this version.]] - rationale - scraper/structured_jd.py
- [[_areas()]] - code - tests/test_structured_jd.py
- [[_job()_3]] - code - tests/test_structured_jd.py
- [[attach_structured_jd()]] - code - scraper/structured_jd.py
- [[counted()]] - code - tests/test_structured_jd.py
- [[extract_structured_jd()]] - code - scraper/structured_jd.py
- [[get_structured_jd()]] - code - scraper/structured_jd.py
- [[sqlalchemy_dialects]] - concept
- [[sqlalchemy_schema]] - concept
- [[structured_jd_is_current()]] - code - scraper/structured_jd.py
- [[test_changed_upsert_drops_the_old_reading()]] - code - tests/test_structured_jd.py
- [[test_experience_shapes()]] - code - tests/test_structured_jd.py
- [[test_functional_signals_are_phrase_evidence()]] - code - tests/test_structured_jd.py
- [[test_good_mba_internship_populates_several_fields()]] - code - tests/test_structured_jd.py
- [[test_mba_required_preferred_and_absent()]] - code - tests/test_structured_jd.py
- [[test_missing_evidence_stays_unknown_or_not_mentioned()]] - code - tests/test_structured_jd.py
- [[test_required_and_preferred_stay_separate()]] - code - tests/test_structured_jd.py
- [[test_same_text_is_not_recomputed_and_a_change_is()]] - code - tests/test_structured_jd.py
- [[test_sponsorship_and_authorization()]] - code - tests/test_structured_jd.py
- [[test_structured_jd.py]] - code - tests/test_structured_jd.py
- [[test_tables_compile_for_sqlite_and_postgres()]] - code - tests/test_structured_jd.py
- [[test_version_must_match_the_current_extractor()]] - code - tests/test_structured_jd.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/test_structured_jdpy
SORT file.name ASC
```

## Connections to other communities
- 10 edges to [[_COMMUNITY_structured_jd.py]]
- 8 edges to [[_COMMUNITY_Source]]
- 7 edges to [[_COMMUNITY_classify_role]]
- 6 edges to [[_COMMUNITY_test_application_deadline.py]]
- 5 edges to [[_COMMUNITY_session_scope]]
- 5 edges to [[_COMMUNITY_textclean.py]]
- 3 edges to [[_COMMUNITY_db.py]]
- 3 edges to [[_COMMUNITY_Job]]
- 3 edges to [[_COMMUNITY_upsert_job]]
- 3 edges to [[_COMMUNITY_test_monitoring.py]]
- 2 edges to [[_COMMUNITY_test_vector_recovery.py]]
- 2 edges to [[_COMMUNITY_ingest.py]]
- 2 edges to [[_COMMUNITY_test_career_intelligence.py]]
- 2 edges to [[_COMMUNITY_scorerengine.py]]
- 2 edges to [[_COMMUNITY_test_company_intelligence_v2.py]]
- 1 edge to [[_COMMUNITY_AsyncSession]]
- 1 edge to [[_COMMUNITY_tracker.py]]
- 1 edge to [[_COMMUNITY_LLMClient]]
- 1 edge to [[_COMMUNITY_test_role_classify.py]]
- 1 edge to [[_COMMUNITY_pytest]]

## Top bridge nodes
- [[test_structured_jd.py]] - degree 37, connects to 9 communities
- [[attach_structured_jd()]] - degree 17, connects to 7 communities
- [[get_structured_jd()]] - degree 14, connects to 6 communities
- [[StructuredJobDescription]] - degree 11, connects to 4 communities
- [[test_same_text_is_not_recomputed_and_a_change_is()]] - degree 10, connects to 4 communities
---
type: community
cohesion: 0.11
members: 33
---

# company_intelligence.py

**Cohesion:** 0.11 - loosely connected
**Members:** 33 nodes

## Members
- [[AsyncSession]] - code
- [[Classify an already-supplied company URL. Does not invent a domain.]] - rationale - scorer/company_intelligence.py
- [[CompanyIntelligence]] - code - core/db.py
- [[Display form of the lookup key, keeping the source casing.]] - rationale - scorer/company_intelligence.py
- [[Factual company records. Not fit, not eligibility, and not a ranking score.]] - rationale - scorer/company_intelligence.py
- [[Factual employer record shared by jobs. Not a score and not a preference.]] - rationale - core/db.py
- [[Lookup key trimmed, lowercased, trailing legal suffix removed. Interior…]] - rationale - scorer/company_intelligence.py
- [[Record a failed first lookup. A later failure keeps facts already stored.]] - rationale - scorer/company_intelligence.py
- [[Refresh signals from this page. A bad extract leaves the previous context.]] - rationale - scorer/company_intelligence.py
- [[Return the stored record for this company, if one exists.]] - rationale - scorer/company_intelligence.py
- [[_apply_context()]] - code - scorer/company_intelligence.py
- [[_apply_facts()]] - code - scorer/company_intelligence.py
- [[_by_key()]] - code - scorer/company_intelligence.py
- [[_clear_facts()]] - code - scorer/company_intelligence.py
- [[_confidence_for()]] - code - scorer/company_intelligence.py
- [[_context_from()]] - code - scorer/company_intelligence.py
- [[_new_row()]] - code - scorer/company_intelligence.py
- [[_reliable_source_url()]] - code - scorer/company_intelligence.py
- [[_source_type()]] - code - scorer/company_intelligence.py
- [[_stamp_signals()]] - code - scorer/company_intelligence.py
- [[_store_failure()]] - code - scorer/company_intelligence.py
- [[_without_trailing_suffix()]] - code - scorer/company_intelligence.py
- [[canonical_company_name()]] - code - scorer/company_intelligence.py
- [[company_intelligence.py]] - code - scorer/company_intelligence.py
- [[datetime_5]] - code
- [[empty_company_context()]] - code - scorer/company_intelligence.py
- [[get_company_intelligence()]] - code - scorer/company_intelligence.py
- [[normalize_company_name()]] - code - scorer/company_intelligence.py
- [[test_company_url_is_not_guessed_or_taken_from_the_job_page()]] - code - tests/test_company_intelligence.py
- [[test_legal_suffixes_do_not_collapse_distinct_names()]] - code - tests/test_company_intelligence.py
- [[test_normalization_is_deterministic()]] - code - tests/test_company_intelligence.py
- [[test_version_and_normalization_stay_explicit()]] - code - tests/test_company_intelligence_v2.py
- [[trustworthy_company_source()]] - code - scorer/company_intelligence.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/company_intelligencepy
SORT file.name ASC
```

## Connections to other communities
- 24 edges to [[_COMMUNITY_test_company_intelligence.py]]
- 12 edges to [[_COMMUNITY_test_company_intelligence_v2.py]]
- 11 edges to [[_COMMUNITY_Any]]
- 5 edges to [[_COMMUNITY_extract_company_signals]]
- 4 edges to [[_COMMUNITY_test_career_intelligence.py]]
- 3 edges to [[_COMMUNITY_Source]]
- 3 edges to [[_COMMUNITY_ingest.py]]
- 2 edges to [[_COMMUNITY_db.py]]
- 2 edges to [[_COMMUNITY_HttpCompanyIntelProvider]]
- 2 edges to [[_COMMUNITY_textclean.py]]
- 1 edge to [[_COMMUNITY_scorerengine.py]]
- 1 edge to [[_COMMUNITY_AsyncSession]]
- 1 edge to [[_COMMUNITY_LLMClient]]
- 1 edge to [[_COMMUNITY_Job]]
- 1 edge to [[_COMMUNITY_linkedin_jobspy.py]]
- 1 edge to [[_COMMUNITY_json]]
- 1 edge to [[_COMMUNITY_re]]
- 1 edge to [[_COMMUNITY_test_apply_url.py]]
- 1 edge to [[_COMMUNITY_test_monitoring.py]]
- 1 edge to [[_COMMUNITY_migrate_to_neon.py]]
- 1 edge to [[_COMMUNITY_test_resume.py]]
- 1 edge to [[_COMMUNITY_typing]]

## Top bridge nodes
- [[company_intelligence.py]] - degree 53, connects to 16 communities
- [[CompanyIntelligence]] - degree 22, connects to 8 communities
- [[_apply_context()]] - degree 10, connects to 4 communities
- [[trustworthy_company_source()]] - degree 7, connects to 3 communities
- [[normalize_company_name()]] - degree 10, connects to 2 communities
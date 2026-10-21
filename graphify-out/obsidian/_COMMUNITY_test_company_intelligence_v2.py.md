---
type: community
cohesion: 0.17
members: 21
---

# test_company_intelligence_v2.py

**Cohesion:** 0.17 - loosely connected
**Members:** 21 nodes

## Members
- [[dot-__init__()_25]] - code - tests/test_company_intelligence_v2.py
- [[dot-lookup()]] - code - scorer/company_intelligence.py
- [[dot-lookup()_1]] - code - scorer/company_intelligence.py
- [[dot-lookup()_2]] - code - tests/test_company_intelligence.py
- [[dot-lookup()_3]] - code - tests/test_company_intelligence_v2.py
- [[A fetched page, or an error. ``claimed`` is never stored on its own.]] - rationale - scorer/company_intelligence.py
- [[CompanyIntelProvider]] - code - scorer/company_intelligence.py
- [[CompanyLookupResult]] - code - scorer/company_intelligence.py
- [[CompanySourceDocument]] - code - scorer/company_intelligence.py
- [[Factual company signals. They do not score employers or change job decisions.]] - rationale - tests/test_company_intelligence_v2.py
- [[Fetch one explicit source URL. Do not search or invent a domain.]] - rationale - scorer/company_intelligence.py
- [[Look up the company again. Does not recompute fit or role-family weight.]] - rationale - scorer/company_intelligence.py
- [[Protocol_4]] - code
- [[_Provider]] - code - tests/test_company_intelligence_v2.py
- [[_one()_1]] - code - tests/test_company_intelligence_v2.py
- [[_signals()]] - code - tests/test_company_intelligence_v2.py
- [[refresh_company_intelligence()]] - code - scorer/company_intelligence.py
- [[test_changed_page_replaces_that_source_and_keeps_another()]] - code - tests/test_company_intelligence_v2.py
- [[test_company_intelligence_v2.py]] - code - tests/test_company_intelligence_v2.py
- [[test_context_column_compiles_for_postgres()]] - code - tests/test_company_intelligence_v2.py
- [[test_profile_signals_persist_with_evidence()]] - code - tests/test_company_intelligence_v2.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/test_company_intelligence_v2py
SORT file.name ASC
```

## Connections to other communities
- 12 edges to [[_COMMUNITY_test_company_intelligence.py]]
- 12 edges to [[_COMMUNITY_company_intelligence.py]]
- 8 edges to [[_COMMUNITY_Source]]
- 7 edges to [[_COMMUNITY_db.py]]
- 4 edges to [[_COMMUNITY_session_scope]]
- 2 edges to [[_COMMUNITY_extract_company_signals]]
- 2 edges to [[_COMMUNITY_Any]]
- 2 edges to [[_COMMUNITY_test_structured_jd.py]]
- 1 edge to [[_COMMUNITY_HttpCompanyIntelProvider]]
- 1 edge to [[_COMMUNITY_textclean.py]]
- 1 edge to [[_COMMUNITY_test_eligibility.py]]
- 1 edge to [[_COMMUNITY_upsert_job]]
- 1 edge to [[_COMMUNITY_get_settings]]
- 1 edge to [[_COMMUNITY_eligibility.py]]
- 1 edge to [[_COMMUNITY_pytest]]
- 1 edge to [[_COMMUNITY_test_monitoring.py]]
- 1 edge to [[_COMMUNITY_baseline.py]]
- 1 edge to [[_COMMUNITY_pathlib]]

## Top bridge nodes
- [[test_company_intelligence_v2.py]] - degree 44, connects to 16 communities
- [[dot-lookup()_1]] - degree 6, connects to 3 communities
- [[refresh_company_intelligence()]] - degree 12, connects to 2 communities
- [[CompanyLookupResult]] - degree 10, connects to 2 communities
- [[CompanySourceDocument]] - degree 9, connects to 2 communities
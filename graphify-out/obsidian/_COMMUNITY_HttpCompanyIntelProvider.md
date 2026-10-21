---
type: community
cohesion: 0.24
members: 10
---

# HttpCompanyIntelProvider

**Cohesion:** 0.24 - loosely connected
**Members:** 10 nodes

## Members
- [[dot-__init__()_31]] - code - scorer/company_intelligence.py
- [[AsyncClient_1]] - code
- [[HttpCompanyIntelProvider]] - code - scorer/company_intelligence.py
- [[One GET of a caller-supplied URL. No crawl and no domain guessing.]] - rationale - scorer/company_intelligence.py
- [[httpx]] - concept
- [[ok()_4]] - code - tests/test_company_intelligence.py
- [[ok()_5]] - code - tests/test_company_intelligence.py
- [[test_http_provider_handles_timeout_and_malformed_pages()]] - code - tests/test_company_intelligence.py
- [[test_http_provider_keeps_the_caller_source_type()]] - code - tests/test_company_intelligence.py
- [[timeout()]] - code - tests/test_company_intelligence.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/HttpCompanyIntelProvider
SORT file.name ASC
```

## Connections to other communities
- 4 edges to [[_COMMUNITY_test_company_intelligence.py]]
- 2 edges to [[_COMMUNITY_company_intelligence.py]]
- 2 edges to [[_COMMUNITY_workday_rest.py]]
- 1 edge to [[_COMMUNITY_Source]]
- 1 edge to [[_COMMUNITY_ingest.py]]
- 1 edge to [[_COMMUNITY_test_company_intelligence_v2.py]]
- 1 edge to [[_COMMUNITY_textclean.py]]
- 1 edge to [[_COMMUNITY_Any]]
- 1 edge to [[_COMMUNITY_pathlib]]

## Top bridge nodes
- [[HttpCompanyIntelProvider]] - degree 9, connects to 5 communities
- [[httpx]] - degree 7, connects to 4 communities
- [[test_http_provider_handles_timeout_and_malformed_pages()]] - degree 7, connects to 3 communities
- [[test_http_provider_keeps_the_caller_source_type()]] - degree 5, connects to 1 community
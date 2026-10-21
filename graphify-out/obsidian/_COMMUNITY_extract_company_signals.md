---
type: community
cohesion: 0.38
members: 7
---

# extract_company_signals

**Cohesion:** 0.38 - loosely connected
**Members:** 7 nodes

## Members
- [[Explicit employer signals. A missing phrase stays absent, not false.]] - rationale - scorer/company_intelligence.py
- [[Match_1]] - code
- [[_compact()]] - code - scorer/company_intelligence.py
- [[_signal()_1]] - code - scorer/company_intelligence.py
- [[_snippet()]] - code - scorer/company_intelligence.py
- [[extract_company_signals()]] - code - scorer/company_intelligence.py
- [[test_signals_are_explicit_and_multi_valued()]] - code - tests/test_company_intelligence_v2.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/extract_company_signals
SORT file.name ASC
```

## Connections to other communities
- 5 edges to [[_COMMUNITY_company_intelligence.py]]
- 2 edges to [[_COMMUNITY_Any]]
- 2 edges to [[_COMMUNITY_test_company_intelligence_v2.py]]

## Top bridge nodes
- [[extract_company_signals()]] - degree 8, connects to 3 communities
- [[_signal()_1]] - degree 5, connects to 2 communities
- [[_snippet()]] - degree 4, connects to 1 community
- [[_compact()]] - degree 3, connects to 1 community
- [[test_signals_are_explicit_and_multi_valued()]] - degree 2, connects to 1 community
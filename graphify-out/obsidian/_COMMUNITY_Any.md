---
type: community
cohesion: 0.15
members: 15
---

# Any

**Cohesion:** 0.15 - loosely connected
**Members:** 15 nodes

## Members
- [[Any_53]] - code
- [[Keep a known fact when the newer page does not state a replacement.]] - rationale - scorer/company_intelligence.py
- [[Keep earlier trustworthy sources and add a new URL once.]] - rationale - scorer/company_intelligence.py
- [[Pull only phrases the source actually states. Missing phrases stay null.]] - rationale - scorer/company_intelligence.py
- [[Replace this source's signals, then keep the higher-priority source on a…]] - rationale - scorer/company_intelligence.py
- [[_accumulate_sources()]] - code - scorer/company_intelligence.py
- [[_prefer_signal()]] - code - scorer/company_intelligence.py
- [[_status_for()]] - code - scorer/company_intelligence.py
- [[extract_company_facts()]] - code - scorer/company_intelligence.py
- [[merge_company_facts()]] - code - scorer/company_intelligence.py
- [[merge_company_signals()]] - code - scorer/company_intelligence.py
- [[test_authoritative_source_wins_a_contradiction()]] - code - tests/test_company_intelligence_v2.py
- [[test_extractor_keeps_unstated_facts_null()]] - code - tests/test_company_intelligence.py
- [[test_merge_company_facts_keeps_omitted_fields()]] - code - tests/test_company_intelligence.py
- [[test_prestige_language_is_not_a_fact()]] - code - tests/test_company_intelligence.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Any
SORT file.name ASC
```

## Connections to other communities
- 11 edges to [[_COMMUNITY_company_intelligence.py]]
- 9 edges to [[_COMMUNITY_test_company_intelligence.py]]
- 2 edges to [[_COMMUNITY_extract_company_signals]]
- 2 edges to [[_COMMUNITY_test_company_intelligence_v2.py]]
- 1 edge to [[_COMMUNITY_HttpCompanyIntelProvider]]

## Top bridge nodes
- [[extract_company_facts()]] - degree 9, connects to 3 communities
- [[Any_53]] - degree 12, connects to 2 communities
- [[merge_company_signals()]] - degree 7, connects to 2 communities
- [[merge_company_facts()]] - degree 6, connects to 2 communities
- [[_accumulate_sources()]] - degree 4, connects to 2 communities
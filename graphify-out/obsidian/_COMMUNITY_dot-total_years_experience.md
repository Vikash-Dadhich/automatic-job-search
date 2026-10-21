---
type: community
cohesion: 0.50
members: 5
---

# .total_years_experience

**Cohesion:** 0.50 - moderately connected
**Members:** 5 nodes

## Members
- [[dot-total_years_experience()]] - code - config/profile.py
- [[Approximate career length in years, spanning earliest start to latest end.]] - rationale - config/profile.py
- [[Parse 'YYYY-MM'  'YYYY'; 'Present' and unparseable values return None.]] - rationale - config/profile.py
- [[_parse_month()]] - code - config/profile.py
- [[date]] - code

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/total_years_experience
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_Profile]]
- 1 edge to [[_COMMUNITY_profile.py]]
- 1 edge to [[_COMMUNITY_Settings]]

## Top bridge nodes
- [[dot-total_years_experience()]] - degree 5, connects to 2 communities
- [[_parse_month()]] - degree 4, connects to 1 community
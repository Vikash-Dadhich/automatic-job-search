---
type: community
cohesion: 0.22
members: 20
---

# test_apply_url.py

**Cohesion:** 0.22 - loosely connected
**Members:** 20 nodes

## Members
- [[ApplyKind]] - code - core/apply_url.py
- [[Classify job apply URLs (Workday vs LinkedIn listing vs other company ATS).]] - rationale - core/apply_url.py
- [[Classify where application happens for a stored job URL.]] - rationale - core/apply_url.py
- [[StrEnum_6]] - code
- [[Tests for apply-URL classification (LinkedIn → company Workday).]] - rationale - tests/test_apply_url.py
- [[True when the URL is a Workday careers  job deep link.]] - rationale - core/apply_url.py
- [[URLs we can hand to WorkdayApplicator today.]] - rationale - core/apply_url.py
- [[Where the candidate actually applies.]] - rationale - core/apply_url.py
- [[_host()]] - code - core/apply_url.py
- [[apply_url.py]] - code - core/apply_url.py
- [[classify_apply_url()]] - code - core/apply_url.py
- [[is_automateable_apply_url()]] - code - core/apply_url.py
- [[is_workday_url()]] - code - core/apply_url.py
- [[test_apply_url.py]] - code - tests/test_apply_url.py
- [[test_classify_company_site()]] - code - tests/test_apply_url.py
- [[test_classify_linkedin_listing()]] - code - tests/test_apply_url.py
- [[test_classify_workday()]] - code - tests/test_apply_url.py
- [[test_classify_ziprecruiter_and_google()]] - code - tests/test_apply_url.py
- [[urllib_parse]] - concept
- [[workday_parts()]] - code - core/apply_url.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/test_apply_urlpy
SORT file.name ASC
```

## Connections to other communities
- 7 edges to [[_COMMUNITY_targets.py]]
- 7 edges to [[_COMMUNITY_Source]]
- 5 edges to [[_COMMUNITY_runner.py]]
- 3 edges to [[_COMMUNITY_tracker.py]]
- 2 edges to [[_COMMUNITY_session_scope]]
- 2 edges to [[_COMMUNITY_main.py]]
- 1 edge to [[_COMMUNITY_discovery_recall.py]]
- 1 edge to [[_COMMUNITY_company_intelligence.py]]
- 1 edge to [[_COMMUNITY_db.py]]
- 1 edge to [[_COMMUNITY_skills.py]]

## Top bridge nodes
- [[workday_parts()]] - degree 11, connects to 5 communities
- [[apply_url.py]] - degree 15, connects to 4 communities
- [[urllib_parse]] - degree 4, connects to 3 communities
- [[test_apply_url.py]] - degree 17, connects to 2 communities
- [[is_automateable_apply_url()]] - degree 12, connects to 2 communities
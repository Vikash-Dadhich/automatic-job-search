---
type: community
cohesion: 0.21
members: 19
---

# prerank.py

**Cohesion:** 0.21 - loosely connected
**Members:** 19 nodes

## Members
- [[Cheap 0..~100 heuristic; higher = score sooner. No network, no LLM.]] - rationale - scorer/prerank.py
- [[Deterministic, LLM-free pre-rank to order jobs before scoring. Recallcost…]] - rationale - scorer/prerank.py
- [[Map a job source to a rank weight. Unknown values score as 1.0.]] - rationale - scorer/prerank.py
- [[Return jobs ordered best-first by ``prerank_score`` (stable on ties).]] - rationale - scorer/prerank.py
- [[Tests for the deterministic pre-rank (scorer.prerank).]] - rationale - tests/test_prerank.py
- [[_job()_15]] - code - tests/test_prerank.py
- [[_source_weight()]] - code - scorer/prerank.py
- [[datetime_14]] - code
- [[prerank.py]] - code - scorer/prerank.py
- [[prerank_jobs()]] - code - scorer/prerank.py
- [[prerank_score()]] - code - scorer/prerank.py
- [[test_dream_company_boost()]] - code - tests/test_prerank.py
- [[test_intern_title_outranks_fulltime()]] - code - tests/test_prerank.py
- [[test_new_source_scored_without_error()]] - code - tests/test_prerank.py
- [[test_prerank.py]] - code - tests/test_prerank.py
- [[test_prerank_jobs_empty()]] - code - tests/test_prerank.py
- [[test_prerank_jobs_orders_best_first()]] - code - tests/test_prerank.py
- [[test_recency_boost()]] - code - tests/test_prerank.py
- [[test_summer_signal_scores_above_bare_title()]] - code - tests/test_prerank.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/prerankpy
SORT file.name ASC
```

## Connections to other communities
- 11 edges to [[_COMMUNITY_Profile]]
- 7 edges to [[_COMMUNITY_discovery_recall.py]]
- 5 edges to [[_COMMUNITY_Source]]
- 5 edges to [[_COMMUNITY_Job]]
- 3 edges to [[_COMMUNITY_pytest]]
- 3 edges to [[_COMMUNITY_scorerengine.py]]
- 3 edges to [[_COMMUNITY_scorer__init__.py]]
- 2 edges to [[_COMMUNITY_db.py]]
- 2 edges to [[_COMMUNITY_profile.py]]
- 1 edge to [[_COMMUNITY_LLMClient]]
- 1 edge to [[_COMMUNITY_How jobs are found, filtered, scored, and sent]]
- 1 edge to [[_COMMUNITY_re]]
- 1 edge to [[_COMMUNITY_baseline.py]]

## Top bridge nodes
- [[prerank.py]] - degree 19, connects to 11 communities
- [[prerank_score()]] - degree 19, connects to 6 communities
- [[test_prerank.py]] - degree 18, connects to 5 communities
- [[prerank_jobs()]] - degree 12, connects to 5 communities
- [[_job()_15]] - degree 10, connects to 2 communities
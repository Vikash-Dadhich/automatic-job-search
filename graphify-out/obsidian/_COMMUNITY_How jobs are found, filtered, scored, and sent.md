---
type: community
cohesion: 0.25
members: 8
---

# How jobs are found, filtered, scored, and sent

**Cohesion:** 0.25 - loosely connected
**Members:** 8 nodes

## Members
- [[1. What a run is]] - document - docs/how-jobs-are-found-scored-and-sent.md
- [[4. How results are prioritised today]] - document - docs/how-jobs-are-found-scored-and-sent.md
- [[4.1 Pre-score rank (`prerank_score`)]] - document - docs/how-jobs-are-found-scored-and-sent.md
- [[4.2 Embedding gate (this does drop jobs)]] - document - docs/how-jobs-are-found-scored-and-sent.md
- [[4.3 Fit-model cap]] - document - docs/how-jobs-are-found-scored-and-sent.md
- [[7. Statuses, in one pass]] - document - docs/how-jobs-are-found-scored-and-sent.md
- [[How jobs are found, filtered, scored, and sent]] - document - docs/how-jobs-are-found-scored-and-sent.md
- [[how-jobs-are-found-scored-and-sent]] - document - docs/how-jobs-are-found-scored-and-sent.md

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/How_jobs_are_found_filtered_scored_and_sent
SORT file.name ASC
```

## Connections to other communities
- 2 edges to [[_COMMUNITY_5. How fit is scored]]
- 1 edge to [[_COMMUNITY_prerank.py]]
- 1 edge to [[_COMMUNITY_3. Hard filters (before any model)]]
- 1 edge to [[_COMMUNITY_6. What is sent to you]]
- 1 edge to [[_COMMUNITY_2. Where jobs come from]]
- 1 edge to [[_COMMUNITY_8. The weight discussion (not built)]]
- 1 edge to [[_COMMUNITY_9. Pain points we have actually hit or spelled out]]

## Top bridge nodes
- [[How jobs are found, filtered, scored, and sent]] - degree 11, connects to 6 communities
- [[4.1 Pre-score rank (`prerank_score`)]] - degree 2, connects to 1 community
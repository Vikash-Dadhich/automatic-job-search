---
type: community
cohesion: 0.12
members: 26
---

# test_pipeline_order_and_aggregation

**Cohesion:** 0.12 - loosely connected
**Members:** 26 nodes

## Members
- [[MonkeyPatch_8]] - code
- [[Offline tests for orchestrator.pipeline (monkeypatched stages).]] - rationale - tests/test_pipeline.py
- [[_FakeSummary]] - code - tests/test_pipeline.py
- [[boom()]] - code - tests/test_pipeline.py
- [[fail_score()]] - code - tests/test_pipeline.py
- [[fake_alerts()]] - code - tests/test_pipeline.py
- [[fake_apply()]] - code - tests/test_pipeline.py
- [[fake_benchmark()]] - code - tests/test_pipeline.py
- [[fake_ingestion()]] - code - tests/test_pipeline.py
- [[fake_outcomes()]] - code - tests/test_pipeline.py
- [[fake_portfolio()]] - code - tests/test_pipeline.py
- [[fake_prep()]] - code - tests/test_pipeline.py
- [[fake_prepare()]] - code - tests/test_pipeline.py
- [[fake_resume()]] - code - tests/test_pipeline.py
- [[fake_reviews()]] - code - tests/test_pipeline.py
- [[fake_score()]] - code - tests/test_pipeline.py
- [[fake_shortlist()]] - code - tests/test_pipeline.py
- [[fake_suggest_gen()]] - code - tests/test_pipeline.py
- [[fake_suggest_send()]] - code - tests/test_pipeline.py
- [[ok()]] - code - tests/test_pipeline.py
- [[test_pipeline.py]] - code - tests/test_pipeline.py
- [[test_pipeline_order_and_aggregation()]] - code - tests/test_pipeline.py
- [[test_pipeline_resume_uses_the_review_queue()]] - code - tests/test_pipeline.py
- [[test_pipeline_skips_apply_and_reviews()]] - code - tests/test_pipeline.py
- [[test_pipeline_stage_isolation()]] - code - tests/test_pipeline.py
- [[track()]] - code - tests/test_pipeline.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/test_pipeline_order_and_aggregation
SORT file.name ASC
```

## Connections to other communities
- 6 edges to [[_COMMUNITY_pipeline.py]]
- 2 edges to [[_COMMUNITY_session_scope]]
- 1 edge to [[_COMMUNITY_pytest]]
- 1 edge to [[_COMMUNITY_db.py]]
- 1 edge to [[_COMMUNITY_test_resume.py]]
- 1 edge to [[_COMMUNITY_typing]]

## Top bridge nodes
- [[test_pipeline.py]] - degree 13, connects to 6 communities
- [[test_pipeline_resume_uses_the_review_queue()]] - degree 5, connects to 2 communities
- [[test_pipeline_order_and_aggregation()]] - degree 16, connects to 1 community
- [[test_pipeline_skips_apply_and_reviews()]] - degree 5, connects to 1 community
- [[test_pipeline_stage_isolation()]] - degree 5, connects to 1 community
---
type: community
cohesion: 0.22
members: 13
---

# scorer/__init__.py

**Cohesion:** 0.22 - loosely connected
**Members:** 13 nodes

## Members
- [[dot-clamp_score()]] - code - scorer/schemas.py
- [[dot-normalize_reasons()]] - code - scorer/schemas.py
- [[dot-normalize_tier_hint()]] - code - scorer/schemas.py
- [[BaseModel_10]] - code
- [[Evaluation]] - code - scorer/schemas.py
- [[LLM match evaluator with tier triage and Tier-1 outreach.]] - rationale - scorer/__init__.py
- [[Normalized evaluation ready to persist on a Job row.]] - rationale - scorer/schemas.py
- [[Pydantic schemas for LLM scoring output.]] - rationale - scorer/schemas.py
- [[ScoreRaw]] - code - scorer/schemas.py
- [[Tolerant raw score payload from the model {s,t,r}.]] - rationale - scorer/schemas.py
- [[field_validator_2]] - code
- [[schemas.py]] - code - scorer/schemas.py
- [[scorer__init__.py]] - code - scorer/__init__.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/scorer/__init__py
SORT file.name ASC
```

## Connections to other communities
- 5 edges to [[_COMMUNITY_Tier]]
- 4 edges to [[_COMMUNITY_scorerengine.py]]
- 3 edges to [[_COMMUNITY_LLMClient]]
- 3 edges to [[_COMMUNITY_prerank.py]]
- 2 edges to [[_COMMUNITY_test_vector_recovery.py]]
- 1 edge to [[_COMMUNITY_db.py]]
- 1 edge to [[_COMMUNITY_linkedin_people.py]]

## Top bridge nodes
- [[scorer__init__.py]] - degree 13, connects to 5 communities
- [[schemas.py]] - degree 8, connects to 4 communities
- [[Evaluation]] - degree 8, connects to 3 communities
- [[ScoreRaw]] - degree 9, connects to 2 communities
---
type: community
cohesion: 0.10
members: 26
---

# conftest.py

**Cohesion:** 0.10 - loosely connected
**Members:** 26 nodes

## Members
- [[AGENTS]] - document - AGENTS.md
- [[AGENTS_1]] - document - AGENTS.md
- [[Build order and status]] - document - AGENTS.md
- [[Coding conventions]] - document - AGENTS.md
- [[Commands]] - document - AGENTS.md
- [[Confirmed product decisions]] - document - AGENTS.md
- [[Initialize a fresh DB for each async test; dispose engine afterward.]] - rationale - tests/conftest.py
- [[Keep scoring offline unless a test opts into the embedding gate.]] - rationale - tests/conftest.py
- [[Keep the suite off the 7–18 minute Workday gap unless a test opts in.]] - rationale - tests/conftest.py
- [[Lock the code default. A developer .env may set INTERNSHIP_ONLY=true.]] - rationale - tests/conftest.py
- [[MonkeyPatch_3]] - code
- [[Path_4]] - code
- [[Point DATABASE_URL at a temp sqlite file and clear cached settingsengine.]] - rationale - tests/conftest.py
- [[Project]] - document - AGENTS.md
- [[Repository layout]] - document - AGENTS.md
- [[Shared pytest fixtures — isolate DB and clear settings caches.]] - rationale - tests/conftest.py
- [[Tech stack]] - document - AGENTS.md
- [[Testing conventions]] - document - AGENTS.md
- [[Workflow for implementing a step]] - document - AGENTS.md
- [[_disable_apply_pacing()]] - code - tests/conftest.py
- [[_disable_vector_gate()]] - code - tests/conftest.py
- [[_internship_only_off()]] - code - tests/conftest.py
- [[conftest.py]] - code - tests/conftest.py
- [[db_ready()]] - code - tests/conftest.py
- [[fixture]] - code
- [[tmp_db()]] - code - tests/conftest.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/conftestpy
SORT file.name ASC
```

## Connections to other communities
- 7 edges to [[_COMMUNITY_db.py]]
- 4 edges to [[_COMMUNITY_scorerengine.py]]
- 2 edges to [[_COMMUNITY_suggest.py]]
- 1 edge to [[_COMMUNITY_bot__init__.py]]
- 1 edge to [[_COMMUNITY_pipeline.py]]
- 1 edge to [[_COMMUNITY_diff.py]]
- 1 edge to [[_COMMUNITY_get_settings]]
- 1 edge to [[_COMMUNITY_vault.py]]
- 1 edge to [[_COMMUNITY_test_discovery.py]]
- 1 edge to [[_COMMUNITY_pytest]]
- 1 edge to [[_COMMUNITY_profile.py]]
- 1 edge to [[_COMMUNITY_typing]]
- 1 edge to [[_COMMUNITY_targets.py]]
- 1 edge to [[_COMMUNITY_scheduler.py]]
- 1 edge to [[_COMMUNITY_pathlib]]
- 1 edge to [[_COMMUNITY_clients.py]]
- 1 edge to [[_COMMUNITY_Settings]]
- 1 edge to [[_COMMUNITY_browser.py]]

## Top bridge nodes
- [[conftest.py]] - degree 20, connects to 12 communities
- [[AGENTS_1]] - degree 14, connects to 4 communities
- [[Testing conventions]] - degree 5, connects to 2 communities
- [[Repository layout]] - degree 3, connects to 2 communities
- [[Tech stack]] - degree 3, connects to 2 communities
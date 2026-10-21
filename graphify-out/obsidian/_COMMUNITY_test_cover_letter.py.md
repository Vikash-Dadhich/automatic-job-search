---
type: community
cohesion: 0.23
members: 13
---

# test_cover_letter.py

**Cohesion:** 0.23 - loosely connected
**Members:** 13 nodes

## Members
- [[dot-__init__()_28]] - code - tests/test_cover_letter.py
- [[dot-complete()_14]] - code - tests/test_cover_letter.py
- [[Any_42]] - code
- [[Offline tests for Tier-1 cover letter drafting.]] - rationale - tests/test_cover_letter.py
- [[Trim to the last sentence that fits, so a runaway letter stays usable.]] - rationale - scorer/cover_letter.py
- [[_ScriptedClient]] - code - tests/test_cover_letter.py
- [[_job()_12]] - code - tests/test_cover_letter.py
- [[cap_cover_letter()]] - code - scorer/cover_letter.py
- [[test_cap_cover_letter_cuts_on_sentence_boundary()]] - code - tests/test_cover_letter.py
- [[test_cap_cover_letter_hard_slice_without_punctuation()]] - code - tests/test_cover_letter.py
- [[test_cover_letter.py]] - code - tests/test_cover_letter.py
- [[test_generate_cover_letter_falls_back_when_strip_empties()]] - code - tests/test_cover_letter.py
- [[test_generate_cover_letter_retries_banned_words()]] - code - tests/test_cover_letter.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/test_cover_letterpy
SORT file.name ASC
```

## Connections to other communities
- 6 edges to [[_COMMUNITY_test_scorer.py]]
- 5 edges to [[_COMMUNITY_upsert_job]]
- 3 edges to [[_COMMUNITY_Profile]]
- 3 edges to [[_COMMUNITY_session_scope]]
- 2 edges to [[_COMMUNITY_Source]]
- 2 edges to [[_COMMUNITY_Job]]
- 1 edge to [[_COMMUNITY_Tier]]
- 1 edge to [[_COMMUNITY_test_vector_recovery.py]]
- 1 edge to [[_COMMUNITY_db.py]]
- 1 edge to [[_COMMUNITY_scorerengine.py]]
- 1 edge to [[_COMMUNITY_pathlib]]
- 1 edge to [[_COMMUNITY_typing]]
- 1 edge to [[_COMMUNITY_profile.py]]

## Top bridge nodes
- [[test_cover_letter.py]] - degree 27, connects to 13 communities
- [[_job()_12]] - degree 6, connects to 3 communities
- [[test_generate_cover_letter_falls_back_when_strip_empties()]] - degree 5, connects to 2 communities
- [[test_generate_cover_letter_retries_banned_words()]] - degree 5, connects to 2 communities
- [[cap_cover_letter()]] - degree 6, connects to 1 community
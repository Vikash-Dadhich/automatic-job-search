---
type: community
cohesion: 0.16
members: 20
---

# application_deadline.py

**Cohesion:** 0.16 - loosely connected
**Members:** 20 nodes

## Members
- [[ApplicationDeadline]] - code - scraper/application_deadline.py
- [[BaseModel_5]] - code
- [[Conservative application-deadline reading. Explicit apply-by or closing dates…]] - rationale - scraper/application_deadline.py
- [[Deadline failure stays on this block. The rest of the reading still returns.]] - rationale - scraper/structured_jd.py
- [[Match_2]] - code
- [[One deadline reading. ``deadline_date`` is set only for a full valid date.]] - rationale - scraper/application_deadline.py
- [[Read an explicit closing date. Unusable text is not guessed.]] - rationale - scraper/application_deadline.py
- [[Reading used when an older document has no deadline block.]] - rationale - scraper/application_deadline.py
- [[_application_deadline()]] - code - scraper/structured_jd.py
- [[_clip()_1]] - code - scraper/application_deadline.py
- [[_excluded()]] - code - scraper/application_deadline.py
- [[_from_match()]] - code - scraper/application_deadline.py
- [[_named()_1]] - code - scraper/application_deadline.py
- [[_parse_date()]] - code - scraper/application_deadline.py
- [[_rule_id()]] - code - scraper/application_deadline.py
- [[_valid()]] - code - scraper/application_deadline.py
- [[application_deadline.py]] - code - scraper/application_deadline.py
- [[empty_application_deadline()]] - code - scraper/application_deadline.py
- [[extract_application_deadline()]] - code - scraper/application_deadline.py
- [[test_date_far_from_the_phrase_is_ambiguous()]] - code - tests/test_application_deadline.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/application_deadlinepy
SORT file.name ASC
```

## Connections to other communities
- 8 edges to [[_COMMUNITY_structured_jd.py]]
- 5 edges to [[_COMMUNITY_test_application_deadline.py]]
- 3 edges to [[_COMMUNITY_re]]
- 1 edge to [[_COMMUNITY_textclean.py]]
- 1 edge to [[_COMMUNITY_baseline.py]]
- 1 edge to [[_COMMUNITY_typing]]
- 1 edge to [[_COMMUNITY_linkedin_people.py]]

## Top bridge nodes
- [[application_deadline.py]] - degree 18, connects to 7 communities
- [[extract_application_deadline()]] - degree 13, connects to 2 communities
- [[ApplicationDeadline]] - degree 9, connects to 1 community
- [[_parse_date()]] - degree 5, connects to 1 community
- [[_application_deadline()]] - degree 5, connects to 1 community
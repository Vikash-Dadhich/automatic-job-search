---
type: community
cohesion: 0.17
members: 21
---

# test_application_deadline.py

**Cohesion:** 0.17 - loosely connected
**Members:** 21 nodes

## Members
- [[Conservative application-deadline extraction. Not a ranking input.]] - rationale - tests/test_application_deadline.py
- [[MonkeyPatch_13]] - code
- [[_pad()]] - code - tests/test_application_deadline.py
- [[_read()_1]] - code - tests/test_application_deadline.py
- [[boom()_3]] - code - tests/test_application_deadline.py
- [[test_application_deadline.py]] - code - tests/test_application_deadline.py
- [[test_deadline_failure_does_not_drop_the_rest_of_the_reading()]] - code - tests/test_application_deadline.py
- [[test_deadline_persists_on_the_structured_row()]] - code - tests/test_application_deadline.py
- [[test_empty_and_unusable_descriptions()]] - code - tests/test_application_deadline.py
- [[test_internship_and_graduation_dates_are_not_deadlines()]] - code - tests/test_application_deadline.py
- [[test_interview_deadline_is_not_an_application_deadline()]] - code - tests/test_application_deadline.py
- [[test_invalid_calendar_date_is_ambiguous()]] - code - tests/test_application_deadline.py
- [[test_markdown_split_year_is_kept()]] - code - tests/test_application_deadline.py
- [[test_meet_deadlines_is_not_an_application_deadline()]] - code - tests/test_application_deadline.py
- [[test_missing_year_stays_ambiguous_without_a_date()]] - code - tests/test_application_deadline.py
- [[test_month_name_and_numeric_dates()]] - code - tests/test_application_deadline.py
- [[test_observed_explicit_deadlines()]] - code - tests/test_application_deadline.py
- [[test_older_document_without_the_field_still_loads()]] - code - tests/test_application_deadline.py
- [[test_phrase_without_a_date_is_ambiguous()]] - code - tests/test_application_deadline.py
- [[test_posting_and_revision_dates_are_not_deadlines()]] - code - tests/test_application_deadline.py
- [[test_structured_document_stores_the_deadline_and_ignores_priority()]] - code - tests/test_application_deadline.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/test_application_deadlinepy
SORT file.name ASC
```

## Connections to other communities
- 6 edges to [[_COMMUNITY_test_structured_jd.py]]
- 5 edges to [[_COMMUNITY_application_deadline.py]]
- 4 edges to [[_COMMUNITY_session_scope]]
- 3 edges to [[_COMMUNITY_structured_jd.py]]
- 3 edges to [[_COMMUNITY_textclean.py]]
- 3 edges to [[_COMMUNITY_priority.py]]
- 2 edges to [[_COMMUNITY_Source]]
- 2 edges to [[_COMMUNITY_Job]]
- 2 edges to [[_COMMUNITY_upsert_job]]
- 1 edge to [[_COMMUNITY_pytest]]
- 1 edge to [[_COMMUNITY_db.py]]

## Top bridge nodes
- [[test_application_deadline.py]] - degree 36, connects to 11 communities
- [[test_deadline_persists_on_the_structured_row()]] - degree 9, connects to 6 communities
- [[test_older_document_without_the_field_still_loads()]] - degree 4, connects to 2 communities
- [[test_structured_document_stores_the_deadline_and_ignores_priority()]] - degree 4, connects to 2 communities
- [[_read()_1]] - degree 13, connects to 1 community
---
type: community
cohesion: 0.12
members: 29
---

# test_doctor.py

**Cohesion:** 0.12 - loosely connected
**Members:** 29 nodes

## Members
- [[Any_48]] - code
- [[Capacity]] - document - docs/phase14-application-portfolio.md
- [[Companies we submitted to within the cooldown window. Statuses included…]] - rationale - core/db.py
- [[Decisions]] - document - docs/phase14-application-portfolio.md
- [[First element of a row tuple; scalars pass through.]] - rationale - main.py
- [[Human-readable health report. JSON mode prints the dict instead.]] - rationale - main.py
- [[Offline tests for the doctor health report.]] - rationale - tests/test_doctor.py
- [[Path_53]] - code
- [[Phase 14 application portfolio]] - document - docs/phase14-application-portfolio.md
- [[Pipeline]] - document - docs/phase14-application-portfolio.md
- [[Read-only pipeline health snapshot. No LLM calls.]] - rationale - main.py
- [[Role-family mix]] - document - docs/phase14-application-portfolio.md
- [[What counts as a recent application]] - document - docs/phase14-application-portfolio.md
- [[Who can be allocated]] - document - docs/phase14-application-portfolio.md
- [[_build_doctor_report()]] - code - main.py
- [[_cmd_doctor()]] - code - main.py
- [[_count_jobs()]] - code - main.py
- [[_job()_16]] - code - tests/test_doctor.py
- [[_print_doctor_report()]] - code - main.py
- [[_unwrap()]] - code - main.py
- [[datetime_16]] - code
- [[get_recently_applied_companies()]] - code - core/db.py
- [[phase14-application-portfolio]] - document - docs/phase14-application-portfolio.md
- [[test_doctor.py]] - code - tests/test_doctor.py
- [[test_doctor_cooldown()]] - code - tests/test_doctor.py
- [[test_doctor_empty_db()]] - code - tests/test_doctor.py
- [[test_doctor_outcomes()]] - code - tests/test_doctor.py
- [[test_doctor_vector_gate()]] - code - tests/test_doctor.py
- [[test_doctor_with_jobs()]] - code - tests/test_doctor.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/test_doctorpy
SORT file.name ASC
```

## Connections to other communities
- 13 edges to [[_COMMUNITY_session_scope]]
- 8 edges to [[_COMMUNITY_main.py]]
- 6 edges to [[_COMMUNITY_Tier]]
- 4 edges to [[_COMMUNITY_Job]]
- 4 edges to [[_COMMUNITY_db.py]]
- 3 edges to [[_COMMUNITY_test_application_portfolio.py]]
- 2 edges to [[_COMMUNITY_Source]]
- 2 edges to [[_COMMUNITY_test_company_intelligence.py]]
- 1 edge to [[_COMMUNITY_handlers.py]]
- 1 edge to [[_COMMUNITY_json]]
- 1 edge to [[_COMMUNITY_get_settings]]
- 1 edge to [[_COMMUNITY_LLMClient]]
- 1 edge to [[_COMMUNITY_scorerengine.py]]
- 1 edge to [[_COMMUNITY_AsyncSession]]
- 1 edge to [[_COMMUNITY_pathlib]]

## Top bridge nodes
- [[_build_doctor_report()]] - degree 15, connects to 8 communities
- [[test_doctor.py]] - degree 17, connects to 7 communities
- [[get_recently_applied_companies()]] - degree 13, connects to 7 communities
- [[_job()_16]] - degree 10, connects to 4 communities
- [[test_doctor_outcomes()]] - degree 7, connects to 2 communities
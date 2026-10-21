---
type: community
cohesion: 0.09
members: 40
---

# runner.py

**Cohesion:** 0.09 - loosely connected
**Members:** 40 nodes

## Members
- [[dot-__init__()_10]] - code - automation/runner.py
- [[dot-__init__()_11]] - code - automation/workday.py
- [[dot-__init__()_12]] - code - tests/test_application_portfolio.py
- [[dot-__init__()_13]] - code - tests/test_phase13_shortlist.py
- [[dot-_persist_blocker()]] - code - automation/runner.py
- [[dot-_persist_error()]] - code - automation/runner.py
- [[dot-_persist_success()]] - code - automation/runner.py
- [[dot-_resolve_applicator()]] - code - automation/runner.py
- [[dot-apply()]] - code - automation/workday.py
- [[dot-apply()_1]] - code - tests/test_application_portfolio.py
- [[dot-apply()_2]] - code - tests/test_application_tracker.py
- [[dot-apply()_3]] - code - tests/test_apply_runner.py
- [[dot-apply()_4]] - code - tests/test_pacing.py
- [[dot-apply()_5]] - code - tests/test_phase13_shortlist.py
- [[dot-apply_pending()]] - code - automation/runner.py
- [[Applicator]] - code - automation/workday.py
- [[ApplyResult]] - code - automation/workday.py
- [[ApplyRunner]] - code - automation/runner.py
- [[ApplySummary]] - code - automation/runner.py
- [[Batch runner staged Workday-eligible jobs - pending_review (or…]] - rationale - automation/runner.py
- [[BlockerError_1]] - code - automation/workday.py
- [[Cloudflare  MFA  unknown hard stop — yield to manual review.]] - rationale - automation/workday.py
- [[Drive Workday pre-fill for staged jobs with injectable Applicator.]] - rationale - automation/runner.py
- [[Injectable applicator used by the runner (mockable offline).]] - rationale - automation/workday.py
- [[Outcome of a single Workday pre-fill attempt.]] - rationale - automation/workday.py
- [[Portfolio handed this id. It must still be staged, allocated, and applyable.]] - rationale - automation/runner.py
- [[Protocol_3]] - code
- [[Random]] - code
- [[RuntimeError_1]] - code
- [[Stamp job.tenant from the Workday URL when missing (LinkedIn→Workday case).]] - rationale - automation/runner.py
- [[Workday source OR any source whose URL is a Workday company apply link.]] - rationale - automation/runner.py
- [[_Blocker]] - code - tests/test_application_tracker.py
- [[_Spy]] - code - tests/test_application_portfolio.py
- [[_SpyApplicator]] - code - tests/test_phase13_shortlist.py
- [[_eligible()]] - code - automation/runner.py
- [[_ensure_tenant()]] - code - automation/runner.py
- [[_log_explicit_skip()]] - code - automation/runner.py
- [[_ready_for_explicit_apply()]] - code - automation/runner.py
- [[datetime_3]] - code
- [[runner.py]] - code - automation/runner.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/runnerpy
SORT file.name ASC
```

## Connections to other communities
- 30 edges to [[_COMMUNITY_session_scope]]
- 16 edges to [[_COMMUNITY_Job]]
- 15 edges to [[_COMMUNITY_test_pacing.py]]
- 9 edges to [[_COMMUNITY_re]]
- 8 edges to [[_COMMUNITY_workday.py]]
- 8 edges to [[_COMMUNITY_test_application_portfolio.py]]
- 8 edges to [[_COMMUNITY_test_application_tracker.py]]
- 7 edges to [[_COMMUNITY_test_phase13_shortlist.py]]
- 5 edges to [[_COMMUNITY_test_apply_url.py]]
- 4 edges to [[_COMMUNITY_tracker.py]]
- 3 edges to [[_COMMUNITY_Profile]]
- 3 edges to [[_COMMUNITY_db.py]]
- 2 edges to [[_COMMUNITY_Source]]
- 2 edges to [[_COMMUNITY_suggest.py]]
- 2 edges to [[_COMMUNITY_get_settings]]
- 1 edge to [[_COMMUNITY_WorkdaySubmitter]]
- 1 edge to [[_COMMUNITY_main.py]]
- 1 edge to [[_COMMUNITY_pipeline.py]]
- 1 edge to [[_COMMUNITY_ingest.py]]
- 1 edge to [[_COMMUNITY_scheduler.py]]
- 1 edge to [[_COMMUNITY_test_resume.py]]
- 1 edge to [[_COMMUNITY_profile.py]]
- 1 edge to [[_COMMUNITY_typing]]

## Top bridge nodes
- [[runner.py]] - degree 50, connects to 21 communities
- [[ApplyResult]] - degree 26, connects to 7 communities
- [[BlockerError_1]] - degree 21, connects to 6 communities
- [[_eligible()]] - degree 11, connects to 6 communities
- [[dot-apply_pending()]] - degree 23, connects to 5 communities
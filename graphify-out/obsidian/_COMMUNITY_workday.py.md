---
type: community
cohesion: 0.11
members: 42
---

# workday.py

**Cohesion:** 0.11 - loosely connected
**Members:** 42 nodes

## Members
- [[dot-apply()_6]] - code - automation/workday.py
- [[dot-submit()_1]] - code - bot/submit.py
- [[Advance a multi-step form without submitting the final application.]] - rationale - automation/workday.py
- [[Approve path reopen Workday session and click Submit (only from Telegram).]] - rationale - bot/submit.py
- [[Attach resume via file input (accessibility-friendly when labeled).]] - rationale - automation/workday.py
- [[Clear and type text with per-keystroke jitter (accessibility-friendly).]] - rationale - automation/telemetry.py
- [[Discover fillable controls via accessible names (get_by_label  roles).]] - rationale - automation/workday.py
- [[Human-like delay and typing helpers for browser automation.]] - rationale - automation/telemetry.py
- [[Locator]] - code
- [[Locator_1]] - code
- [[MonkeyPatch_16]] - code
- [[Page_1]] - code
- [[Path_29]] - code
- [[Return (min_ms, max_ms) for between-action pauses.]] - rationale - automation/telemetry.py
- [[Return (min_ms, max_ms) for per-keystroke typing delay.]] - rationale - automation/telemetry.py
- [[Return a short reason if the page looks like a botMFA wall.]] - rationale - automation/workday.py
- [[Sleep a jittered duration; return the seconds slept.]] - rationale - automation/telemetry.py
- [[Tests for human delay  typing bound helpers.]] - rationale - tests/test_telemetry.py
- [[Workday application pre-fill stop at review, never submit.]] - rationale - automation/workday.py
- [[_collect_labeled_fields()]] - code - automation/workday.py
- [[_fill_field()]] - code - automation/workday.py
- [[_upload_resume()]] - code - automation/workday.py
- [[action_delay_bounds()]] - code - automation/telemetry.py
- [[click_by_role()]] - code - automation/workday.py
- [[click_next()]] - code - automation/workday.py
- [[detect_blocker()]] - code - automation/workday.py
- [[human_delay()]] - code - automation/telemetry.py
- [[is_review_page()]] - code - automation/workday.py
- [[playwright_async_api]] - concept
- [[random_2]] - concept
- [[safe_click()]] - code - automation/workday.py
- [[screenshot()]] - code - automation/workday.py
- [[submit.py]] - code - bot/submit.py
- [[telemetry.py]] - code - automation/telemetry.py
- [[test_delay_bounds_from_settings()]] - code - tests/test_telemetry.py
- [[test_delay_bounds_swap_when_inverted()]] - code - tests/test_telemetry.py
- [[test_human_delay_jitter_in_range()]] - code - tests/test_telemetry.py
- [[test_human_delay_respects_explicit_bounds()]] - code - tests/test_telemetry.py
- [[test_telemetry.py]] - code - tests/test_telemetry.py
- [[type_like_human()]] - code - automation/telemetry.py
- [[typing_delay_bounds()]] - code - automation/telemetry.py
- [[workday.py]] - code - automation/workday.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/workdaypy
SORT file.name ASC
```

## Connections to other communities
- 11 edges to [[_COMMUNITY_browser.py]]
- 10 edges to [[_COMMUNITY_re]]
- 8 edges to [[_COMMUNITY_runner.py]]
- 8 edges to [[_COMMUNITY_get_settings]]
- 8 edges to [[_COMMUNITY_typing]]
- 6 edges to [[_COMMUNITY_linkedin_people.py]]
- 5 edges to [[_COMMUNITY_Job]]
- 5 edges to [[_COMMUNITY_WorkdaySubmitter]]
- 4 edges to [[_COMMUNITY_test_application_tracker.py]]
- 4 edges to [[_COMMUNITY_targets.py]]
- 3 edges to [[_COMMUNITY_bot__init__.py]]
- 2 edges to [[_COMMUNITY_asyncio]]
- 2 edges to [[_COMMUNITY_clients.py]]
- 2 edges to [[_COMMUNITY_test_pacing.py]]
- 2 edges to [[_COMMUNITY_db.py]]
- 2 edges to [[_COMMUNITY_ingest.py]]
- 2 edges to [[_COMMUNITY_test_resume.py]]
- 2 edges to [[_COMMUNITY_pathlib]]
- 1 edge to [[_COMMUNITY_Profile]]
- 1 edge to [[_COMMUNITY_suggest.py]]
- 1 edge to [[_COMMUNITY_handlers.py]]
- 1 edge to [[_COMMUNITY_test_phase13_shortlist.py]]
- 1 edge to [[_COMMUNITY_profile.py]]
- 1 edge to [[_COMMUNITY_test_application_portfolio.py]]
- 1 edge to [[_COMMUNITY_session_scope]]
- 1 edge to [[_COMMUNITY_handle_callback]]
- 1 edge to [[_COMMUNITY_pytest]]

## Top bridge nodes
- [[workday.py]] - degree 46, connects to 20 communities
- [[submit.py]] - degree 33, connects to 15 communities
- [[dot-submit()_1]] - degree 14, connects to 7 communities
- [[dot-apply()_6]] - degree 18, connects to 5 communities
- [[telemetry.py]] - degree 15, connects to 4 communities
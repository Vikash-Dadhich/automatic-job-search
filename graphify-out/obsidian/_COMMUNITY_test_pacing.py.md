---
type: community
cohesion: 0.11
members: 49
---

# test_pacing.py

**Cohesion:** 0.11 - loosely connected
**Members:** 49 nodes

## Members
- [[dot-__call__()]] - code - tests/test_pacing.py
- [[dot-__init__()_15]] - code - tests/test_pacing.py
- [[dot-__init__()_16]] - code - tests/test_pacing.py
- [[235959 in ``tz_name``, returned as UTC. Unknown zones fall back to UTC.]] - rationale - automation/pacing.py
- [[AcquireResult]] - code - automation/pacing.py
- [[Count a clean pre-fill. Every ``apply_clean_streak`` successes halves the gap.]] - rationale - automation/pacing.py
- [[Double the gap and black out the rest of the local day.]] - rationale - automation/pacing.py
- [[Gap between apply sessions for one platform. The runner uses ``workday``.]] - rationale - core/db.py
- [[MonkeyPatch_7]] - code
- [[Persisted gap between Workday pre-fills. A captcha or Cloudflare block doubles…]] - rationale - automation/pacing.py
- [[PlatformPacing]] - code - core/db.py
- [[Random_1]] - code
- [[Random baseline gap times the clamped multiplier.]] - rationale - automation/pacing.py
- [[Reserve the next Workday slot. Disabled pacing returns immediately and writes…]] - rationale - automation/pacing.py
- [[SleepFn]] - code
- [[True when a blocker looks like a bot wall, not MFA or a missing session.]] - rationale - automation/pacing.py
- [[Workday apply throttle classifier, AIMD, blackout, and runner wiring.]] - rationale - tests/test_pacing.py
- [[_Applicator]] - code - tests/test_pacing.py
- [[_Sleep]] - code - tests/test_pacing.py
- [[_asyncio_sleep()]] - code - automation/pacing.py
- [[_clamp_multiplier()]] - code - automation/pacing.py
- [[_clock()]] - code - automation/pacing.py
- [[_enable()]] - code - tests/test_pacing.py
- [[_row()_1]] - code - tests/test_pacing.py
- [[_seed()]] - code - tests/test_pacing.py
- [[acquire()]] - code - automation/pacing.py
- [[datetime_4]] - code
- [[end_of_local_day()]] - code - automation/pacing.py
- [[gap_seconds()]] - code - automation/pacing.py
- [[is_pace_blocker()]] - code - automation/pacing.py
- [[note_pace_block()]] - code - automation/pacing.py
- [[note_success()]] - code - automation/pacing.py
- [[pacing.py]] - code - automation/pacing.py
- [[parametrize_1]] - code
- [[test_acquire_after_blackout_keeps_multiplier()]] - code - tests/test_pacing.py
- [[test_acquire_skips_during_blackout()]] - code - tests/test_pacing.py
- [[test_block_doubles_until_cap_and_resets_streak()]] - code - tests/test_pacing.py
- [[test_end_of_los_angeles_day()]] - code - tests/test_pacing.py
- [[test_gap_treats_max_below_min_as_min()]] - code - tests/test_pacing.py
- [[test_pace_hints_ignore_mfa_and_empty()]] - code - tests/test_pacing.py
- [[test_pace_hints_match()]] - code - tests/test_pacing.py
- [[test_pacing.py]] - code - tests/test_pacing.py
- [[test_runner_blackout_leaves_second_job_staged()]] - code - tests/test_pacing.py
- [[test_runner_mfa_does_not_black_out()]] - code - tests/test_pacing.py
- [[test_runner_pacing_disabled_does_not_sleep()]] - code - tests/test_pacing.py
- [[test_runner_waits_then_both_pending()]] - code - tests/test_pacing.py
- [[test_successes_at_multiplier_one_stay_at_one()]] - code - tests/test_pacing.py
- [[test_three_successes_halve_multiplier()]] - code - tests/test_pacing.py
- [[test_unknown_timezone_uses_utc()]] - code - tests/test_pacing.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/test_pacingpy
SORT file.name ASC
```

## Connections to other communities
- 18 edges to [[_COMMUNITY_session_scope]]
- 15 edges to [[_COMMUNITY_runner.py]]
- 9 edges to [[_COMMUNITY_test_monitoring.py]]
- 8 edges to [[_COMMUNITY_db.py]]
- 7 edges to [[_COMMUNITY_get_settings]]
- 3 edges to [[_COMMUNITY_Job]]
- 2 edges to [[_COMMUNITY_Source]]
- 2 edges to [[_COMMUNITY_upsert_job]]
- 2 edges to [[_COMMUNITY_scheduler.py]]
- 2 edges to [[_COMMUNITY_typing]]
- 2 edges to [[_COMMUNITY_workday.py]]
- 1 edge to [[_COMMUNITY_AsyncSession]]
- 1 edge to [[_COMMUNITY_asyncio]]
- 1 edge to [[_COMMUNITY_ingest.py]]
- 1 edge to [[_COMMUNITY_test_resume.py]]
- 1 edge to [[_COMMUNITY_pytest]]
- 1 edge to [[_COMMUNITY_baseline.py]]

## Top bridge nodes
- [[test_pacing.py]] - degree 47, connects to 12 communities
- [[pacing.py]] - degree 28, connects to 10 communities
- [[acquire()]] - degree 18, connects to 5 communities
- [[note_pace_block()]] - degree 17, connects to 4 communities
- [[note_success()]] - degree 14, connects to 4 communities
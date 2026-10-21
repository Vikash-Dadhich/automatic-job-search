---
source_file: "tests/test_pacing.py"
type: "code"
community: "test_pacing.py"
location: "L1"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/test_pacingpy
---

# test_pacing.py

## Connections
- [[ApplyResult]] - `imports` [EXTRACTED]
- [[BlockerError_1]] - `imports` [EXTRACTED]
- [[Job]] - `imports` [EXTRACTED]
- [[PlatformPacing]] - `imports` [EXTRACTED]
- [[Source]] - `imports` [EXTRACTED]
- [[Status]] - `imports` [EXTRACTED]
- [[Workday apply throttle classifier, AIMD, blackout, and runner wiring.]] - `rationale_for` [EXTRACTED]
- [[_Applicator]] - `contains` [EXTRACTED]
- [[_Sleep]] - `contains` [EXTRACTED]
- [[_as_utc()_1]] - `imports` [EXTRACTED]
- [[_enable()]] - `contains` [EXTRACTED]
- [[_row()_1]] - `contains` [EXTRACTED]
- [[_seed()]] - `contains` [EXTRACTED]
- [[acquire()]] - `imports` [EXTRACTED]
- [[apply_pending()]] - `imports` [EXTRACTED]
- [[datetime_17]] - `imports_from` [EXTRACTED]
- [[db.py]] - `imports_from` [EXTRACTED]
- [[end_of_local_day()]] - `imports` [EXTRACTED]
- [[gap_seconds()]] - `imports` [EXTRACTED]
- [[get_job_by_id()]] - `imports` [EXTRACTED]
- [[get_settings()]] - `imports` [EXTRACTED]
- [[is_pace_blocker()]] - `imports` [EXTRACTED]
- [[note_pace_block()]] - `imports` [EXTRACTED]
- [[note_success()]] - `imports` [EXTRACTED]
- [[pacing.py]] - `imports_from` [EXTRACTED]
- [[pytest]] - `imports` [EXTRACTED]
- [[random_2]] - `imports` [EXTRACTED]
- [[runner.py]] - `imports_from` [EXTRACTED]
- [[session_scope()]] - `imports` [EXTRACTED]
- [[settings.py]] - `imports_from` [EXTRACTED]
- [[sqlmodel_2]] - `imports_from` [EXTRACTED]
- [[test_acquire_after_blackout_keeps_multiplier()]] - `contains` [EXTRACTED]
- [[test_acquire_skips_during_blackout()]] - `contains` [EXTRACTED]
- [[test_block_doubles_until_cap_and_resets_streak()]] - `contains` [EXTRACTED]
- [[test_end_of_los_angeles_day()]] - `contains` [EXTRACTED]
- [[test_gap_treats_max_below_min_as_min()]] - `contains` [EXTRACTED]
- [[test_pace_hints_ignore_mfa_and_empty()]] - `contains` [EXTRACTED]
- [[test_pace_hints_match()]] - `contains` [EXTRACTED]
- [[test_runner_blackout_leaves_second_job_staged()]] - `contains` [EXTRACTED]
- [[test_runner_mfa_does_not_black_out()]] - `contains` [EXTRACTED]
- [[test_runner_pacing_disabled_does_not_sleep()]] - `contains` [EXTRACTED]
- [[test_runner_waits_then_both_pending()]] - `contains` [EXTRACTED]
- [[test_successes_at_multiplier_one_stay_at_one()]] - `contains` [EXTRACTED]
- [[test_three_successes_halve_multiplier()]] - `contains` [EXTRACTED]
- [[test_unknown_timezone_uses_utc()]] - `contains` [EXTRACTED]
- [[upsert_job()]] - `imports` [EXTRACTED]
- [[workday.py]] - `imports_from` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/test_pacingpy
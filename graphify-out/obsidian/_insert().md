---
source_file: "tests/test_telegram_output.py"
type: "code"
community: "send_prep_pack"
location: "L32"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/send_prep_pack
---

# _insert()

## Connections
- [[Job]] - `uses` [INFERRED]
- [[session_scope()]] - `calls` [EXTRACTED]
- [[test_card_shows_stored_fields_without_changing_them()]] - `calls` [EXTRACTED]
- [[test_empty_shortlist_sends_no_cards()]] - `calls` [EXTRACTED]
- [[test_order_follows_shortlist_rank_not_fit()]] - `calls` [EXTRACTED]
- [[test_output_matches_the_canonical_shortlist()]] - `calls` [EXTRACTED]
- [[test_production_send_does_not_call_legacy_select_shortlist()]] - `calls` [EXTRACTED]
- [[test_selected_job_below_old_thresholds_is_shown()]] - `calls` [EXTRACTED]
- [[test_telegram_output.py]] - `contains` [EXTRACTED]
- [[test_three_selected_jobs_are_not_filled_out()]] - `calls` [EXTRACTED]
- [[upsert_job()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/send_prep_pack
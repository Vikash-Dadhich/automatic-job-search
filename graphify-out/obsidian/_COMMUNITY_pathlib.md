---
type: community
cohesion: 0.09
members: 40
---

# pathlib

**Cohesion:** 0.09 - loosely connected
**Members:** 40 nodes

## Members
- [[dot-__init__()_18]] - code - tests/test_telegram.py
- [[dot-complete()_8]] - code - tests/test_prep_delivery.py
- [[dot-post()_3]] - code - tests/test_telegram.py
- [[Any_22]] - code
- [[Any_23]] - code
- [[BaseException]] - code
- [[Decode callback_data into (action, job_id).]] - rationale - bot/telegram.py
- [[Encode inline-keyboard callback_data v1actionjob_id (=64 bytes).]] - rationale - bot/telegram.py
- [[FakeClient_1]] - code - tests/test_prep_delivery.py
- [[FakeTransport_1]] - code - tests/test_telegram.py
- [[MonkeyPatch_11]] - code
- [[Offline tests for Telegram codec + client (FakeTransport).]] - rationale - tests/test_telegram.py
- [[Offline tests for prep-pack Telegram delivery + dedupe.]] - rationale - tests/test_prep_delivery.py
- [[Offline tests for the long-poll update processor.]] - rationale - tests/test_poller.py
- [[Path_21]] - code
- [[Path_22]] - code
- [[Path_23]] - code
- [[Retry transport errors and HTTP 5xx; never retry 4xx client errors.]] - rationale - bot/telegram.py
- [[Telegram Bot API client behind a mockable transport protocol.]] - rationale - bot/telegram.py
- [[_should_retry_telegram()]] - code - bot/telegram.py
- [[decode_callback()]] - code - bot/telegram.py
- [[encode_callback()]] - code - bot/telegram.py
- [[is_outcome_callback()]] - code - bot/telegram.py
- [[pathlib]] - concept
- [[telegram.py]] - code - bot/telegram.py
- [[tenacity]] - concept
- [[test_answer_callback()]] - code - tests/test_telegram.py
- [[test_chat_id_property()]] - code - tests/test_telegram.py
- [[test_decode_invalid()]] - code - tests/test_telegram.py
- [[test_encode_decode_roundtrip()]] - code - tests/test_telegram.py
- [[test_get_updates_extends_http_timeout()]] - code - tests/test_telegram.py
- [[test_poller.py]] - code - tests/test_poller.py
- [[test_prep_delivery.py]] - code - tests/test_prep_delivery.py
- [[test_process_updates_routes_callback()]] - code - tests/test_poller.py
- [[test_send_document_builds_payload()]] - code - tests/test_telegram.py
- [[test_send_photo_builds_payload()]] - code - tests/test_telegram.py
- [[test_send_prep_pack_empty()]] - code - tests/test_prep_delivery.py
- [[test_send_prep_pack_marks_jobs()]] - code - tests/test_prep_delivery.py
- [[test_should_retry_telegram()]] - code - tests/test_telegram.py
- [[test_telegram.py]] - code - tests/test_telegram.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/pathlib
SORT file.name ASC
```

## Connections to other communities
- 26 edges to [[_COMMUNITY_handle_callback]]
- 17 edges to [[_COMMUNITY_handlers.py]]
- 14 edges to [[_COMMUNITY_TelegramClient]]
- 14 edges to [[_COMMUNITY_send_prep_pack]]
- 13 edges to [[_COMMUNITY_session_scope]]
- 13 edges to [[_COMMUNITY_profile.py]]
- 12 edges to [[_COMMUNITY_review.py]]
- 11 edges to [[_COMMUNITY_Job]]
- 10 edges to [[_COMMUNITY_test_application_tracker.py]]
- 10 edges to [[_COMMUNITY_bot__init__.py]]
- 9 edges to [[_COMMUNITY_alerts.py]]
- 7 edges to [[_COMMUNITY_typing]]
- 6 edges to [[_COMMUNITY_test_career_intelligence.py]]
- 6 edges to [[_COMMUNITY_Source]]
- 5 edges to [[_COMMUNITY_suggest.py]]
- 5 edges to [[_COMMUNITY_pytest]]
- 5 edges to [[_COMMUNITY_get_settings]]
- 5 edges to [[_COMMUNITY_db.py]]
- 4 edges to [[_COMMUNITY_upsert_job]]
- 3 edges to [[_COMMUNITY_browser.py]]
- 2 edges to [[_COMMUNITY_Tier]]
- 2 edges to [[_COMMUNITY_asyncio]]
- 2 edges to [[_COMMUNITY_linkedin_people.py]]
- 2 edges to [[_COMMUNITY_discovery_recall.py]]
- 2 edges to [[_COMMUNITY_ingest.py]]
- 2 edges to [[_COMMUNITY_test_phase13_shortlist.py]]
- 2 edges to [[_COMMUNITY_json]]
- 2 edges to [[_COMMUNITY_workday.py]]
- 2 edges to [[_COMMUNITY_test_application_portfolio.py]]
- 2 edges to [[_COMMUNITY_vault.py]]
- 2 edges to [[_COMMUNITY_test_discovery.py]]
- 1 edge to [[_COMMUNITY_Profile]]
- 1 edge to [[_COMMUNITY_calibration.py]]
- 1 edge to [[_COMMUNITY_test_calibration.py]]
- 1 edge to [[_COMMUNITY_workday_rest.py]]
- 1 edge to [[_COMMUNITY_conftest.py]]
- 1 edge to [[_COMMUNITY_test_workday_locators.py]]
- 1 edge to [[_COMMUNITY_textclean.py]]
- 1 edge to [[_COMMUNITY_test_resume.py]]
- 1 edge to [[_COMMUNITY_targets.py]]
- 1 edge to [[_COMMUNITY_diff.py]]
- 1 edge to [[_COMMUNITY_test_company_intelligence.py]]
- 1 edge to [[_COMMUNITY_test_eligibility.py]]
- 1 edge to [[_COMMUNITY_test_phase0_baseline.py]]
- 1 edge to [[_COMMUNITY_HttpCompanyIntelProvider]]
- 1 edge to [[_COMMUNITY_skills.py]]
- 1 edge to [[_COMMUNITY_builder.py]]
- 1 edge to [[_COMMUNITY_test_feedback.py]]
- 1 edge to [[_COMMUNITY_test_priority.py]]
- 1 edge to [[_COMMUNITY_test_company_intelligence_v2.py]]
- 1 edge to [[_COMMUNITY_priority.py]]
- 1 edge to [[_COMMUNITY_test_vector_recovery.py]]
- 1 edge to [[_COMMUNITY_test_monitoring.py]]
- 1 edge to [[_COMMUNITY_test_cover_letter.py]]
- 1 edge to [[_COMMUNITY_migrate_to_neon.py]]
- 1 edge to [[_COMMUNITY_feedback.py]]
- 1 edge to [[_COMMUNITY_test_role_classify.py]]
- 1 edge to [[_COMMUNITY_test_fit.py]]
- 1 edge to [[_COMMUNITY_test_doctor.py]]
- 1 edge to [[_COMMUNITY_test_scorer.py]]
- 1 edge to [[_COMMUNITY_scorerengine.py]]
- 1 edge to [[_COMMUNITY_test_recruiting_universe.py]]

## Top bridge nodes
- [[pathlib]] - degree 76, connects to 53 communities
- [[telegram.py]] - degree 46, connects to 17 communities
- [[test_prep_delivery.py]] - degree 32, connects to 13 communities
- [[test_telegram.py]] - degree 29, connects to 11 communities
- [[test_poller.py]] - degree 24, connects to 10 communities
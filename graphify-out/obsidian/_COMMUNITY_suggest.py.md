---
type: community
cohesion: 0.08
members: 52
---

# suggest.py

**Cohesion:** 0.08 - loosely connected
**Members:** 52 nodes

## Members
- [[dot-__init__()_7]] - code - tests/test_suggest.py
- [[dot-_resolve_profile()]] - code - scorer/engine.py
- [[dot-post()]] - code - tests/test_suggest.py
- [[Any_14]] - code
- [[Any_15]] - code
- [[Clear cache and reload (useful after editing profile.yaml).]] - rationale - config/profile.py
- [[Create skill suggestions for the jobs this run placed in review. Leftover…]] - rationale - orchestrator/pipeline.py
- [[Decode suggestion callback_data into (action, suggestion_id).]] - rationale - bot/telegram.py
- [[Encode suggestion callback_data s1actionsuggestion_id (=64 bytes).]] - rationale - bot/telegram.py
- [[Extract JD skills, diff vs role baseline, persist SkillSuggestion rows.]] - rationale - resume/diff.py
- [[FakeTransport]] - code - tests/test_suggest.py
- [[Generate a Typst-tailored resume for one job and persist resume_path.]] - rationale - resume/compiler.py
- [[Handle incoming text messages — specifically force_reply captures for pending…]] - rationale - bot/handlers.py
- [[If all suggestions for a job are decided, recompile resume with approvals.…]] - rationale - bot/suggest.py
- [[Load and validate profile.yaml. Cached after first successful load.]] - rationale - config/profile.py
- [[Mark a suggestion approvedrejectededited and maybe recompile.]] - rationale - bot/suggest.py
- [[Per-JD skill addition proposed against a role baseline (Telegram approval).]] - rationale - core/db.py
- [[Send Telegram cards for jobs with unsent pending suggestions.]] - rationale - bot/suggest.py
- [[SkillSuggestion]] - code - core/db.py
- [[StrEnum_2]] - code
- [[SuggestAction]] - code - bot/telegram.py
- [[SuggestSummary]] - code - bot/suggest.py
- [[SuggestionStatus]] - code - core/db.py
- [[Telegram delivery and apply path for skill suggestions.]] - rationale - bot/suggest.py
- [[Tests for Telegram skill-suggestion callbacks and apply-on-approve.]] - rationale - tests/test_suggest.py
- [[_cmd_tailor_resume()]] - code - main.py
- [[_format_card()]] - code - bot/suggest.py
- [[_generate_suggestions_stage()]] - code - orchestrator/pipeline.py
- [[_suggestion_keyboard()]] - code - bot/suggest.py
- [[apply_decided_suggestions()]] - code - bot/suggest.py
- [[asyncio_2]] - code
- [[asyncio_3]] - code
- [[compile_for_job()]] - code - resume/compiler.py
- [[copy]] - concept
- [[decide_suggestion()]] - code - bot/suggest.py
- [[decode_suggest_callback()]] - code - bot/telegram.py
- [[encode_suggest_callback()]] - code - bot/telegram.py
- [[generate_suggestions_for_job()]] - code - resume/diff.py
- [[get_pending_suggestions_for_job()]] - code - core/db.py
- [[get_role_baseline_by_id()]] - code - core/db.py
- [[get_skill_suggestion_by_id()]] - code - core/db.py
- [[get_suggestions_for_job()]] - code - core/db.py
- [[handle_message()]] - code - bot/handlers.py
- [[load_profile()]] - code - config/profile.py
- [[reload_profile()]] - code - config/profile.py
- [[send_pending_suggestions()]] - code - bot/suggest.py
- [[suggest.py]] - code - bot/suggest.py
- [[test_generate_suggestions_for_job()]] - code - tests/test_diff.py
- [[test_send_and_decide_suggestions()]] - code - tests/test_suggest.py
- [[test_suggest.py]] - code - tests/test_suggest.py
- [[test_suggest_callback_rejects_review_namespace()]] - code - tests/test_suggest.py
- [[test_suggest_callback_roundtrip()]] - code - tests/test_suggest.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/suggestpy
SORT file.name ASC
```

## Connections to other communities
- 34 edges to [[_COMMUNITY_diff.py]]
- 23 edges to [[_COMMUNITY_session_scope]]
- 19 edges to [[_COMMUNITY_get_settings]]
- 16 edges to [[_COMMUNITY_db.py]]
- 12 edges to [[_COMMUNITY_profile.py]]
- 11 edges to [[_COMMUNITY_handlers.py]]
- 11 edges to [[_COMMUNITY_main.py]]
- 8 edges to [[_COMMUNITY_bot__init__.py]]
- 7 edges to [[_COMMUNITY_AsyncSession]]
- 7 edges to [[_COMMUNITY_baseline.py]]
- 6 edges to [[_COMMUNITY_Profile]]
- 6 edges to [[_COMMUNITY_Job]]
- 6 edges to [[_COMMUNITY_pipeline.py]]
- 5 edges to [[_COMMUNITY_pathlib]]
- 5 edges to [[_COMMUNITY_TelegramClient]]
- 4 edges to [[_COMMUNITY_Source]]
- 4 edges to [[_COMMUNITY_test_resume.py]]
- 4 edges to [[_COMMUNITY_typing]]
- 3 edges to [[_COMMUNITY_LLMClient]]
- 3 edges to [[_COMMUNITY_pytest]]
- 3 edges to [[_COMMUNITY_re]]
- 3 edges to [[_COMMUNITY_upsert_job]]
- 2 edges to [[_COMMUNITY_runner.py]]
- 2 edges to [[_COMMUNITY_benchmarkengine.py]]
- 2 edges to [[_COMMUNITY_json]]
- 2 edges to [[_COMMUNITY_builder.py]]
- 2 edges to [[_COMMUNITY_scorerengine.py]]
- 2 edges to [[_COMMUNITY_test_scorer.py]]
- 2 edges to [[_COMMUNITY_targets.py]]
- 2 edges to [[_COMMUNITY_ingest.py]]
- 2 edges to [[_COMMUNITY_conftest.py]]
- 1 edge to [[_COMMUNITY_FakeClient]]
- 1 edge to [[_COMMUNITY_migrate_to_neon.py]]
- 1 edge to [[_COMMUNITY_tracker.py]]
- 1 edge to [[_COMMUNITY_handle_callback]]
- 1 edge to [[_COMMUNITY_telegram_webhook]]
- 1 edge to [[_COMMUNITY_send_prep_pack]]
- 1 edge to [[_COMMUNITY_workday.py]]
- 1 edge to [[_COMMUNITY_Tier]]
- 1 edge to [[_COMMUNITY_skills.py]]

## Top bridge nodes
- [[load_profile()]] - degree 42, connects to 23 communities
- [[suggest.py]] - degree 42, connects to 16 communities
- [[test_suggest.py]] - degree 40, connects to 14 communities
- [[generate_suggestions_for_job()]] - degree 27, connects to 9 communities
- [[test_generate_suggestions_for_job()]] - degree 13, connects to 8 communities
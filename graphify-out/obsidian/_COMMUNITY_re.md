---
type: community
cohesion: 0.07
members: 56
---

# re

**Cohesion:** 0.07 - loosely connected
**Members:** 56 nodes

## Members
- [[dot-__init__()_20]] - code - automation/answers.py
- [[dot-__init__()_21]] - code - automation/workday.py
- [[dot-__init__()_22]] - code - tests/test_answers.py
- [[dot-_resolve_answers()]] - code - automation/workday.py
- [[dot-_resolve_profile()_1]] - code - automation/workday.py
- [[dot-_unanswered_source()]] - code - automation/answers.py
- [[dot-complete()_10]] - code - tests/test_answers.py
- [[dot-resolve()]] - code - automation/answers.py
- [[dot-resolve_many()]] - code - automation/answers.py
- [[dot-to_dict()_1]] - code - automation/answers.py
- [[AnswerResolver]] - code - automation/answers.py
- [[AnswerSource]] - code - automation/answers.py
- [[Any_31]] - code
- [[Any_32]] - code
- [[FakeAnswerClient]] - code - tests/test_answers.py
- [[Heuristic long-form  why  cover-letter style questions.]] - rationale - automation/answers.py
- [[Map Workday form questions to profile facts or LLM-drafted answers.]] - rationale - automation/answers.py
- [[Most recent degree, not just the first listed entry.]] - rationale - automation/answers.py
- [[Name the channel the posting actually came from.]] - rationale - automation/answers.py
- [[Offline tests for AnswerResolver (deterministic + mock LLM).]] - rationale - tests/test_answers.py
- [[Persistable JSON blob for Job.application_answers.]] - rationale - automation/answers.py
- [[Pre-fill a Workday application and pause at the review screen.]] - rationale - automation/workday.py
- [[Resolve form labels to answers; LLM only for open-ended unknowns.]] - rationale - automation/answers.py
- [[Resolve questions concurrently, preserving input order.]] - rationale - automation/answers.py
- [[ResolvedAnswer]] - code - automation/answers.py
- [[Return a profile-backed answer when the question matches a known pattern.]] - rationale - automation/answers.py
- [[StrEnum_4]] - code
- [[True for fields that commonly gate submission and cannot be guessed safely.]] - rationale - automation/answers.py
- [[True if any needle appears as a whole phrase (word-boundary safe).]] - rationale - automation/answers.py
- [[Workday application automation (Step 5).]] - rationale - automation/__init__.py
- [[WorkdayApplicator]] - code - automation/workday.py
- [[_discovery_channel()]] - code - automation/answers.py
- [[_latest_education()]] - code - automation/answers.py
- [[_matches()]] - code - automation/answers.py
- [[_norm()_1]] - code - automation/answers.py
- [[_split_name()]] - code - automation/answers.py
- [[answers.py]] - code - automation/answers.py
- [[answers_to_payload()]] - code - automation/answers.py
- [[automation__init__.py]] - code - automation/__init__.py
- [[is_open_ended()]] - code - automation/answers.py
- [[needs_human_review()]] - code - automation/answers.py
- [[one()]] - code - automation/answers.py
- [[re]] - concept
- [[resolve_deterministic()]] - code - automation/answers.py
- [[test_answers.py]] - code - tests/test_answers.py
- [[test_answers_to_payload()]] - code - tests/test_answers.py
- [[test_cover_letter_field_uses_stored_text()]] - code - tests/test_answers.py
- [[test_deterministic_eeo_decline()]] - code - tests/test_answers.py
- [[test_deterministic_identity_and_auth()]] - code - tests/test_answers.py
- [[test_deterministic_source_and_unknown()]] - code - tests/test_answers.py
- [[test_is_open_ended()]] - code - tests/test_answers.py
- [[test_load_profile_fixture()]] - code - tests/test_answers.py
- [[test_resolver_banned_word_retry()]] - code - tests/test_answers.py
- [[test_resolver_blank_for_unknown_closed()]] - code - tests/test_answers.py
- [[test_resolver_deterministic_path()]] - code - tests/test_answers.py
- [[test_resolver_open_ended_llm()]] - code - tests/test_answers.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/re
SORT file.name ASC
```

## Connections to other communities
- 11 edges to [[_COMMUNITY_Job]]
- 10 edges to [[_COMMUNITY_workday.py]]
- 9 edges to [[_COMMUNITY_Profile]]
- 9 edges to [[_COMMUNITY_runner.py]]
- 9 edges to [[_COMMUNITY_test_scorer.py]]
- 6 edges to [[_COMMUNITY_Source]]
- 5 edges to [[_COMMUNITY_builder.py]]
- 4 edges to [[_COMMUNITY_LLMClient]]
- 4 edges to [[_COMMUNITY_role_classify.py]]
- 4 edges to [[_COMMUNITY_discovery_recall.py]]
- 4 edges to [[_COMMUNITY_eligibility.py]]
- 4 edges to [[_COMMUNITY_get_settings]]
- 3 edges to [[_COMMUNITY_filters.py]]
- 3 edges to [[_COMMUNITY_textclean.py]]
- 3 edges to [[_COMMUNITY_suggest.py]]
- 3 edges to [[_COMMUNITY_application_deadline.py]]
- 3 edges to [[_COMMUNITY_skills.py]]
- 3 edges to [[_COMMUNITY_clients.py]]
- 3 edges to [[_COMMUNITY_baseline.py]]
- 3 edges to [[_COMMUNITY_test_fit.py]]
- 3 edges to [[_COMMUNITY_profile.py]]
- 3 edges to [[_COMMUNITY_typing]]
- 2 edges to [[_COMMUNITY_linkedin_people.py]]
- 2 edges to [[_COMMUNITY_workday_rest.py]]
- 2 edges to [[_COMMUNITY_browser.py]]
- 2 edges to [[_COMMUNITY_diff.py]]
- 2 edges to [[_COMMUNITY_test_vector_recovery.py]]
- 2 edges to [[_COMMUNITY_test_resume.py]]
- 2 edges to [[_COMMUNITY_db.py]]
- 1 edge to [[_COMMUNITY_WorkdaySubmitter]]
- 1 edge to [[_COMMUNITY_session_scope]]
- 1 edge to [[_COMMUNITY_structured_jd.py]]
- 1 edge to [[_COMMUNITY_targets.py]]
- 1 edge to [[_COMMUNITY_scheduler.py]]
- 1 edge to [[_COMMUNITY_company_intelligence.py]]
- 1 edge to [[_COMMUNITY_ingest.py]]
- 1 edge to [[_COMMUNITY_asyncio]]
- 1 edge to [[_COMMUNITY_test_career_intelligence.py]]
- 1 edge to [[_COMMUNITY_prerank.py]]
- 1 edge to [[_COMMUNITY_scorerengine.py]]

## Top bridge nodes
- [[re]] - degree 55, connects to 26 communities
- [[answers.py]] - degree 38, connects to 16 communities
- [[test_answers.py]] - degree 26, connects to 6 communities
- [[AnswerResolver]] - degree 24, connects to 6 communities
- [[WorkdayApplicator]] - degree 15, connects to 5 communities
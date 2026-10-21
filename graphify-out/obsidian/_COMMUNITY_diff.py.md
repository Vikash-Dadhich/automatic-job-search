---
type: community
cohesion: 0.11
members: 44
---

# diff.py

**Cohesion:** 0.11 - loosely connected
**Members:** 44 nodes

## Members
- [[dot-clamp_importance()]] - code - resume/skills.py
- [[dot-clean_name()]] - code - resume/skills.py
- [[dot-coerce_category()]] - code - resume/skills.py
- [[Any_19]] - code
- [[Async version of diff_against_baseline with optional LLM bullet weaving.]] - rationale - resume/diff.py
- [[Deterministic proposed wording for skill placement. For experience bullets we…]] - rationale - resume/diff.py
- [[JdSkill]] - code - resume/skills.py
- [[LLM-woven experience bullet that naturally incorporates the missing skill.…]] - rationale - resume/diff.py
- [[LLMClient_2]] - code
- [[Merge approvededited suggestions into resume_data (skills section).]] - rationale - resume/diff.py
- [[One skill demanded by a single job description.]] - rationale - resume/skills.py
- [[Path_16]] - code
- [[Per-JD skill diff against a role baseline + suggestion persistence.]] - rationale - resume/diff.py
- [[Per-role baseline resume built from aggregating ~15-20 JDs.]] - rationale - core/db.py
- [[Return suggestion dicts for JD skills missing from the baseline resume.]] - rationale - resume/diff.py
- [[RoleBaseline]] - code - core/db.py
- [[Scoring and writing always go through OpenAI.]] - rationale - scorer/clients.py
- [[SkillPlacement]] - code - core/db.py
- [[SkillProvenance]] - code - core/db.py
- [[Tests for per-JD skill diff and suggestion generation.]] - rationale - tests/test_diff.py
- [[Write JSON + Markdown tailoring report under the job resume folder.]] - rationale - resume/diff.py
- [[_baseline_skill_keys()]] - code - resume/diff.py
- [[_load_role_client()]] - code - scraper/ingest.py
- [[_norm()]] - code - resume/diff.py
- [[_profile_skill_keys()]] - code - resume/diff.py
- [[_row()]] - code - resume/diff.py
- [[_skill_covered()]] - code - resume/diff.py
- [[apply_approved_suggestions_to_resume_data()]] - code - resume/diff.py
- [[build_llm_client()]] - code - scorer/clients.py
- [[classify_provenance()]] - code - resume/diff.py
- [[client()]] - code - tests/test_webhook.py
- [[diff.py]] - code - resume/diff.py
- [[diff_against_baseline()]] - code - resume/diff.py
- [[diff_against_baseline_async()]] - code - resume/diff.py
- [[draft_proposed_text()]] - code - resume/diff.py
- [[draft_proposed_text_llm()]] - code - resume/diff.py
- [[field_validator_1]] - code
- [[fixture_1]] - code
- [[grounded if the skill is in profile.skills or provable from bullets.]] - rationale - resume/diff.py
- [[test_apply_approved_suggestions_to_resume_data()]] - code - tests/test_diff.py
- [[test_classify_provenance_grounded_vs_inferred()]] - code - tests/test_diff.py
- [[test_diff.py]] - code - tests/test_diff.py
- [[test_diff_against_baseline_only_missing()]] - code - tests/test_diff.py
- [[write_tailoring_report()]] - code - resume/diff.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/diffpy
SORT file.name ASC
```

## Connections to other communities
- 34 edges to [[_COMMUNITY_suggest.py]]
- 16 edges to [[_COMMUNITY_skills.py]]
- 13 edges to [[_COMMUNITY_profile.py]]
- 12 edges to [[_COMMUNITY_baseline.py]]
- 8 edges to [[_COMMUNITY_Profile]]
- 7 edges to [[_COMMUNITY_benchmarkengine.py]]
- 6 edges to [[_COMMUNITY_db.py]]
- 5 edges to [[_COMMUNITY_test_llm_provider.py]]
- 5 edges to [[_COMMUNITY_typing]]
- 4 edges to [[_COMMUNITY_session_scope]]
- 4 edges to [[_COMMUNITY_LLMClient]]
- 4 edges to [[_COMMUNITY_get_settings]]
- 3 edges to [[_COMMUNITY_Job]]
- 3 edges to [[_COMMUNITY_ingest.py]]
- 2 edges to [[_COMMUNITY_tracker.py]]
- 2 edges to [[_COMMUNITY_Source]]
- 2 edges to [[_COMMUNITY_scorerengine.py]]
- 2 edges to [[_COMMUNITY_re]]
- 2 edges to [[_COMMUNITY_json]]
- 2 edges to [[_COMMUNITY_clients.py]]
- 1 edge to [[_COMMUNITY_FakeClient]]
- 1 edge to [[_COMMUNITY_migrate_to_neon.py]]
- 1 edge to [[_COMMUNITY_AsyncSession]]
- 1 edge to [[_COMMUNITY_workday_rest.py]]
- 1 edge to [[_COMMUNITY_main.py]]
- 1 edge to [[_COMMUNITY_builder.py]]
- 1 edge to [[_COMMUNITY_Settings]]
- 1 edge to [[_COMMUNITY_conftest.py]]
- 1 edge to [[_COMMUNITY_test_scorer.py]]
- 1 edge to [[_COMMUNITY_upsert_job]]
- 1 edge to [[_COMMUNITY_pipeline.py]]
- 1 edge to [[_COMMUNITY_pathlib]]
- 1 edge to [[_COMMUNITY_pytest]]

## Top bridge nodes
- [[diff.py]] - degree 45, connects to 15 communities
- [[test_diff.py]] - degree 39, connects to 14 communities
- [[build_llm_client()]] - degree 23, connects to 11 communities
- [[RoleBaseline]] - degree 21, connects to 5 communities
- [[JdSkill]] - degree 33, connects to 4 communities
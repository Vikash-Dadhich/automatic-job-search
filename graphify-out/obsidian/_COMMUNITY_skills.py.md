---
type: community
cohesion: 0.08
members: 47
---

# skills.py

**Cohesion:** 0.08 - loosely connected
**Members:** 47 nodes

## Members
- [[dot-__init__()_19]] - code - tests/test_skills.py
- [[dot-complete()_9]] - code - tests/test_skills.py
- [[dot-weight()]] - code - resume/skills.py
- [[A skill summarized across many JDs for one target role.]] - rationale - resume/skills.py
- [[Aggregated skill demand for a role, used to build the baseline resume.]] - rationale - resume/skills.py
- [[AggregatedSkill]] - code - resume/skills.py
- [[Any_30]] - code
- [[BaseModel_6]] - code
- [[Close a truncated JSON array so partial skill lists still parse.]] - rationale - resume/skills.py
- [[Compact job description for scoring titlecompanylocation + cleaned JD.]] - rationale - core/token_optimizer.py
- [[Extract per-JD skills via LLM, falling back to the deterministic ranker.]] - rationale - resume/skills.py
- [[FakeSkillClient]] - code - tests/test_skills.py
- [[JD skill extraction and cross-JD aggregation for the two-tier resume flow. Per-…]] - rationale - resume/skills.py
- [[Offline fallback rank repeated, non-filler terms from the posting.]] - rationale - resume/skills.py
- [[Parse a JSON skill array from model output; tolerant of fences and dupes.]] - rationale - resume/skills.py
- [[RoleSkillProfile]] - code - resume/skills.py
- [[Roll per-JD skills into prevalence-weighted role demand.]] - rationale - resume/skills.py
- [[SkillCategory]] - code - resume/skills.py
- [[Sponsorship  YOE lines live at the bottom of a JD and must survive.]] - rationale - tests/test_scorer.py
- [[StrEnum_3]] - code
- [[Tests for JD skill extraction and multi-JD aggregation.]] - rationale - tests/test_skills.py
- [[_categorize()]] - code - resume/skills.py
- [[_job()_7]] - code - tests/test_skills.py
- [[_repair_truncated_json_array()]] - code - resume/skills.py
- [[aggregate_role_skills()]] - code - resume/skills.py
- [[asyncio_5]] - code
- [[collections]] - concept
- [[enum]] - concept
- [[extract_top_skills()]] - code - resume/skills.py
- [[extract_top_skills_deterministic()]] - code - resume/skills.py
- [[minify_job()]] - code - core/token_optimizer.py
- [[parse_skills_json()]] - code - resume/skills.py
- [[rank()]] - code - resume/skills.py
- [[skills.py]] - code - resume/skills.py
- [[test_aggregate_empty()]] - code - tests/test_skills.py
- [[test_aggregate_role_skills_prevalence_and_ranking()]] - code - tests/test_skills.py
- [[test_build_baseline_resume_data_orders_skills()]] - code - tests/test_baseline.py
- [[test_deterministic_extract_ranks_frequent_terms()]] - code - tests/test_skills.py
- [[test_extract_top_skills_falls_back_on_failure()]] - code - tests/test_skills.py
- [[test_extract_top_skills_no_client_is_deterministic()]] - code - tests/test_skills.py
- [[test_extract_top_skills_uses_llm()]] - code - tests/test_skills.py
- [[test_minify_job_keeps_head_and_tail()]] - code - tests/test_scorer.py
- [[test_parse_skills_json_clamps_importance()]] - code - tests/test_skills.py
- [[test_parse_skills_json_fenced_and_dedupes()]] - code - tests/test_skills.py
- [[test_parse_skills_json_plain()]] - code - tests/test_skills.py
- [[test_parse_skills_json_repairs_truncated_array()]] - code - tests/test_skills.py
- [[test_skills.py]] - code - tests/test_skills.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/skillspy
SORT file.name ASC
```

## Connections to other communities
- 16 edges to [[_COMMUNITY_diff.py]]
- 15 edges to [[_COMMUNITY_baseline.py]]
- 9 edges to [[_COMMUNITY_test_scorer.py]]
- 6 edges to [[_COMMUNITY_Job]]
- 6 edges to [[_COMMUNITY_get_settings]]
- 4 edges to [[_COMMUNITY_profile.py]]
- 4 edges to [[_COMMUNITY_benchmarkengine.py]]
- 3 edges to [[_COMMUNITY_Source]]
- 3 edges to [[_COMMUNITY_re]]
- 3 edges to [[_COMMUNITY_db.py]]
- 3 edges to [[_COMMUNITY_typing]]
- 2 edges to [[_COMMUNITY_LLMClient]]
- 2 edges to [[_COMMUNITY_test_fit.py]]
- 2 edges to [[_COMMUNITY_json]]
- 2 edges to [[_COMMUNITY_pytest]]
- 2 edges to [[_COMMUNITY_ingest.py]]
- 1 edge to [[_COMMUNITY_discovery_recall.py]]
- 1 edge to [[_COMMUNITY_suggest.py]]
- 1 edge to [[_COMMUNITY_textclean.py]]
- 1 edge to [[_COMMUNITY_pathlib]]
- 1 edge to [[_COMMUNITY_linkedin_people.py]]
- 1 edge to [[_COMMUNITY_clients.py]]
- 1 edge to [[_COMMUNITY_migrate_to_neon.py]]
- 1 edge to [[_COMMUNITY_test_apply_url.py]]

## Top bridge nodes
- [[skills.py]] - degree 34, connects to 15 communities
- [[extract_top_skills()]] - degree 20, connects to 7 communities
- [[enum]] - degree 8, connects to 7 communities
- [[test_skills.py]] - degree 26, connects to 6 communities
- [[minify_job()]] - degree 16, connects to 5 communities
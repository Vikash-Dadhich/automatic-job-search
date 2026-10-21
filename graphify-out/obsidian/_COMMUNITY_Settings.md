---
type: community
cohesion: 0.13
members: 26
---

# Settings

**Cohesion:** 0.13 - loosely connected
**Members:** 26 nodes

## Members
- [[dot-active_scorer_model()]] - code - config/settings.py
- [[dot-active_writer_model()]] - code - config/settings.py
- [[dot-base_resume_file()]] - code - config/settings.py
- [[dot-baselines_path()]] - code - config/settings.py
- [[dot-benchmarks_path()]] - code - config/settings.py
- [[dot-credentials_file()]] - code - config/settings.py
- [[dot-fallback_models_for()]] - code - config/settings.py
- [[dot-is_gemini()]] - code - config/settings.py
- [[dot-prep_packs_path()]] - code - config/settings.py
- [[dot-resolve_path()]] - code - config/settings.py
- [[dot-resumes_path()]] - code - config/settings.py
- [[dot-screenshots_path()]] - code - config/settings.py
- [[dot-sessions_path()]] - code - config/settings.py
- [[BaseSettings]] - code
- [[Central configuration for the job agent. Secrets and overrides come from…]] - rationale - config/settings.py
- [[Fixed path for the candidate's personal resume PDF (default for applications).]] - rationale - config/settings.py
- [[Model id used for outreach  open-ended answers. Always OpenAI.]] - rationale - config/settings.py
- [[Model id used for scoring. Always the OpenAI scorer.]] - rationale - config/settings.py
- [[Ordered alternates for a primary model (Gemini only), excluding duplicates.]] - rationale - config/settings.py
- [[Path_37]] - code
- [[Return an absolute path rooted at the project directory when relative.]] - rationale - config/settings.py
- [[Scoring specifics (Step 3)]] - document - AGENTS.md
- [[Settings]] - code - config/settings.py
- [[test_fallback_models_empty_for_anthropic()]] - code - tests/test_llm_provider.py
- [[test_fallback_models_exclude_primary()]] - code - tests/test_llm_provider.py
- [[test_settings_defaults_provider_gemini()]] - code - tests/test_llm_provider.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Settings
SORT file.name ASC
```

## Connections to other communities
- 5 edges to [[_COMMUNITY_test_llm_provider.py]]
- 4 edges to [[_COMMUNITY_json]]
- 2 edges to [[_COMMUNITY_test_phase0_baseline.py]]
- 2 edges to [[_COMMUNITY_Tier]]
- 1 edge to [[_COMMUNITY_get_settings]]
- 1 edge to [[_COMMUNITY_targets.py]]
- 1 edge to [[_COMMUNITY_typing]]
- 1 edge to [[_COMMUNITY_5. How fit is scored]]
- 1 edge to [[_COMMUNITY_dot-total_years_experience]]
- 1 edge to [[_COMMUNITY_diff.py]]
- 1 edge to [[_COMMUNITY_conftest.py]]

## Top bridge nodes
- [[Settings]] - degree 28, connects to 6 communities
- [[Scoring specifics (Step 3)]] - degree 9, connects to 6 communities
- [[test_fallback_models_empty_for_anthropic()]] - degree 2, connects to 1 community
- [[test_fallback_models_exclude_primary()]] - degree 2, connects to 1 community
- [[test_settings_defaults_provider_gemini()]] - degree 2, connects to 1 community
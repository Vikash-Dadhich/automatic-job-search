---
type: community
cohesion: 0.06
members: 61
---

# scorer/engine.py

**Cohesion:** 0.06 - loosely connected
**Members:** 61 nodes

## Members
- [[dot-__init__()_37]] - code - scorer/embeddings.py
- [[dot-_embed_chunk()]] - code - scorer/embeddings.py
- [[dot-embed()_1]] - code - scorer/embeddings.py
- [[dot-embed()_2]] - code - scorer/embeddings.py
- [[Any_56]] - code
- [[BaseException_2]] - code
- [[Batch embedder. Result length matches ``texts``.]] - rationale - scorer/embeddings.py
- [[Cosine already computed for this profile text, width, and embedding model.]] - rationale - scorer/embeddings.py
- [[Cosine similarity. Mismatched or empty vectors raise ``ValueError``.]] - rationale - scorer/embeddings.py
- [[Depleted credits  bad key surfaces as 429 or 403 but will never recover.]] - rationale - scorer/clients.py
- [[Embedder]] - code - scorer/embeddings.py
- [[Hard negative or company cooldown. Those jobs are not embedded.]] - rationale - scorer/engine.py
- [[LLM match evaluator score, tier, and persist discovered jobs.]] - rationale - scorer/engine.py
- [[Load the project profile.yaml (placeholders are fine for filter tests).]] - rationale - tests/conftest.py
- [[Load the stored structured JD and apply the recovery rule.]] - rationale - scorer/engine.py
- [[OpenAI embedder when the gate is on and a key is set. Otherwise ``None``.]] - rationale - scorer/embeddings.py
- [[OpenAI embeddings. Width is ``vector_dimensions``.]] - rationale - scorer/embeddings.py
- [[OpenAIEmbedder]] - code - scorer/embeddings.py
- [[Path_57]] - code
- [[Persist pass or reject. Dream companies always pass.]] - rationale - scorer/engine.py
- [[Profile and job-description embeddings for the scoring gate. Cosine similarity…]] - rationale - scorer/embeddings.py
- [[Profile vector from disk, or one embed call. ``None`` means fail open.]] - rationale - scorer/engine.py
- [[Protocol_6]] - code
- [[RecoveryDecision]] - code - scorer/vector_recovery.py
- [[Reopen a stored reject when recovery evidence or config has changed.]] - rationale - scorer/engine.py
- [[Return a cached profile vector when the model and width still match.]] - rationale - scorer/embeddings.py
- [[Send stored rejects back to discovered when they now clear the threshold.]] - rationale - scorer/engine.py
- [[Stored JD vector when width and embedding model both match.]] - rationale - scorer/embeddings.py
- [[Title and company first, then a tail-truncated description.]] - rationale - scorer/embeddings.py
- [[True when cosine is high enough to spend an LLM scoring call.]] - rationale - scorer/embeddings.py
- [[Walk best-first. Rejects do not consume ``score_budget``. Returns accepted…]] - rationale - scorer/engine.py
- [[_apply_vector_gate()]] - code - scorer/engine.py
- [[_cache_path()]] - code - scorer/embeddings.py
- [[_decide_vector()]] - code - scorer/engine.py
- [[_embed_texts()]] - code - scorer/engine.py
- [[_hard_blocked()]] - code - scorer/engine.py
- [[_log_embed_failure()]] - code - scorer/engine.py
- [[_maybe_recover_reject()]] - code - scorer/engine.py
- [[_recovery_for()]] - code - scorer/engine.py
- [[_refresh_recovery_reject()]] - code - scorer/engine.py
- [[_reopen_recovered()]] - code - scorer/engine.py
- [[_reopen_vector_rejects()]] - code - scorer/engine.py
- [[_resolve_profile_vector()]] - code - scorer/engine.py
- [[_save_vector()]] - code - scorer/engine.py
- [[_touch_vector_score()]] - code - scorer/engine.py
- [[_vectors_from_response()]] - code - scorer/embeddings.py
- [[accept_or_reject()]] - code - scorer/engine.py
- [[build_embedder()]] - code - scorer/embeddings.py
- [[clears_threshold()]] - code - scorer/embeddings.py
- [[cosine()]] - code - scorer/embeddings.py
- [[embeddings.py]] - code - scorer/embeddings.py
- [[is_permanent_account_error()]] - code - scorer/clients.py
- [[jd_vector()]] - code - scorer/embeddings.py
- [[job_embed_text()]] - code - scorer/embeddings.py
- [[load_profile_embedding()]] - code - scorer/embeddings.py
- [[profile()]] - code - tests/conftest.py
- [[profile_vec()]] - code - scorer/engine.py
- [[save_profile_embedding()]] - code - scorer/embeddings.py
- [[scorerengine.py]] - code - scorer/engine.py
- [[stored_score()]] - code - scorer/embeddings.py
- [[text_is_too_short()]] - code - scorer/embeddings.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/scorer/enginepy
SORT file.name ASC
```

## Connections to other communities
- 31 edges to [[_COMMUNITY_test_vector_recovery.py]]
- 19 edges to [[_COMMUNITY_session_scope]]
- 15 edges to [[_COMMUNITY_clients.py]]
- 14 edges to [[_COMMUNITY_Job]]
- 13 edges to [[_COMMUNITY_get_settings]]
- 12 edges to [[_COMMUNITY_LLMClient]]
- 8 edges to [[_COMMUNITY_Profile]]
- 8 edges to [[_COMMUNITY_Tier]]
- 6 edges to [[_COMMUNITY_test_scorer.py]]
- 5 edges to [[_COMMUNITY_json]]
- 4 edges to [[_COMMUNITY_scorer__init__.py]]
- 4 edges to [[_COMMUNITY_conftest.py]]
- 4 edges to [[_COMMUNITY_typing]]
- 3 edges to [[_COMMUNITY_filters.py]]
- 3 edges to [[_COMMUNITY_discovery_recall.py]]
- 3 edges to [[_COMMUNITY_db.py]]
- 3 edges to [[_COMMUNITY_prerank.py]]
- 2 edges to [[_COMMUNITY_TokenUsage]]
- 2 edges to [[_COMMUNITY_Any_1]]
- 2 edges to [[_COMMUNITY_pytest]]
- 2 edges to [[_COMMUNITY_test_structured_jd.py]]
- 2 edges to [[_COMMUNITY_suggest.py]]
- 2 edges to [[_COMMUNITY_diff.py]]
- 2 edges to [[_COMMUNITY_test_career_intelligence.py]]
- 2 edges to [[_COMMUNITY_test_fit.py]]
- 2 edges to [[_COMMUNITY_ingest.py]]
- 2 edges to [[_COMMUNITY_asyncio]]
- 1 edge to [[_COMMUNITY_structured_jd.py]]
- 1 edge to [[_COMMUNITY_company_intelligence.py]]
- 1 edge to [[_COMMUNITY_calculate_priority]]
- 1 edge to [[_COMMUNITY_test_eligibility.py]]
- 1 edge to [[_COMMUNITY_test_phase13_shortlist.py]]
- 1 edge to [[_COMMUNITY_test_priority.py]]
- 1 edge to [[_COMMUNITY_test_doctor.py]]
- 1 edge to [[_COMMUNITY_pipeline.py]]
- 1 edge to [[_COMMUNITY_test_company_intelligence.py]]
- 1 edge to [[_COMMUNITY_builder.py]]
- 1 edge to [[_COMMUNITY_priority.py]]
- 1 edge to [[_COMMUNITY_test_cover_letter.py]]
- 1 edge to [[_COMMUNITY_profile.py]]
- 1 edge to [[_COMMUNITY_test_llm_provider.py]]
- 1 edge to [[_COMMUNITY_pathlib]]
- 1 edge to [[_COMMUNITY_re]]
- 1 edge to [[_COMMUNITY_test_monitoring.py]]
- 1 edge to [[_COMMUNITY_test_resume.py]]
- 1 edge to [[_COMMUNITY_baseline.py]]

## Top bridge nodes
- [[scorerengine.py]] - degree 110, connects to 43 communities
- [[embeddings.py]] - degree 33, connects to 10 communities
- [[_apply_vector_gate()]] - degree 19, connects to 6 communities
- [[_reopen_vector_rejects()]] - degree 18, connects to 6 communities
- [[_recovery_for()]] - degree 10, connects to 5 communities
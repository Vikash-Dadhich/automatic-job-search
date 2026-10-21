---
type: community
cohesion: 0.08
members: 45
---

# test_scorer.py

**Cohesion:** 0.08 - loosely connected
**Members:** 45 nodes

## Members
- [[dot-_draft_open_ended()]] - code - automation/answers.py
- [[Any_54]] - code
- [[Any_55]] - code
- [[Build an Anthropic system content block with ephemeral prompt caching.]] - rationale - core/token_optimizer.py
- [[Deterministic letter used when the model keeps failing the style gate.]] - rationale - scorer/cover_letter.py
- [[Deterministic, profile-grounded note used when the model keeps failing the gate.]] - rationale - scorer/outreach.py
- [[Draft a 3-sentence outreach note; retry once if banned words appear.]] - rationale - scorer/outreach.py
- [[Draft a short cover letter; retry once if banned words appear.]] - rationale - scorer/cover_letter.py
- [[Drop sentences that contain banned words; keep the rest.]] - rationale - scorer/outreach.py
- [[Dynamic user content minified job posting only.]] - rationale - scorer/prompts.py
- [[Minified, cacheable LLM prompts for scoring and outreach.]] - rationale - scorer/prompts.py
- [[Offline tests for the LLM scorer (mock client — no network).]] - rationale - tests/test_scorer.py
- [[Payload compression, schema minification, and prompt-caching utilities.]] - rationale - core/token_optimizer.py
- [[Return banned phrases present as whole words (case-insensitive).]] - rationale - scorer/outreach.py
- [[Rough token estimate (~4 charstoken). Good enough for budgeting.]] - rationale - core/token_optimizer.py
- [[Serialize JSON with no extra whitespace (minimize output tokens).]] - rationale - core/token_optimizer.py
- [[Static system content candidate facts + rubric (prompt-cache friendly).]] - rationale - scorer/prompts.py
- [[Tier-1 alumnireferral outreach drafting with anti-AI style gate.]] - rationale - scorer/outreach.py
- [[Tier-1 cover letter drafting with the same anti-AI gate as outreach.]] - rationale - scorer/cover_letter.py
- [[User prompt for Tier-1 referralalumni outreach.]] - rationale - scorer/prompts.py
- [[User prompt for a Tier-1 cover letter. Phrase is matched by test fakes.]] - rationale - scorer/prompts.py
- [[_fallback_cover_letter()]] - code - scorer/cover_letter.py
- [[_fallback_outreach()]] - code - scorer/outreach.py
- [[approx_tokens()]] - code - core/token_optimizer.py
- [[build_cover_letter_user()]] - code - scorer/prompts.py
- [[build_outreach_user()]] - code - scorer/prompts.py
- [[build_scoring_system_blocks()]] - code - scorer/prompts.py
- [[build_scoring_user()]] - code - scorer/prompts.py
- [[cache_block()]] - code - core/token_optimizer.py
- [[compact_json_dumps()]] - code - core/token_optimizer.py
- [[contains_banned()]] - code - scorer/outreach.py
- [[cover_letter.py]] - code - scorer/cover_letter.py
- [[generate_cover_letter()]] - code - scorer/cover_letter.py
- [[generate_outreach()]] - code - scorer/outreach.py
- [[outreach.py]] - code - scorer/outreach.py
- [[prompts.py]] - code - scorer/prompts.py
- [[run_one()]] - code - scorer/engine.py
- [[strip_banned_sentences()]] - code - scorer/outreach.py
- [[test_contains_banned()]] - code - tests/test_scorer.py
- [[test_generate_outreach_retries_on_banned()]] - code - tests/test_scorer.py
- [[test_load_profile_for_scorer()]] - code - tests/test_scorer.py
- [[test_prompt_builders_cache_and_content()]] - code - tests/test_scorer.py
- [[test_scorer.py]] - code - tests/test_scorer.py
- [[test_token_optimizer_helpers()]] - code - tests/test_scorer.py
- [[token_optimizer.py]] - code - core/token_optimizer.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/test_scorerpy
SORT file.name ASC
```

## Connections to other communities
- 16 edges to [[_COMMUNITY_Job]]
- 13 edges to [[_COMMUNITY_Profile]]
- 9 edges to [[_COMMUNITY_re]]
- 9 edges to [[_COMMUNITY_LLMClient]]
- 9 edges to [[_COMMUNITY_Tier]]
- 9 edges to [[_COMMUNITY_skills.py]]
- 8 edges to [[_COMMUNITY_typing]]
- 6 edges to [[_COMMUNITY_upsert_job]]
- 6 edges to [[_COMMUNITY_get_settings]]
- 6 edges to [[_COMMUNITY_test_cover_letter.py]]
- 6 edges to [[_COMMUNITY_scorerengine.py]]
- 5 edges to [[_COMMUNITY_test_vector_recovery.py]]
- 5 edges to [[_COMMUNITY_discovery_recall.py]]
- 4 edges to [[_COMMUNITY_session_scope]]
- 4 edges to [[_COMMUNITY_Source]]
- 4 edges to [[_COMMUNITY_db.py]]
- 4 edges to [[_COMMUNITY_profile.py]]
- 3 edges to [[_COMMUNITY_test_fit.py]]
- 2 edges to [[_COMMUNITY_suggest.py]]
- 2 edges to [[_COMMUNITY_json]]
- 2 edges to [[_COMMUNITY_clients.py]]
- 2 edges to [[_COMMUNITY_ingest.py]]
- 1 edge to [[_COMMUNITY_TokenUsage]]
- 1 edge to [[_COMMUNITY_diff.py]]
- 1 edge to [[_COMMUNITY_test_career_intelligence.py]]
- 1 edge to [[_COMMUNITY_pathlib]]

## Top bridge nodes
- [[test_scorer.py]] - degree 56, connects to 17 communities
- [[outreach.py]] - degree 24, connects to 12 communities
- [[cover_letter.py]] - degree 21, connects to 11 communities
- [[token_optimizer.py]] - degree 16, connects to 7 communities
- [[generate_cover_letter()]] - degree 16, connects to 6 communities
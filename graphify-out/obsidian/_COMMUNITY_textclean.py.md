---
type: community
cohesion: 0.09
members: 42
---

# textclean.py

**Cohesion:** 0.09 - loosely connected
**Members:** 42 nodes

## Members
- [[dot-ensure_clean_description()]] - code - scraper/models.py
- [[Flow]] - document - docs/phase4-jd-ingestion.md
- [[HTML → clean text and section extraction for token-efficient scoring.]] - rationale - scraper/textclean.py
- [[Hash and upsert]] - document - docs/phase4-jd-ingestion.md
- [[JdStatus]] - code - scraper/textclean.py
- [[Keep the JD body, including text before the first known heading. Falls back to…]] - rationale - scraper/textclean.py
- [[Limits_1]] - document - docs/phase4-jd-ingestion.md
- [[Normalization]] - document - docs/phase4-jd-ingestion.md
- [[Normalize one JD and record whether it is missing, short, or cut off.]] - rationale - scraper/textclean.py
- [[Normalize the best available JD and record extraction quality.]] - rationale - scraper/models.py
- [[NormalizedJd]] - code - scraper/textclean.py
- [[Persisted description plus how it was produced. Not a fit judgment.]] - rationale - scraper/textclean.py
- [[Phase 4 JD ingestion]] - document - docs/phase4-jd-ingestion.md
- [[Phase 4 JD normalization, hashing, and upsert protection.]] - rationale - tests/test_jd_ingest.py
- [[Stable SHA-256 of normalized text for dedup.]] - rationale - scraper/textclean.py
- [[StrEnum]] - code
- [[Strip boilerplate tags and return readable plain text.]] - rationale - scraper/textclean.py
- [[Tests for HTML → text cleaning and section extraction.]] - rationale - tests/test_textclean.py
- [[_drop_boilerplate_lines()]] - code - scraper/textclean.py
- [[_extract_body()]] - code - scraper/textclean.py
- [[_normalize_whitespace()]] - code - scraper/textclean.py
- [[_status()]] - code - scraper/textclean.py
- [[content_hash()]] - code - scraper/textclean.py
- [[empty()]] - code - tests/test_company_intelligence.py
- [[extract_sections()]] - code - scraper/textclean.py
- [[html_to_text()]] - code - scraper/textclean.py
- [[normalize_description()]] - code - scraper/textclean.py
- [[phase4-jd-ingestion]] - document - docs/phase4-jd-ingestion.md
- [[selectolax_parser]] - concept
- [[test_content_hash_ignores_formatting_and_tracks_meaning()]] - code - tests/test_jd_ingest.py
- [[test_content_hash_stable()]] - code - tests/test_textclean.py
- [[test_extract_sections_fallback_without_headers()]] - code - tests/test_textclean.py
- [[test_extract_sections_keeps_known_headers()]] - code - tests/test_textclean.py
- [[test_html_strips_script_style_and_nav()]] - code - tests/test_jd_ingest.py
- [[test_html_to_text_strips_boilerplate()]] - code - tests/test_textclean.py
- [[test_jd_ingest.py]] - code - tests/test_jd_ingest.py
- [[test_jobsy_and_workday_descriptions_and_provenance()]] - code - tests/test_jd_ingest.py
- [[test_markdown_and_unknown_sections_are_kept()]] - code - tests/test_jd_ingest.py
- [[test_missing_short_and_truncated_descriptions()]] - code - tests/test_jd_ingest.py
- [[test_plain_text_and_whitespace()]] - code - tests/test_jd_ingest.py
- [[test_textclean.py]] - code - tests/test_textclean.py
- [[textclean.py]] - code - scraper/textclean.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/textcleanpy
SORT file.name ASC
```

## Connections to other communities
- 15 edges to [[_COMMUNITY_Source]]
- 5 edges to [[_COMMUNITY_test_structured_jd.py]]
- 4 edges to [[_COMMUNITY_discovery_recall.py]]
- 3 edges to [[_COMMUNITY_test_application_deadline.py]]
- 3 edges to [[_COMMUNITY_db.py]]
- 3 edges to [[_COMMUNITY_re]]
- 3 edges to [[_COMMUNITY_upsert_job]]
- 2 edges to [[_COMMUNITY_json]]
- 2 edges to [[_COMMUNITY_structured_jd.py]]
- 2 edges to [[_COMMUNITY_company_intelligence.py]]
- 1 edge to [[_COMMUNITY_Career Intelligence]]
- 1 edge to [[_COMMUNITY_Structured JD intelligence]]
- 1 edge to [[_COMMUNITY_test_company_intelligence_v2.py]]
- 1 edge to [[_COMMUNITY_HttpCompanyIntelProvider]]
- 1 edge to [[_COMMUNITY_linkedin_jobspy.py]]
- 1 edge to [[_COMMUNITY_Discovery recall benchmark]]
- 1 edge to [[_COMMUNITY_get_settings]]
- 1 edge to [[_COMMUNITY_session_scope]]
- 1 edge to [[_COMMUNITY_application_deadline.py]]
- 1 edge to [[_COMMUNITY_typing]]
- 1 edge to [[_COMMUNITY_test_resume.py]]
- 1 edge to [[_COMMUNITY_skills.py]]
- 1 edge to [[_COMMUNITY_pathlib]]

## Top bridge nodes
- [[textclean.py]] - degree 30, connects to 13 communities
- [[content_hash()]] - degree 26, connects to 8 communities
- [[test_jd_ingest.py]] - degree 22, connects to 5 communities
- [[normalize_description()]] - degree 18, connects to 3 communities
- [[html_to_text()]] - degree 13, connects to 3 communities
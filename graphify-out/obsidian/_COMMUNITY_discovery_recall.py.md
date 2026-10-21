---
type: community
cohesion: 0.05
members: 89
---

# discovery_recall.py

**Cohesion:** 0.05 - loosely connected
**Members:** 89 nodes

## Members
- [[Another source's row for this posting. Same-source ids are never folded…]] - rationale - core/db.py
- [[BenchmarkCase]] - code - scraper/discovery_recall.py
- [[Both sides name a compatible place. A missing location does not count.]] - rationale - core/job_identity.py
- [[Company, title, and an agreeing location. Not enough without a shared…]] - rationale - core/job_identity.py
- [[Deterministic posting identity. Uncertain matches stay separate jobs.]] - rationale - core/job_identity.py
- [[Drop fragments and tracking parameters. Keep query keys that can be the posting…]] - rationale - core/job_identity.py
- [[Exact company tokens. A shorter name is not treated as the same employer.]] - rationale - core/job_identity.py
- [[Keep the head and tail of long text. Job descriptions bury sponsorship and YOE…]] - rationale - core/textmatch.py
- [[Observation]] - code - scraper/discovery_recall.py
- [[ObservedJob]] - code - scraper/discovery_recall.py
- [[Offline recall against a frozen posting list. Synthetic rows are not the sample.]] - rationale - tests/test_discovery_recall.py
- [[Path_7]] - code
- [[Path_8]] - code
- [[Recall of a frozen posting list against stored jobs. This does not search,…]] - rationale - scraper/discovery_recall.py
- [[RecallReport]] - code - scraper/discovery_recall.py
- [[Relevant Summer 2027 internships. Other rows stay out of the denominator.]] - rationale - scraper/discovery_recall.py
- [[Same safeguards as a cross-source URL match. A blank field is not a conflict.]] - rationale - scraper/discovery_recall.py
- [[Shared matching + truncation helpers used by filters, scoring, and answers.…]] - rationale - core/textmatch.py
- [[Significant tokens of a company name with legal suffixes removed.]] - rationale - core/textmatch.py
- [[Source id, posting URL, or strong field match. Conflicts stay unmatched.]] - rationale - scraper/discovery_recall.py
- [[Split 'Seattle, WA, US' into ('seattle', 'wa').]] - rationale - core/textmatch.py
- [[Tests for the shared matching  truncation helpers.]] - rationale - tests/test_textmatch.py
- [[The substring blocklist used to drop MetLife whenever Meta was excluded.]] - rationale - tests/test_textmatch.py
- [[True when a posting location satisfies one preference entry. Compares city and…]] - rationale - core/textmatch.py
- [[True when both URLs canonicalize to one posting identity.]] - rationale - core/job_identity.py
- [[True when both URLs identify postings and those postings differ.]] - rationale - core/job_identity.py
- [[True when both locations are specific and name different places.]] - rationale - core/job_identity.py
- [[True when the URL is a posting, not a bare site homepage. A homepage query…]] - rationale - core/job_identity.py
- [[True when two company names refer to the same employer. 'Google' == 'Google…]] - rationale - core/textmatch.py
- [[Unique relevant cases over stored jobs. Title similarity is not a match.]] - rationale - scraper/discovery_recall.py
- [[Whole-phrase, word-boundary match — avoids 'Meta' hitting 'MetLife'.]] - rationale - core/textmatch.py
- [[Whole-word remote detection so 'Remoteville, IN' is not treated as remote.]] - rationale - core/textmatch.py
- [[_assign_canonical_url()]] - code - core/db.py
- [[_bucket()]] - code - scraper/discovery_recall.py
- [[_case()_1]] - code - scraper/discovery_recall.py
- [[_case()_2]] - code - tests/test_discovery_recall.py
- [[_city_state()]] - code - core/textmatch.py
- [[_find_cross_source_job()]] - code - core/db.py
- [[_identity_conflict()]] - code - scraper/discovery_recall.py
- [[_is_tracking_param()]] - code - core/job_identity.py
- [[_job()_2]] - code - tests/test_discovery_recall.py
- [[_location_ok()]] - code - scraper/filters.py
- [[_optional_str()]] - code - scraper/discovery_recall.py
- [[_recall()]] - code - scraper/discovery_recall.py
- [[_require_str()]] - code - scraper/discovery_recall.py
- [[_truncate()]] - code - scraper/textclean.py
- [[canonicalize_job_url()]] - code - core/job_identity.py
- [[case_is_captured()]] - code - scraper/discovery_recall.py
- [[company_matches()]] - code - core/textmatch.py
- [[company_tokens()]] - code - core/textmatch.py
- [[contains_phrase()]] - code - core/textmatch.py
- [[discovery_recall.py]] - code - scraper/discovery_recall.py
- [[eligible()]] - code - scraper/discovery_recall.py
- [[is_remote_location()]] - code - core/textmatch.py
- [[job_identity.py]] - code - core/job_identity.py
- [[load_benchmark()]] - code - scraper/discovery_recall.py
- [[location_matches()]] - code - core/textmatch.py
- [[locations_agree()]] - code - core/job_identity.py
- [[locations_conflict()]] - code - core/job_identity.py
- [[measure_recall()]] - code - scraper/discovery_recall.py
- [[normalize_text()]] - code - core/textmatch.py
- [[normalize_title()]] - code - core/job_identity.py
- [[observation_matches()]] - code - scraper/discovery_recall.py
- [[same_employer()]] - code - core/job_identity.py
- [[same_posting_url()]] - code - core/job_identity.py
- [[strong_field_match()]] - code - core/job_identity.py
- [[test_checked_in_sample_does_not_claim_recall()]] - code - tests/test_discovery_recall.py
- [[test_company_matches_ignores_legal_suffixes()]] - code - tests/test_textmatch.py
- [[test_company_matches_rejects_lookalikes()]] - code - tests/test_textmatch.py
- [[test_contains_phrase_is_word_bounded()]] - code - tests/test_textmatch.py
- [[test_discovery_recall.py]] - code - tests/test_discovery_recall.py
- [[test_empty_sample_is_unavailable_not_perfect()]] - code - tests/test_discovery_recall.py
- [[test_invalid_records_are_rejected()]] - code - tests/test_discovery_recall.py
- [[test_irrelevant_rows_are_not_in_the_denominator()]] - code - tests/test_discovery_recall.py
- [[test_is_remote_location_word_bounded()]] - code - tests/test_textmatch.py
- [[test_location_matches_respects_state()]] - code - tests/test_textmatch.py
- [[test_repeated_measurement_is_identical()]] - code - tests/test_discovery_recall.py
- [[test_source_id_matches_and_title_alone_does_not()]] - code - tests/test_discovery_recall.py
- [[test_source_id_respects_employer_and_location_conflicts()]] - code - tests/test_discovery_recall.py
- [[test_textmatch.py]] - code - tests/test_textmatch.py
- [[test_truncate_middle_keeps_both_ends()]] - code - tests/test_textmatch.py
- [[test_truncate_middle_noop_when_short()]] - code - tests/test_textmatch.py
- [[test_two_boards_count_as_one_expected_job()]] - code - tests/test_discovery_recall.py
- [[test_unmatched_case_is_named()]] - code - tests/test_discovery_recall.py
- [[test_url_canonicalization_drops_tracking_and_keeps_posting_ids()]] - code - tests/test_job_identity.py
- [[textmatch.py]] - code - core/textmatch.py
- [[truncate_middle()]] - code - core/textmatch.py
- [[url_identifies_posting()]] - code - core/job_identity.py
- [[urls_conflict()]] - code - core/job_identity.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/discovery_recallpy
SORT file.name ASC
```

## Connections to other communities
- 10 edges to [[_COMMUNITY_db.py]]
- 8 edges to [[_COMMUNITY_filters.py]]
- 7 edges to [[_COMMUNITY_prerank.py]]
- 6 edges to [[_COMMUNITY_Source]]
- 5 edges to [[_COMMUNITY_test_application_portfolio.py]]
- 5 edges to [[_COMMUNITY_test_scorer.py]]
- 4 edges to [[_COMMUNITY_Profile]]
- 4 edges to [[_COMMUNITY_textclean.py]]
- 4 edges to [[_COMMUNITY_re]]
- 4 edges to [[_COMMUNITY_pytest]]
- 3 edges to [[_COMMUNITY_scorerengine.py]]
- 3 edges to [[_COMMUNITY_test_phase13_shortlist.py]]
- 2 edges to [[_COMMUNITY_Job]]
- 2 edges to [[_COMMUNITY_upsert_job]]
- 2 edges to [[_COMMUNITY_pathlib]]
- 1 edge to [[_COMMUNITY_AsyncSession]]
- 1 edge to [[_COMMUNITY_Tier]]
- 1 edge to [[_COMMUNITY_LLMClient]]
- 1 edge to [[_COMMUNITY_skills.py]]
- 1 edge to [[_COMMUNITY_linkedin_jobspy.py]]
- 1 edge to [[_COMMUNITY_get_settings]]
- 1 edge to [[_COMMUNITY_test_apply_url.py]]
- 1 edge to [[_COMMUNITY_typing]]
- 1 edge to [[_COMMUNITY_test_resume.py]]

## Top bridge nodes
- [[textmatch.py]] - degree 20, connects to 8 communities
- [[company_matches()]] - degree 16, connects to 7 communities
- [[discovery_recall.py]] - degree 29, connects to 6 communities
- [[contains_phrase()]] - degree 13, connects to 4 communities
- [[_find_cross_source_job()]] - degree 12, connects to 4 communities
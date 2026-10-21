---
type: community
cohesion: 0.09
members: 58
---

# get_settings

**Cohesion:** 0.09 - loosely connected
**Members:** 58 nodes

## Members
- [[Advance to the next least-destructive fit lever; None if floors reached.]] - rationale - resume/compiler.py
- [[Any_29]] - code
- [[Attach the best available resume to jobs in one status that are missing…]] - rationale - resume/compiler.py
- [[Cached settings singleton.]] - rationale - config/settings.py
- [[Compile a tailored resume PDF for one job; return absolute path.]] - rationale - resume/compiler.py
- [[Compile resume JSON to PDF; optionally iterate until one page.]] - rationale - resume/compiler.py
- [[Compile resumes for staged jobs missing resume_path (unless force).]] - rationale - resume/compiler.py
- [[Copy the candidate's base PDF for one job, sanitize metadata, return path.]] - rationale - resume/compiler.py
- [[Create a valid PDF via Typst to stand in for the user's base resume.]] - rationale - tests/test_base_resume.py
- [[FitReport]] - code - resume/compiler.py
- [[Levers pulled to keep the resume on one page.]] - rationale - resume/compiler.py
- [[Normalize a person's name for filenames 'Jane Q. Doe' - 'Jane_Q_Doe'.]] - rationale - resume/compiler.py
- [[Overwrite CreatorProducer and strip author-ish metadata.]] - rationale - resume/compiler.py
- [[Path_30]] - code
- [[Path_31]] - code
- [[Path_32]] - code
- [[Resolve the per-job resume PDF path (create parent dirs).]] - rationale - resume/compiler.py
- [[Resume preparation static base PDF by default, Typst tailoring on demand.]] - rationale - resume/__init__.py
- [[ResumeSummary]] - code - resume/compiler.py
- [[Return a copy of resume data with content caps and typography knobs applied.]] - rationale - resume/compiler.py
- [[Return the number of pages in a PDF.]] - rationale - resume/compiler.py
- [[Return the role baseline PDF for this job when one exists, else None.]] - rationale - resume/compiler.py
- [[Tests for one-page auto-fit resume compilation.]] - rationale - tests/test_autofit.py
- [[Tests for static base resume preparation and on-demand Typst tailoring.]] - rationale - tests/test_base_resume.py
- [[Typst resume compiler + static base resume + one-page auto-fit + pikepdf…]] - rationale - resume/compiler.py
- [[_base_data()]] - code - tests/test_autofit.py
- [[_baseline_pdf_for_job()]] - code - resume/compiler.py
- [[_job_resume_output()]] - code - resume/compiler.py
- [[_make_base_pdf()]] - code - tests/test_base_resume.py
- [[_next_fit_state()]] - code - resume/compiler.py
- [[_profile()]] - code - tests/test_base_resume.py
- [[_sample_job()_1]] - code - tests/test_base_resume.py
- [[apply_fit_caps()]] - code - resume/compiler.py
- [[clean_name()]] - code - resume/compiler.py
- [[compile_pending()]] - code - resume/compiler.py
- [[compile_resume()]] - code - resume/compiler.py
- [[compile_resume_data()]] - code - resume/compiler.py
- [[compiler.py]] - code - resume/compiler.py
- [[get_settings()]] - code - config/settings.py
- [[pdf_page_count()]] - code - resume/compiler.py
- [[pikepdf]] - concept
- [[prepare_base_resume()]] - code - resume/compiler.py
- [[prepare_pending()]] - code - resume/compiler.py
- [[resume__init__.py]] - code - resume/__init__.py
- [[sanitize_pdf()]] - code - resume/compiler.py
- [[shutil]] - concept
- [[test_apply_fit_caps_trims_skills_and_bullets()]] - code - tests/test_autofit.py
- [[test_autofit.py]] - code - tests/test_autofit.py
- [[test_base_resume.py]] - code - tests/test_base_resume.py
- [[test_base_resume_file_property()]] - code - tests/test_base_resume.py
- [[test_clean_name()]] - code - tests/test_resume.py
- [[test_compile_for_job_overwrites()]] - code - tests/test_base_resume.py
- [[test_compile_oversized_autofits_to_one_page()]] - code - tests/test_autofit.py
- [[test_compile_small_resume_one_page()]] - code - tests/test_autofit.py
- [[test_prepare_base_resume_copies_and_sanitizes()]] - code - tests/test_base_resume.py
- [[test_prepare_base_resume_missing_file()]] - code - tests/test_base_resume.py
- [[test_prepare_pending_missing_base_no_crash()]] - code - tests/test_base_resume.py
- [[test_prepare_pending_sets_resume_path()]] - code - tests/test_base_resume.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/get_settings
SORT file.name ASC
```

## Connections to other communities
- 22 edges to [[_COMMUNITY_session_scope]]
- 21 edges to [[_COMMUNITY_test_resume.py]]
- 19 edges to [[_COMMUNITY_suggest.py]]
- 17 edges to [[_COMMUNITY_profile.py]]
- 14 edges to [[_COMMUNITY_Job]]
- 13 edges to [[_COMMUNITY_Profile]]
- 13 edges to [[_COMMUNITY_scorerengine.py]]
- 12 edges to [[_COMMUNITY_baseline.py]]
- 9 edges to [[_COMMUNITY_db.py]]
- 9 edges to [[_COMMUNITY_test_vector_recovery.py]]
- 8 edges to [[_COMMUNITY_workday.py]]
- 7 edges to [[_COMMUNITY_linkedin_people.py]]
- 7 edges to [[_COMMUNITY_browser.py]]
- 7 edges to [[_COMMUNITY_pipeline.py]]
- 7 edges to [[_COMMUNITY_test_pacing.py]]
- 6 edges to [[_COMMUNITY_json]]
- 6 edges to [[_COMMUNITY_test_scorer.py]]
- 6 edges to [[_COMMUNITY_skills.py]]
- 6 edges to [[_COMMUNITY_typing]]
- 5 edges to [[_COMMUNITY_Source]]
- 5 edges to [[_COMMUNITY_pathlib]]
- 4 edges to [[_COMMUNITY_Any_1]]
- 4 edges to [[_COMMUNITY_diff.py]]
- 4 edges to [[_COMMUNITY_upsert_job]]
- 4 edges to [[_COMMUNITY_test_phase13_shortlist.py]]
- 4 edges to [[_COMMUNITY_builder.py]]
- 4 edges to [[_COMMUNITY_re]]
- 4 edges to [[_COMMUNITY_vault.py]]
- 3 edges to [[_COMMUNITY_asyncio]]
- 3 edges to [[_COMMUNITY_TelegramClient]]
- 3 edges to [[_COMMUNITY_scheduler.py]]
- 3 edges to [[_COMMUNITY_test_monitoring.py]]
- 3 edges to [[_COMMUNITY_test_application_portfolio.py]]
- 3 edges to [[_COMMUNITY_Tier]]
- 3 edges to [[_COMMUNITY_test_llm_provider.py]]
- 2 edges to [[_COMMUNITY_TokenUsage]]
- 2 edges to [[_COMMUNITY_filters.py]]
- 2 edges to [[_COMMUNITY_runner.py]]
- 2 edges to [[_COMMUNITY_benchmarkengine.py]]
- 2 edges to [[_COMMUNITY_send_prep_pack]]
- 2 edges to [[_COMMUNITY_main.py]]
- 2 edges to [[_COMMUNITY_LLMClient]]
- 2 edges to [[_COMMUNITY_migrate_to_neon.py]]
- 2 edges to [[_COMMUNITY_pytest]]
- 1 edge to [[_COMMUNITY_Settings]]
- 1 edge to [[_COMMUNITY_telegram_webhook]]
- 1 edge to [[_COMMUNITY_discovery_recall.py]]
- 1 edge to [[_COMMUNITY_test_doctor.py]]
- 1 edge to [[_COMMUNITY_targets.py]]
- 1 edge to [[_COMMUNITY_clients.py]]
- 1 edge to [[_COMMUNITY_textclean.py]]
- 1 edge to [[_COMMUNITY_conftest.py]]
- 1 edge to [[_COMMUNITY_test_career_intelligence.py]]
- 1 edge to [[_COMMUNITY_test_company_intelligence_v2.py]]
- 1 edge to [[_COMMUNITY_test_eligibility.py]]
- 1 edge to [[_COMMUNITY_test_phase0_baseline.py]]
- 1 edge to [[_COMMUNITY_test_recruiting_universe.py]]
- 1 edge to [[_COMMUNITY_sort_by_priority]]
- 1 edge to [[_COMMUNITY_ingest.py]]

## Top bridge nodes
- [[get_settings()]] - degree 166, connects to 53 communities
- [[compiler.py]] - degree 49, connects to 16 communities
- [[test_base_resume.py]] - degree 36, connects to 11 communities
- [[prepare_pending()]] - degree 23, connects to 7 communities
- [[compile_resume()]] - degree 20, connects to 6 communities
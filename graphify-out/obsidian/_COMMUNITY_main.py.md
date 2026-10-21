---
type: community
cohesion: 0.09
members: 37
---

# main.py

**Cohesion:** 0.09 - loosely connected
**Members:** 37 nodes

## Members
- [[ArgumentParser]] - code
- [[Central structlog configuration.]] - rationale - core/logging.py
- [[Configure structlog + stdlib logging once at process start. Console renderer…]] - rationale - core/logging.py
- [[Job Agent CLI — schedule, run-once, poll, send-reviews, webhook, baselines,…]] - rationale - main.py
- [[Offline tests for main.py CLI routing.]] - rationale - tests/test_main_cli.py
- [[_cmd_benchmark()]] - code - main.py
- [[_cmd_build_baseline()]] - code - main.py
- [[_cmd_health()]] - code - main.py
- [[_cmd_poll()]] - code - main.py
- [[_cmd_prep_pack()]] - code - main.py
- [[_cmd_run_once()]] - code - main.py
- [[_cmd_save_linkedin_session()]] - code - main.py
- [[_cmd_send_reviews()]] - code - main.py
- [[_cmd_send_suggestions()]] - code - main.py
- [[_cmd_serve()]] - code - main.py
- [[_cmd_suggest()]] - code - main.py
- [[_cmd_webhook()]] - code - main.py
- [[argparse]] - concept
- [[build_parser()]] - code - main.py
- [[configure_logging()]] - code - core/logging.py
- [[fake_cmd()]] - code - tests/test_main_cli.py
- [[fake_tailor()]] - code - tests/test_main_cli.py
- [[logging.py]] - code - core/logging.py
- [[main()]] - code - main.py
- [[main.py]] - code - main.py
- [[sys]] - concept
- [[test_build_parser_default_serve()]] - code - tests/test_main_cli.py
- [[test_default_command_is_serve()]] - code - tests/test_main_cli.py
- [[test_doctor_cli()]] - code - tests/test_main_cli.py
- [[test_main_cli.py]] - code - tests/test_main_cli.py
- [[test_poll_invokes_run_polling()]] - code - tests/test_main_cli.py
- [[test_prep_pack_cli()]] - code - tests/test_main_cli.py
- [[test_run_once_invokes_pipeline()]] - code - tests/test_main_cli.py
- [[test_send_reviews_invokes_once()]] - code - tests/test_main_cli.py
- [[test_serve_invokes_run_service()]] - code - tests/test_main_cli.py
- [[test_tailor_resume_cli()]] - code - tests/test_main_cli.py
- [[test_webhook_invokes_uvicorn()]] - code - tests/test_main_cli.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/mainpy
SORT file.name ASC
```

## Connections to other communities
- 11 edges to [[_COMMUNITY_suggest.py]]
- 8 edges to [[_COMMUNITY_test_doctor.py]]
- 6 edges to [[_COMMUNITY_session_scope]]
- 6 edges to [[_COMMUNITY_asyncio]]
- 6 edges to [[_COMMUNITY_test_monitoring.py]]
- 3 edges to [[_COMMUNITY_pipeline.py]]
- 3 edges to [[_COMMUNITY_baseline.py]]
- 2 edges to [[_COMMUNITY_bot__init__.py]]
- 2 edges to [[_COMMUNITY_browser.py]]
- 2 edges to [[_COMMUNITY_get_settings]]
- 2 edges to [[_COMMUNITY_review.py]]
- 2 edges to [[_COMMUNITY_ingest.py]]
- 2 edges to [[_COMMUNITY_benchmarkengine.py]]
- 2 edges to [[_COMMUNITY_send_prep_pack]]
- 2 edges to [[_COMMUNITY_test_apply_url.py]]
- 2 edges to [[_COMMUNITY_typing]]
- 1 edge to [[_COMMUNITY_handlers.py]]
- 1 edge to [[_COMMUNITY_Job]]
- 1 edge to [[_COMMUNITY_Tier]]
- 1 edge to [[_COMMUNITY_test_resume.py]]
- 1 edge to [[_COMMUNITY_runner.py]]
- 1 edge to [[_COMMUNITY_diff.py]]
- 1 edge to [[_COMMUNITY_MonkeyPatch]]
- 1 edge to [[_COMMUNITY_test_phase13_shortlist.py]]
- 1 edge to [[_COMMUNITY_db.py]]
- 1 edge to [[_COMMUNITY_json]]
- 1 edge to [[_COMMUNITY_vault.py]]
- 1 edge to [[_COMMUNITY_scheduler.py]]
- 1 edge to [[_COMMUNITY_WorkdaySubmitter]]

## Top bridge nodes
- [[main.py]] - degree 69, connects to 26 communities
- [[main()]] - degree 30, connects to 6 communities
- [[test_main_cli.py]] - degree 14, connects to 2 communities
- [[configure_logging()]] - degree 7, connects to 2 communities
- [[logging.py]] - degree 6, connects to 2 communities
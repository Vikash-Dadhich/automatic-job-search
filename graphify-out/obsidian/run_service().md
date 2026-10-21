---
source_file: "orchestrator/service.py"
type: "code"
community: "asyncio"
location: "L20"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/asyncio
---

# run_service()

## Connections
- [[Event_1]] - `references` [EXTRACTED]
- [[Start the scheduler and (optionally) the Telegram poller until stopped.…]] - `rationale_for` [EXTRACTED]
- [[_cmd_serve()]] - `calls` [EXTRACTED]
- [[_request_shutdown()]] - `indirect_call` [INFERRED]
- [[asyncio_11]] - `calls` [EXTRACTED]
- [[build_scheduler()]] - `calls` [EXTRACTED]
- [[configure_logging()]] - `calls` [EXTRACTED]
- [[get_settings()]] - `calls` [EXTRACTED]
- [[init_db()]] - `calls` [EXTRACTED]
- [[main.py]] - `imports` [EXTRACTED]
- [[orchestrator__init__.py]] - `imports` [EXTRACTED]
- [[run_polling()]] - `calls` [EXTRACTED]
- [[service.py]] - `contains` [EXTRACTED]
- [[signal]] - `calls` [EXTRACTED]
- [[test_run_service_stops_without_poller()]] - `calls` [EXTRACTED]
- [[test_run_service_with_poller_respects_stop()]] - `calls` [EXTRACTED]
- [[test_service.py]] - `imports` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/asyncio
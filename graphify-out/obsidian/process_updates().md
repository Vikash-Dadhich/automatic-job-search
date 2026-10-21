---
source_file: "bot/poller.py"
type: "code"
community: "bot/__init__.py"
location: "L17"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/bot/__init__py
---

# process_updates()

## Connections
- [[Any_3]] - `references` [EXTRACTED]
- [[Route a batch of updates; return the next offset (last update_id + 1).]] - `rationale_for` [EXTRACTED]
- [[Submitter]] - `uses` [INFERRED]
- [[TelegramClient]] - `uses` [INFERRED]
- [[bot__init__.py]] - `imports` [EXTRACTED]
- [[handle_callback()]] - `calls` [EXTRACTED]
- [[handle_message()]] - `calls` [EXTRACTED]
- [[poller.py]] - `contains` [EXTRACTED]
- [[run_polling()]] - `calls` [EXTRACTED]
- [[test_poller.py]] - `imports` [EXTRACTED]
- [[test_process_updates_routes_callback()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/bot/__init__py
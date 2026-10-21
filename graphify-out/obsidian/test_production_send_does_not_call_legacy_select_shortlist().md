---
source_file: "tests/test_telegram_output.py"
type: "code"
community: "send_prep_pack"
location: "L290"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/send_prep_pack
---

# test_production_send_does_not_call_legacy_select_shortlist()

## Connections
- [[FakeTransport_1]] - `calls` [EXTRACTED]
- [[Job]] - `uses` [INFERRED]
- [[MonkeyPatch_22]] - `references` [EXTRACTED]
- [[Path_41]] - `references` [EXTRACTED]
- [[TelegramClient]] - `calls` [EXTRACTED]
- [[_enable_brief()]] - `calls` [EXTRACTED]
- [[_insert()]] - `calls` [EXTRACTED]
- [[_legacy()]] - `indirect_call` [INFERRED]
- [[_row()_2]] - `calls` [EXTRACTED]
- [[send_prep_pack()]] - `calls` [EXTRACTED]
- [[test_telegram_output.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/send_prep_pack
---
source_file: "tests/test_workday_pairing.py"
type: "code"
community: "targets.py"
location: "L17"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/targetspy
---

# test_details_pair_with_correct_listing()

## Connections
- [[A listing without externalPath used to shift details onto the wrong jobs.]] - `rationale_for` [EXTRACTED]
- [[MonkeyPatch_6]] - `references` [EXTRACTED]
- [[WorkdayTenant]] - `uses` [INFERRED]
- [[asyncio_4]] - `references` [EXTRACTED]
- [[fake_detail()]] - `indirect_call` [INFERRED]
- [[fake_listing()]] - `indirect_call` [INFERRED]
- [[fetch_workday()]] - `calls` [EXTRACTED]
- [[parse_workday_url()]] - `calls` [EXTRACTED]
- [[test_workday_pairing.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/targetspy
# Priority 2.0

Priority answers which stored opportunity should be looked at first. It is an attention order from 0 to 100. It is not a second fit score, not an eligibility decision, and not a company ranking.

Fit stays the Phase 6 number on `Job.score`. Eligibility stays the Phase 9 state. Portfolio weights stay 40, 40, 15, and 5. Shortlist capacity, company cap, and diversity margin are unchanged. Applications, feedback, calibration, and monitoring do not read this formula back into their own decisions.

## Weights

`config/priority.yaml`, version `phase12-v2`. The weights sum to 100.

| Component | Weight | Meaning |
| --- | --- | --- |
| Fit | 32 | The stored fit score, unchanged. |
| Primary role alignment | 12 | Whether the primary family is a search target. |
| Secondary role bonus | 3 | A small extra when the job itself performs a second target function. |
| Eligibility | 16 | Phase 9 state. Clearly ineligible is 0. Unknown is 60, not 0. |
| Role confidence | 6 | high 100, medium 70, low 50. Missing confidence is left out. |
| JD evidence quality | 6 | Usable text is 80. A truncated or thin description is 40. Structured sections can raise a usable description toward 100. |
| Program evidence | 7 | The strongest explicit internship, MBA, or U.S. program fact. |
| Company domain relevance | 5 | One match between a factual company domain and the target families. |
| Freshness | 6 | 100 today, down to 40 at 45 days, then 40. |
| Dream company | 4 | The profile list only. An empty list is left out. |
| Workflow | 3 | Open 100, submitted or ignored 0, filtered or error 40. |

Fit is the largest piece and is still not the whole score. Eligibility stays large enough that a clearly ineligible job falls behind an otherwise similar unknown job. Company facts are capped so they cannot outrank fit or eligibility.

A missing component is left out of the average. It is not stored as zero. No company record, no secondary family, and no relevant domain are omissions, not penalties. The all-missing case is 50.

## Role alignment

Primary alignment, before weighting:

- Product management and consulting: 100
- Strategy and transformation, including technology strategy as that family's subfamily: 70
- Product marketing, marketing, and program or project operations: 45
- OTHER, UNKNOWN, and a missing family: left out

The secondary component is 100 when a second target family is present, and its weight is only 3. That is the whole bonus. A product role with a strategy secondary does not receive strategy's alignment score again. OTHER and UNKNOWN are never a secondary bonus. Portfolio weights are not this table. `role_family_component` still scales those portfolio weights and is not the priority alignment score.

## Program and domain evidence

Program evidence keeps the strongest fact only. An explicit MBA internship, MBA recruiting, or full-time MBA recruiting phrase is 100. A summer, graduate, or U.S. internship phrase is 70. A generic internship program is 40. U.S. operations or an office is 50. Saying both MBA and generic internship stays 100. A generic internship does not become an MBA signal.

Domain relevance is the mapping in `config/priority.yaml`. One relevant domain sets the component to 100. More matches do not add points. An unrelated domain is left out. Company size, revenue, and exchange are not inputs.

There is no prestige, culture, brand, or employer-quality component. An official source does not add points by itself. Sponsorship text on a company page is not a priority input and does not change Phase 9.

## Freshness, dream company, and workflow

Freshness still uses `posted_at`, or `discovered_at` when posted time is missing. The cache key is the UTC date, not the clock time. Dream company is still only the names on the profile. Workflow still lowers submitted and ignored jobs. Status is not changed. A clearly ineligible job stays stored.

## Hash

`phase12-v2` is stored with `priority_components`, `priority_reasons`, and `priority_input_hash`. The hash includes the weight table, the domain map, fit score and fit version, primary and secondary role fields, eligibility state and version, JD flags, the structured section states that affect evidence quality, the company signals that affect program or domain evidence, posted and discovered times, company name, status, the dream-company list, and `freshness_day`. Revenue, office count, and other unused company facts are not in the hash. Discovery labels and embeddings are not inputs.

The same inputs on the same UTC day reuse the stored score. A later day, or a change to a hashed input, computes the score again. Fit, eligibility, role, and status are not cleared because priority was computed.

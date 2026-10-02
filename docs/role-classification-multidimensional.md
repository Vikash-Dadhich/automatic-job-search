# Multi-dimensional role classification

Role classification says what the job is. It does not score the candidate, change eligibility, or change priority, shortlist, portfolio, or discovery weights. Those systems still read the primary family only.

## Contract

The classifier version is `phase5-v3`.

The primary family remains `role_family`, with `role_subfamily`, `role_confidence`, and `role_evidence`. Those names are unchanged.

A real second function is stored as:

- `role_secondary_family`
- `role_secondary_subfamily`
- `role_secondary_confidence`
- `role_secondary_evidence`

Families stay the existing set: `PRODUCT_MANAGEMENT`, `CONSULTING`, `STRATEGY_TRANSFORMATION`, `PRODUCT_MARKETING`, `PROGRAM_PROJECT_OPERATIONS`, `MARKETING`, `OTHER`, and `UNKNOWN`. Subfamilies stay the existing map. `TECHNOLOGY_STRATEGY` is a subfamily of `STRATEGY_TRANSFORMATION`, not a new family.

`OTHER` and `UNKNOWN` are never used just to fill the secondary field. When there is no second family, the secondary family, subfamily, and confidence are empty and the evidence list is empty.

Confidence is still `high`, `medium`, or `low`. A missing secondary classification has no confidence.

## What the classifier reads

It reads structured JD evidence when a current `phase19-v1` reading exists, then the normalized description, then the title. Discovery labels stay context and do not override the description. Company name, dream-company status, the candidate profile, and fit score are not inputs. Sponsorship, citizenship, and clearance are not role evidence.

## Function versus interaction

A secondary family requires the role to perform that function: more than one explicit phrase, or one phrase confirmed by structured JD evidence that is not an interaction note. "Collaborate with product managers" or "work closely with marketing" does not create that family. A truncated description does not receive a secondary family.

## Cache

A stored label is current only when `role_content_hash` matches the normalized JD and `role_classifier_version` is `phase5-v3`. A changed description clears the primary and secondary fields. An older classifier version is recomputed. The same hash and version are not recomputed.

## Non-goals

This does not change fit, eligibility, priority, shortlist selection, portfolio allocation, application flow, feedback, calibration, monitoring, or discovery capacity.

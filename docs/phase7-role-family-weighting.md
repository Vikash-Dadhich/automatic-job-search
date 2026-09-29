# Phase 7 role-family weighting

Phase 7 records how important a role family is in the candidate's internship search. It does not say whether the candidate matches the job, and it does not decide which job to open first.

## Four different questions

Discovery weighting asks how much search capacity a family should get. Those fractions live in `config/discovery.yaml` and drive how many queries run. Changing them changes search volume.

Candidate fit asks how well the candidate matches one job description. That number stays `score` when fit is available. Phase 7 does not read it and does not write it.

Role-family weighting asks how strategically important the classified family is inside the target internship portfolio. That number is `role_family_weight`.

Priority and ranking will later ask which job should get attention first, using fit, this weight, company, eligibility, and other signals. That combination is not built here. There is no product of fit and weight, no sum, and no new sort.

## Canonical portfolio

The portfolio is four buckets:

| Bucket | Weight |
| --- | --- |
| Product management | 40 |
| Consulting | 40 |
| Strategy and transformation | 15 |
| Everything else | 5 |

Those four buckets add to 100. The stored map does not. Product marketing, program and project operations, `OTHER`, and `UNKNOWN` each belong to the broad "everything else" bucket, so each of those families is stored as 5. The seven stored numbers add to 115. That is intentional. They are not seven mutually exclusive probabilities.

## Where the family comes from

The weight uses the Phase 5 `role_family` already stored on the job. It does not use the discovery family, discovery bucket, discovery query, title, source, company, dream-company list, or vector similarity.

Subfamilies do not have their own weights. `PM_CORE` and `APM_MBA_PM` use the product-management weight. Consulting subfamilies use 40. Strategy subfamilies use 15. Program, project, operations, and customer-success subfamilies use 5.

## Unknown classification

A missing family, `UNKNOWN`, or a name that is not a Phase 5 primary family receives the unknown weight, 5. The job is not filtered, the fit score is not lowered, and the status does not change. An unclassified job is uncertain, not a bad match.

## Configuration

The map is `config/role_family_weights.yaml`. `scorer/role_weights.py` loads it. `get_role_family_weight` is the only lookup. The file must name every Phase 5 primary family and no other key. Each weight is an integer from 0 through 100. A bad file raises instead of inventing a family or a default other than the unknown weight for a missing job label.

Discovery capacity is a separate file. Editing the portfolio file does not change how many searches run. Editing discovery capacity does not change `role_family_weight`.

## What is stored

`role_family_weight` and `role_family_weight_version` (`phase7-v1`) are written when a job row is saved. The value is computed from `role_family`. A caller-supplied weight is replaced. The model that scores fit does not set this field, and discovery does not set it. If the portfolio file later changes, the version string is how a later phase can see that a stored weight came from an older configuration. This phase does not rebuild old rows on its own.

## What this phase does not do

It does not multiply or add the fit score. It does not change tiers, statuses, hard filters, visa rules, the vector gate, prerank, the shortlist, outreach, or cover letters. It does not add company preference, recency, or a priority score.

# Phase 12 priority ranking

Priority answers which stored job should be looked at first. Fit answers how well the candidate matches the description. Priority reads the fit number. It does not calculate it again, and it does not remove jobs.

The result is `priority_score`, from 0 to 100, plus the component values and short factual reasons. `Job.score` stays the fit number. Tier and status are unchanged.

## Components

Each component is 0–100. The weights in `config/priority.yaml` sum to 100. The score is the weighted average of the components that are present. A missing component is left out of that average. It is not stored as zero.

| Component | What it reads | Missing or unknown |
| --- | --- | --- |
| Fit | `Job.score` when it is set | Left out. Not treated as 0. |
| Role family | Stored `role_family` portfolio weight | UNKNOWN and a missing family use weight 5, scaled like any other family. |
| Eligibility | Phase 9 state | Confirmed 100, likely 80, unknown 60, clearly ineligible 0. A missing state is left out. |
| Role confidence | high / medium / low | 100 / 70 / 50. Missing confidence is left out. |
| JD quality | `jd_status` and `jd_truncated` | Present 100, truncated 55, suspicious or missing 40. The job stays stored. |
| Freshness | `posted_at`, or `discovered_at` if posted time is absent | 100 today, down to 40 at 45 days, then 40. No age cutoff. |
| Dream company | Names listed on the profile | 100 if the existing company match hits, otherwise 0. An empty list is left out. |
| Workflow | `status` | Open jobs 100. Submitted or ignored 0. Filtered or error 40. Status itself is not changed. |

Role-family weight 40 scales to 100. Weight 15 scales to 38. Weight 5 scales to 13. Fit is not multiplied by 0.40.

Discovery family, discovery query, vector similarity, company size, and company prestige are not inputs. Dream-company status is only the profile list, not a quality judgment.

## Version

`phase12-v1` is stored with a hash of the inputs and the weight table. The same inputs reuse the stored priority. A changed fit number, role, eligibility, description flag, posted time, status, dream-company list, or weight table is computed again. Fit, eligibility, and role classification are not cleared because priority was computed.

Ordering when scores tie is fit number, then posted or discovered time, then job id.

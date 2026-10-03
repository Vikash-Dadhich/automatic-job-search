# Vector recovery

The embedding gate is unchanged. Cosine below the threshold is still a reject. Recovery only answers whether that reject may enter the existing fit scorer.

A job is recovered when all of these are true:

- It passed the hard filters.
- `eligibility_state` is not `CLEARLY_INELIGIBLE`.
- At least two independent evidence groups are present.
- At least one of those groups is a role or responsibility group.

The groups are:

- `primary_role`: stored primary family is a configured target, confidence is high or medium, and role evidence is present. `UNKNOWN` and `OTHER` do not count. Low confidence does not count.
- `secondary_role`: the same rule for the stored secondary family.
- `responsibility_function`: a configured multi-word phrase appears in structured responsibility text. Qualification text does not count.
- `mba_program`: the structured reading says `mba_internship` is true. The words MBA or internship alone do not count, and this group cannot recover a job by itself.

Dream companies, salary, and company prestige are not recovery inputs. The fit score, priority score, shortlist, and portfolio allocation are not changed here.

`vector_decision` is `pass` when the gate accepts the job, `reject` when recovery also declines, and `recovered` when the job goes on to the normal scorer. `vector_recovery`, `vector_recovery_reason`, and `vector_recovery_hash` record the recovery result. A changed job description clears them. A changed recovery version, config, job input, or candidate profile reopens a stored reject so the decision is made again. The stored hash includes a fingerprint of the profile, not the profile text. A recovery error leaves the vector reject in place.

Configuration is `config/vector_recovery.yaml`, version `phase10-v2`.

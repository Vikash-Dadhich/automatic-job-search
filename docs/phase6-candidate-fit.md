# Phase 6 candidate fit

This phase asks how well the candidate matches one job description. It does not ask what kind of role the job is, whether the candidate is eligible to work, or how the job should be ranked against other jobs.

Role classification says what the job is. Fit uses that label as context. The discovery query is not included in the fit prompt and does not change the score. Company name and dream-company preference do not add points. Vector similarity is not the fit score.

## Dimensions

The model scores eight dimensions. Weights are 20, 20, 15, 15, 10, 10, 5, and 5:

role alignment, experience relevance, skills, responsibilities, education and MBA context, experience level, location and work mode, and requirement risk.

A preferred gap is `unknown` or a light `gap`. A missing required item is a `gap`. A direct contradiction is a `conflict`. A skill the profile actually lists is a `confirmed_match`. Related work that is not the same job title is a `transferable_match`. Unknown is not stored as a negative.

## When the model is not called

If Phase 4 marked the description missing or suspicious, or the description is empty, fit is unavailable. The score stays empty. The job is not given 0 and is not filtered out. A description without that Phase 4 flag still goes through the existing scoring path so older rows keep their behavior.

The fit prompt uses education, experience, skills, and location or work-mode facts. It does not include contact details, profile URLs, visa status, or dream companies. The same description hash, that fit profile hash, and `phase6-v2` reuse the stored fit and do not call the model. A stored `phase6-v1` result is stale. A new description, a changed fit fact, or a new fit version asks again. A changed description also clears the stored fit when the job row is updated.

## Output

`score` remains the number downstream tiers use, and only when fit is available. Richer fields are `fit_confidence`, `fit_strengths`, `fit_gaps`, `fit_evidence`, `fit_dimensions`, `fit_version`, `fit_content_hash`, and `fit_profile_hash`.

Lines that name a concrete fact absent from the profile and the job text are dropped. A payload that is not valid JSON, uses a bad confidence, or uses a dimension outside the set is unavailable rather than a fake score.

Hard filters still run before fit. Tier rules, including dream-company tier placement, are unchanged and are not part of the fit number.

## Not in this phase

Search weights, company intelligence, visa policy, false-negative rescue, deduplication, ranking, and the shortlist are unchanged.

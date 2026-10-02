# Phase 16 feedback learning

This layer reads submitted applications and reports how often each recorded outcome showed up. It does not change fit, priority, role-family weights, eligibility, the shortlist, or portfolio allocation.

The raw history stays on `applications` and `application_events`. A feedback run stores only derived counts and rates.

## Who is counted

An application is counted only when `submitted_at` is on or before `as_of`. A pre-fill still `in_progress`, a `manual_review` with no submission time, a shortlist card, and a portfolio allocation are not applications in this layer.

An outcome counts only when its event time is on or before `as_of`. The current `application.outcome` column is not used, because that value can move after the cutoff. A submission on 1 January with an interview event on 1 February is an application with no interview on 15 January, and an application with an interview on 1 March.

No outcome event by the cutoff means the result is unknown. Unknown is not rejected and not a success.

## Rates

Denominators are submitted applications, except `offer_rate_among_known`, which uses applications that have at least one outcome event by the cutoff.

`screening_rate`, `interview_rate`, `offer_rate`, `rejected_rate`, and `ghosted_rate` count applications that have that exact event. They are not exclusive: a later interview does not remove a screening event.

Group rates use the lists in `config/feedback.yaml`:

- early positive: screening, interview, or offer
- strong positive: interview or offer
- final positive: offer
- negative: rejected or ghosted

## Segments

The same rates are computed for the whole set, for fit bands, for priority bands, for role family, for role subfamily, for eligibility, for application method, and for job source. A missing fit or priority score is the band `missing`. A missing role family is `UNKNOWN`, which is not folded into `OTHER`. Empty subfamilies are omitted. Company-level rates are not computed.

Bands are 0–49, 50–64, 65–74, 75–84, and 85–100.

## Evidence and shrinkage

`minimum_overall` is 20, `minimum_segment` is 10, and `minimum_subfamily` is 20. Below that, the signal is `insufficient_evidence` and the adjustment is 0.

When the sample is large enough, the strong-positive rate is pulled toward the overall strong-positive rate:

`(sample * segment rate + prior * overall rate) / (sample + prior)`

`shrinkage_prior` is 20. A gap of 0.20 after shrinkage is an adjustment of 5, then clamped to `max_adjustment` (5). The overall segment is the baseline, so its adjustment is 0. The adjustment is a separate integer. It is not multiplied into fit or priority. `priority_integration` is false, and this phase does not read the adjustment from anywhere in scoring.

`phase16-v1` and a hash of the configuration are stored on each run. The same applications, events, configuration, and `as_of` produce the same signals. Phase 17 is where those signals would be tested before any scoring change. That phase is not implemented.

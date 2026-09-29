# Phase 9 visa and eligibility

Phase 9 asks whether a posting is compatible with the candidate's known authorization and other hard constraints. It does not score how well the candidate matches the work, and it is not legal advice. It is a heuristic over the posting text and `config/profile.yaml`.

## States

The stored result is one of:

- `CONFIRMED_ELIGIBLE` — the posting explicitly accepts a path the profile can use, and nothing in the text is a hard conflict.
- `LIKELY_ELIGIBLE` — the posting looks like an internship, sponsorship is not refused, and no hard conflict is stated.
- `UNKNOWN` — an important restriction is ambiguous, or the posting lists dates the profile cannot confirm.
- `CLEARLY_INELIGIBLE` — the posting states a concrete conflict.

Missing sponsorship is not a rejection. A posting that never mentions visas stays `LIKELY_ELIGIBLE` when the title is an internship. Wording such as "authorized to work" without a permanent-authorization rule stays `UNKNOWN`.

## What the profile contributes

Candidate facts come from the `Profile` object: F-1/CPT status, sponsorship flags, degrees, graduation dates, experience dates, and location rules. Future full-time sponsorship does not by itself reject an internship. The engine does not infer citizenship or clearance, and it does not invent an internship availability window.

## Sponsorship, citizenship, and clearance

Visa phrases use the same hostile and friendly patterns as the ingest filter. Hostile language wins when a posting also says sponsorship is available. "We sponsor employee events" and "international candidates welcome" are not visa sponsorship.

U.S.-citizens-only language is `CLEARLY_INELIGIBLE` for this profile. Equal-opportunity wording is not a citizenship rule.

An active or required clearance is `CLEARLY_INELIGIBLE`. "Ability to obtain a clearance preferred" is not.

Explicit permanent or unrestricted work authorization is `CLEARLY_INELIGIBLE` in this engine. The older sponsorship signal still classifies "Must have permanent work authorization" and "without sponsorship" as unknown, so ingest does not newly drop those two locked phrases. The eligibility record is the place that marks a clear permanent-authorization requirement.

## Education, graduation, experience, location, dates

MBA required, or current enrollment in an MBA, matches the profile. MBA preferred does not block. A mandatory current bachelor's program does not match an MBA student. A graduation window that excludes June 2028 blocks. "Graduating in 2028" matches. Preferred timing does not block. No graduation sentence leaves that dimension unknown and does not reject the job.

A mandatory experience floor is compared with the existing years-of-experience ceiling. Preferred years do not block. The ingest years filter is unchanged.

A U.S. office, a relocation requirement, or a remote posting is not rejected because Seattle is the preferred city. Internship dates in the posting stay unknown when the profile has no availability window, and the overall state stays `UNKNOWN` rather than a guess.

## Cache and storage

The version is `phase9-v1`. A stored result is reused when the job description hash, the eligibility profile hash, and the version all match. The profile hash covers authorization, education, experience dates, and location flags. It does not include dream companies, fit, discovery, or company intelligence.

Columns on `jobs`: `eligibility_state`, `eligibility_reasons`, `eligibility_evidence`, `eligibility_dimensions`, `eligibility_version`, `eligibility_content_hash`, `eligibility_profile_hash`. A changed description clears them. An unchanged description does not.

Eligibility runs after a job is saved and again during scoring. A failure is logged and does not stop ingestion or change `score`, tier, or status.

## What this phase does not do

It does not change candidate-fit scoring, role-family weights, company facts, discovery, the vector gate, or ranking. The same description produces the same eligibility result if only the discovery query, discovery family, company record, fit score, role weight, or vector score changes.

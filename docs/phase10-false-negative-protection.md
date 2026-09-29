# Phase 10 false-negative protection

A job is rejected only when the posting clearly establishes a disqualifier. Missing, ambiguous, preferred, or unknown information is not treated as that disqualifier.

The hard filters still drop an explicit clearance requirement, an explicit sponsorship refusal, a citizenship-only rule, a mandatory years floor above the candidate's ceiling, a blocked company, and a title with no internship signal when internship-only mode is on. A preferred clearance mention does not, even when another sentence says must or active about something else. An explicit intern or internship title is not dropped because it also contains a seniority word such as VP.

Unknown role labels, unknown eligibility, a missing or short description, and a preferred years statement do not by themselves remove the job. Fit still stores an unknown judgment as unknown. Truncated descriptions stay incomplete for fit, as Correction 2 defined.

This phase does not rank jobs, merge identities, or change fit weights, eligibility state names, or discovery.

# Phase 17 calibration

Phase 16 reports historical rates. Phase 17 checks whether those rates describe later applications. It does not turn feedback on.

Training uses applications whose `submitted_at` is on or before the fold cutoff, and only events on or before that cutoff. Holdout applications are submitted after the cutoff. Their outcomes are used only to score the prediction. A random split is not used.

An application is matured when `submitted_at` plus `evaluation_maturity_days` (default 45) is on or before the fold's evaluation end. Until then it is left out. A matured application with no outcome event in the evaluation window is not counted as a failure. Screening, rejection, ghosting, interview, and offer are known outcomes. Strong positive means an interview event or an offer event, counted once even if screening and both later events are present.

The baseline prediction is the training-window strong-positive rate. The feedback prediction is the segment's shrunk rate from that same window when Phase 16 marked the segment sufficient. Otherwise the baseline is used. The holdout does not decide the fallback.

Brier score is the mean squared error of those predictions against 1 or 0. Calibration error is the absolute gap between the training prediction and the holdout rate. Coverage is the share of evaluated holdout applications that had a sufficient training segment. A negative Brier gap means feedback's error was lower in that fold. The report does not name a winner.

Folds are expanding chronological windows, up to `fold_count` (default 3). A fold is kept only when both the training minimum and the holdout minimum are met. If none are met, the report status is `insufficient_history` and no metrics are invented.

Top-slice rates describe the existing priority order. Hypothetical priority, when the config flag is on, adds the training role-family adjustment in memory only. The default is off. Nothing writes `Job.score`, `Job.priority_score`, role-family weight, eligibility, shortlist, portfolio, or application rows.

Company-level learning is not included. Phase 18 is not implemented.

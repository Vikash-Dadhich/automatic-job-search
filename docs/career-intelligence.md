# Career Intelligence

Career Intelligence answers whether an internship is useful for this candidate's MBA transition and later career. It is not a fit score, not a priority score, and not a prediction of an interview, an offer, or a full-time conversion.

Fit stays the model's reading of how the profile matches this posting. Priority 2.0 and Shortlist 2.0 do not read this layer. Telegram still sends the persisted shortlist and does not add or drop jobs because of it.

## Dimensions

Each scored dimension is `STRONG`, `MODERATE`, `WEAK`, or `UNKNOWN`.

| State | Stored score |
| --- | --- |
| STRONG | 100 |
| MODERATE | 60 |
| WEAK | 20 |
| UNKNOWN | omitted |

Conversion and MBA recruiting are `CONFIRMED`, `NOT_FOUND`, or `UNKNOWN`. `CONFIRMED` maps to 100. `NOT_FOUND` means the posting was readable and did not contain the phrase. It is not a "no" and it is not a penalty. `UNKNOWN` means the posting could not be read. Both are omitted from the overall score.

The dimensions are career transition, career story, internship quality, learning value, conversion signal, MBA recruiting, opportunity quality, application effort, and competitiveness.

Transition, story, learning, and opportunity quality use structured responsibility text and the stored role family. A missing previous title is not a negative. Qualification-only mentions and company prestige are not used. Conversion uses explicit phrases such as "return offer" or "high-performing interns". MBA recruiting uses an explicit MBA internship, recruiting phrase, or a stored company-intelligence program signal.

Competitiveness checks explicit required years, a required MBA, and required qualification lines that overlap profile skills. An unchecked requirement stays unknown. It does not copy the fit score.

Application effort records an explicit cover letter, portfolio, essay, or writing sample. Its weight is 0, so it does not pull the overall score down.

## Overall score

`config/career_intelligence.yaml`, version `career-intelligence-v1`, gives weight 1 to every dimension except application effort. The overall score is the rounded mean of the dimensions that have a number. Unknown and not-found dimensions are left out. If none remain, the overall score is empty.

## Cache

One `career_intelligence` row is stored per job. `content_hash` is a fingerprint of the version, config, profile fingerprint, description, structured JD, role classification, and company-intelligence context. The raw profile is not stored. The row is reused when that fingerprint matches and rewritten when it does not.

## Failures

A failed reading is logged and discarded. Fit, priority, eligibility, shortlist rank, and application state stay as they were.

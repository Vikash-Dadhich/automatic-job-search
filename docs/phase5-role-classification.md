# Phase 5 role classification

This phase answers what kind of role a posting describes. It does not answer whether the candidate should apply.

Discovery family is how the job was found. Role classification is what the job is. Candidate fit is a later phase.

## Taxonomy

Primary families: product management, consulting, strategy and transformation, product marketing, program/project/operations, other, and unknown.

Subfamilies follow the Phase 2 buckets where the description supports them, plus strategy and operations, corporate development, and customer success. Other and unknown have no subfamily.

Other means the role is understood and is outside this list, such as software engineering or investing. Unknown means the title and description are too thin, or they conflict so evenly that the label would be a guess.

## Inputs

The classifier reads the title and the normalized job description. Discovery family, bucket, and query can be passed in and are not copied onto the role. The candidate profile is not loaded.

A description under 80 characters is unknown and is not sent to a model. Clear phrase evidence is decided locally. If a long description has no clear label, an optional model may be asked. The model must return the allowed labels. Invalid JSON, an unknown label, or a model error becomes unknown. The job stays stored either way.

## Output

Stored fields are `role_family`, `role_subfamily`, `role_confidence` (`high`, `medium`, or `low`), `role_evidence`, `role_classifier_version` (`phase5-v4`), and `role_content_hash`. A second family, when the role itself performs one, is stored beside those fields. See `docs/role-classification-multidimensional.md`.

Confidence is how sure the label is. It is not a fit score and it does not change tier, rank, or status.

Evidence is one or two sentences about the posting. It does not mention the candidate.

## When it runs again

If the stored description hash is unchanged and the label was produced by this classifier version, a later ingest keeps the stored label. If the description hash changes, the old label is cleared and the new text is classified. That is the same moment embeddings are cleared. A refetch that is too short to replace a good description also leaves the label alone.

## Limits

Phrase rules cover the common wording in the tests. Unusual wording can stay unknown until a model call, or be labeled other when the text is clearly a different function. Employer brand is not used. Cross-board identity is unchanged.

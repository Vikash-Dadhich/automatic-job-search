# Phase 4 JD ingestion

Every discovered posting gets one normalized description, plus a record of whether that text is missing, usable, cut off, or too short to trust. This is extraction quality, not job quality and not a role classification.

## Flow

JobSpy stores the board text on `description_clean`. Workday stores the detail HTML on `description_html` and does not invent text when that detail is missing. `RawPosting.ensure_clean_description()` runs `normalize_description()` and writes:

- `description_clean` — the text that is stored and hashed
- `jd_status` — `missing`, `present`, `truncated`, or `suspicious`
- `jd_char_count` — length of the stored text
- `jd_truncated` — whether the stored text was cut, including a later pass that still contains the trim marker
- `jd_extraction_path` — `empty`, `plain`, `markdown`, `html`, or `sections`

Discovery family, bucket, and query stay on their own fields.

## Normalization

HTML parsing removes script, style, nav, footer, header, and svg. Malformed HTML is still reduced to text. Whitespace is collapsed. A line that is an exact repeat of the line above is dropped once.

If the text has a known heading, the words before that heading are kept when they are long enough to be a real introduction. Lines that are only equal-opportunity, privacy, cookie, or copyright wording are left out of that introduction. Headings that are not on the list stay in the body instead of being deleted. If the headed extract collapses below 80 characters, the full normalized text is kept.

`suspicious` means the normalized text is non-empty and shorter than 80 characters, and it was not truncated. That threshold is about extraction completeness, not whether the role is a good fit. `truncated` means the stored text was cut with the existing head-and-tail trim. The storage cap is unchanged: twice `max_jd_chars`, and at least 4,000 characters. Scoring still applies its own shorter cap later.

## Hash and upsert

`content_hash` is the SHA-256 of the normalized stored text, lowercased. Matching HTML and plain text hash the same after normalization. A real wording change hashes differently.

A later fetch that is `missing` or `suspicious` does not replace a stored `present` or `truncated` description, and it does not clear embeddings. A later `present` or `truncated` description replaces the stored text. If that hash changes, embeddings are cleared and an unreviewed scored or staged job is sent back to be scored, as before. Submitted and in-review jobs are still left alone.

Rows saved before these columns existed are treated as usable when `description_clean` is at least 80 characters.

## Limits

The heading list is small on purpose. Unusual headings survive only because the surrounding text is kept, not because every company label is recognized. Cross-board job identity is unchanged: source plus external id. Nothing here classifies the role or scores the candidate.

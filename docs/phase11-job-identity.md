# Phase 11 job identity

One real posting should be one job. If the evidence is not strong enough, the postings stay separate.

The same source and external id is always one job. Seeing it again updates that row. The first discovery family, bucket, and query stay. Fit, eligibility, role classification, company intelligence, and the vector score stay unless the description hash actually changes. That content-change rule is the one already used for a rewritten job description.

A different source can attach to that job in two cases only. The posting URLs canonicalize to the same job link, after tracking parameters and the fragment are removed, and the locations do not name two different places. Or the company, title, and location all agree and the normalized description hash is the same, and the URLs do not point at two different postings. A query parameter that can be the posting id, such as `id`, is kept. `id=123` and `id=456` stay different. A homepage is not a posting identity.

Same company and title are not enough. Different cities stay separate. A missing location does not block a matching posting URL, and it is not enough for the company-title-location match. Fit score, role family, and vector similarity are not identity.

Rows already stored are not merged in bulk. A `canonical_url` value is filled the next time that job is saved. Until then, an older row can only match a new source when its description hash, company, title, and location already agree.

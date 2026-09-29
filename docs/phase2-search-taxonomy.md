# Phase 2 search taxonomy

The search vocabulary was expanded so internship discovery is less dependent on one exact title. Recall comes first. A phrase is not a fit score, and family weights are still only search capacity: 40% product management, 40% consulting, 15% strategy and transformation, 5% other.

Phase 1 still decides how many of these phrases run. With no capacity cap, every enabled phrase runs once. Title variants are alternate wordings on the same bucket. They are searched after that bucket's primary queries. They are not a second taxonomy.

## What was added

Product management now covers manager and management wording, a broad "Product Intern", associate and MBA word order, digital and platform product titles, and product development and innovation.

Consulting now covers consultant and consulting wording, a broad "Consulting Intern", MBA consulting, advisory wording used by large firms, and digital and transformation consulting. Company names are not queries.

Strategy and transformation now covers corporate, enterprise, and growth strategy, strategy and operations, planning, commercial and revenue strategy, transformation word order, and go-to-market strategy. Generic strategy stays in corporate strategy.

Other stays small: product marketing, program management, project management, customer success, customer experience, and one business-operations phrase.

Generic titles were not added: MBA intern, business intern, marketing intern, software engineering, data science, finance, investing, sales, or HR.

## Ambiguous phrases

| Phrase | Home | Why it stays |
|---|---|---|
| Strategy Intern | Corporate strategy | Many relevant internships never say "corporate". Classification can drop the rest. |
| Product Intern | Product manager | Same reason. Dropping it would miss untitled product internships. |
| Consulting Intern | Management consulting | Firms often post this exact title. |
| Advisory Intern | Management consulting | Common Big 4 and consulting wording. Financial-advisory noise is a later filter. |
| Corporate Development Intern | Corporate strategy | Often a corporate strategy-adjacent MBA internship. Banking uses of the same words are not searched on purpose and are not removed here. |
| Business Operations Intern | Other | Adjacent, and easy to over-match. It is one phrase, not an operations family. |
| Customer Success Intern | Other | Kept from Phase 1. Still broad, still inside the small family. |
| Program Manager Intern | Program management | Common title. "Program Management Intern" is the wording twin. |
| Project Manager Intern | Project management | Same pattern. Sales operations, revenue operations, and commercial operations were left out. |

Strategy and operations lives under business strategy, not under Other. The MBA wording is there too, and the generic wording remains.

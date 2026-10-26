"""Measure profile-to-job cosine similarity under a few setups. Costs a few cents at most."""

from __future__ import annotations

import asyncio

from config.profile import load_profile
from config.settings import get_settings
from scorer.embeddings import OpenAIEmbedder, cosine, profile_embed_text
from scorer.fit import fit_context_block

JOBS = {
    "PM intern (MBA)": (
        "Product Manager Intern, MBA Level - Summer 2027\nAcme Games\n"
        "You will own a roadmap, work with engineering and design, run customer interviews, "
        "write requirements, analyze product metrics and present recommendations to leadership. "
        "Pursuing an MBA with an interest in product management."
    ),
    "Strategy consulting intern": (
        "Strategy Intern, MBA\nBigCo\n"
        "Support the corporate strategy team with market sizing, competitive analysis, financial "
        "modeling and executive presentations. Rising second year MBA students."
    ),
    "Business ops intern": (
        "Business Operations Intern\nStartup Inc\n"
        "Help the operations team improve processes, build dashboards, and run cross functional "
        "projects across sales, finance and product."
    ),
    "Software engineer intern": (
        "Software Engineer Intern (Summer 2027)\nFigma\n"
        "Write production code in TypeScript and C++, design APIs, review code, and ship features "
        "used by millions. Pursuing a BS or MS in computer science."
    ),
    "PhD research intern": (
        "PhD Intern, Data Science\nFigma\n"
        "Conduct original research in machine learning, publish papers, and work with applied "
        "scientists on large scale models. Currently enrolled in a PhD program."
    ),
    "Accounting intern": (
        "Accounting Intern\nCoinbase\n"
        "Assist with month end close, reconciliations, journal entries and audit support. "
        "Pursuing a degree in accounting."
    ),
}


async def main() -> None:
    settings = get_settings()
    profile = load_profile()
    summary = (
        "MBA candidate at UW Foster with five years of software engineering and engineering "
        "management experience in financial services, co-founder and technical product lead of a "
        "startup. Seeking summer 2027 internships in product management, management consulting "
        "and strategy."
    )
    profiles = {
        "current static block": profile_embed_text(profile),
        "fit context block": fit_context_block(profile),
        "short summary": summary,
    }
    jobs = list(JOBS.items())
    embedder = OpenAIEmbedder()
    lines = [f"model={settings.openai_embedding_model} dims={settings.vector_dimensions}"]
    lines.append(f"profile lengths: { {k: len(v) for k, v in profiles.items()} }")
    texts = [*profiles.values(), *(text for _name, text in jobs)]
    vectors = await embedder.embed(texts)
    pvecs = vectors[: len(profiles)]
    jvecs = vectors[len(profiles) :]
    for (pname, _), pvec in zip(profiles.items(), pvecs, strict=True):
        lines.append(f"-- {pname}")
        for (jname, _), jvec in zip(jobs, jvecs, strict=True):
            lines.append(f"   {cosine(pvec, jvec):+.3f}  {jname}")
    # Job to job: do similar jobs cluster?
    lines.append("-- job to job")
    lines.append(f"   PM vs strategy {cosine(jvecs[0], jvecs[1]):+.3f}")
    lines.append(f"   PM vs SWE {cosine(jvecs[0], jvecs[3]):+.3f}")
    print("::notice title=Probe::" + "%0A".join(lines))


asyncio.run(main())

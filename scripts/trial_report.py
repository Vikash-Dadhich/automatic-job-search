"""Print a short report of a trial database as GitHub notice annotations.

Usage: python scripts/trial_report.py storage/trial.db [pipeline_output.txt]
Reads the database only. It never calls the network or any model.
"""

from __future__ import annotations

import re
import sqlite3
import sys
from collections import Counter
from pathlib import Path


def _notice(title: str, lines: list[str]) -> None:
    clean = [line.replace("%", "%25").replace("\r", " ").replace("\n", " ") for line in lines]
    body = "%0A".join(clean)
    print(f"::notice title={title}::{body}")


_RELEVANT = re.compile(
    r"product|strateg|consult|business|operations|marketing|program|analyst|growth|"
    r"partnership|finance|\bmba\b|associate|transformation|chief of staff",
    re.IGNORECASE,
)


def _vector_report(conn: sqlite3.Connection) -> None:
    rows = conn.execute(
        "SELECT source, company, title, vector_score, vector_decision, role_family FROM jobs"
    ).fetchall()
    decisions = Counter(str(row["vector_decision"]) for row in rows)
    values = sorted(r["vector_score"] for r in rows if r["vector_score"] is not None)
    spread = (
        [f"min {values[0]:.2f}  median {values[len(values) // 2]:.2f}  max {values[-1]:.2f}"]
        if values
        else ["no vector scores"]
    )
    _notice("Vector gate", [f"decisions: {dict(decisions)}", *spread])
    ranked = sorted(
        (r for r in rows if r["vector_score"] is not None),
        key=lambda r: r["vector_score"],
        reverse=True,
    )
    _notice(
        "Highest vector scores",
        [
            f"{r['vector_score']:.2f} {r['vector_decision']} {r['source']} {r['company']} | "
            f"{r['title']}"
            for r in ranked[:15]
        ]
        or ["none"],
    )
    relevant = [r for r in rows if _RELEVANT.search(r["title"] or "")]
    by_source = Counter(str(r["source"]) for r in relevant)
    _notice(
        "Relevant-looking titles",
        [
            f"{len(relevant)} of {len(rows)} titles look like business roles: {dict(by_source)}",
            *[
                f"{(r['vector_score'] if r['vector_score'] is not None else -1):.2f} "
                f"{r['vector_decision']} {r['company']} | {r['title']}"
                for r in relevant[:25]
            ],
        ],
    )
    families = Counter(str(r["role_family"]) for r in rows)
    _notice("Role families", [str(dict(families))])
    linked = [r for r in rows if str(r["source"]) in {"linkedin", "Source.linkedin"}][:10]
    _notice(
        "LinkedIn sample",
        [f"{r['vector_score']} {r['vector_decision']} {r['company']} | {r['title']}" for r in linked]
        or ["none"],
    )


def main() -> int:
    db = Path(sys.argv[1])
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT source, status, tier, score, company, title, location, fit_confidence, "
        "last_error, url FROM jobs"
    ).fetchall()

    by_status = Counter(str(row["status"]) for row in rows)
    by_source = Counter(str(row["source"]) for row in rows)
    scored = [row for row in rows if row["score"] is not None]
    scores = sorted((row["score"] for row in scored), reverse=True)
    _notice(
        "Counts",
        [
            f"jobs saved: {len(rows)}",
            f"by status: {dict(by_status)}",
            f"by source: {dict(by_source)}",
            f"scored: {len(scored)}  best scores: {scores[:10]}",
            f"errors: {sum(1 for r in rows if r['last_error'])}",
        ],
    )

    top = sorted(scored, key=lambda row: row["score"], reverse=True)[:12]
    _notice(
        "Top scored",
        [
            f"{r['score']:>3} T{r['tier']} {r['company']} | {r['title']} | {r['location']}"
            for r in top
        ]
        or ["nothing scored"],
    )

    kept = [row for row in rows if str(row["status"]) in {"Status.discovered", "discovered"}]
    _notice(
        "Waiting to be scored",
        [f"{r['company']} | {r['title']} | {r['location']}" for r in kept[:12]] or ["none"],
    )

    errors = [row for row in rows if row["last_error"]][:5]
    if errors:
        _notice("Errors", [f"{r['company']} | {str(r['last_error'])[:160]}" for r in errors])

    _vector_report(conn)

    if len(sys.argv) > 2:
        out = Path(sys.argv[2]).read_text(encoding="utf-8", errors="replace")
        _notice("Pipeline output", [out[-1800:]])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

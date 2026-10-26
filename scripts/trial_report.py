"""Print a short report of a trial database as GitHub notice annotations.

Usage: python scripts/trial_report.py storage/trial.db [pipeline_output.txt]
Reads the database only. It never calls the network or any model.
"""

from __future__ import annotations

import sqlite3
import sys
from collections import Counter
from pathlib import Path


def _notice(title: str, lines: list[str]) -> None:
    clean = [line.replace("%", "%25").replace("\r", " ").replace("\n", " ") for line in lines]
    body = "%0A".join(clean)
    print(f"::notice title={title}::{body}")


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

    if len(sys.argv) > 2:
        out = Path(sys.argv[2]).read_text(encoding="utf-8", errors="replace")
        _notice("Pipeline output", [out[-1800:]])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

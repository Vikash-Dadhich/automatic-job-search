"""Child process for one JobSpy query at a time.

Stdin is JSON lines. Stdout is one JSON object per line. Logging stays on stderr
so it cannot break the result line. This process is killed by its parent when a
query exceeds ``jobspy_query_timeout_seconds``. The parent sends one site per line.
"""

from __future__ import annotations

import json
import sys
from typing import Any

from config.targets import SearchConfig
from scraper.linkedin_jobspy import _scrape_term


def _records(frame: Any) -> list[dict[str, Any]]:
    if frame is None or getattr(frame, "empty", True):
        return []
    raw = frame.to_json(orient="records", date_format="iso", default_handler=str)
    parsed = json.loads(raw)
    if not isinstance(parsed, list):
        return []
    return [row for row in parsed if isinstance(row, dict)]


def _one(payload: dict[str, Any]) -> dict[str, Any]:
    search = SearchConfig.model_validate(payload["search"])
    sites = [str(site) for site in payload["sites"]]
    term = str(payload["term"])
    try:
        frame = _scrape_term(search, term, sites)
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
    return {"ok": True, "records": _records(frame)}


def main() -> None:
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            body = {"ok": False, "error": str(exc)}
        else:
            if not isinstance(payload, dict):
                body = {"ok": False, "error": "query payload must be an object"}
            else:
                body = _one(payload)
        sys.stdout.write(json.dumps(body) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()

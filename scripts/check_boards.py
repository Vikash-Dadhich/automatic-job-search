"""Check every board in config/targets.yaml and print the result as annotations.

Network only to the public board feeds. No OpenAI, no database.
"""

from __future__ import annotations

import asyncio

from config.targets import load_targets
from scraper.ats_boards import check_boards


def _notice(title: str, lines: list[str]) -> None:
    print(f"::notice title={title}::" + "%0A".join(line.replace("%", "%25") for line in lines))


async def main() -> None:
    boards = load_targets().ats_boards
    results = await check_boards(boards)
    good = [r for r in results if r["status"] == "ok"]
    bad = [r for r in results if r["status"] != "ok"]
    _notice("Summary", [f"{len(good)} working, {len(bad)} not working, {len(results)} checked"])
    _notice(
        "Not working",
        [f"{r['name']} ({r['provider']}:{r['token']}) {r['status']}" for r in bad] or ["none"],
    )
    # Keep each annotation small enough to read.
    ordered = sorted(good, key=lambda r: -int(str(r["business_internships"])))
    for start in range(0, len(ordered), 40):
        chunk = ordered[start : start + 40]
        _notice(
            f"Working {start // 40 + 1}",
            [
                f"{r['name']} {r['provider']}:{r['token']} open={r['open_roles']} "
                f"business_internships={r['business_internships']}"
                for r in chunk
            ],
        )


asyncio.run(main())

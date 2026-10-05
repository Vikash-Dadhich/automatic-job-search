"""One JobSpy query per process so a hung scrape can actually be stopped.

``asyncio.wait_for`` only cancels the awaiting task. A thread blocked in
JobSpy keeps running, and so do its sockets. This module starts one child
process, reads one JSON line per query, and on timeout, cancellation, or a
broken result line kills the child's process group. The next query starts a
new process. Only one child exists at a time.

Stdout is only the JSON-line protocol. Diagnostics stay on stderr.

``STDOUT_LIMIT`` is 16 MiB, not asyncio's 64 KiB default. One query can return
50 rows on each of four sites with full descriptions, which is several
megabytes of JSON. The parent holds at most one line, then discards it. A line
past this limit fails that query, the worker is reaped, and the next query
starts clean. It is not a silent empty result.
"""

from __future__ import annotations

import asyncio
import json
import os
import signal
from typing import Any

from scraper.redact import redact_error

# One in-flight result line. Sized for a full four-site query with descriptions.
STDOUT_LIMIT = 16 * 1024 * 1024


class QueryTimeoutError(Exception):
    """The query process was killed because it exceeded the configured limit."""

    def __init__(self, timeout: float) -> None:
        self.timeout = timeout
        super().__init__(
            f"query exceeded {timeout:g}s and the worker process was stopped"
        )


async def kill_process_group(proc: asyncio.subprocess.Process) -> None:
    """Stop the child and every process it spawned. Wait until it is reaped."""
    if proc.returncode is not None:
        return
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError:
        return
    except OSError:
        proc.kill()
    try:
        await asyncio.wait_for(proc.wait(), timeout=5)
    except TimeoutError:
        proc.kill()
        await proc.wait()


class LineWorker:
    """A long-lived JSON-line child. A timeout kills it; the next call respawns."""

    def __init__(self, argv: list[str], *, stream_limit: int = STDOUT_LIMIT) -> None:
        self.argv = argv
        self.stream_limit = stream_limit
        self.proc: asyncio.subprocess.Process | None = None
        self.stderr_tail = ""
        self._drain: asyncio.Task[None] | None = None

    async def request(self, payload: dict[str, Any], timeout: float) -> dict[str, Any]:
        await self._ensure()
        proc = self.proc
        if proc is None or proc.stdin is None or proc.stdout is None:
            raise RuntimeError("jobspy worker is not running")
        proc.stdin.write(json.dumps(payload).encode() + b"\n")
        await proc.stdin.drain()
        try:
            raw = await _read_json_line(proc, timeout)
        except TimeoutError:
            await self._stop()
            raise QueryTimeoutError(timeout) from None
        except asyncio.CancelledError:
            await self._stop()
            raise
        except (ValueError, asyncio.LimitOverrunError) as exc:
            await self._stop()
            raise RuntimeError(
                redact_error(f"jobspy worker output exceeded the reader limit: {exc}")
            ) from None
        if raw is None:
            detail = self.stderr_tail or "jobspy worker exited before a result"
            await self._stop()
            raise RuntimeError(redact_error(detail))
        return raw

    async def close(self) -> None:
        await self._stop()

    async def _ensure(self) -> None:
        if self.proc is not None and self.proc.returncode is None:
            return
        self.stderr_tail = ""
        self.proc = await asyncio.create_subprocess_exec(
            *self.argv,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            start_new_session=True,
            limit=self.stream_limit,
        )
        self._drain = asyncio.create_task(self._drain_stderr())

    async def _stop(self) -> None:
        proc = self.proc
        self.proc = None
        drain = self._drain
        self._drain = None
        if proc is not None and proc.returncode is None:
            await kill_process_group(proc)
        if drain is not None:
            drain.cancel()
            try:
                await drain
            except asyncio.CancelledError:
                pass

    async def _drain_stderr(self) -> None:
        proc = self.proc
        if proc is None or proc.stderr is None:
            return
        chunks: list[bytes] = []
        while True:
            block = await proc.stderr.read(4096)
            if not block:
                break
            chunks.append(block)
            kept = b"".join(chunks)[-2000:]
            chunks = [kept]
            self.stderr_tail = redact_error(kept.decode("utf-8", errors="replace"), limit=500)


async def _read_json_line(
    proc: asyncio.subprocess.Process,
    timeout: float,
) -> dict[str, Any] | None:
    """Read until one JSON object, ignoring stray log lines. Bound the whole wait."""
    if proc.stdout is None:
        return None
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout
    while True:
        remaining = deadline - loop.time()
        if remaining <= 0:
            raise TimeoutError
        raw = await asyncio.wait_for(proc.stdout.readline(), remaining)
        if not raw:
            return None
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
        return {"ok": False, "error": "jobspy worker returned a non-object"}


def worker_argv() -> list[str]:
    import sys

    return [sys.executable, "-m", "scraper.jobspy_worker"]

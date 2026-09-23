"""Long-running service: APScheduler + Telegram long-poll."""

from __future__ import annotations

import asyncio
import signal
from typing import Any

import structlog

from bot.poller import run_polling
from config.settings import get_settings
from core.db import init_db
from core.logging import configure_logging
from orchestrator.scheduler import build_scheduler

log = structlog.get_logger(__name__)


async def run_service(
    *,
    run_poller: bool = True,
    stop_event: asyncio.Event | None = None,
) -> None:
    """Start the scheduler and (optionally) the Telegram poller until stopped.

    SIGINT/SIGTERM set the stop event and shut down the scheduler gracefully.
    """
    settings = get_settings()
    configure_logging(settings.log_level)
    await init_db()

    stop = stop_event or asyncio.Event()
    scheduler = build_scheduler()
    scheduler.start()
    log.info(
        "service_started",
        run_poller=run_poller,
        jobs=[j.id for j in scheduler.get_jobs()],
        timezone=settings.timezone,
    )

    loop = asyncio.get_running_loop()

    def _request_shutdown(signame: str = "signal") -> None:
        log.info("service_shutdown_requested", signal=signame)
        stop.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _request_shutdown, sig.name)
        except (NotImplementedError, RuntimeError):
            # Windows / restricted environments: fall back to default
            signal.signal(sig, lambda *_args, s=sig: _request_shutdown(s.name))

    poller_task: asyncio.Task[Any] | None = None
    try:
        if run_poller:
            poller_task = asyncio.create_task(
                run_polling(stop_event=stop),
                name="telegram_poller",
            )
            # Also wait for stop so we can exit even if poller is between polls
            waiter = asyncio.create_task(stop.wait(), name="stop_waiter")
            done, pending = await asyncio.wait(
                {poller_task, waiter},
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()
            # Propagate poller errors (if any) after shutdown
            if poller_task in done and not poller_task.cancelled():
                exc = poller_task.exception()
                if exc is not None:
                    log.warning("poller_exited_with_error", error=str(exc))
        else:
            await stop.wait()
    finally:
        if poller_task is not None and not poller_task.done():
            poller_task.cancel()
            try:
                await poller_task
            except (asyncio.CancelledError, Exception):
                pass
        try:
            scheduler.shutdown(wait=False)
        except Exception as exc:
            log.warning("scheduler_shutdown_failed", error=str(exc))
        log.info("service_stopped")

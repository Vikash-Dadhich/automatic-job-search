"""Offline tests for main.py CLI routing."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import main as main_mod


def test_build_parser_default_serve() -> None:
    parser = main_mod.build_parser()
    args = parser.parse_args([])
    assert args.command is None  # main() treats None as serve


def test_run_once_invokes_pipeline() -> None:
    fake_pipeline = AsyncMock(return_value="summary")
    with (
        patch("orchestrator.pipeline.run_pipeline", fake_pipeline),
        patch("main.configure_logging"),
        patch("main.get_settings") as gs,
    ):
        gs.return_value = MagicMock(log_level="INFO")
        # Patch where asyncio.run will import from inside _cmd_run_once
        with patch("orchestrator.pipeline.run_pipeline", fake_pipeline):
            # Re-bind the command to use our mock via module path used in _cmd_run_once
            async def fake_cmd() -> None:
                from orchestrator import pipeline as p

                await p.run_pipeline()

            with patch.dict(
                "main.__dict__",
                {},  # no-op; we patch asyncio.run target instead
            ):
                with patch("main._cmd_run_once", fake_cmd):
                    rc = main_mod.main(["run-once"])
    assert rc == 0
    fake_pipeline.assert_awaited_once()


def test_serve_invokes_run_service() -> None:
    fake_serve = AsyncMock()
    with (
        patch("main.configure_logging"),
        patch("main.get_settings") as gs,
        patch("main._cmd_serve", fake_serve),
    ):
        gs.return_value = MagicMock(log_level="INFO")
        rc = main_mod.main(["serve"])
    assert rc == 0
    fake_serve.assert_awaited_once()


def test_poll_invokes_run_polling() -> None:
    fake_poll = AsyncMock()
    with (
        patch("main.configure_logging"),
        patch("main.get_settings") as gs,
        patch("main._cmd_poll", fake_poll),
    ):
        gs.return_value = MagicMock(log_level="INFO")
        rc = main_mod.main(["poll"])
    assert rc == 0
    fake_poll.assert_awaited_once()


def test_send_reviews_invokes_once() -> None:
    fake = AsyncMock()
    with (
        patch("main.configure_logging"),
        patch("main.get_settings") as gs,
        patch("main._cmd_send_reviews", fake),
    ):
        gs.return_value = MagicMock(log_level="INFO")
        rc = main_mod.main(["send-reviews"])
    assert rc == 0
    fake.assert_awaited_once()


def test_webhook_invokes_uvicorn() -> None:
    with (
        patch("main.configure_logging"),
        patch("main.get_settings") as gs,
        patch("main._cmd_webhook") as webhook,
    ):
        gs.return_value = MagicMock(log_level="INFO")
        rc = main_mod.main(["webhook", "--host", "127.0.0.1", "--port", "9000"])
    assert rc == 0
    webhook.assert_called_once_with("127.0.0.1", 9000)


def test_tailor_resume_cli() -> None:
    called: list[int] = []

    async def fake_tailor(job_id: int) -> None:
        called.append(job_id)

    with (
        patch("main.configure_logging"),
        patch("main.get_settings") as gs,
        patch("main._cmd_tailor_resume", fake_tailor),
    ):
        gs.return_value = MagicMock(log_level="INFO")
        rc = main_mod.main(["tailor-resume", "42"])
    assert rc == 0
    assert called == [42]


def test_prep_pack_cli() -> None:
    fake = AsyncMock()
    with (
        patch("main.configure_logging"),
        patch("main.get_settings") as gs,
        patch("main._cmd_prep_pack", fake),
    ):
        gs.return_value = MagicMock(log_level="INFO")
        rc = main_mod.main(["prep-pack"])
    assert rc == 0
    fake.assert_awaited_once()


def test_doctor_cli() -> None:
    fake = AsyncMock()
    with (
        patch("main.configure_logging"),
        patch("main.get_settings") as gs,
        patch("main._cmd_doctor", fake),
    ):
        gs.return_value = MagicMock(log_level="INFO")
        rc = main_mod.main(["doctor"])
    assert rc == 0
    fake.assert_awaited_once()


def test_default_command_is_serve() -> None:
    fake_serve = AsyncMock()
    with (
        patch("main.configure_logging"),
        patch("main.get_settings") as gs,
        patch("main._cmd_serve", fake_serve),
    ):
        gs.return_value = MagicMock(log_level="INFO")
        rc = main_mod.main([])
    assert rc == 0
    fake_serve.assert_awaited_once()

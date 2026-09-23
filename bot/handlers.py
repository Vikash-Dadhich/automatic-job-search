"""Dispatch Telegram callback_query decisions for pending_review jobs and skill suggestions."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import structlog

from bot.submit import Submitter, WorkdaySubmitter
from bot.suggest import decide_suggestion
from bot.telegram import (
    ReviewAction,
    SuggestAction,
    TelegramClient,
    decode_callback,
    decode_suggest_callback,
    is_suggest_callback,
)
from core.db import Job, Status, get_job_by_id, init_db, session_scope

log = structlog.get_logger(__name__)

# In-memory map of (chat_id, bot_message_id) -> suggestion_id for pending Edit replies.
# Single-process assumption: the poller and handlers share the same memory space.
_PENDING_EDIT_REPLIES: dict[tuple[int, int], int] = {}


async def _safe_answer(
    client: TelegramClient,
    callback_id: str,
    *,
    text: str | None = None,
    show_alert: bool = False,
) -> None:
    """Ack a callback_query; never raise (expired/fake IDs return Telegram 400)."""
    if not callback_id:
        return
    try:
        await client.answer_callback_query(
            callback_id, text=text, show_alert=show_alert
        )
    except Exception as exc:
        log.warning("answer_callback_failed", error=str(exc), callback_id=callback_id)


def _decision_caption(job: Job, decision: str, *, detail: str | None = None) -> str:
    base = f"{job.title} @ {job.company}\nDecision: {decision}"
    if detail:
        base = f"{base}\n{detail}"
    if len(base) > 1024:
        return base[:1023] + "…"
    return base


async def _handle_suggest_callback(
    cq: dict[str, Any],
    *,
    client: TelegramClient,
) -> Status | None:
    """Handle s1|approve|id / edit / reject suggestion callbacks."""
    callback_id = str(cq.get("id") or "")
    data = str(cq.get("data") or "")
    try:
        action, suggestion_id = decode_suggest_callback(data)
    except ValueError as exc:
        log.warning("suggest_callback_decode_failed", data=data, error=str(exc))
        await _safe_answer(
            client, callback_id, text="Invalid suggestion button", show_alert=True
        )
        return None

    try:
        if action == SuggestAction.edit:
            # Send a force_reply prompt so the user can type their replacement text.
            message = cq.get("message") or {}
            chat = message.get("chat") or {}
            chat_id = chat.get("id")
            if chat_id is not None:
                # selective=False is required: with selective=True Telegram only
                # shows the reply UI to @mentioned users, so the pencil looked dead.
                prompt_result = await client.send_message(
                    (
                        f"✏️ Reply to THIS message with your replacement text "
                        f"for suggestion #{suggestion_id}."
                    ),
                    chat_id=str(chat_id),
                    reply_markup={
                        "force_reply": True,
                        "selective": False,
                        "input_field_placeholder": "Type the new skill / bullet…",
                    },
                )
                bot_msg_id = prompt_result.get("message_id")
                if isinstance(bot_msg_id, int):
                    _PENDING_EDIT_REPLIES[(int(chat_id), bot_msg_id)] = suggestion_id
                    log.info(
                        "edit_reply_pending",
                        suggestion_id=suggestion_id,
                        chat_id=chat_id,
                        prompt_message_id=bot_msg_id,
                    )
            await _safe_answer(client, callback_id, text="Reply with your text ✏️")
            return None
        else:
            status = await decide_suggestion(suggestion_id, action)
            label = {
                SuggestAction.approve: "✅ APPROVED",
                SuggestAction.reject: "❌ REJECTED",
            }.get(action, status.value)
    except Exception as exc:
        log.warning(
            "suggest_decide_failed",
            suggestion_id=suggestion_id,
            error=str(exc),
        )
        await _safe_answer(
            client, callback_id, text=f"Failed: {exc}", show_alert=True
        )
        return None

    await _safe_answer(client, callback_id, text=label)
    log.info(
        "suggest_callback_handled",
        suggestion_id=suggestion_id,
        action=action.value,
        status=status.value,
    )
    return None


async def handle_message(
    update: dict[str, Any],
    *,
    client: TelegramClient | None = None,
) -> None:
    """Handle incoming text messages — specifically force_reply captures for pending edits.

    All errors are isolated; the poller loop must never crash from a bad message.
    """
    try:
        client = client or TelegramClient()
        msg = update.get("message") or {}
        chat = msg.get("chat") or {}
        chat_id = chat.get("id")
        text = msg.get("text") or ""
        reply_to = msg.get("reply_to_message") or {}
        replied_msg_id = reply_to.get("message_id")

        if not text or chat_id is None or replied_msg_id is None:
            return

        key = (int(chat_id), int(replied_msg_id))
        suggestion_id = _PENDING_EDIT_REPLIES.pop(key, None)
        if suggestion_id is None:
            return  # Not a pending edit reply — ignore

        await init_db()
        status = await decide_suggestion(
            suggestion_id, SuggestAction.edit, edited_text=text.strip()
        )
        log.info(
            "edit_reply_applied",
            suggestion_id=suggestion_id,
            status=status.value,
            text_preview=text[:60],
        )
        await client.send_message(
            f'\u2705 Skill updated to: \u201c{text.strip()}\u201d',
            chat_id=str(chat_id),
        )
    except Exception as exc:
        log.warning("handle_message_failed", error=str(exc))


async def handle_callback(
    update: dict[str, Any],
    *,
    client: TelegramClient | None = None,
    submitter: Submitter | None = None,
) -> Status | None:
    """Handle one Telegram update containing a callback_query.

    Returns the resulting Status on success, or None if the update was ignored.
    Errors are logged and isolated — never raised to the caller loop.
    """
    try:
        await init_db()
        client = client or TelegramClient()
        submitter = submitter or WorkdaySubmitter()

        cq = update.get("callback_query")
        if not isinstance(cq, dict):
            return None

        callback_id = str(cq.get("id") or "")
        data = str(cq.get("data") or "")
        message = cq.get("message") or {}
        message_id = message.get("message_id")
        chat = message.get("chat") or {}
        chat_id = chat.get("id")

        if is_suggest_callback(data):
            return await _handle_suggest_callback(cq, client=client)

        try:
            action, job_id = decode_callback(data)
        except ValueError as exc:
            log.warning("callback_decode_failed", data=data, error=str(exc))
            await _safe_answer(
                client, callback_id, text="Invalid button data", show_alert=True
            )
            return None

        async with session_scope() as session:
            job = await get_job_by_id(session, job_id)

        if job is None:
            log.warning("callback_unknown_job", job_id=job_id)
            await _safe_answer(client, callback_id, text="Job not found", show_alert=True)
            return None

        if job.status != Status.pending_review:
            log.info(
                "callback_already_decided",
                job_id=job_id,
                status=job.status.value,
            )
            await _safe_answer(client, callback_id, text=f"Already {job.status.value}")
            return job.status

        new_status: Status
        detail: str | None = None
        screenshot: str | None = None

        if action == ReviewAction.ok:
            result = await submitter.submit(job)
            if result.submitted:
                new_status = Status.submitted
                detail = "Submitted via Workday."
            else:
                new_status = Status.manual_review
                detail = f"Submit blocked: {result.reason or 'unknown'}"
            screenshot = result.screenshot_path
        elif action == ReviewAction.manual:
            new_status = Status.manual_review
            detail = "Manual takeover requested."
        elif action == ReviewAction.discard:
            new_status = Status.ignored
            detail = "Discarded."
        else:
            log.warning("callback_unknown_action", action=action)
            await _safe_answer(client, callback_id, text="Unknown action")
            return None

        now = datetime.now(UTC)
        async with session_scope() as session:
            target = await get_job_by_id(session, job_id)
            if target is None:
                return None
            # Re-check race: another tap may have decided already
            if target.status != Status.pending_review:
                await _safe_answer(
                    client, callback_id, text=f"Already {target.status.value}"
                )
                return target.status
            target.status = new_status
            target.decided_at = now
            target.updated_at = now
            if screenshot:
                target.screenshot_path = screenshot
            session.add(target)

        decision_label = {
            Status.submitted: "APPROVED / SUBMITTED",
            Status.manual_review: "MANUAL REVIEW",
            Status.ignored: "DISCARDED",
        }.get(new_status, new_status.value)

        edit_chat = chat_id or job.review_chat_id
        edit_msg = message_id or job.review_message_id
        if edit_chat is not None and edit_msg is not None:
            try:
                await client.edit_message_caption(
                    chat_id=edit_chat,
                    message_id=int(edit_msg),
                    caption=_decision_caption(job, decision_label, detail=detail),
                    reply_markup={"inline_keyboard": []},
                )
            except Exception:
                # Message may be text-only (no photo) — clear keyboard at least
                try:
                    await client.edit_message_reply_markup(
                        chat_id=edit_chat,
                        message_id=int(edit_msg),
                        reply_markup={"inline_keyboard": []},
                    )
                except Exception as edit_exc:
                    log.warning(
                        "edit_message_failed",
                        job_id=job_id,
                        error=str(edit_exc),
                    )

        # Approve-path block: send a fresh blocker screenshot as a new photo
        if (
            action == ReviewAction.ok
            and new_status == Status.manual_review
            and screenshot
        ):
            from pathlib import Path

            shot_path = Path(screenshot)
            if shot_path.is_file():
                try:
                    await client.send_photo(
                        shot_path,
                        caption=_decision_caption(
                            job,
                            "SUBMIT BLOCKED",
                            detail=detail,
                        ),
                        chat_id=str(edit_chat) if edit_chat is not None else None,
                    )
                except Exception as photo_exc:
                    log.warning(
                        "blocker_photo_failed",
                        job_id=job_id,
                        error=str(photo_exc),
                    )

        await _safe_answer(client, callback_id, text=decision_label)

        log.info(
            "callback_handled",
            job_id=job_id,
            action=action.value,
            status=new_status.value,
        )
        return new_status
    except Exception as exc:
        log.warning("handle_callback_failed", error=str(exc), update_id=update.get("update_id"))
        return None

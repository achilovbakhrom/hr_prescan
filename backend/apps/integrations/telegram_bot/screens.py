"""Reusable single-message screen helpers for Telegram bots."""

from __future__ import annotations

import logging
from typing import Any

from apps.integrations.telegram_bot.sessions import get_session, update_session

logger = logging.getLogger(__name__)

SCREEN_MESSAGE_ID = "screen_message_id"
SCREEN_NAME = "screen_name"


def send_screen(
    *,
    client,
    role: str,
    telegram_id: int,
    chat_id: int,
    text: str,
    reply_markup: dict[str, Any] | None = None,
    parse_mode: str | None = "Markdown",
    screen_name: str = "",
    source_message_id: int | None = None,
) -> None:
    """Render a bot "page" into one active Telegram message when possible."""
    session = get_session(role=role, telegram_id=telegram_id)
    message_id = source_message_id or session.get(SCREEN_MESSAGE_ID)
    if message_id and _edit(
        client=client,
        chat_id=chat_id,
        message_id=int(message_id),
        text=text,
        parse_mode=parse_mode,
        reply_markup=reply_markup,
    ):
        _remember(role=role, telegram_id=telegram_id, message_id=int(message_id), screen_name=screen_name)
        return

    sent = client.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=parse_mode,
        reply_markup=reply_markup,
    )
    new_id = (sent.get("result") or {}).get("message_id")
    if new_id:
        old_id = session.get(SCREEN_MESSAGE_ID)
        if old_id and old_id != new_id:
            delete_message(client=client, chat_id=chat_id, message_id=int(old_id))
        _remember(role=role, telegram_id=telegram_id, message_id=int(new_id), screen_name=screen_name)


def delete_message(*, client, chat_id: int, message_id: int | None) -> None:
    if not message_id:
        return
    try:
        client.delete_message(chat_id=chat_id, message_id=int(message_id))
    except Exception as exc:  # pragma: no cover - Telegram cleanup is best-effort
        logger.debug("Telegram message cleanup failed: %s", exc)


def clear_screen(*, client, role: str, telegram_id: int, chat_id: int) -> None:
    session = get_session(role=role, telegram_id=telegram_id)
    delete_message(client=client, chat_id=chat_id, message_id=session.get(SCREEN_MESSAGE_ID))
    update_session(role=role, telegram_id=telegram_id, **{SCREEN_MESSAGE_ID: None, SCREEN_NAME: ""})


def _edit(
    *,
    client,
    chat_id: int,
    message_id: int,
    text: str,
    parse_mode: str | None,
    reply_markup: dict | None,
) -> bool:
    result = client.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=text,
        parse_mode=parse_mode,
        reply_markup=reply_markup,
    )
    if result.get("ok"):
        return True
    description = str(result.get("description") or result.get("error") or "")
    return "message is not modified" in description.lower()


def _remember(*, role: str, telegram_id: int, message_id: int, screen_name: str) -> None:
    update_session(role=role, telegram_id=telegram_id, **{SCREEN_MESSAGE_ID: message_id, SCREEN_NAME: screen_name})

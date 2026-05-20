"""HR Telegram callback dispatcher."""

from __future__ import annotations

import logging

from apps.integrations.telegram_bot.bots import ROLE_HR, get_client
from apps.integrations.telegram_bot.hr.assistant import route_to_assistant
from apps.integrations.telegram_bot.hr.linking import get_hr_bot_user
from apps.integrations.telegram_bot.hr.menus import handle_menu_callback, is_menu_callback
from apps.integrations.telegram_bot.hr.onboarding_flow import (
    ensure_onboarding_ready,
    handle_onboarding_callback,
    is_onboarding_callback,
)

logger = logging.getLogger(__name__)


def handle_callback(*, callback: dict) -> None:
    client = get_client(role=ROLE_HR)
    callback_id = callback.get("id")
    try:
        process_callback(client=client, callback=callback)
    finally:
        if callback_id:
            client.answer_callback_query(callback_query_id=callback_id)


def process_callback(*, client, callback: dict) -> None:
    data = callback.get("data", "")
    chat_id = callback.get("message", {}).get("chat", {}).get("id")
    sender = callback.get("from", {})
    telegram_id = sender.get("id")
    if not chat_id or not telegram_id:
        return

    if is_onboarding_callback(data=data):
        handle_onboarding_callback(client=client, chat_id=chat_id, telegram_id=telegram_id, data=data)
        return

    from apps.integrations.telegram_bot.hr.deep_link import handle_link_callback, is_link_callback

    if is_link_callback(data=data):
        handle_link_callback(
            client=client,
            chat_id=chat_id,
            telegram_id=telegram_id,
            telegram_username=sender.get("username", ""),
            data=data,
        )
        return

    user = get_hr_bot_user(telegram_id=telegram_id)
    if user is not None and is_menu_callback(data=data):
        if not ensure_onboarding_ready(client=client, chat_id=chat_id, user=user, text=""):
            return
        handle_menu_callback(
            client=client,
            chat_id=chat_id,
            telegram_id=telegram_id,
            user=user,
            data=data,
            route_to_assistant=route_to_assistant,
        )
        return

    logger.debug("Unhandled HR callback: %r", data)

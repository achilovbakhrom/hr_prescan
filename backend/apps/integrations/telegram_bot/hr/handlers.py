"""HR bot update handler.

Routes incoming Telegram updates to the existing LangChain assistant
(``apps.common.ai_assistant.process_ai_command``). The HR bot is currently
free-text driven; PR3 will add an inline-keyboard menu layer on top of this.
"""

from __future__ import annotations

import logging

from apps.integrations.telegram_bot.bots import ROLE_HR, get_client
from apps.integrations.telegram_bot.hr.i18n import text as hr_text
from apps.integrations.telegram_bot.hr.linking import get_hr_bot_user
from apps.integrations.telegram_bot.hr.onboarding_flow import (
    ensure_onboarding_ready,
    handle_company_name_reply,
    handle_onboarding_callback,
    is_onboarding_callback,
)
from apps.integrations.telegram_bot.i18n import normalize_language
from apps.integrations.telegram_bot.voice import transcribe_voice

logger = logging.getLogger(__name__)


def handle_update(update_data: dict) -> None:
    """Process an incoming Telegram update for the HR bot."""
    callback = update_data.get("callback_query")
    if callback:
        _handle_callback(callback=callback)
        return

    message = update_data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    if not chat_id:
        return

    client = get_client(role=ROLE_HR)
    telegram_id = message.get("from", {}).get("id")
    telegram_username = message.get("from", {}).get("username", "")
    language_code = message.get("from", {}).get("language_code", "")
    fallback_lang = normalize_language(lang_code=language_code)

    voice = message.get("voice")
    if voice:
        text = transcribe_voice(client=client, file_id=voice.get("file_id"))
        if not text:
            client.send_message(
                chat_id=chat_id,
                text=hr_text("voice_error", lang=fallback_lang),
            )
            return
        client.send_message(chat_id=chat_id, text=f"__{text}__", parse_mode="Markdown")
    else:
        text = message.get("text", "").strip()

    if not text:
        return

    if text == "/start" or text.startswith("/start "):
        payload = text[7:].strip() if text.startswith("/start ") else ""
        first_name = message.get("from", {}).get("first_name", "")
        last_name = message.get("from", {}).get("last_name", "")
        from apps.integrations.telegram_bot.hr.auth import handle_start

        handle_start(
            client=client,
            chat_id=chat_id,
            telegram_id=telegram_id,
            telegram_username=telegram_username,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code,
            payload=payload,
        )
        return

    if text == "/help":
        _handle_help(client=client, chat_id=chat_id)
        return

    user = get_hr_bot_user(telegram_id=telegram_id)
    if user is None:
        from apps.integrations.telegram_bot.hr.auth import try_link_code

        handled = try_link_code(
            client=client,
            chat_id=chat_id,
            telegram_id=telegram_id,
            telegram_username=telegram_username,
            text=text,
            language_code=language_code,
        )
        if handled:
            return

        from apps.integrations.telegram_bot.hr.onboarding import get_or_create_hr_bot_user

        sender = message.get("from", {})
        user = get_or_create_hr_bot_user(
            telegram_id=telegram_id,
            telegram_username=telegram_username,
            first_name=sender.get("first_name", ""),
            last_name=sender.get("last_name", ""),
            language=fallback_lang,
        )
        client.send_message(
            chat_id=chat_id,
            text=hr_text("workspace_created", user=user),
            parse_mode="Markdown",
        )

    if handle_company_name_reply(client=client, chat_id=chat_id, user=user, text=text):
        return

    if not ensure_onboarding_ready(client=client, chat_id=chat_id, user=user, text=text):
        return

    _route_to_assistant(client=client, chat_id=chat_id, user=user, text=text)


def _route_to_assistant(*, client, chat_id, user, text: str) -> None:
    """Hand a free-text message to the LangChain HR assistant."""
    from apps.common.ai_assistant import process_ai_command
    from apps.integrations.telegram_bot.hr.history import (
        get_hr_context,
        save_hr_history,
    )

    context = get_hr_context(telegram_id=user.telegram_id, text=text)
    result = process_ai_command(user=user, message=text, context=context)
    response_text = result.get("message", "Something went wrong.")

    save_hr_history(
        telegram_id=user.telegram_id,
        user_msg=text,
        bot_msg=response_text,
    )
    client.send_message(chat_id=chat_id, text=response_text, parse_mode="Markdown")


def _handle_callback(*, callback: dict) -> None:
    client = get_client(role=ROLE_HR)
    callback_id = callback.get("id")
    try:
        _process_callback(client=client, callback=callback)
    finally:
        if callback_id:
            client.answer_callback_query(callback_query_id=callback_id)


def _process_callback(*, client, callback: dict) -> None:
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

    logger.debug("Unhandled HR callback: %r", data)


def _handle_help(*, client, chat_id) -> None:
    user = get_hr_bot_user(telegram_id=chat_id)
    if user is not None and not ensure_onboarding_ready(client=client, chat_id=chat_id, user=user, text="/help"):
        return

    client.send_message(
        chat_id=chat_id,
        text=hr_text("help", user=user),
    )

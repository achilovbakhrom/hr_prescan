"""HR bot update handler.

Routes incoming Telegram updates to the existing LangChain assistant
(``apps.common.ai_assistant.process_ai_command``). The HR bot is currently
free-text driven; PR3 will add an inline-keyboard menu layer on top of this.
"""

from __future__ import annotations

import logging

from apps.integrations.telegram_bot.bots import ROLE_HR, get_client
from apps.integrations.telegram_bot.hr.linking import get_hr_bot_user
from apps.integrations.telegram_bot.voice import transcribe_voice

logger = logging.getLogger(__name__)


def handle_update(update_data: dict) -> None:
    """Process an incoming Telegram update for the HR bot."""
    message = update_data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    if not chat_id:
        return

    client = get_client(role=ROLE_HR)
    telegram_id = message.get("from", {}).get("id")
    telegram_username = message.get("from", {}).get("username", "")

    voice = message.get("voice")
    if voice:
        text = transcribe_voice(client=client, file_id=voice.get("file_id"))
        if not text:
            client.send_message(
                chat_id=chat_id,
                text="Sorry, I couldn't transcribe that voice message.",
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
            payload=payload,
        )
        return

    if text == "/help":
        _handle_help(client=client, chat_id=chat_id)
        return

    user = get_hr_bot_user(telegram_id=telegram_id)
    if user is None:
        from apps.integrations.telegram_bot.hr.auth import try_link_code

        try_link_code(
            client=client,
            chat_id=chat_id,
            telegram_id=telegram_id,
            telegram_username=telegram_username,
            text=text,
        )
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


def _handle_help(*, client, chat_id) -> None:
    client.send_message(
        chat_id=chat_id,
        text=(
            "I can help with:\n\n"
            "*Vacancies* -- list, create, update, publish, pause, archive, delete\n"
            "*Companies* -- list, create, update, delete\n"
            "*Candidates* -- list, status changes, notes\n"
            "*Interviews* -- list, cancel, reset\n"
            "*Dashboard* -- stats, summaries\n"
            "*Subscription* -- plan info, usage\n"
            "*Team* -- invite, manage members\n\n"
            "Just describe what you need in natural language!\n"
            "You can also send voice messages."
        ),
    )

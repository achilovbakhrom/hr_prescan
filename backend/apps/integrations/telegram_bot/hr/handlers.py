"""HR bot update handler.

Routes incoming Telegram updates to the existing LangChain assistant
(``apps.common.ai_assistant.process_ai_command``) through text, voice, and
button shortcuts.
"""

from __future__ import annotations

from apps.integrations.telegram_bot.bots import ROLE_HR, get_client
from apps.integrations.telegram_bot.hr.assistant import route_to_assistant
from apps.integrations.telegram_bot.hr.callbacks import handle_callback
from apps.integrations.telegram_bot.hr.i18n import text as hr_text
from apps.integrations.telegram_bot.hr.linking import get_hr_bot_user
from apps.integrations.telegram_bot.hr.menus import (
    main_menu_keyboard,
    send_main_menu,
)
from apps.integrations.telegram_bot.hr.onboarding_flow import (
    ensure_onboarding_ready,
    handle_company_name_reply,
    send_language_picker,
)
from apps.integrations.telegram_bot.i18n import normalize_language
from apps.integrations.telegram_bot.sessions import get_session, update_session
from apps.integrations.telegram_bot.voice import transcribe_voice


def handle_update(update_data: dict) -> None:
    """Process an incoming Telegram update for the HR bot."""
    callback = update_data.get("callback_query")
    if callback:
        handle_callback(callback=callback)
        return

    message = update_data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    message_id = message.get("message_id")
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

    if text in ("/language", "/lang"):
        send_language_picker(client=client, chat_id=chat_id)
        return

    if text in ("/menu", "/start_menu"):
        update_session(role=ROLE_HR, telegram_id=telegram_id, ai_mode=False, state="", vacancy_wizard={})
        send_main_menu(client=client, chat_id=chat_id, user=user)
        return
    if text in ("/exit_ai", "/cancel"):
        update_session(role=ROLE_HR, telegram_id=telegram_id, ai_mode=False, state="", vacancy_wizard={})
        send_main_menu(client=client, chat_id=chat_id, user=user)
        return

    if handle_company_name_reply(client=client, chat_id=chat_id, user=user, text=text):
        return

    if not ensure_onboarding_ready(client=client, chat_id=chat_id, user=user, text=text):
        return

    session = get_session(role=ROLE_HR, telegram_id=telegram_id)
    from apps.integrations.telegram_bot.hr.vacancy_wizard import handle_text as handle_vacancy_wizard_text

    if handle_vacancy_wizard_text(
        client=client,
        chat_id=chat_id,
        telegram_id=telegram_id,
        user=user,
        text=text,
        message_id=message_id,
    ):
        return

    if not session.get("ai_mode"):
        client.send_message(
            chat_id=chat_id,
            text=hr_text("free_text_blocked", user=user),
            reply_markup=main_menu_keyboard(user=user),
        )
        return

    route_to_assistant(client=client, chat_id=chat_id, user=user, text=text)


def _handle_help(*, client, chat_id) -> None:
    user = get_hr_bot_user(telegram_id=chat_id)
    if user is not None and not ensure_onboarding_ready(client=client, chat_id=chat_id, user=user, text="/help"):
        return

    client.send_message(
        chat_id=chat_id,
        text=hr_text("help", user=user),
        reply_markup=main_menu_keyboard(user=user),
    )

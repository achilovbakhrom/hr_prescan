"""Candidate bot — top-level update dispatcher.

Splits incoming updates into:
    * /start (with optional ``vac_<uuid>`` deep link)
    * /menu, /help
    * Document upload (CV)
    * Voice message (transcribed, then routed as text)
    * Inline-keyboard callback (vacancy actions etc.)
    * Free-text fallback (placeholder until PR2 ships the AI agent)

Authentication is implicit: every Telegram identity that messages this bot is
auto-onboarded as a candidate ``User`` (see ``candidate/auth.py``).
"""
from __future__ import annotations

import logging
from uuid import UUID

from apps.integrations.telegram_bot.bots import ROLE_CANDIDATE, get_client
from apps.integrations.telegram_bot.candidate.apply import (
    confirm_apply,
    parse_deep_link_vacancy,
    show_vacancy_card,
)
from apps.integrations.telegram_bot.candidate.auth import get_or_create_candidate_user
from apps.integrations.telegram_bot.candidate.menus import (
    CB_MENU,
    CB_VAC_APPLY,
    parse_callback,
)
from apps.integrations.telegram_bot.candidate.uploads import handle_document
from apps.integrations.telegram_bot.i18n import normalize_language, t
from apps.integrations.telegram_bot.sessions import get_session
from apps.integrations.telegram_bot.voice import transcribe_voice

logger = logging.getLogger(__name__)


def handle_update(update_data: dict) -> None:
    """Process an incoming Telegram update for the candidate bot."""
    client = get_client(role=ROLE_CANDIDATE)

    callback = update_data.get("callback_query")
    if callback:
        _handle_callback(client=client, callback=callback)
        return

    message = update_data.get("message")
    if not message:
        return
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    if not chat_id:
        return

    sender = message.get("from", {})
    telegram_id = sender.get("id")
    if not telegram_id:
        return
    lang = normalize_language(lang_code=sender.get("language_code"))

    user = get_or_create_candidate_user(
        telegram_id=telegram_id,
        telegram_username=sender.get("username", ""),
        first_name=sender.get("first_name", ""),
        last_name=sender.get("last_name", ""),
    )

    document = message.get("document")
    if document:
        handle_document(
            client=client, chat_id=chat_id, user=user, document=document, lang=lang,
        )
        return

    voice = message.get("voice")
    if voice:
        transcribed = transcribe_voice(client=client, file_id=voice.get("file_id"))
        if not transcribed:
            client.send_message(chat_id=chat_id, text=t("common.error_generic", lang=lang))
            return
        text = transcribed
    else:
        text = (message.get("text") or "").strip()

    if not text:
        return

    if text == "/start" or text.startswith("/start "):
        payload = text[7:].strip() if text.startswith("/start ") else ""
        _handle_start(
            client=client, chat_id=chat_id, user=user, payload=payload, lang=lang,
        )
        return

    if text in ("/menu", "/help"):
        _send_main_menu(client=client, chat_id=chat_id, lang=lang)
        return

    # Free-text fallback — the AI agent ships in PR2.
    client.send_message(chat_id=chat_id, text=t("common.unknown_command", lang=lang))


def _handle_start(*, client, chat_id: int, user, payload: str, lang: str) -> None:
    vacancy_id = parse_deep_link_vacancy(payload=payload)
    if vacancy_id is not None:
        show_vacancy_card(client=client, chat_id=chat_id, vacancy_id=vacancy_id, lang=lang)
        return
    client.send_message(chat_id=chat_id, text=t("candidate.welcome", lang=lang))


def _send_main_menu(*, client, chat_id: int, lang: str) -> None:
    # PR2 expands this with the candidate AI agent menu. For now, a stub.
    client.send_message(chat_id=chat_id, text=t("candidate.welcome", lang=lang))


def _handle_callback(*, client, callback: dict) -> None:
    callback_id = callback.get("id")
    try:
        _process_callback(client=client, callback=callback)
    finally:
        # Always answer so Telegram stops showing a spinner on the user's button.
        if callback_id:
            client.answer_callback_query(callback_query_id=callback_id)


def _process_callback(*, client, callback: dict) -> None:
    data = callback.get("data", "")
    chat = callback.get("message", {}).get("chat", {})
    chat_id = chat.get("id")
    sender = callback.get("from", {})
    telegram_id = sender.get("id")
    if not chat_id or not telegram_id:
        return

    lang = normalize_language(lang_code=sender.get("language_code"))
    user = get_or_create_candidate_user(
        telegram_id=telegram_id,
        telegram_username=sender.get("username", ""),
        first_name=sender.get("first_name", ""),
        last_name=sender.get("last_name", ""),
    )

    action, arg = parse_callback(data=data)

    if action == CB_VAC_APPLY and arg:
        _handle_apply_callback(
            client=client, chat_id=chat_id, user=user, vacancy_arg=arg, lang=lang,
        )
    elif action == CB_MENU:
        _send_main_menu(client=client, chat_id=chat_id, lang=lang)
    else:
        logger.debug("Unhandled callback action: %r (data=%r)", action, data)


def _handle_apply_callback(
    *, client, chat_id: int, user, vacancy_arg: str, lang: str,
) -> None:
    try:
        vacancy_id = UUID(vacancy_arg)
    except (ValueError, TypeError):
        return
    session = get_session(role=ROLE_CANDIDATE, telegram_id=user.telegram_id)
    confirm_apply(
        client=client,
        chat_id=chat_id,
        user=user,
        vacancy_id=vacancy_id,
        cv_file_path=session.get("cv_file_path", ""),
        cv_original_filename=session.get("cv_original_filename", ""),
        lang=lang,
    )

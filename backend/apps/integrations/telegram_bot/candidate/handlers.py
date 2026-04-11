"""Candidate bot — top-level update dispatcher."""
from __future__ import annotations

import logging
from uuid import UUID

from apps.integrations.telegram_bot.bots import ROLE_CANDIDATE, get_client
from apps.integrations.telegram_bot.candidate.apply import (
    confirm_apply, parse_deep_link_vacancy, show_vacancy_card,
)
from apps.integrations.telegram_bot.candidate.auth import get_or_create_candidate_user
from apps.integrations.telegram_bot.candidate.menus import (
    CB_MENU, CB_VAC_APPLY, main_menu_keyboard, parse_callback,
)
from apps.integrations.telegram_bot.candidate.states import STATE_PS_CV, STATE_PS_INTERVIEW
from apps.integrations.telegram_bot.candidate.uploads import handle_document
from apps.integrations.telegram_bot.i18n import normalize_language, t
from apps.integrations.telegram_bot.sessions import get_session
from apps.integrations.telegram_bot.voice import transcribe_voice

logger = logging.getLogger(__name__)


def handle_update(update_data: dict) -> None:
    client = get_client(role=ROLE_CANDIDATE)

    callback = update_data.get("callback_query")
    if callback:
        _handle_callback(client=client, callback=callback)
        return

    message = update_data.get("message")
    if not message:
        return
    chat_id = message.get("chat", {}).get("id")
    sender = message.get("from", {})
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
    session = get_session(role=ROLE_CANDIDATE, telegram_id=telegram_id)

    document = message.get("document")
    if document:
        _handle_document(client=client, chat_id=chat_id, user=user, document=document, session=session, lang=lang)
        return

    voice = message.get("voice")
    if voice:
        text = transcribe_voice(client=client, file_id=voice.get("file_id")) or ""
        if not text:
            client.send_message(chat_id=chat_id, text=t("common.error_generic", lang=lang))
            return
    else:
        text = (message.get("text") or "").strip()

    if text:
        _handle_text(client=client, chat_id=chat_id, user=user, text=text, session=session, lang=lang)


def _handle_text(*, client, chat_id: int, user, text: str, session: dict, lang: str) -> None:
    if not user.phone:
        from apps.integrations.telegram_bot.candidate.registration import (
            handle_registration_text, prompt_registration,
        )
        if session.get("state") in ("reg_name", "reg_phone"):
            handle_registration_text(client=client, chat_id=chat_id, user=user, text=text, session=session, lang=lang)
        else:
            prompt_registration(client=client, chat_id=chat_id, user=user, lang=lang)
        return

    state = session.get("state", "")
    if state.startswith("ps_"):
        from apps.integrations.telegram_bot.candidate.prescreening import handle_prescreening_text
        handle_prescreening_text(client=client, chat_id=chat_id, user=user, text=text, session=session, lang=lang)
        return

    if text == "/start" or text.startswith("/start "):
        payload = text[7:].strip() if text.startswith("/start ") else ""
        if payload:
            vacancy_id = parse_deep_link_vacancy(payload=payload)
            if vacancy_id:
                show_vacancy_card(client=client, chat_id=chat_id, vacancy_id=vacancy_id, lang=lang)
                return
        _send_main_menu(client=client, chat_id=chat_id, lang=lang)
        return

    if text in ("/menu", "/help"):
        _send_main_menu(client=client, chat_id=chat_id, lang=lang)
        return

    client.send_message(chat_id=chat_id, text=t("common.unknown_command", lang=lang))


def _handle_document(*, client, chat_id: int, user, document: dict, session: dict, lang: str) -> None:
    state = session.get("state", "")
    if state == STATE_PS_CV:
        from apps.integrations.telegram_bot.candidate.prescreening import handle_cv_upload
        handle_cv_upload(client=client, chat_id=chat_id, user=user, document=document, session=session, lang=lang)
    elif state != STATE_PS_INTERVIEW:
        handle_document(client=client, chat_id=chat_id, user=user, document=document, lang=lang)


def _handle_callback(*, client, callback: dict) -> None:
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

    lang = normalize_language(lang_code=sender.get("language_code"))
    user = get_or_create_candidate_user(
        telegram_id=telegram_id,
        telegram_username=sender.get("username", ""),
        first_name=sender.get("first_name", ""),
        last_name=sender.get("last_name", ""),
    )
    session = get_session(role=ROLE_CANDIDATE, telegram_id=telegram_id)
    action, arg = parse_callback(data=data)

    if action == CB_VAC_APPLY and arg:
        try:
            vacancy_id = UUID(arg)
        except (ValueError, TypeError):
            return
        confirm_apply(
            client=client, chat_id=chat_id, user=user, vacancy_id=vacancy_id,
            cv_file_path=session.get("cv_file_path", ""),
            cv_original_filename=session.get("cv_original_filename", ""),
            lang=lang,
        )
    elif action == CB_MENU:
        _send_main_menu(client=client, chat_id=chat_id, lang=lang)
    elif data.startswith("cand:ps:"):
        from apps.integrations.telegram_bot.candidate.prescreening import handle_prescreening_callback
        handle_prescreening_callback(client=client, chat_id=chat_id, user=user, data=data, session=session, lang=lang)
    else:
        logger.debug("Unhandled callback: %r", data)


def _send_main_menu(*, client, chat_id: int, lang: str) -> None:
    client.send_message(
        chat_id=chat_id,
        text=t("candidate.main_menu", lang=lang),
        reply_markup=main_menu_keyboard(lang=lang),
    )

"""Candidate bot — top-level update dispatcher."""

from __future__ import annotations

from apps.integrations.telegram_bot.bots import ROLE_CANDIDATE, get_client
from apps.integrations.telegram_bot.candidate import cv_screens, onboarding
from apps.integrations.telegram_bot.candidate import language_settings as lang_settings
from apps.integrations.telegram_bot.candidate.assistant import route_to_assistant
from apps.integrations.telegram_bot.candidate.auth import get_or_create_candidate_user
from apps.integrations.telegram_bot.candidate.callbacks import handle_callback
from apps.integrations.telegram_bot.candidate.language import telegram_language, user_language
from apps.integrations.telegram_bot.candidate.menus import send_main_menu
from apps.integrations.telegram_bot.candidate.start import handle_account_link_start, handle_start_command
from apps.integrations.telegram_bot.candidate.states import STATE_CV_UPLOAD, STATE_PS_CV, STATE_PS_INTERVIEW
from apps.integrations.telegram_bot.candidate.uploads import handle_document
from apps.integrations.telegram_bot.i18n import t
from apps.integrations.telegram_bot.sessions import get_session
from apps.integrations.telegram_bot.voice import transcribe_voice


def handle_update(update_data: dict) -> None:
    client = get_client(role=ROLE_CANDIDATE)

    callback = update_data.get("callback_query")
    if callback:
        handle_callback(client=client, callback=callback)
        return

    message = update_data.get("message")
    if not message:
        return
    chat_id = message.get("chat", {}).get("id")
    sender = message.get("from", {})
    telegram_id = sender.get("id")
    if not chat_id or not telegram_id:
        return

    lang = telegram_language(telegram_id=telegram_id, lang_code=sender.get("language_code"))

    document = message.get("document")
    voice = message.get("voice")
    contact = message.get("contact")
    if not document and not voice and not contact:
        text = (message.get("text") or "").strip()
        if text == "/start" or text.startswith("/start "):
            payload = text[7:].strip() if text.startswith("/start ") else ""
            if handle_account_link_start(
                client=client,
                chat_id=chat_id,
                telegram_id=telegram_id,
                telegram_username=sender.get("username", ""),
                payload=payload,
                lang=lang,
            ):
                return

    user = get_or_create_candidate_user(
        telegram_id=telegram_id,
        telegram_username=sender.get("username", ""),
        first_name=sender.get("first_name", ""),
        last_name=sender.get("last_name", ""),
        language=lang,
    )
    lang = user_language(user=user, fallback=lang)
    session = get_session(role=ROLE_CANDIDATE, telegram_id=telegram_id)
    contact_phone = _contact_phone(contact=contact, telegram_id=telegram_id)
    if contact_phone:
        _handle_text(client=client, chat_id=chat_id, user=user, text=contact_phone, session=session, lang=lang)
        return

    if onboarding.is_required(user=user) and not document and not voice:
        _handle_text(client=client, chat_id=chat_id, user=user, text=text, session=session, lang=lang)
        return

    if document:
        if onboarding.is_required(user=user):
            onboarding.handle_text(client=client, chat_id=chat_id, user=user, text="", session=session, lang=lang)
            return
        _handle_document(client=client, chat_id=chat_id, user=user, document=document, session=session, lang=lang)
        return

    if voice:
        text = transcribe_voice(client=client, file_id=voice.get("file_id")) or ""
        if not text:
            client.send_message(chat_id=chat_id, text=t("common.error_generic", lang=lang))
            return
    else:
        text = (message.get("text") or "").strip()

    if text:
        _handle_text(client=client, chat_id=chat_id, user=user, text=text, session=session, lang=lang)


def _contact_phone(*, contact: dict | None, telegram_id: int) -> str:
    if not contact:
        return ""
    contact_user_id = contact.get("user_id")
    if contact_user_id and contact_user_id != telegram_id:
        return ""
    return (contact.get("phone_number") or "").strip()


def _handle_text(*, client, chat_id: int, user, text: str, session: dict, lang: str) -> None:
    state = session.get("state", "")
    if onboarding.handle_text(client=client, chat_id=chat_id, user=user, text=text, session=session, lang=lang):
        return

    if text == "/start" or text.startswith("/start "):
        payload = text[7:].strip() if text.startswith("/start ") else ""
        if handle_start_command(client=client, chat_id=chat_id, user=user, payload=payload, lang=lang):
            return
        send_main_menu(client=client, chat_id=chat_id, lang=lang)
        return

    if text in ("/language", "/lang"):
        lang_settings.send_language_picker(client=client, chat_id=chat_id, lang=lang)
        return

    if text in ("/jobs", "/search_jobs"):
        route_to_assistant(
            client=client,
            chat_id=chat_id,
            user=user,
            text=t("candidate.ai_prompt_search_jobs", lang=lang),
            lang=lang,
        )
        return

    if text in ("/create_cv", "/build_cv"):
        route_to_assistant(
            client=client,
            chat_id=chat_id,
            user=user,
            text=t("candidate.ai_prompt_create_cv", lang=lang),
            lang=lang,
        )
        return

    if text in ("/cv", "/cvs", "/resume"):
        cv_screens.send_cv_center(client=client, chat_id=chat_id, lang=lang)
        return

    if text in ("/generate_cv", "/cv_generate"):
        cv_screens.generate_platform_cv(client=client, chat_id=chat_id, user=user, lang=lang)
        return

    if state in ("reg_name", "reg_phone"):
        from apps.integrations.telegram_bot.candidate.registration import handle_registration_text

        handle_registration_text(client=client, chat_id=chat_id, user=user, text=text, session=session, lang=lang)
        return

    if state.startswith("ps_"):
        from apps.integrations.telegram_bot.candidate.prescreening import handle_prescreening_text

        handle_prescreening_text(client=client, chat_id=chat_id, user=user, text=text, session=session, lang=lang)
        return

    if text in ("/menu", "/help"):
        send_main_menu(client=client, chat_id=chat_id, lang=lang)
        return

    if text == "/register":
        from apps.integrations.telegram_bot.candidate.registration import prompt_registration

        prompt_registration(client=client, chat_id=chat_id, user=user, lang=lang)
        return

    route_to_assistant(client=client, chat_id=chat_id, user=user, text=text, lang=lang)


def _handle_document(*, client, chat_id: int, user, document: dict, session: dict, lang: str) -> None:
    state = session.get("state", "")
    if state == STATE_CV_UPLOAD:
        cv_screens.handle_cv_upload(client=client, chat_id=chat_id, user=user, document=document, lang=lang)
    elif state == STATE_PS_CV:
        from apps.integrations.telegram_bot.candidate.prescreening import handle_cv_upload

        handle_cv_upload(client=client, chat_id=chat_id, user=user, document=document, session=session, lang=lang)
    elif state != STATE_PS_INTERVIEW:
        handle_document(client=client, chat_id=chat_id, user=user, document=document, lang=lang)

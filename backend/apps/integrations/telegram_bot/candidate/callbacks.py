"""Candidate bot callback dispatcher."""

from __future__ import annotations

from uuid import UUID

from apps.integrations.telegram_bot.bots import ROLE_CANDIDATE
from apps.integrations.telegram_bot.candidate import cv_screens, onboarding
from apps.integrations.telegram_bot.candidate import language_settings as lang_settings
from apps.integrations.telegram_bot.candidate.apply import confirm_apply
from apps.integrations.telegram_bot.candidate.auth import get_or_create_candidate_user
from apps.integrations.telegram_bot.candidate.language import telegram_language, user_language
from apps.integrations.telegram_bot.candidate.linking import handle_account_link_callback, is_account_link_callback
from apps.integrations.telegram_bot.candidate.menus import (
    CB_CV_ASSISTANT,
    CB_JOB_SEARCH,
    CB_MENU,
    CB_VAC_APPLY,
    parse_callback,
    send_main_menu,
)
from apps.integrations.telegram_bot.i18n import t
from apps.integrations.telegram_bot.sessions import get_session


def handle_callback(*, client, callback: dict) -> None:
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

    lang = telegram_language(telegram_id=telegram_id, lang_code=sender.get("language_code"))
    if is_account_link_callback(data=data):
        handle_account_link_callback(
            client=client,
            chat_id=chat_id,
            telegram_id=telegram_id,
            telegram_username=sender.get("username", ""),
            data=data,
            lang=lang,
        )
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
    if lang_settings.is_language_callback(data=data):
        lang_settings.handle_language_callback(client=client, chat_id=chat_id, user=user, data=data, lang=lang)
        return
    if onboarding.is_required(user=user):
        onboarding.handle_text(client=client, chat_id=chat_id, user=user, text="", session=session, lang=lang)
        return
    if cv_screens.is_cv_callback(data=data):
        cv_screens.handle_cv_callback(client=client, chat_id=chat_id, user=user, data=data, lang=lang)
        return

    action, arg = parse_callback(data=data)
    if action == CB_VAC_APPLY and arg:
        _confirm_apply(client=client, chat_id=chat_id, user=user, arg=arg, session=session, lang=lang)
    elif action == CB_JOB_SEARCH:
        _route_button_to_assistant(
            client=client,
            chat_id=chat_id,
            user=user,
            text=t("candidate.ai_prompt_search_jobs", lang=lang),
            lang=lang,
        )
    elif action == CB_CV_ASSISTANT:
        _route_button_to_assistant(
            client=client,
            chat_id=chat_id,
            user=user,
            text=t("candidate.ai_prompt_create_cv", lang=lang),
            lang=lang,
        )
    elif action == CB_MENU:
        send_main_menu(client=client, chat_id=chat_id, lang=lang)
    elif data.startswith("cand:ps:"):
        from apps.integrations.telegram_bot.candidate.prescreening import handle_prescreening_callback

        handle_prescreening_callback(client=client, chat_id=chat_id, user=user, data=data, session=session, lang=lang)


def _confirm_apply(*, client, chat_id: int, user, arg: str, session: dict, lang: str) -> None:
    try:
        vacancy_id = UUID(arg)
    except (ValueError, TypeError):
        return
    confirm_apply(
        client=client,
        chat_id=chat_id,
        user=user,
        vacancy_id=vacancy_id,
        cv_file_path=session.get("cv_file_path", ""),
        cv_original_filename=session.get("cv_original_filename", ""),
        lang=lang,
    )


def _route_button_to_assistant(*, client, chat_id: int, user, text: str, lang: str) -> None:
    from apps.integrations.telegram_bot.candidate.assistant import route_to_assistant

    route_to_assistant(client=client, chat_id=chat_id, user=user, text=text, lang=lang)

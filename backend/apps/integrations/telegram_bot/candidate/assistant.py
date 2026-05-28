"""Candidate bot routing into the candidate AI assistant."""

from __future__ import annotations

from apps.common.candidate_ai_assistant import process_candidate_ai_command
from apps.integrations.telegram_bot.candidate.history import (
    get_candidate_context,
    save_candidate_history,
)
from apps.integrations.telegram_bot.i18n import t


def route_to_assistant(*, client, chat_id: int, user, text: str, lang: str) -> None:
    context = get_candidate_context(telegram_id=user.telegram_id)
    result = process_candidate_ai_command(user=user, message=text, context=context)
    response_text = result.get("message") or t("common.error_generic", lang=lang)

    save_candidate_history(
        telegram_id=user.telegram_id,
        user_msg=text,
        bot_msg=response_text,
    )
    from apps.integrations.telegram_bot.bots import ROLE_CANDIDATE
    from apps.integrations.telegram_bot.candidate.menus import ai_mode_keyboard, main_menu_keyboard
    from apps.integrations.telegram_bot.sessions import get_session

    in_ai_mode = get_session(role=ROLE_CANDIDATE, telegram_id=user.telegram_id).get("ai_mode")
    keyboard = ai_mode_keyboard(lang=lang) if in_ai_mode else main_menu_keyboard(lang=lang)
    client.send_message(
        chat_id=chat_id,
        text=response_text,
        parse_mode="Markdown",
        reply_markup=keyboard,
    )

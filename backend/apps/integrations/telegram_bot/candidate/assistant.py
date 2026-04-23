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
    client.send_message(chat_id=chat_id, text=response_text, parse_mode="Markdown")

"""Candidate bot /start routing helpers."""

from __future__ import annotations

from apps.integrations.telegram_bot.candidate.deep_links import (
    get_prescreen_interview,
    parse_deep_link_vacancy,
)
from apps.integrations.telegram_bot.candidate.language import set_user_language
from apps.integrations.telegram_bot.candidate.linking import request_account_link
from apps.integrations.telegram_bot.i18n import t


def handle_start_command(*, client, chat_id: int, user, payload: str, lang: str) -> bool:
    if payload:
        interview = get_prescreen_interview(payload=payload)
        if interview is not None:
            if interview.application.candidate_id is None:
                interview.application.candidate = user
                interview.application.save(update_fields=["candidate", "updated_at"])

            from apps.integrations.telegram_bot.candidate.interview_resume import resume_bot_interview

            lang = set_user_language(user=user, language=interview.language, fallback=lang)
            resume_bot_interview(client=client, chat_id=chat_id, user=user, interview=interview, lang=lang)
            return True

        vacancy_id = parse_deep_link_vacancy(payload=payload)
        if vacancy_id:
            from apps.integrations.telegram_bot.candidate.apply import show_vacancy_card

            show_vacancy_card(client=client, chat_id=chat_id, vacancy_id=vacancy_id, lang=lang)
            return True

    client.send_message(chat_id=chat_id, text=t("candidate.welcome", lang=lang))
    return False


def handle_account_link_start(
    *,
    client,
    chat_id: int,
    telegram_id: int,
    telegram_username: str,
    payload: str,
    lang: str,
) -> bool:
    return request_account_link(client=client, chat_id=chat_id, telegram_id=telegram_id, payload=payload, lang=lang)

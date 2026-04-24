"""Candidate bot — in-Telegram conversational prescreening.

Flow:
  start_bot_interview()     → starts the shared chat interview engine and sends the AI greeting.
  handle_interview_answer() → routes each answer through the shared conversational AI service.
  _finish_interview()       → thanks user and clears Telegram session when the AI ends the chat.
"""

from __future__ import annotations

import logging

from apps.integrations.telegram_bot.bots import ROLE_CANDIDATE
from apps.integrations.telegram_bot.candidate.states import (
    SK_INTERVIEW_ID,
    SK_VACANCY_ID,
    STATE_PS_INTERVIEW,
)
from apps.integrations.telegram_bot.i18n import t
from apps.integrations.telegram_bot.sessions import clear_session, update_session

logger = logging.getLogger(__name__)


def start_bot_interview(
    *,
    client,
    chat_id: int,
    user,
    interview,
    vacancy_title: str,
    lang: str,
) -> None:
    """Mark interview IN_PROGRESS, store state, send intro + AI greeting."""
    from apps.interviews.models import Interview
    from apps.interviews.services import start_interview

    if interview.status == Interview.Status.PENDING:
        interview.channel = Interview.Channel.TELEGRAM
        interview.save(update_fields=["channel", "updated_at"])
        interview = start_interview(interview=interview)

    update_session(
        role=ROLE_CANDIDATE,
        telegram_id=user.telegram_id,
        state=STATE_PS_INTERVIEW,
        **{
            SK_INTERVIEW_ID: str(interview.id),
            SK_VACANCY_ID: str(interview.application.vacancy_id),
        },
    )

    client.send_message(
        chat_id=chat_id,
        text=t("candidate.ps_starting", lang=lang, title=vacancy_title),
        parse_mode="Markdown",
    )
    _send_last_ai_message(client=client, chat_id=chat_id, interview=interview, lang=lang)


def handle_interview_answer(
    *,
    client,
    chat_id: int,
    user,
    text: str,
    session: dict,
    lang: str,
) -> None:
    """Process a text or transcribed-voice answer during the interview."""
    from apps.interviews.chat_service import process_candidate_message
    from apps.interviews.models import Interview

    interview_id = session.get(SK_INTERVIEW_ID)

    try:
        interview = Interview.objects.select_related(
            "application__vacancy__company",
        ).get(id=interview_id)
    except (Interview.DoesNotExist, Exception):
        client.send_message(chat_id=chat_id, text=t("common.error_generic", lang=lang))
        return

    if interview.status != Interview.Status.IN_PROGRESS:
        client.send_message(chat_id=chat_id, text=t("candidate.ps_not_available", lang=lang))
        clear_session(role=ROLE_CANDIDATE, telegram_id=user.telegram_id)
        return

    try:
        result = process_candidate_message(interview, text)
    except Exception:
        logger.exception("Telegram conversational prescreening failed: session=%s", interview.id)
        client.send_message(chat_id=chat_id, text=t("common.error_generic", lang=lang))
        return

    if result.get("ai_message"):
        client.send_message(chat_id=chat_id, text=result["ai_message"], parse_mode="Markdown")

    if result.get("is_complete"):
        _finish_interview(client=client, chat_id=chat_id, user=user, interview=interview, lang=lang)


def _send_last_ai_message(*, client, chat_id: int, interview, lang: str) -> None:
    last_ai_message = next(
        (message for message in reversed(interview.chat_history or []) if message.get("role") == "ai"),
        None,
    )
    if last_ai_message and last_ai_message.get("text"):
        client.send_message(chat_id=chat_id, text=last_ai_message["text"], parse_mode="Markdown")
    else:
        client.send_message(chat_id=chat_id, text=t("common.error_generic", lang=lang))


def _finish_interview(*, client, chat_id: int, user, interview, lang: str) -> None:
    client.send_message(
        chat_id=chat_id,
        text=t("candidate.ps_complete", lang=lang),
        parse_mode="Markdown",
    )
    clear_session(role=ROLE_CANDIDATE, telegram_id=user.telegram_id)
    logger.info("Telegram interview completed: session=%s user_tg=%s", interview.id, user.telegram_id)

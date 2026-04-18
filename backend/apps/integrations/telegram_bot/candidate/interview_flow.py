"""Candidate bot — in-Telegram prescreening interview Q&A loop.

Flow:
  start_bot_interview()   → sets interview IN_PROGRESS, appends Q1 to
                            chat_history, sends Q1 to user.
  handle_interview_answer() → appends user answer to chat_history, then
                              either sends next question or completes the interview.
  _complete_interview()   → thanks user, clears session, fires async evaluation.
"""

from __future__ import annotations

import logging

from django.utils import timezone

from apps.integrations.telegram_bot.bots import ROLE_CANDIDATE
from apps.integrations.telegram_bot.candidate.states import (
    SK_INTERVIEW_ID,
    SK_QUESTION_COUNT,
    SK_QUESTION_IDX,
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
    questions: list[str],
    vacancy_title: str,
    lang: str,
) -> None:
    """Mark interview IN_PROGRESS, store state, send intro + first question."""
    from apps.interviews.models import Interview

    interview.status = Interview.Status.IN_PROGRESS
    interview.started_at = timezone.now()
    interview.chat_history = []
    interview.save(update_fields=["status", "started_at", "chat_history", "updated_at"])

    update_session(
        role=ROLE_CANDIDATE,
        telegram_id=user.telegram_id,
        state=STATE_PS_INTERVIEW,
        **{
            SK_INTERVIEW_ID: str(interview.id),
            SK_QUESTION_IDX: 0,
            SK_QUESTION_COUNT: len(questions),
        },
    )

    client.send_message(
        chat_id=chat_id,
        text=t("candidate.ps_starting", lang=lang, title=vacancy_title),
        parse_mode="Markdown",
    )
    _send_question(client=client, chat_id=chat_id, interview=interview, questions=questions, idx=0, lang=lang)


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
    from apps.interviews.models import Interview
    from apps.vacancies.models import InterviewQuestion

    interview_id = session.get(SK_INTERVIEW_ID)
    idx = session.get(SK_QUESTION_IDX, 0)
    vacancy_id = session.get(SK_VACANCY_ID)

    try:
        interview = Interview.objects.select_related(
            "application__vacancy__company",
            "application__vacancy__employer",
        ).get(id=interview_id)
    except (Interview.DoesNotExist, Exception):
        client.send_message(chat_id=chat_id, text=t("common.error_generic", lang=lang))
        return

    questions = list(
        InterviewQuestion.objects.filter(
            vacancy_id=vacancy_id,
            step="prescanning",
            is_active=True,
        )
        .order_by("order")
        .values_list("text", flat=True)
    )

    # Append user's answer to chat_history
    history = list(interview.chat_history or [])
    history.append({"role": "user", "text": text, "timestamp": timezone.now().isoformat()})
    interview.chat_history = history
    interview.save(update_fields=["chat_history", "updated_at"])

    next_idx = idx + 1
    if next_idx < len(questions):
        update_session(role=ROLE_CANDIDATE, telegram_id=user.telegram_id, **{SK_QUESTION_IDX: next_idx})
        _send_question(
            client=client, chat_id=chat_id, interview=interview, questions=questions, idx=next_idx, lang=lang
        )
    else:
        _complete_interview(client=client, chat_id=chat_id, user=user, interview=interview, lang=lang)


def _send_question(*, client, chat_id: int, interview, questions: list[str], idx: int, lang: str) -> None:
    """Append question to chat_history, save, and send to user."""
    q_text = questions[idx]
    history = list(interview.chat_history or [])
    history.append({"role": "ai", "text": q_text, "timestamp": timezone.now().isoformat()})
    interview.chat_history = history
    interview.save(update_fields=["chat_history", "updated_at"])

    client.send_message(
        chat_id=chat_id,
        text=t("candidate.ps_question", lang=lang, n=idx + 1, total=len(questions), text=q_text),
        parse_mode="Markdown",
    )


def _complete_interview(*, client, chat_id: int, user, interview, lang: str) -> None:
    from apps.interviews.tasks import evaluate_telegram_interview

    client.send_message(
        chat_id=chat_id,
        text=t("candidate.ps_complete", lang=lang),
        parse_mode="Markdown",
    )
    clear_session(role=ROLE_CANDIDATE, telegram_id=user.telegram_id)
    evaluate_telegram_interview.delay(str(interview.id))
    logger.info("Telegram interview completed: session=%s user_tg=%s", interview.id, user.telegram_id)

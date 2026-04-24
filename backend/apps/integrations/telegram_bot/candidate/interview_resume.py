"""Resume Telegram prescreening sessions from deep links."""

from __future__ import annotations

from apps.integrations.telegram_bot.bots import ROLE_CANDIDATE
from apps.integrations.telegram_bot.candidate.interview_flow import (
    _send_last_ai_message,
    start_bot_interview,
)
from apps.integrations.telegram_bot.candidate.states import (
    SK_INTERVIEW_ID,
    SK_VACANCY_ID,
    STATE_PS_INTERVIEW,
)
from apps.integrations.telegram_bot.i18n import t
from apps.integrations.telegram_bot.sessions import clear_session, update_session


def resume_bot_interview(*, client, chat_id: int, user, interview, lang: str) -> None:
    from apps.interviews.models import Interview
    from apps.vacancies.models import InterviewQuestion

    if interview.session_type != Interview.SessionType.PRESCANNING:
        client.send_message(chat_id=chat_id, text=t("candidate.ps_not_available", lang=lang))
        return

    if interview.status in (
        Interview.Status.COMPLETED,
        Interview.Status.CANCELLED,
        Interview.Status.EXPIRED,
    ):
        client.send_message(chat_id=chat_id, text=t("candidate.ps_not_available", lang=lang))
        return

    questions = list(
        InterviewQuestion.objects.filter(
            vacancy_id=interview.application.vacancy_id,
            step="prescanning",
            is_active=True,
        )
        .order_by("order")
        .values_list("text", flat=True)
    )
    if not questions:
        client.send_message(chat_id=chat_id, text=t("candidate.ps_no_questions", lang=lang))
        clear_session(role=ROLE_CANDIDATE, telegram_id=user.telegram_id)
        return

    if interview.status == Interview.Status.IN_PROGRESS and interview.channel != Interview.Channel.TELEGRAM:
        client.send_message(chat_id=chat_id, text=t("candidate.ps_continue_on_web", lang=lang))
        return

    if interview.status == Interview.Status.PENDING:
        interview.channel = Interview.Channel.TELEGRAM
        interview.save(update_fields=["channel", "updated_at"])
        start_bot_interview(
            client=client,
            chat_id=chat_id,
            user=user,
            interview=interview,
            vacancy_title=interview.application.vacancy.title,
            lang=lang,
        )
        return

    update_session(
        role=ROLE_CANDIDATE,
        telegram_id=user.telegram_id,
        state=STATE_PS_INTERVIEW,
        **{
            SK_VACANCY_ID: str(interview.application.vacancy_id),
            SK_INTERVIEW_ID: str(interview.id),
        },
    )

    client.send_message(
        chat_id=chat_id,
        text=t("candidate.ps_resume", lang=lang, title=interview.application.vacancy.title),
        parse_mode="Markdown",
    )
    _send_last_ai_message(client=client, chat_id=chat_id, interview=interview, lang=lang)

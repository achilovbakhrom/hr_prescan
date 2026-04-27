"""CV selection helpers for Telegram prescreening."""

from __future__ import annotations

from uuid import UUID

from apps.accounts.models import CandidateCV
from apps.integrations.telegram_bot.bots import ROLE_CANDIDATE
from apps.integrations.telegram_bot.candidate.menus import cv_keyboard, cv_selection_keyboard
from apps.integrations.telegram_bot.candidate.states import SK_CV_FILENAME, SK_CV_PATH, SK_VACANCY_ID, STATE_PS_CV
from apps.integrations.telegram_bot.i18n import t
from apps.integrations.telegram_bot.sessions import update_session
from apps.vacancies.models import Vacancy


def go_to_cv_step(*, client, chat_id: int, user, session: dict, lang: str) -> None:
    vacancy = Vacancy.objects.filter(id=session.get(SK_VACANCY_ID)).first()
    update_session(role=ROLE_CANDIDATE, telegram_id=user.telegram_id, state=STATE_PS_CV)
    cv_required = bool(vacancy and vacancy.cv_required)
    cv_options = _cv_options(user=user)

    if cv_options:
        client.send_message(
            chat_id=chat_id,
            text=t("candidate.ps_cv_choose", lang=lang),
            reply_markup=cv_selection_keyboard(cv_options=cv_options, lang=lang, cv_required=cv_required),
            parse_mode="Markdown",
        )
    elif cv_required:
        client.send_message(chat_id=chat_id, text=t("candidate.ps_cv_required", lang=lang))
    else:
        client.send_message(
            chat_id=chat_id,
            text=t("candidate.ps_cv_optional", lang=lang),
            reply_markup=cv_keyboard(lang=lang),
            parse_mode="Markdown",
        )


def handle_cv_select(*, client, chat_id: int, user, cv_id: str, session: dict, lang: str) -> None:
    cv = _get_cv(user=user, cv_id=cv_id)
    if cv is None:
        client.send_message(chat_id=chat_id, text=t("candidate.ps_cv_not_found", lang=lang))
        return

    updated_session = {
        **session,
        SK_CV_PATH: cv.file,
        SK_CV_FILENAME: cv.name,
    }
    update_session(
        role=ROLE_CANDIDATE,
        telegram_id=user.telegram_id,
        **{SK_CV_PATH: cv.file, SK_CV_FILENAME: cv.name},
    )
    client.send_message(chat_id=chat_id, text=t("candidate.ps_cv_selected", lang=lang, name=cv.name))

    from apps.integrations.telegram_bot.candidate.prescreening_steps import start_interview_submission

    start_interview_submission(client=client, chat_id=chat_id, user=user, session=updated_session, lang=lang)


def prompt_upload_new_cv(*, client, chat_id: int, lang: str) -> None:
    client.send_message(chat_id=chat_id, text=t("candidate.ps_cv_upload_prompt", lang=lang))


def _cv_options(*, user) -> list[dict]:
    return [
        {"id": str(cv.id), "name": cv.name, "is_active": cv.is_active}
        for cv in CandidateCV.objects.filter(profile__user=user)
        .exclude(file="")
        .order_by("-is_active", "-created_at")[:8]
    ]


def _get_cv(*, user, cv_id: str) -> CandidateCV | None:
    try:
        parsed_id = UUID(str(cv_id))
    except (TypeError, ValueError):
        return None
    return CandidateCV.objects.filter(id=parsed_id, profile__user=user).exclude(file="").first()

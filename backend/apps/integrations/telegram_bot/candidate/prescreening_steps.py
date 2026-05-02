"""Internal step helpers for the prescreening flow.

Called only from prescreening.py — not part of the public bot API.
"""

from __future__ import annotations

import logging
import re
from uuid import UUID

from apps.common.exceptions import ApplicationError
from apps.integrations.telegram_bot.bots import ROLE_CANDIDATE
from apps.integrations.telegram_bot.candidate.language import set_user_language
from apps.integrations.telegram_bot.candidate.menus import (
    confirm_name_keyboard,
    confirm_phone_keyboard,
)
from apps.integrations.telegram_bot.candidate.states import (
    SK_CV_FILENAME,
    SK_CV_PATH,
    SK_LANG,
    SK_NAME,
    SK_PHONE,
    SK_VACANCY_ID,
    STATE_PS_CHANGE_PHONE,
    STATE_PS_CONFIRM_NAME,
    STATE_PS_CONFIRM_PHONE,
)
from apps.integrations.telegram_bot.i18n import t
from apps.integrations.telegram_bot.sessions import clear_session, update_session

logger = logging.getLogger(__name__)

_CONTACT_MIN_LENGTH = 3
_CONTACT_MAX_LENGTH = 50


def handle_vacancy_code(*, client, chat_id: int, user, text: str, lang: str) -> None:
    from apps.vacancies.models import Vacancy

    text = text.strip()
    if not text.isdigit() or len(text) != 6:
        client.send_message(chat_id=chat_id, text=t("candidate.ps_code_invalid", lang=lang))
        return

    vacancy = (
        Vacancy.objects.filter(
            telegram_code=int(text),
            is_deleted=False,
            status=Vacancy.Status.PUBLISHED,
        )
        .select_related("company")
        .first()
    )

    if not vacancy:
        client.send_message(chat_id=chat_id, text=t("candidate.ps_code_not_found", lang=lang, code=text))
        return

    lang = _apply_prescreening_language(user=user, language=vacancy.prescanning_language, fallback=lang)
    name = user.full_name or ""
    update_session(
        role=ROLE_CANDIDATE,
        telegram_id=user.telegram_id,
        state=STATE_PS_CONFIRM_NAME,
        **{SK_VACANCY_ID: str(vacancy.id), SK_NAME: name, SK_LANG: lang},
    )
    client.send_message(
        chat_id=chat_id,
        text=t(
            "candidate.ps_confirm_name",
            lang=lang,
            title=_md_escape(vacancy.title),
            company=_md_escape(vacancy.company.name),
            name=_md_escape(name),
        ),
        reply_markup=confirm_name_keyboard(lang=lang),
        parse_mode="Markdown",
    )


def handle_new_name(*, client, chat_id: int, user, text: str, session: dict, lang: str) -> None:
    words = text.strip().split()
    if len(words) < 2:
        client.send_message(chat_id=chat_id, text=t("candidate.reg_invalid_name", lang=lang))
        return
    update_session(role=ROLE_CANDIDATE, telegram_id=user.telegram_id, **{SK_NAME: text.strip()})
    go_to_confirm_phone(
        client=client, chat_id=chat_id, user=user, session={**session, SK_NAME: text.strip()}, lang=lang
    )


def handle_new_phone(*, client, chat_id: int, user, text: str, session: dict, lang: str) -> None:
    contact = re.sub(r"\s+", " ", text.strip())
    if not (_CONTACT_MIN_LENGTH <= len(contact) <= _CONTACT_MAX_LENGTH):
        client.send_message(chat_id=chat_id, text=t("candidate.ps_invalid_contact", lang=lang))
        return
    update_session(role=ROLE_CANDIDATE, telegram_id=user.telegram_id, **{SK_PHONE: contact})
    go_to_cv_step(client=client, chat_id=chat_id, user=user, session={**session, SK_PHONE: contact}, lang=lang)


def go_to_confirm_phone(*, client, chat_id: int, user, session: dict, lang: str) -> None:
    phone = session.get(SK_PHONE) or user.phone or ""
    if not phone:
        update_session(role=ROLE_CANDIDATE, telegram_id=user.telegram_id, state=STATE_PS_CHANGE_PHONE)
        client.send_message(chat_id=chat_id, text=t("candidate.ps_ask_new_phone", lang=lang))
        return

    update_session(
        role=ROLE_CANDIDATE,
        telegram_id=user.telegram_id,
        state=STATE_PS_CONFIRM_PHONE,
        **{SK_PHONE: phone},
    )
    client.send_message(
        chat_id=chat_id,
        text=t("candidate.ps_confirm_phone", lang=lang, phone=_md_escape(phone or "—")),
        reply_markup=confirm_phone_keyboard(lang=lang),
        parse_mode="Markdown",
    )


def go_to_cv_step(*, client, chat_id: int, user, session: dict, lang: str) -> None:
    from apps.integrations.telegram_bot.candidate.prescreening_cv import go_to_cv_step as show_cv_step

    show_cv_step(client=client, chat_id=chat_id, user=user, session=session, lang=lang)


def start_interview_submission(*, client, chat_id: int, user, session: dict, lang: str) -> None:
    from apps.applications.services import submit_application
    from apps.integrations.telegram_bot.candidate.interview_flow import start_bot_interview
    from apps.vacancies.models import InterviewQuestion, Vacancy

    try:
        vacancy_id = UUID(session.get(SK_VACANCY_ID, ""))
    except (ValueError, TypeError):
        client.send_message(chat_id=chat_id, text=t("common.error_generic", lang=lang))
        return

    try:
        result = submit_application(
            vacancy_id=vacancy_id,
            candidate_name=session.get(SK_NAME) or user.full_name or "Candidate",
            candidate_email=user.email,
            candidate_phone=session.get(SK_PHONE) or user.phone or "",
            cv_file_path=session.get(SK_CV_PATH, ""),
            cv_original_filename=session.get(SK_CV_FILENAME, ""),
            candidate=user,
            channel="telegram",
        )
    except ApplicationError as exc:
        client.send_message(chat_id=chat_id, text=str(exc.message))
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
    if not questions:
        client.send_message(chat_id=chat_id, text=t("candidate.ps_no_questions", lang=lang))
        clear_session(role=ROLE_CANDIDATE, telegram_id=user.telegram_id)
        return

    vacancy = Vacancy.objects.filter(id=vacancy_id).first()
    update_session(role=ROLE_CANDIDATE, telegram_id=user.telegram_id, **{SK_VACANCY_ID: str(vacancy_id)})
    start_bot_interview(
        client=client,
        chat_id=chat_id,
        user=user,
        interview=result["prescan_session"],
        vacancy_title=vacancy.title if vacancy else "",
        lang=lang,
    )


def _apply_prescreening_language(*, user, language: str, fallback: str) -> str:
    return set_user_language(user=user, language=language, fallback=fallback)


def _md_escape(text: str) -> str:
    """Escape Telegram Markdown (legacy) special characters."""
    return text.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("`", "\\`")

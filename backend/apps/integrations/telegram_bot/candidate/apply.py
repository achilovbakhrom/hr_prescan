"""Candidate bot vacancy cards and apply actions.

End-to-end:
    1. /start vac_<uuid|code>      -> show_vacancy_card
    2. user uploads CV (document)  -> store cv_file_path on session
    3. user taps [Apply]           -> submit_application -> confirmation

If the vacancy requires a CV and none is uploaded yet, the bot prompts and
remembers the pending apply on the session so the user can resume after
sending the document.
"""

from __future__ import annotations

import logging

from apps.applications.services import get_candidate_platform_cv, submit_application
from apps.common.exceptions import ApplicationError
from apps.common.messages import MSG_ALREADY_APPLIED
from apps.integrations.telegram_bot.bots import ROLE_CANDIDATE
from apps.integrations.telegram_bot.candidate.menus import vacancy_actions_keyboard
from apps.integrations.telegram_bot.client import TelegramClient
from apps.integrations.telegram_bot.i18n import t
from apps.integrations.telegram_bot.sessions import (
    clear_session_field,
    update_session,
)
from apps.vacancies.models import Vacancy
from apps.vacancies.selectors import get_vacancy_by_id

logger = logging.getLogger(__name__)


def show_vacancy_card(
    *,
    client: TelegramClient,
    chat_id: int,
    vacancy_id,
    lang: str,
) -> None:
    """Render a vacancy detail card with Apply / Back buttons."""
    vacancy = get_vacancy_by_id(vacancy_id=vacancy_id)
    if vacancy is None or vacancy.status != Vacancy.Status.PUBLISHED or vacancy.visibility != Vacancy.Visibility.PUBLIC:
        client.send_message(
            chat_id=chat_id,
            text=t("candidate.vacancy_not_found", lang=lang),
        )
        return

    text = _format_vacancy(vacancy=vacancy)
    client.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="Markdown",
        reply_markup=vacancy_actions_keyboard(vacancy_id=vacancy.id, lang=lang),
        disable_web_page_preview=True,
    )


def confirm_apply(
    *,
    client: TelegramClient,
    chat_id: int,
    user,
    vacancy_id,
    cv_file_path: str,
    cv_original_filename: str,
    lang: str,
) -> bool:
    """Submit the application. Returns True on success."""
    vacancy = get_vacancy_by_id(vacancy_id=vacancy_id)
    if vacancy is None or vacancy.status != Vacancy.Status.PUBLISHED:
        client.send_message(chat_id=chat_id, text=t("candidate.vacancy_not_found", lang=lang))
        return False

    platform_cv_path, _ = get_candidate_platform_cv(candidate=user)
    if vacancy.cv_required and not cv_file_path and not platform_cv_path:
        update_session(
            role=ROLE_CANDIDATE,
            telegram_id=user.telegram_id,
            pending_apply_vacancy_id=str(vacancy_id),
        )
        client.send_message(
            chat_id=chat_id,
            text=t("candidate.cv_required_prompt", lang=lang),
            parse_mode="Markdown",
        )
        return False

    try:
        submit_application(
            vacancy_id=vacancy.id,
            candidate=user,
            candidate_name=user.full_name or "Telegram User",
            candidate_email=user.email,
            candidate_phone=user.phone or "",
            cv_file_path=cv_file_path,
            cv_original_filename=cv_original_filename,
        )
    except ApplicationError as exc:
        # Friendly mapping for the most common case: already applied.
        if str(exc.message) == str(MSG_ALREADY_APPLIED):
            client.send_message(chat_id=chat_id, text=t("candidate.already_applied", lang=lang))
        else:
            client.send_message(chat_id=chat_id, text=str(exc.message))
        return False

    clear_session_field(
        role=ROLE_CANDIDATE,
        telegram_id=user.telegram_id,
        field="pending_apply_vacancy_id",
    )
    client.send_message(
        chat_id=chat_id,
        text=t("candidate.application_submitted", lang=lang, title=vacancy.title),
        parse_mode="Markdown",
    )
    return True


def _format_vacancy(*, vacancy: Vacancy) -> str:
    """Render a vacancy as a Markdown card for Telegram."""
    parts = [f"*{_md_escape(vacancy.title)}*"]
    if vacancy.company and vacancy.company.name:
        parts.append(f"_{_md_escape(vacancy.company.name)}_")

    meta: list[str] = []
    if vacancy.location:
        meta.append(vacancy.location)
    if vacancy.is_remote:
        meta.append("Remote")
    meta.append(vacancy.get_employment_type_display())
    meta.append(vacancy.get_experience_level_display())
    parts.append(" · ".join(meta))

    if vacancy.salary_min or vacancy.salary_max:
        parts.append(f"💰 {_format_salary(vacancy)}")

    desc = vacancy.description or ""
    if len(desc) > 600:
        desc = desc[:600].rsplit(" ", 1)[0] + "…"
    if desc:
        parts.append("")
        parts.append(_md_escape(desc))

    return "\n".join(parts)


def _format_salary(vacancy: Vacancy) -> str:
    if vacancy.salary_min and vacancy.salary_max:
        return f"{int(vacancy.salary_min)}–{int(vacancy.salary_max)} {vacancy.salary_currency}"
    if vacancy.salary_min:
        return f"from {int(vacancy.salary_min)} {vacancy.salary_currency}"
    return f"up to {int(vacancy.salary_max)} {vacancy.salary_currency}"


def _md_escape(text: str) -> str:
    """Escape Telegram Markdown (legacy) special characters."""
    return text.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("`", "\\`")

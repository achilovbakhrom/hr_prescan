"""Vacancy picker for candidate Telegram prescreening."""

from __future__ import annotations

from uuid import UUID

from apps.integrations.telegram_bot.bots import ROLE_CANDIDATE
from apps.integrations.telegram_bot.candidate.language import set_user_language
from apps.integrations.telegram_bot.candidate.menus import CB_MENU, confirm_name_keyboard
from apps.integrations.telegram_bot.i18n import t
from apps.integrations.telegram_bot.keyboards import button, inline_keyboard
from apps.integrations.telegram_bot.sessions import update_session
from apps.vacancies.models import Vacancy

CB_PS_CODE_ENTRY = "cand:ps:code"
CB_PS_VACANCY_PREFIX = "cand:ps:vac:"


def send_vacancy_picker(*, client, chat_id: int, lang: str) -> None:
    vacancies = list(
        Vacancy.objects.filter(
            is_deleted=False,
            status=Vacancy.Status.PUBLISHED,
            visibility=Vacancy.Visibility.PUBLIC,
        )
        .select_related("company")
        .order_by("-created_at")[:8]
    )
    rows = [
        [button(text=_vacancy_label(vacancy), callback_data=f"{CB_PS_VACANCY_PREFIX}{vacancy.id}")]
        for vacancy in vacancies
    ]
    rows.append([button(text=t("candidate.btn_enter_code", lang=lang), callback_data=CB_PS_CODE_ENTRY)])
    rows.append([button(text=t("candidate.button_back", lang=lang), callback_data=CB_MENU)])
    client.send_message(
        chat_id=chat_id,
        text=t("candidate.ps_choose_vacancy" if vacancies else "candidate.ps_choose_empty", lang=lang),
        reply_markup=inline_keyboard(rows),
    )


def handle_vacancy_code(*, client, chat_id: int, user, text: str, lang: str) -> None:
    code = text.strip()
    if not code.isdigit() or len(code) != 6:
        client.send_message(chat_id=chat_id, text=t("candidate.ps_code_invalid", lang=lang))
        return

    vacancy = _visible_vacancies().filter(telegram_code=int(code)).first()
    if not vacancy:
        client.send_message(chat_id=chat_id, text=t("candidate.ps_code_not_found", lang=lang, code=code))
        return
    start_vacancy_prescreening(client=client, chat_id=chat_id, user=user, vacancy=vacancy, lang=lang)


def handle_vacancy_selection(*, client, chat_id: int, user, vacancy_id: str, lang: str) -> None:
    try:
        parsed_id = UUID(str(vacancy_id))
    except (TypeError, ValueError):
        client.send_message(chat_id=chat_id, text=t("candidate.vacancy_not_found", lang=lang))
        return

    vacancy = _visible_vacancies().filter(id=parsed_id).first()
    if vacancy is None:
        client.send_message(chat_id=chat_id, text=t("candidate.vacancy_not_found", lang=lang))
        return
    start_vacancy_prescreening(client=client, chat_id=chat_id, user=user, vacancy=vacancy, lang=lang)


def start_vacancy_prescreening(*, client, chat_id: int, user, vacancy: Vacancy, lang: str) -> None:
    from apps.integrations.telegram_bot.candidate.states import (
        SK_LANG,
        SK_NAME,
        SK_VACANCY_ID,
        STATE_PS_CONFIRM_NAME,
    )

    lang = set_user_language(user=user, language=vacancy.prescanning_language, fallback=lang)
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


def _visible_vacancies():
    return Vacancy.objects.filter(
        is_deleted=False,
        status=Vacancy.Status.PUBLISHED,
        visibility=Vacancy.Visibility.PUBLIC,
    ).select_related("company")


def _vacancy_label(vacancy: Vacancy) -> str:
    company = f" · {vacancy.company.name}" if vacancy.company_id else ""
    label = f"{vacancy.title}{company}"
    return f"🎯 {label[:48]}"


def _md_escape(text: str) -> str:
    return text.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("`", "\\`")

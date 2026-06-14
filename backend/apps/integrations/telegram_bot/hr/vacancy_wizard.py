"""Screen-based HR vacancy creation wizard for Telegram."""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

from apps.common.ai_assistant.handlers_vacancy_generation import ensure_vacancy_screening_setup
from apps.common.ai_assistant.vacancy_company_resolver import user_live_companies
from apps.integrations.telegram_bot.bots import ROLE_HR
from apps.integrations.telegram_bot.screens import delete_message, send_screen
from apps.integrations.telegram_bot.sessions import get_session, update_session
from apps.vacancies.models import ScreeningStep, Vacancy
from apps.vacancies.services import create_vacancy, publish_vacancy

from .vacancy_wizard_constants import (
    CB_BACK,
    CB_CANCEL,
    CB_CONFIRM,
    CB_DRAFT,
    CB_PREFIX,
    CB_PUBLISH,
    CB_SET_PREFIX,
    CB_SKIP,
    STATE,
    STEPS,
    WIZARD,
)
from .vacancy_wizard_ui import nav_keyboard, render_wizard, step_index


def is_vacancy_wizard_callback(*, data: str) -> bool:
    return data.startswith(CB_PREFIX)


def start_wizard(*, client, chat_id: int, telegram_id: int, user, source_message_id: int | None = None) -> None:
    companies = list(user_live_companies(user))
    if not companies:
        send_screen(
            client=client,
            role=ROLE_HR,
            telegram_id=telegram_id,
            chat_id=chat_id,
            text="Create your company first, then come back to create a vacancy.",
            reply_markup=nav_keyboard(include_back=False),
            screen_name=WIZARD,
            source_message_id=source_message_id,
        )
        return
    step = "company" if len(companies) > 1 else "title"
    data = {"company_id": str(companies[0].id)} if len(companies) == 1 else {}
    update_session(role=ROLE_HR, telegram_id=telegram_id, state=STATE, vacancy_wizard={"step": step, "data": data})
    render_wizard(
        client=client,
        chat_id=chat_id,
        telegram_id=telegram_id,
        user=user,
        source_message_id=source_message_id,
    )


def handle_callback(
    *,
    client,
    chat_id: int,
    telegram_id: int,
    user,
    data: str,
    source_message_id: int | None = None,
) -> None:
    wizard = get_session(role=ROLE_HR, telegram_id=telegram_id).get("vacancy_wizard") or {}
    if data in (CB_CANCEL, CB_DRAFT):
        _finish(client=client, chat_id=chat_id, telegram_id=telegram_id, user=user, source_message_id=source_message_id)
    elif data == CB_BACK:
        _go_back(telegram_id=telegram_id, wizard=wizard)
        render_wizard(
            client=client,
            chat_id=chat_id,
            telegram_id=telegram_id,
            user=user,
            source_message_id=source_message_id,
        )
    elif data == CB_SKIP:
        _advance(telegram_id=telegram_id, wizard=wizard)
        render_wizard(
            client=client,
            chat_id=chat_id,
            telegram_id=telegram_id,
            user=user,
            source_message_id=source_message_id,
        )
    elif data.startswith(CB_SET_PREFIX):
        _handle_set_callback(telegram_id=telegram_id, wizard=wizard, data=data)
        render_wizard(
            client=client,
            chat_id=chat_id,
            telegram_id=telegram_id,
            user=user,
            source_message_id=source_message_id,
        )
    elif data == CB_CONFIRM:
        _create(client=client, chat_id=chat_id, telegram_id=telegram_id, user=user, wizard=wizard)
    elif data == CB_PUBLISH:
        _publish(client=client, chat_id=chat_id, telegram_id=telegram_id, user=user, wizard=wizard)


def handle_text(*, client, chat_id: int, telegram_id: int, user, text: str, message_id: int | None = None) -> bool:
    session = get_session(role=ROLE_HR, telegram_id=telegram_id)
    if session.get("state") != STATE:
        return False
    delete_message(client=client, chat_id=chat_id, message_id=message_id)
    normalized = text.strip()
    if normalized.lower() in {"/cancel", "cancel", "отмена", "bekor", "/menu", "menu", "main menu"}:
        _finish(client=client, chat_id=chat_id, telegram_id=telegram_id, user=user)
        return True
    wizard = session.get("vacancy_wizard") or {}
    if normalized.lower() not in {"skip", "пропустить", "o'tkazib yuborish"}:
        _store_answer(wizard=wizard, answer=normalized)
    _advance(telegram_id=telegram_id, wizard=wizard)
    render_wizard(client=client, chat_id=chat_id, telegram_id=telegram_id, user=user)
    return True


def _handle_set_callback(*, telegram_id: int, wizard: dict, data: str) -> None:
    _, field, value = data.split(":", 4)[2:]
    values = wizard.setdefault("data", {})
    values[field] = value == "yes" if field == "interview_enabled" else value
    _advance(telegram_id=telegram_id, wizard=wizard)


def _store_answer(*, wizard: dict, answer: str) -> None:
    data = wizard.setdefault("data", {})
    step = wizard.get("step", "title")
    if step == "title":
        data["title"] = answer[:255]
    elif step == "description":
        data["description"] = answer
    elif step == "skills":
        data["skills"] = [s.strip() for s in answer.split(",") if s.strip()]
    elif step == "location":
        data["location"] = answer
        data["is_remote"] = "remote" in answer.lower()
    elif step == "salary":
        data.update(_parse_salary(answer))


def _advance(*, telegram_id: int, wizard: dict) -> None:
    current = wizard.get("step", "title")
    wizard["step"] = _first_missing(wizard.get("data", {})) if current == STEPS[-1] else _next_after(current)
    update_session(role=ROLE_HR, telegram_id=telegram_id, state=STATE, vacancy_wizard=wizard)


def _go_back(*, telegram_id: int, wizard: dict) -> None:
    wizard["step"] = STEPS[max(0, step_index(wizard.get("step", "title")) - 1)]
    update_session(role=ROLE_HR, telegram_id=telegram_id, state=STATE, vacancy_wizard=wizard)


def _next_after(step: str) -> str:
    index = step_index(step)
    return "confirm" if index >= len(STEPS) - 1 else STEPS[index + 1]


def _first_missing(data: dict) -> str:
    for field, step in (("company_id", "company"), ("title", "title"), ("description", "description")):
        if not data.get(field):
            return step
    return "confirm"


def _parse_salary(answer: str) -> dict:
    numbers = re.findall(r"\d+(?:[.,]\d+)?", answer)
    try:
        parsed = {"salary_min": Decimal(numbers[0].replace(",", "."))} if numbers else {}
        if len(numbers) > 1:
            parsed["salary_max"] = Decimal(numbers[1].replace(",", "."))
    except InvalidOperation:
        return {}
    currency = re.search(r"\b(USD|EUR|UZS|RUB|KZT|TRY)\b", answer.upper())
    if currency:
        parsed["salary_currency"] = currency.group(1)
    return parsed


def _create(*, client, chat_id: int, telegram_id: int, user, wizard: dict) -> None:
    data = wizard.get("data", {})
    company = user_live_companies(user).filter(id=data["company_id"]).first()
    if company is None:
        wizard["step"] = "company"
        update_session(role=ROLE_HR, telegram_id=telegram_id, state=STATE, vacancy_wizard=wizard)
        render_wizard(client=client, chat_id=chat_id, telegram_id=telegram_id, user=user)
        return
    vacancy = create_vacancy(company=company, created_by=user, **_vacancy_kwargs(data))
    data["vacancy_id"] = str(vacancy.id)
    wizard["step"] = "created"
    update_session(role=ROLE_HR, telegram_id=telegram_id, state=STATE, vacancy_wizard=wizard)
    render_wizard(client=client, chat_id=chat_id, telegram_id=telegram_id, user=user)


def _publish(*, client, chat_id: int, telegram_id: int, user, wizard: dict) -> None:
    vacancy = Vacancy.objects.filter(id=(wizard.get("data") or {}).get("vacancy_id"), created_by=user).first()
    if vacancy is not None:
        ensure_vacancy_screening_setup(vacancy=vacancy, step=ScreeningStep.PRESCANNING)
        if vacancy.interview_enabled:
            ensure_vacancy_screening_setup(vacancy=vacancy, step=ScreeningStep.INTERVIEW)
        publish_vacancy(vacancy=vacancy)
    _finish(client=client, chat_id=chat_id, telegram_id=telegram_id, user=user)


def _vacancy_kwargs(data: dict) -> dict:
    kwargs = {
        "title": data["title"],
        "description": data["description"],
        "skills": data.get("skills") or [],
        "location": data.get("location", ""),
        "is_remote": data.get("is_remote", False),
        "experience_level": data.get("experience_level", Vacancy.ExperienceLevel.MIDDLE),
        "visibility": data.get("visibility", Vacancy.Visibility.PUBLIC),
        "interview_enabled": data.get("interview_enabled", False),
    }
    kwargs.update({key: data[key] for key in ("salary_min", "salary_max", "salary_currency") if data.get(key)})
    return kwargs


def _finish(*, client, chat_id: int, telegram_id: int, user, source_message_id: int | None = None) -> None:
    update_session(role=ROLE_HR, telegram_id=telegram_id, state="", vacancy_wizard={})
    from apps.integrations.telegram_bot.hr.menus import send_main_menu

    send_main_menu(client=client, chat_id=chat_id, user=user, source_message_id=source_message_id)

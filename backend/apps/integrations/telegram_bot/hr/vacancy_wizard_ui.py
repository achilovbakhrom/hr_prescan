"""Rendering helpers for the HR Telegram vacancy wizard."""

from __future__ import annotations

from apps.common.ai_assistant.vacancy_company_resolver import user_live_companies
from apps.integrations.telegram_bot.bots import ROLE_HR
from apps.integrations.telegram_bot.keyboards import button, inline_keyboard
from apps.integrations.telegram_bot.screens import send_screen
from apps.integrations.telegram_bot.sessions import get_session
from apps.vacancies.models import Vacancy

from .vacancy_wizard_constants import (
    CB_BACK,
    CB_CANCEL,
    CB_CONFIRM,
    CB_DRAFT,
    CB_PUBLISH,
    CB_SET_PREFIX,
    CB_SKIP,
    STEPS,
    WIZARD,
)


def render_wizard(*, client, chat_id: int, telegram_id: int, user, source_message_id: int | None = None) -> None:
    wizard = get_session(role=ROLE_HR, telegram_id=telegram_id).get("vacancy_wizard") or {}
    step = wizard.get("step", "title")
    if step == "confirm":
        text = _summary(wizard)
    elif step == "created":
        text = _created_text(wizard)
    else:
        text = _prompt(wizard=wizard, step=step)
    send_screen(
        client=client,
        role=ROLE_HR,
        telegram_id=telegram_id,
        chat_id=chat_id,
        text=text,
        reply_markup=_keyboard(user=user, wizard=wizard, step=step),
        screen_name=WIZARD,
        source_message_id=source_message_id,
    )


def nav_keyboard(*, include_back: bool = True) -> dict:
    return inline_keyboard(_nav_rows(include_back=include_back))


def step_index(step: str) -> int:
    try:
        return STEPS.index(step)
    except ValueError:
        return 0


def _prompt(*, wizard: dict, step: str) -> str:
    prompts = {
        "company": "Choose the company for this vacancy.",
        "title": "What is the job title?",
        "description": "What should this person mainly do? Send a short description.",
        "skills": "Send key skills separated by commas, or tap Skip.",
        "location": "Where is the role based? You can write Remote, city, or tap Skip.",
        "salary": "What salary range should we show? Example: 1000-1500 USD. Or tap Skip.",
        "experience": "Choose the expected seniority.",
        "interview": "Should qualified candidates pass a video interview after prescreening?",
        "visibility": "Should the vacancy be public or private?",
    }
    progress = _compact_progress(wizard)
    suffix = f"\n\n{progress}" if progress else ""
    return f"*Create vacancy*\n\n{prompts.get(step, prompts['title'])}{suffix}"


def _keyboard(*, user, wizard: dict, step: str) -> dict:
    if step == "company":
        rows = [
            [button(text=c.name[:36], callback_data=f"{CB_SET_PREFIX}company_id:{c.id}")]
            for c in user_live_companies(user)[:8]
        ]
    elif step == "experience":
        rows = [
            [button(text=label, callback_data=f"{CB_SET_PREFIX}experience_level:{value}")]
            for value, label in Vacancy.ExperienceLevel.choices
        ]
    elif step == "interview":
        rows = [
            [
                button(text="Yes", callback_data=f"{CB_SET_PREFIX}interview_enabled:yes"),
                button(text="No", callback_data=f"{CB_SET_PREFIX}interview_enabled:no"),
            ]
        ]
    elif step == "visibility":
        rows = [
            [
                button(text="Public", callback_data=f"{CB_SET_PREFIX}visibility:public"),
                button(text="Private", callback_data=f"{CB_SET_PREFIX}visibility:private"),
            ]
        ]
    elif step == "confirm":
        rows = [[button(text="Create draft", callback_data=CB_CONFIRM)]]
    elif step == "created":
        rows = [
            [button(text="Generate instructions + publish", callback_data=CB_PUBLISH)],
            [button(text="Keep as draft", callback_data=CB_DRAFT)],
        ]
    else:
        rows = [[button(text="Skip", callback_data=CB_SKIP)]] if step in {"skills", "location", "salary"} else []
    rows.extend(_nav_rows(include_back=step_index(wizard.get("step", "title")) > 0))
    return inline_keyboard(rows)


def _nav_rows(*, include_back: bool) -> list[list[dict]]:
    row = []
    if include_back:
        row.append(button(text="Back", callback_data=CB_BACK))
    row.extend([button(text="Cancel", callback_data=CB_CANCEL), button(text="Main menu", callback_data="hr:menu")])
    return [row]


def _summary(wizard: dict) -> str:
    data = wizard.get("data", {})
    return (
        "*Create vacancy*\n\n"
        "Review before creating:\n\n"
        f"Title: {data.get('title', '')}\n"
        f"Description: {data.get('description', '')}\n"
        f"Skills: {', '.join(data.get('skills') or []) or 'Not specified'}\n"
        f"Location: {data.get('location') or 'Not specified'}\n"
        f"Salary: {_salary_text(data)}\n"
        f"Experience: {data.get('experience_level') or Vacancy.ExperienceLevel.MIDDLE}\n"
        f"Video interview: {'Yes' if data.get('interview_enabled') else 'No'}\n"
        f"Visibility: {data.get('visibility') or Vacancy.Visibility.PUBLIC}\n\n"
        "Create this vacancy as a draft?"
    )


def _created_text(wizard: dict) -> str:
    title = (wizard.get("data") or {}).get("title", "Vacancy")
    return (
        f"*{title}* was created as a draft.\n\n"
        "It will not accept candidates until published. I can generate AI instructions and criteria "
        "and publish it now, or keep it as a draft."
    )


def _compact_progress(wizard: dict) -> str:
    data = wizard.get("data", {})
    lines = [
        f"{key.replace('_', ' ').title()}: {data[key]}"
        for key in ("title", "location", "experience_level", "visibility")
        if data.get(key)
    ]
    return "\n".join(lines[-4:])


def _salary_text(data: dict) -> str:
    if not data.get("salary_min") and not data.get("salary_max"):
        return "Negotiable"
    currency = data.get("salary_currency") or "USD"
    if data.get("salary_min") and data.get("salary_max"):
        return f"{data['salary_min']}-{data['salary_max']} {currency}"
    return f"{data.get('salary_min') or data.get('salary_max')} {currency}"

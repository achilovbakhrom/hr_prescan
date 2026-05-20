"""Button menu for common HR Telegram actions."""

from __future__ import annotations

from collections.abc import Callable

from apps.integrations.telegram_bot.hr.i18n import text as hr_text
from apps.integrations.telegram_bot.hr.onboarding_flow import CB_LANG_MENU
from apps.integrations.telegram_bot.keyboards import button, inline_keyboard

CB_MENU = "hr:menu"
CB_CMD_PREFIX = "hr:cmd:"

PROMPTS = {
    "dashboard": "menu_prompt_dashboard",
    "vacancies": "menu_prompt_vacancies",
    "create_vacancy": "menu_prompt_create_vacancy",
    "candidates": "menu_prompt_candidates",
    "message_candidate": "menu_prompt_message_candidate",
    "interviews": "menu_prompt_interviews",
    "team": "menu_prompt_team",
    "subscription": "menu_prompt_subscription",
}


def main_menu_keyboard(*, user) -> dict:
    return inline_keyboard(
        [
            [
                button(text=hr_text("btn_dashboard", user=user), callback_data=f"{CB_CMD_PREFIX}dashboard"),
                button(text=hr_text("btn_vacancies", user=user), callback_data=f"{CB_CMD_PREFIX}vacancies"),
            ],
            [
                button(text=hr_text("btn_create_vacancy", user=user), callback_data=f"{CB_CMD_PREFIX}create_vacancy"),
            ],
            [
                button(text=hr_text("btn_candidates", user=user), callback_data=f"{CB_CMD_PREFIX}candidates"),
                button(
                    text=hr_text("btn_message_candidate", user=user),
                    callback_data=f"{CB_CMD_PREFIX}message_candidate",
                ),
            ],
            [
                button(text=hr_text("btn_interviews", user=user), callback_data=f"{CB_CMD_PREFIX}interviews"),
            ],
            [
                button(text=hr_text("btn_team", user=user), callback_data=f"{CB_CMD_PREFIX}team"),
                button(text=hr_text("btn_subscription", user=user), callback_data=f"{CB_CMD_PREFIX}subscription"),
            ],
            [button(text=hr_text("btn_language", user=user), callback_data=CB_LANG_MENU)],
        ]
    )


def send_main_menu(*, client, chat_id: int, user) -> None:
    client.send_message(
        chat_id=chat_id,
        text=hr_text("menu", user=user),
        reply_markup=main_menu_keyboard(user=user),
    )


def is_menu_callback(*, data: str) -> bool:
    return data == CB_MENU or data.startswith(CB_CMD_PREFIX)


def handle_menu_callback(
    *,
    client,
    chat_id: int,
    user,
    data: str,
    route_to_assistant: Callable,
) -> None:
    if data == CB_MENU:
        send_main_menu(client=client, chat_id=chat_id, user=user)
        return

    key = data.removeprefix(CB_CMD_PREFIX)
    prompt_key = PROMPTS.get(key)
    if not prompt_key:
        send_main_menu(client=client, chat_id=chat_id, user=user)
        return
    route_to_assistant(client=client, chat_id=chat_id, user=user, text=hr_text(prompt_key, user=user))

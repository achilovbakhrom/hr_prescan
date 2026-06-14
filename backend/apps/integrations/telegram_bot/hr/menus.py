"""Button menu for common HR Telegram actions."""

from __future__ import annotations

from collections.abc import Callable

from apps.integrations.telegram_bot.hr.i18n import text as hr_text
from apps.integrations.telegram_bot.hr.onboarding_flow import CB_LANG_MENU
from apps.integrations.telegram_bot.keyboards import button, inline_keyboard
from apps.integrations.telegram_bot.screens import send_screen
from apps.integrations.telegram_bot.sessions import update_session

CB_MENU = "hr:menu"
CB_CMD_PREFIX = "hr:cmd:"
CB_AI_START = "hr:ai:start"
CB_AI_EXIT = "hr:ai:exit"

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
            [button(text=hr_text("btn_ai_mode", user=user), callback_data=CB_AI_START)],
            [button(text=hr_text("btn_language", user=user), callback_data=CB_LANG_MENU)],
        ]
    )


def ai_mode_keyboard(*, user) -> dict:
    return inline_keyboard(
        [
            [button(text=hr_text("btn_exit_ai", user=user), callback_data=CB_AI_EXIT)],
            [button(text=hr_text("btn_main_menu", user=user), callback_data=CB_MENU)],
        ]
    )


def send_main_menu(*, client, chat_id: int, user, source_message_id: int | None = None) -> None:
    send_screen(
        client=client,
        role="hr",
        telegram_id=user.telegram_id,
        chat_id=chat_id,
        text=hr_text("menu", user=user),
        reply_markup=main_menu_keyboard(user=user),
        screen_name="main_menu",
        source_message_id=source_message_id,
    )


def is_menu_callback(*, data: str) -> bool:
    return data in (CB_MENU, CB_AI_START, CB_AI_EXIT) or data.startswith(CB_CMD_PREFIX)


def handle_menu_callback(
    *,
    client,
    chat_id: int,
    telegram_id: int,
    user,
    data: str,
    route_to_assistant: Callable,
    source_message_id: int | None = None,
) -> None:
    if data == CB_MENU:
        update_session(role="hr", telegram_id=telegram_id, ai_mode=False, state="", vacancy_wizard={})
        send_main_menu(client=client, chat_id=chat_id, user=user, source_message_id=source_message_id)
        return
    if data == CB_AI_START:
        update_session(role="hr", telegram_id=telegram_id, ai_mode=True)
        send_screen(
            client=client,
            role="hr",
            telegram_id=telegram_id,
            chat_id=chat_id,
            text=hr_text("ai_mode_started", user=user),
            reply_markup=ai_mode_keyboard(user=user),
            screen_name="ai_mode",
            source_message_id=source_message_id,
        )
        return
    if data == CB_AI_EXIT:
        update_session(role="hr", telegram_id=telegram_id, ai_mode=False)
        send_main_menu(client=client, chat_id=chat_id, user=user, source_message_id=source_message_id)
        return

    key = data.removeprefix(CB_CMD_PREFIX)
    if key == "create_vacancy":
        from apps.integrations.telegram_bot.hr.vacancy_wizard import start_wizard

        start_wizard(
            client=client,
            chat_id=chat_id,
            telegram_id=telegram_id,
            user=user,
            source_message_id=source_message_id,
        )
        return
    prompt_key = PROMPTS.get(key)
    if not prompt_key:
        send_main_menu(client=client, chat_id=chat_id, user=user)
        return
    route_to_assistant(client=client, chat_id=chat_id, user=user, text=hr_text(prompt_key, user=user))

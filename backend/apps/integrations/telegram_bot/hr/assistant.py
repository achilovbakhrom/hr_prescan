"""HR Telegram assistant routing."""

from __future__ import annotations


def route_to_assistant(*, client, chat_id, user, text: str) -> None:
    """Hand a free-text message to the LangChain HR assistant."""
    from apps.common.ai_assistant import process_ai_command
    from apps.integrations.telegram_bot.hr.history import (
        get_hr_context,
        save_hr_history,
    )

    context = get_hr_context(telegram_id=user.telegram_id, text=text)
    result = process_ai_command(user=user, message=text, context=context)
    response_text = result.get("message", "Something went wrong.")

    save_hr_history(
        telegram_id=user.telegram_id,
        user_msg=text,
        bot_msg=response_text,
    )
    from apps.integrations.telegram_bot.bots import ROLE_HR
    from apps.integrations.telegram_bot.hr.menus import ai_mode_keyboard, main_menu_keyboard
    from apps.integrations.telegram_bot.sessions import get_session

    in_ai_mode = get_session(role=ROLE_HR, telegram_id=user.telegram_id).get("ai_mode")
    keyboard = ai_mode_keyboard(user=user) if in_ai_mode else main_menu_keyboard(user=user)
    client.send_message(
        chat_id=chat_id,
        text=response_text,
        parse_mode="Markdown",
        reply_markup=keyboard,
    )

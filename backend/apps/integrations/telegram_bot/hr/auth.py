"""HR bot account linking via deep-link tokens.

A logged-in HR user generates a token from the web settings page; the bot
deep-link ``t.me/<bot>?start=<token>`` carries the token to the bot, which
matches it against an unused ``TelegramLinkCode`` and links the accounts.
"""

from __future__ import annotations

from apps.integrations.telegram_bot.client import TelegramClient
from apps.integrations.telegram_bot.hr.i18n import text as hr_text
from apps.integrations.telegram_bot.hr.linking import (
    get_hr_bot_user,
    looks_like_code,
    looks_like_email,
    send_email_link_code,
    verify_email_link_code,
)
from apps.integrations.telegram_bot.i18n import normalize_language
from apps.integrations.telegram_bot.sessions import get_session


def handle_start(
    *,
    client: TelegramClient,
    chat_id: int,
    telegram_id: int,
    telegram_username: str = "",
    first_name: str = "",
    last_name: str = "",
    language_code: str = "",
    payload: str = "",
) -> None:
    """Handle ``/start`` for the HR bot, optionally auto-linking via deep-link payload."""
    if payload:
        from apps.integrations.telegram_bot.hr.deep_link import request_deep_link_confirmation

        request_deep_link_confirmation(client=client, chat_id=chat_id, telegram_id=telegram_id, token=payload)
        return

    user = get_hr_bot_user(telegram_id=telegram_id)
    if user:
        from apps.integrations.telegram_bot.hr.onboarding_flow import ensure_onboarding_ready

        if not ensure_onboarding_ready(client=client, chat_id=chat_id, user=user, text=""):
            return
        client.send_message(
            chat_id=chat_id,
            text=hr_text("welcome_back", user=user, name=user.first_name),
        )
        return

    from apps.integrations.telegram_bot.hr.onboarding import get_or_create_hr_bot_user
    from apps.integrations.telegram_bot.hr.onboarding_flow import send_language_picker

    language = normalize_language(lang_code=language_code)
    user = get_or_create_hr_bot_user(
        telegram_id=telegram_id,
        telegram_username=telegram_username,
        first_name=first_name,
        last_name=last_name,
        language=language,
    )
    client.send_message(
        chat_id=chat_id,
        text=(
            "Welcome to PreScreen AI!\n\n"
            f"I created a Telegram workspace for you as {user.first_name}.\n\n"
            "Choose your language to continue.\n\n"
            "Later, sign in on the web with Google and use Settings -> Telegram to connect this bot. "
            "I'll ask you to confirm here before merging the accounts."
        ),
        parse_mode="Markdown",
    )
    send_language_picker(client=client, chat_id=chat_id)


def try_link_code(
    *,
    client: TelegramClient,
    chat_id: int,
    telegram_id: int,
    telegram_username: str,
    text: str,
    language_code: str = "",
) -> bool:
    """Handle existing-account email verification.

    Returns True when the message was consumed by auth. A False return means
    the caller can create a Telegram-first workspace and route the text to AI.
    """
    language = normalize_language(lang_code=language_code)
    if looks_like_email(text=text):
        success, result = send_email_link_code(telegram_id=telegram_id, email=text)
        if success:
            client.send_message(
                chat_id=chat_id,
                text=hr_text("email_code_sent", lang=language, email=result),
            )
        else:
            client.send_message(
                chat_id=chat_id,
                text=result + hr_text("email_link_failed_suffix", lang=language),
                parse_mode="Markdown",
            )
        return True

    session = get_session(role="hr", telegram_id=telegram_id)
    if session.get("state") == "awaiting_email_code" and looks_like_code(text=text):
        user, error = verify_email_link_code(
            telegram_id=telegram_id,
            telegram_username=telegram_username,
            code=text,
        )
        if user is not None:
            company_name = user.company.name if user.company else ""
            client.send_message(
                chat_id=chat_id,
                text=hr_text(
                    "connected",
                    user=user,
                    email=user.email,
                    company=f" ({company_name})" if company_name else "",
                ),
            )
            return True
        client.send_message(chat_id=chat_id, text=error)
        return True

    return False

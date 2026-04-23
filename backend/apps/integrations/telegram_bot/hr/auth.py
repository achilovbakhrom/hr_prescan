"""HR bot account linking via deep-link tokens.

A logged-in HR user generates a token from the web settings page; the bot
deep-link ``t.me/<bot>?start=<token>`` carries the token to the bot, which
matches it against an unused ``TelegramLinkCode`` and links the accounts.
"""

from __future__ import annotations

from apps.integrations.telegram_bot.client import TelegramClient
from apps.integrations.telegram_bot.hr.linking import (
    get_hr_bot_user,
    looks_like_code,
    looks_like_email,
    send_email_link_code,
    verify_email_link_code,
)
from apps.integrations.telegram_bot.sessions import get_session


def handle_start(
    *,
    client: TelegramClient,
    chat_id: int,
    telegram_id: int,
    telegram_username: str = "",
    first_name: str = "",
    last_name: str = "",
    payload: str = "",
) -> None:
    """Handle ``/start`` for the HR bot, optionally auto-linking via deep-link payload."""
    user = get_hr_bot_user(telegram_id=telegram_id)
    if user:
        client.send_message(
            chat_id=chat_id,
            text=(f"Welcome back, {user.first_name}!\n\nType your request or /help to see what I can do."),
        )
        return

    if payload:
        _try_deep_link(
            client=client,
            chat_id=chat_id,
            telegram_id=telegram_id,
            telegram_username=telegram_username,
            token=payload,
        )
        return

    client.send_message(
        chat_id=chat_id,
        text=(
            "Welcome to PreScreen AI!\n\n"
            "If you already have an HR or admin account, send me your work email and I'll send a 6-digit code.\n\n"
            "If you're new, create your company at "
            f"{_public_site_url()} and come back here."
        ),
    )


def try_link_code(
    *,
    client: TelegramClient,
    chat_id: int,
    telegram_id: int,
    telegram_username: str,
    text: str,
) -> None:
    """Handle messages from unlinked HR users via work-email verification."""
    if looks_like_email(text=text):
        success, result = send_email_link_code(telegram_id=telegram_id, email=text)
        if success:
            client.send_message(
                chat_id=chat_id,
                text=(
                    f"I sent a 6-digit code to {result}.\n\n"
                    "Reply here with that code to connect your Telegram account."
                ),
            )
        else:
            client.send_message(
                chat_id=chat_id,
                text=result + f"\n\nIf you don't have an account yet, start at {_public_site_url()}.",
            )
        return

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
                text=(
                    f"Connected as {user.email}"
                    + (f" ({company_name})" if company_name else "")
                    + "\n\nYou can now manage your HR tasks here. Type /help to see what I can do."
                ),
            )
            return
        client.send_message(chat_id=chat_id, text=error)
        return

    client.send_message(
        chat_id=chat_id,
        text=(
            "Your Telegram account is not linked yet.\n\n"
            "Send your HR/admin work email and I'll email you a 6-digit verification code.\n\n"
            "You can still use the web Settings -> Telegram deep link if you prefer."
        ),
    )


def _try_deep_link(
    *,
    client: TelegramClient,
    chat_id: int,
    telegram_id: int,
    telegram_username: str,
    token: str,
) -> None:
    """Auto-link an HR account using a deep-link token from the /start payload."""
    from django.db import IntegrityError, transaction
    from django.utils import timezone

    from apps.integrations.models import TelegramLinkCode

    try:
        with transaction.atomic():
            link = (
                TelegramLinkCode.objects.filter(
                    code=token,
                    is_used=False,
                    expires_at__gt=timezone.now(),
                )
                .select_related("user")
                .select_for_update()
                .first()
            )

            if link is None:
                client.send_message(
                    chat_id=chat_id,
                    text=(
                        "This link has expired or is invalid.\n\nPlease generate a new one from Settings -> Telegram."
                    ),
                )
                return

            if not isinstance(telegram_id, int) or telegram_id <= 0:
                client.send_message(chat_id=chat_id, text="Invalid Telegram account.")
                return

            user = link.user
            user.telegram_id = telegram_id
            user.telegram_username = telegram_username
            user.save(update_fields=["telegram_id", "telegram_username", "updated_at"])

            link.is_used = True
            link.save(update_fields=["is_used", "updated_at"])
    except IntegrityError:
        client.send_message(
            chat_id=chat_id,
            text="This Telegram account is already linked to another user. Please unlink it first.",
        )
        return

    company_name = user.company.name if user.company else ""
    client.send_message(
        chat_id=chat_id,
        text=(
            f"Connected as {user.email}"
            + (f" ({company_name})" if company_name else "")
            + "\n\nYou can now manage your HR tasks here. Type /help to see what I can do."
        ),
    )


def _public_site_url() -> str:
    from django.conf import settings

    return settings.FRONTEND_URL.rstrip("/")

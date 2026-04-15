"""HR bot account linking via deep-link tokens.

A logged-in HR user generates a token from the web settings page; the bot
deep-link ``t.me/<bot>?start=<token>`` carries the token to the bot, which
matches it against an unused ``TelegramLinkCode`` and links the accounts.
"""
from __future__ import annotations

from apps.integrations.telegram_bot.client import TelegramClient


def handle_start(
    *,
    client: TelegramClient,
    chat_id: int,
    telegram_id: int,
    telegram_username: str = "",
    first_name: str = "",  # noqa: ARG001 — kept for symmetry with candidate bot
    last_name: str = "",  # noqa: ARG001 — kept for symmetry with candidate bot
    payload: str = "",
) -> None:
    """Handle ``/start`` for the HR bot, optionally auto-linking via deep-link payload."""
    from apps.accounts.models import User

    user = User.objects.filter(telegram_id=telegram_id, role=User.Role.HR).first()
    if user:
        client.send_message(
            chat_id=chat_id,
            text=(
                f"Welcome back, {user.first_name}!\n\n"
                "Type your request or /help to see what I can do."
            ),
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
            "To connect your account, go to Settings -> Telegram in the web app "
            "and click the Connect button.\n\n"
            "Don't have an account? Visit https://prescreenai.com to get started."
        ),
    )


def try_link_code(
    *,
    client: TelegramClient,
    chat_id: int,
    telegram_id: int,  # noqa: ARG001 — reserved for future use
    telegram_username: str,  # noqa: ARG001 — reserved for future use
    text: str,  # noqa: ARG001 — reserved for future use
) -> None:
    """Handle messages from unlinked HR users (no auto-linking by free text)."""
    client.send_message(
        chat_id=chat_id,
        text=(
            "Your Telegram account is not linked yet.\n\n"
            "To connect, go to Settings -> Telegram in the web app "
            "and click the Connect button."
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
                    code=token, is_used=False, expires_at__gt=timezone.now(),
                )
                .select_related("user")
                .select_for_update()
                .first()
            )

            if link is None:
                client.send_message(
                    chat_id=chat_id,
                    text=(
                        "This link has expired or is invalid.\n\n"
                        "Please generate a new one from Settings -> Telegram."
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

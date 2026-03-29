from apps.integrations.telegram_bot.handlers import send_message


def handle_start(*, chat_id, telegram_id, telegram_username="", first_name="", last_name="", payload=""):
    """Handle the /start command, optionally auto-linking via deep-link payload."""
    from apps.accounts.models import User

    user = User.objects.filter(telegram_id=telegram_id).first()
    if user:
        send_message(
            chat_id=chat_id,
            text=(
                f"Welcome back, {user.first_name}!\n\n"
                "Type your request or /help to see what I can do."
            ),
        )
        return

    # If a deep-link payload is present, try to auto-link (HR account)
    if payload:
        _try_deep_link(
            chat_id=chat_id,
            telegram_id=telegram_id,
            telegram_username=telegram_username,
            token=payload,
        )
        return

    send_message(
        chat_id=chat_id,
        text=(
            "Welcome to PreScreen AI!\n\n"
            "To connect your account, go to Settings -> Telegram in the web app "
            "and click the Connect button.\n\n"
            "Don't have an account? Visit https://prescreenai.com to get started."
        ),
    )


def try_link_code(*, chat_id, telegram_id, telegram_username, text):
    """Handle messages from unlinked users."""
    send_message(
        chat_id=chat_id,
        text=(
            "Your Telegram account is not linked yet.\n\n"
            "To connect, go to Settings -> Telegram in the web app "
            "and click the Connect button."
        ),
    )


def _try_deep_link(*, chat_id, telegram_id, telegram_username, token):
    """Auto-link account using a deep-link token from /start payload."""
    from django.db import IntegrityError, transaction
    from django.utils import timezone

    from apps.integrations.models import TelegramLinkCode

    try:
        with transaction.atomic():
            link = (
                TelegramLinkCode.objects.filter(
                    code=token, is_used=False, expires_at__gt=timezone.now()
                )
                .select_related("user")
                .select_for_update()
                .first()
            )

            if link is None:
                send_message(
                    chat_id=chat_id,
                    text=(
                        "This link has expired or is invalid.\n\n"
                        "Please generate a new one from Settings -> Telegram."
                    ),
                )
                return

            if not isinstance(telegram_id, int) or telegram_id <= 0:
                send_message(chat_id=chat_id, text="Invalid Telegram account.")
                return

            user = link.user
            user.telegram_id = telegram_id
            user.telegram_username = telegram_username
            user.save(update_fields=["telegram_id", "telegram_username", "updated_at"])

            link.is_used = True
            link.save(update_fields=["is_used", "updated_at"])
    except IntegrityError:
        send_message(
            chat_id=chat_id,
            text="This Telegram account is already linked to another user. Please unlink it first.",
        )
        return

    company_name = user.company.name if user.company else ""
    send_message(
        chat_id=chat_id,
        text=(
            f"Connected as {user.email}"
            + (f" ({company_name})" if company_name else "")
            + "\n\nYou can now manage your HR tasks here. Type /help to see what I can do."
        ),
    )

"""Candidate bot — user auth helpers.

Covers two cases:
  1. Auto-signup on first message (get_or_create_candidate_user) — Telegram-only
     account with placeholder email, no password set yet.
  2. Registration completion (complete_registration) — sets real name, phone and
     a generated password; returns the password so the bot can DM it.
"""

from __future__ import annotations

import logging
import secrets
import string

from django.db import IntegrityError, transaction

from apps.accounts.models import User

logger = logging.getLogger(__name__)

PLACEHOLDER_EMAIL_DOMAIN = "telegram.local"
_PASSWORD_CHARS = string.ascii_letters + string.digits
_PASSWORD_LENGTH = 10


def generate_password() -> str:
    return "".join(secrets.choice(_PASSWORD_CHARS) for _ in range(_PASSWORD_LENGTH))


def get_or_create_candidate_user(
    *,
    telegram_id: int,
    telegram_username: str = "",
    first_name: str = "",
    last_name: str = "",
    language: str = User.Language.EN,
) -> User:
    """Return the candidate User for this Telegram identity, creating it if needed.

    Idempotent and concurrency-safe. New users have a placeholder email and no
    phone — registration is completed separately via complete_registration().
    """
    if not isinstance(telegram_id, int) or telegram_id <= 0:
        raise ValueError(f"Invalid telegram_id: {telegram_id!r}")

    user = User.objects.filter(telegram_id=telegram_id).first()
    if user is not None:
        if telegram_username and user.telegram_username != telegram_username:
            user.telegram_username = telegram_username
            user.save(update_fields=["telegram_username", "updated_at"])
        return user

    placeholder_email = f"tg_{telegram_id}@{PLACEHOLDER_EMAIL_DOMAIN}"
    try:
        with transaction.atomic():
            user = User.objects.create_user(
                email=placeholder_email,
                password=None,
                first_name=first_name or "Telegram",
                last_name=last_name or "User",
                role=User.Role.CANDIDATE,
                email_verified=False,
            )
            user.telegram_id = telegram_id
            user.telegram_username = telegram_username
            if language in User.Language.values:
                user.language = language
            user.onboarding_completed = False
            user.save(
                update_fields=[
                    "telegram_id",
                    "telegram_username",
                    "language",
                    "onboarding_completed",
                    "updated_at",
                ]
            )
    except IntegrityError:
        existing = User.objects.filter(telegram_id=telegram_id).first()
        if existing is not None:
            return existing
        raise

    logger.info("Created candidate user via Telegram bot: tg_id=%s", telegram_id)

    try:
        from apps.applications.services import bind_existing_applications

        bind_existing_applications(user=user)
    except Exception as exc:
        logger.warning("bind_existing_applications failed for tg_id=%s: %s", telegram_id, exc)

    return user


def complete_registration(
    *,
    user: User,
    full_name: str,
    phone: str,
) -> str:
    """Set real name, phone and a generated password. Returns the plain password."""
    parts = full_name.strip().split(None, 1)
    first_name = parts[0]
    last_name = parts[1] if len(parts) > 1 else ""

    password = generate_password()
    user.first_name = first_name
    user.last_name = last_name
    user.phone = phone
    user.set_password(password)
    user.save(update_fields=["first_name", "last_name", "phone", "password", "updated_at"])

    logger.info("Registration completed for tg_id=%s", user.telegram_id)
    return password

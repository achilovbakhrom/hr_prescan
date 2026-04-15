"""Candidate bot — auto-signup on first /start.

Telegram never gives us an email address, so we mint a placeholder
``tg_<id>@telegram.local`` (matching the existing TelegramAuthApi convention)
and create a candidate ``User`` row. The same telegram_id reaching the bot
again returns the existing user, so the flow is idempotent.

This module is intentionally narrow: only signup. The /start payload (deep
link to a vacancy) is handled separately in ``apply.py``.
"""
from __future__ import annotations

import logging

from django.db import IntegrityError, transaction

from apps.accounts.models import User

logger = logging.getLogger(__name__)

PLACEHOLDER_EMAIL_DOMAIN = "telegram.local"


def get_or_create_candidate_user(
    *,
    telegram_id: int,
    telegram_username: str = "",
    first_name: str = "",
    last_name: str = "",
) -> User:
    """Return the candidate User for this Telegram identity, creating it if needed.

    Idempotent and concurrency-safe: if two webhook updates race to create the
    same user, the second one catches the IntegrityError and re-fetches.
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
            user.onboarding_completed = False
            user.save(update_fields=[
                "telegram_id",
                "telegram_username",
                "onboarding_completed",
                "updated_at",
            ])
    except IntegrityError:
        # Concurrent create from another webhook update for the same identity.
        existing = User.objects.filter(telegram_id=telegram_id).first()
        if existing is not None:
            return existing
        raise

    logger.info("Created candidate user via Telegram bot: tg_id=%s", telegram_id)

    # Bind any anonymous applications that already match this identity.
    try:
        from apps.applications.services import bind_existing_applications
        bind_existing_applications(user=user)
    except Exception as exc:  # noqa: BLE001 — non-fatal
        logger.warning("bind_existing_applications failed for tg_id=%s: %s", telegram_id, exc)

    return user

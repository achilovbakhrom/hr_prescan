"""HR bot account lookup and email-code linking helpers."""

from __future__ import annotations

import logging
import re
import secrets

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.db import IntegrityError, transaction

from apps.accounts.models import User
from apps.integrations.telegram_bot.bots import ROLE_HR
from apps.integrations.telegram_bot.hr.onboarding import is_hr_placeholder, merge_hr_placeholder
from apps.integrations.telegram_bot.sessions import update_session

logger = logging.getLogger(__name__)

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
CODE_RE = re.compile(r"^\d{6}$")
EMAIL_LINK_CACHE_KEY = "tg_hr_email_link:{telegram_id}"
EMAIL_LINK_TTL_SECONDS = 60 * 10
ALLOWED_ROLES = (User.Role.ADMIN, User.Role.HR)


def get_hr_bot_user(*, telegram_id: int):
    return (
        User.objects.filter(
            telegram_id=telegram_id,
            role__in=ALLOWED_ROLES,
            is_active=True,
        )
        .select_related("company")
        .first()
    )


def looks_like_email(*, text: str) -> bool:
    return bool(EMAIL_RE.match(text.strip()))


def looks_like_code(*, text: str) -> bool:
    return bool(CODE_RE.match(text.strip()))


def send_email_link_code(*, telegram_id: int, email: str) -> tuple[bool, str]:
    user = (
        User.objects.filter(
            email__iexact=email.strip(),
            role__in=ALLOWED_ROLES,
            is_active=True,
        )
        .select_related("company")
        .first()
    )
    if user is None:
        return False, "No active HR or admin account was found for that email."

    code = f"{secrets.randbelow(1_000_000):06d}"
    cache.set(
        EMAIL_LINK_CACHE_KEY.format(telegram_id=telegram_id),
        {"user_id": str(user.id), "code": code},
        timeout=EMAIL_LINK_TTL_SECONDS,
    )
    update_session(role=ROLE_HR, telegram_id=telegram_id, state="awaiting_email_code")

    subject = "Your PreScreen AI Telegram verification code"
    body = (
        "Use this code in the PreScreen AI HR Telegram bot to connect your account:\n\n"
        f"{code}\n\n"
        "The code expires in 10 minutes."
    )
    try:
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
    except Exception:
        logger.exception("Failed to send HR Telegram auth code to %s", user.email)
        return False, "I couldn't send the verification code right now. Please try again in a moment."

    return True, user.email


def verify_email_link_code(
    *,
    telegram_id: int,
    telegram_username: str,
    code: str,
):
    payload = cache.get(EMAIL_LINK_CACHE_KEY.format(telegram_id=telegram_id))
    if not payload or payload.get("code") != code.strip():
        return None, "That verification code is invalid or expired."

    try:
        with transaction.atomic():
            user = (
                User.objects.select_for_update()
                .filter(
                    id=payload.get("user_id"),
                    role__in=ALLOWED_ROLES,
                    is_active=True,
                )
                .select_related("company")
                .first()
            )
            if user is None:
                cache.delete(EMAIL_LINK_CACHE_KEY.format(telegram_id=telegram_id))
                return None, "That account is no longer available."

            existing = (
                User.objects.select_for_update()
                .filter(telegram_id=telegram_id, role__in=ALLOWED_ROLES)
                .exclude(id=user.id)
                .first()
            )
            if existing is not None:
                if not is_hr_placeholder(user=existing, telegram_id=telegram_id):
                    return None, "This Telegram account is already linked to another user."
                merge_hr_placeholder(source=existing, target=user)

            user.telegram_id = telegram_id
            user.telegram_username = telegram_username
            user.save(update_fields=["telegram_id", "telegram_username", "updated_at"])
    except IntegrityError:
        return None, "This Telegram account is already linked to another user."

    cache.delete(EMAIL_LINK_CACHE_KEY.format(telegram_id=telegram_id))
    update_session(role=ROLE_HR, telegram_id=telegram_id, state="")
    return user, ""

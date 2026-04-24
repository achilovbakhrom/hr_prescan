"""Candidate Telegram language helpers."""

from __future__ import annotations

from apps.accounts.models import User
from apps.integrations.telegram_bot.i18n import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES, normalize_language


def initial_language(*, lang_code: str | None) -> str:
    return normalize_language(lang_code=lang_code)


def telegram_language(*, telegram_id: int, lang_code: str | None) -> str:
    return stored_language_for_telegram(telegram_id=telegram_id, fallback=initial_language(lang_code=lang_code))


def stored_language_for_telegram(*, telegram_id: int, fallback: str = DEFAULT_LANGUAGE) -> str:
    user = User.objects.filter(telegram_id=telegram_id).only("language").first()
    if user is None:
        return fallback if fallback in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
    return user_language(user=user, fallback=fallback)


def user_language(*, user: User, fallback: str = DEFAULT_LANGUAGE) -> str:
    lang = user.language or fallback
    return lang if lang in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE

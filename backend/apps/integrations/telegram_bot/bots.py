"""Bot registry — maps a ``role`` (hr / candidate) to its config + client.

Centralising this lets the webhook view, polling command, and handlers all
look up "the HR client" or "the candidate client" without each one having to
know the env var names.
"""
from __future__ import annotations

from dataclasses import dataclass

from django.conf import settings

from apps.integrations.telegram_bot.client import TelegramClient

ROLE_HR = "hr"
ROLE_CANDIDATE = "candidate"
VALID_ROLES = (ROLE_HR, ROLE_CANDIDATE)


@dataclass(frozen=True)
class BotConfig:
    role: str
    token: str
    username: str
    webhook_secret: str
    webhook_url: str


def get_bot_config(*, role: str) -> BotConfig:
    if role == ROLE_HR:
        return BotConfig(
            role=ROLE_HR,
            token=settings.TELEGRAM_HR_BOT_TOKEN,
            username=settings.TELEGRAM_HR_BOT_USERNAME,
            webhook_secret=settings.TELEGRAM_HR_WEBHOOK_SECRET,
            webhook_url=settings.TELEGRAM_HR_WEBHOOK_URL,
        )
    if role == ROLE_CANDIDATE:
        return BotConfig(
            role=ROLE_CANDIDATE,
            token=settings.TELEGRAM_CANDIDATE_BOT_TOKEN,
            username=settings.TELEGRAM_CANDIDATE_BOT_USERNAME,
            webhook_secret=settings.TELEGRAM_CANDIDATE_WEBHOOK_SECRET,
            webhook_url=settings.TELEGRAM_CANDIDATE_WEBHOOK_URL,
        )
    raise ValueError(f"Unknown bot role: {role!r} (expected one of {VALID_ROLES})")


def get_client(*, role: str) -> TelegramClient:
    config = get_bot_config(role=role)
    return TelegramClient(token=config.token)


def dispatch_update(*, role: str, update_data: dict) -> None:
    """Send a Telegram update payload to the right bot's handler."""
    if role == ROLE_HR:
        from apps.integrations.telegram_bot.hr.handlers import handle_update as hr_handle
        hr_handle(update_data)
        return
    if role == ROLE_CANDIDATE:
        from apps.integrations.telegram_bot.candidate.handlers import handle_update as cand_handle
        cand_handle(update_data)
        return
    raise ValueError(f"Unknown bot role: {role!r}")

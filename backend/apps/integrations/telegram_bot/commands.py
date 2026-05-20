"""Telegram slash-command menus shown by Telegram clients."""

from __future__ import annotations

from apps.integrations.telegram_bot.bots import ROLE_CANDIDATE, ROLE_HR

HR_COMMANDS = [
    {"command": "start", "description": "Start or link your HR workspace"},
    {"command": "menu", "description": "Show HR action buttons"},
    {"command": "help", "description": "Show what the HR bot can do"},
    {"command": "language", "description": "Change bot language"},
]

CANDIDATE_COMMANDS = [
    {"command": "start", "description": "Start or resume candidate flow"},
    {"command": "menu", "description": "Show candidate action buttons"},
    {"command": "help", "description": "Show candidate menu"},
    {"command": "language", "description": "Change bot language"},
    {"command": "jobs", "description": "Search available jobs"},
    {"command": "create_cv", "description": "Create a CV with AI"},
    {"command": "cv", "description": "Open CV center"},
    {"command": "register", "description": "Complete candidate registration"},
]


def commands_for_role(*, role: str) -> list[dict[str, str]]:
    if role == ROLE_HR:
        return HR_COMMANDS
    if role == ROLE_CANDIDATE:
        return CANDIDATE_COMMANDS
    raise ValueError(f"Unknown bot role: {role!r}")

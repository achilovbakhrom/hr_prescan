from __future__ import annotations

from django.core.management import call_command

from apps.integrations.telegram_bot.bots import ROLE_CANDIDATE, ROLE_HR
from apps.integrations.telegram_bot.commands import CANDIDATE_COMMANDS, HR_COMMANDS, commands_for_role


class FakeTelegramClient:
    def __init__(self):
        self.calls = []

    def set_my_commands(self, *, commands):
        self.calls.append(("set_my_commands", commands))
        return {"ok": True, "description": "commands set"}

    def set_webhook(self, *, url: str, secret_token: str = ""):
        self.calls.append(("set_webhook", {"url": url, "secret_token": secret_token}))
        return {"ok": True, "description": "webhook set"}


def test_commands_for_role_returns_hr_menu():
    commands = commands_for_role(role=ROLE_HR)

    assert commands == HR_COMMANDS
    assert {item["command"] for item in commands} >= {"start", "menu", "help", "language"}


def test_commands_for_role_returns_candidate_menu():
    commands = commands_for_role(role=ROLE_CANDIDATE)

    assert commands == CANDIDATE_COMMANDS
    assert {item["command"] for item in commands} >= {"start", "menu", "help", "jobs", "create_cv", "cv"}


def test_setup_webhook_registers_commands_before_webhook(settings, monkeypatch):
    settings.TELEGRAM_HR_BOT_TOKEN = "test-token"
    settings.TELEGRAM_HR_WEBHOOK_SECRET = "secret"
    client = FakeTelegramClient()
    monkeypatch.setattr("apps.integrations.management.commands.setup_telegram_webhook.get_client", lambda role: client)

    call_command("setup_telegram_webhook", "https://example.com/api/telegram/hr/webhook/", "--role", ROLE_HR)

    assert client.calls == [
        ("set_my_commands", HR_COMMANDS),
        (
            "set_webhook",
            {
                "url": "https://example.com/api/telegram/hr/webhook/",
                "secret_token": "secret",
            },
        ),
    ]

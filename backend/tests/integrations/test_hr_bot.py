"""Integration tests for HR Telegram account linking."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from apps.accounts.models import Company, CompanyMembership, User
from apps.integrations.models import TelegramLinkCode
from apps.integrations.telegram_bot.bots import ROLE_HR
from apps.integrations.telegram_bot.hr.handlers import handle_update
from apps.integrations.telegram_bot.hr.onboarding import get_or_create_hr_bot_user
from apps.integrations.telegram_bot.sessions import clear_session
from apps.vacancies.models import Vacancy

TG_USER = {
    "id": 438237137,
    "first_name": "Telegram",
    "last_name": "HR",
    "username": "telegram_hr",
    "language_code": "en",
}


@pytest.fixture(autouse=True)
def _bot_config(settings):
    settings.TELEGRAM_BOT_TOKEN = "test-hr-token"
    settings.TELEGRAM_HR_BOT_USERNAME = "TestHRBot"
    settings.TELEGRAM_HR_WEBHOOK_SECRET = ""


@pytest.fixture(autouse=True)
def _clean_session():
    yield
    clear_session(role=ROLE_HR, telegram_id=TG_USER["id"])


def _make_message_update(text: str) -> dict:
    return {
        "update_id": 1,
        "message": {
            "message_id": 1,
            "from": TG_USER,
            "chat": {"id": TG_USER["id"], "type": "private"},
            "text": text,
        },
    }


def _make_callback_update(data: str) -> dict:
    return {
        "update_id": 2,
        "callback_query": {
            "id": "cb1",
            "from": TG_USER,
            "data": data,
            "message": {
                "message_id": 99,
                "chat": {"id": TG_USER["id"], "type": "private"},
            },
        },
    }


@pytest.fixture()
def web_admin_with_company():
    user = User.objects.create_user(
        email="web-admin@example.com",
        password="testpass123",
        first_name="Web",
        last_name="Admin",
        role=User.Role.ADMIN,
        email_verified=True,
    )
    company = Company.objects.create(
        account_owner=user,
        name="Web Company",
        size=Company.Size.SMALL,
        country="Uzbekistan",
    )
    CompanyMembership.objects.create(
        user=user,
        company=company,
        role=User.Role.ADMIN,
        is_default=True,
    )
    user.company = company
    user.save(update_fields=["company", "updated_at"])
    return user, company


def _create_telegram_workspace(language: str = User.Language.RU) -> tuple[User, Company, Vacancy]:
    placeholder = get_or_create_hr_bot_user(
        telegram_id=TG_USER["id"],
        telegram_username=TG_USER["username"],
        first_name=TG_USER["first_name"],
        last_name=TG_USER["last_name"],
        language=language,
    )
    company = Company.objects.create(
        account_owner=placeholder,
        name="Telegram Company",
        size=Company.Size.SMALL,
        country="Uzbekistan",
    )
    CompanyMembership.objects.create(
        user=placeholder,
        company=company,
        role=User.Role.ADMIN,
        is_default=True,
    )
    placeholder.company = company
    placeholder.save(update_fields=["company", "updated_at"])
    vacancy = Vacancy.objects.create(
        company=company,
        created_by=placeholder,
        title="Telegram Vacancy",
        description="Created from Telegram",
        status=Vacancy.Status.PUBLISHED,
    )
    return placeholder, company, vacancy


class TestHRDeepLinking:
    def test_start_link_payload_asks_confirmation_even_when_placeholder_exists(self, web_admin_with_company):
        web_admin, _web_company = web_admin_with_company
        _create_telegram_workspace()
        link = TelegramLinkCode.generate(user=web_admin)

        with (
            patch("apps.integrations.telegram_bot.client.requests.post") as post_mock,
            patch("apps.integrations.telegram_bot.client.requests.get"),
        ):
            post_mock.return_value.json.return_value = {"ok": True, "result": {}}
            handle_update(_make_message_update(f"/start {link.code}"))

        web_admin.refresh_from_db()
        link.refresh_from_db()
        assert web_admin.telegram_id is None
        assert link.is_used is False
        sent_text = "".join(str(call.kwargs.get("json", {}).get("text", "")) for call in post_mock.call_args_list)
        assert "Подключить этот Telegram-аккаунт" in sent_text
        assert "Welcome back" not in sent_text

    def test_link_confirmation_merges_hr_placeholder_workspace(self, web_admin_with_company):
        web_admin, web_company = web_admin_with_company
        placeholder, telegram_company, vacancy = _create_telegram_workspace()
        link = TelegramLinkCode.generate(user=web_admin)

        with (
            patch("apps.integrations.telegram_bot.client.requests.post") as post_mock,
            patch("apps.integrations.telegram_bot.client.requests.get"),
        ):
            post_mock.return_value.json.return_value = {"ok": True, "result": {}}
            handle_update(_make_callback_update(f"hr:link:ok:{link.code}"))

        placeholder.refresh_from_db()
        web_admin.refresh_from_db()
        telegram_company.refresh_from_db()
        vacancy.refresh_from_db()
        link.refresh_from_db()

        assert placeholder.is_active is False
        assert placeholder.telegram_id is None
        assert web_admin.telegram_id == TG_USER["id"]
        assert web_admin.telegram_username == TG_USER["username"]
        assert web_admin.language == User.Language.RU
        assert link.is_used is True
        assert vacancy.created_by == web_admin
        assert telegram_company.account_owner == web_admin
        assert CompanyMembership.objects.filter(user=web_admin, company=telegram_company).exists()
        assert CompanyMembership.objects.get(user=web_admin, company=web_company).is_default is True
        assert CompanyMembership.objects.get(user=web_admin, company=telegram_company).is_default is False
        assert web_admin.company == web_company

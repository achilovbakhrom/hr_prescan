"""Integration tests for the candidate Telegram bot — PR1 deep-link apply flow."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from apps.accounts.models import User
from apps.applications.models import Application
from apps.integrations.telegram_bot.bots import ROLE_CANDIDATE
from apps.integrations.telegram_bot.candidate.auth import get_or_create_candidate_user
from apps.integrations.telegram_bot.candidate.handlers import handle_update
from apps.integrations.telegram_bot.sessions import clear_session, get_session
from apps.interviews.models import Interview

TG_USER = {
    "id": 12345678,
    "first_name": "Alex",
    "last_name": "Tester",
    "username": "alextester",
    "language_code": "en",
}


@pytest.fixture(autouse=True)
def _bot_config(settings):
    settings.TELEGRAM_CANDIDATE_BOT_TOKEN = "test-token"
    settings.TELEGRAM_CANDIDATE_BOT_USERNAME = "TestCandidateBot"
    settings.TELEGRAM_CANDIDATE_WEBHOOK_SECRET = ""


@pytest.fixture(autouse=True)
def _clean_session():
    yield
    clear_session(role=ROLE_CANDIDATE, telegram_id=TG_USER["id"])


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


class TestGetOrCreateCandidateUser:
    def test_creates_user_with_placeholder_email(self):
        user = get_or_create_candidate_user(
            telegram_id=TG_USER["id"],
            telegram_username=TG_USER["username"],
            first_name=TG_USER["first_name"],
            last_name=TG_USER["last_name"],
        )
        assert user.id is not None
        assert user.role == User.Role.CANDIDATE
        assert user.email == f"tg_{TG_USER['id']}@telegram.local"
        assert user.email_verified is False
        assert user.telegram_id == TG_USER["id"]
        assert user.telegram_username == TG_USER["username"]

    def test_idempotent(self):
        a = get_or_create_candidate_user(telegram_id=TG_USER["id"], first_name="A")
        b = get_or_create_candidate_user(telegram_id=TG_USER["id"], first_name="A")
        assert a.id == b.id
        assert User.objects.filter(telegram_id=TG_USER["id"]).count() == 1


class TestStartCommand:
    def test_plain_start_creates_user_and_sends_welcome(self):
        with (
            patch(
                "apps.integrations.telegram_bot.client.requests.post",
            ) as post_mock,
            patch(
                "apps.integrations.telegram_bot.client.requests.get",
            ),
        ):
            post_mock.return_value.json.return_value = {"ok": True, "result": {}}
            handle_update(_make_message_update("/start"))

        assert User.objects.filter(telegram_id=TG_USER["id"]).exists()
        # The welcome message was sent via sendMessage
        assert any("sendMessage" in str(c) for c in post_mock.call_args_list)

    def test_start_with_vacancy_uuid_deep_link(self, vacancy):
        with (
            patch(
                "apps.integrations.telegram_bot.client.requests.post",
            ) as post_mock,
            patch(
                "apps.integrations.telegram_bot.client.requests.get",
            ),
        ):
            post_mock.return_value.json.return_value = {"ok": True, "result": {}}
            handle_update(_make_message_update(f"/start vac_{vacancy.id}"))

        # User created
        assert User.objects.filter(telegram_id=TG_USER["id"]).exists()
        # Vacancy card sent — payload contains the vacancy title
        sent_text = "".join(str(call.kwargs.get("json", {}).get("text", "")) for call in post_mock.call_args_list)
        assert vacancy.title in sent_text

    def test_start_with_vacancy_telegram_code_deep_link(self, vacancy):
        with (
            patch(
                "apps.integrations.telegram_bot.client.requests.post",
            ) as post_mock,
            patch(
                "apps.integrations.telegram_bot.client.requests.get",
            ),
        ):
            post_mock.return_value.json.return_value = {"ok": True, "result": {}}
            handle_update(_make_message_update(f"/start vac_{vacancy.telegram_code}"))

        sent_text = "".join(str(call.kwargs.get("json", {}).get("text", "")) for call in post_mock.call_args_list)
        assert vacancy.title in sent_text

    def test_start_with_prescan_token_resumes_same_session(self, vacancy):
        application = Application.objects.create(
            vacancy=vacancy,
            candidate_name="Anon Candidate",
            candidate_email="anon@example.com",
        )
        interview = Interview.objects.create(
            application=application,
            session_type=Interview.SessionType.PRESCANNING,
            screening_mode=Interview.ScreeningMode.CHAT,
            status=Interview.Status.PENDING,
            language="en",
        )

        with (
            patch(
                "apps.integrations.telegram_bot.client.requests.post",
            ) as post_mock,
            patch(
                "apps.integrations.telegram_bot.client.requests.get",
            ),
        ):
            post_mock.return_value.json.return_value = {"ok": True, "result": {}}
            handle_update(_make_message_update(f"/start ps_{interview.interview_token}"))

        application.refresh_from_db()
        interview.refresh_from_db()
        tg_user = User.objects.get(telegram_id=TG_USER["id"])
        assert application.candidate == tg_user
        assert interview.status == Interview.Status.IN_PROGRESS


class TestApplyFlow:
    def test_apply_callback_without_cv_when_required_prompts_for_cv(self, vacancy):
        vacancy.cv_required = True
        vacancy.save(update_fields=["cv_required"])

        with (
            patch(
                "apps.integrations.telegram_bot.client.requests.post",
            ) as post_mock,
            patch(
                "apps.integrations.telegram_bot.client.requests.get",
            ),
        ):
            post_mock.return_value.json.return_value = {"ok": True, "result": {}}
            handle_update(_make_callback_update(f"cand:vac:apply:{vacancy.id}"))

        # No application created — pending state set instead
        assert not Application.objects.filter(vacancy=vacancy).exists()
        session = get_session(role=ROLE_CANDIDATE, telegram_id=TG_USER["id"])
        assert session.get("pending_apply_vacancy_id") == str(vacancy.id)

    def test_apply_callback_without_cv_when_not_required_creates_application(self, vacancy):
        vacancy.cv_required = False
        vacancy.save(update_fields=["cv_required"])

        with (
            patch(
                "apps.integrations.telegram_bot.client.requests.post",
            ) as post_mock,
            patch(
                "apps.integrations.telegram_bot.client.requests.get",
            ),
        ):
            post_mock.return_value.json.return_value = {"ok": True, "result": {}}
            handle_update(_make_callback_update(f"cand:vac:apply:{vacancy.id}"))

        app = Application.objects.filter(vacancy=vacancy).first()
        assert app is not None
        user = User.objects.get(telegram_id=TG_USER["id"])
        assert app.candidate == user
        assert app.candidate_email == user.email

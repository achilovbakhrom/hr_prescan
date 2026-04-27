"""Integration tests for the candidate Telegram bot — PR1 deep-link apply flow."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from apps.accounts.models import CandidateCV, CandidateProfile, User
from apps.applications.models import Application
from apps.integrations.models import TelegramLinkCode
from apps.integrations.telegram_bot.bots import ROLE_CANDIDATE
from apps.integrations.telegram_bot.candidate.auth import get_or_create_candidate_user
from apps.integrations.telegram_bot.candidate.handlers import handle_update
from apps.integrations.telegram_bot.candidate.menus import (
    CB_CV_ASSISTANT,
    CB_JOB_SEARCH,
    CB_PS_CV_SELECT_PREFIX,
)
from apps.integrations.telegram_bot.candidate.states import (
    SK_NAME,
    SK_PHONE,
    SK_VACANCY_ID,
    STATE_ONBOARD_PHONE,
    STATE_PS_CODE,
    STATE_PS_CV,
)
from apps.integrations.telegram_bot.sessions import clear_session, get_session, update_session
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


def _make_contact_update(phone: str) -> dict:
    return {
        "update_id": 3,
        "message": {
            "message_id": 3,
            "from": TG_USER,
            "chat": {"id": TG_USER["id"], "type": "private"},
            "contact": {"user_id": TG_USER["id"], "phone_number": phone},
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


def _create_onboarded_candidate(language: str = User.Language.EN) -> User:
    user = get_or_create_candidate_user(
        telegram_id=TG_USER["id"],
        telegram_username=TG_USER["username"],
        first_name=TG_USER["first_name"],
        last_name=TG_USER["last_name"],
        language=language,
    )
    user.phone = "+998901234567"
    user.onboarding_completed = True
    user.save(update_fields=["phone", "onboarding_completed", "updated_at"])
    return user


class TestGetOrCreateCandidateUser:
    def test_creates_user_with_placeholder_email(self):
        user = get_or_create_candidate_user(
            telegram_id=TG_USER["id"],
            telegram_username=TG_USER["username"],
            first_name=TG_USER["first_name"],
            last_name=TG_USER["last_name"],
            language=User.Language.RU,
        )
        assert user.id is not None
        assert user.role == User.Role.CANDIDATE
        assert user.email == f"tg_{TG_USER['id']}@telegram.local"
        assert user.email_verified is False
        assert user.telegram_id == TG_USER["id"]
        assert user.telegram_username == TG_USER["username"]
        assert user.language == User.Language.RU

    def test_idempotent(self):
        a = get_or_create_candidate_user(telegram_id=TG_USER["id"], first_name="A")
        b = get_or_create_candidate_user(telegram_id=TG_USER["id"], first_name="A")
        assert a.id == b.id
        assert User.objects.filter(telegram_id=TG_USER["id"]).count() == 1


class TestStartCommand:
    def test_plain_start_creates_user_and_prompts_phone_registration(self):
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
        sent_text = "".join(str(call.kwargs.get("json", {}).get("text", "")) for call in post_mock.call_args_list)
        markups = [call.kwargs.get("json", {}).get("reply_markup", {}) for call in post_mock.call_args_list]
        assert "Let's register you first" in sent_text
        assert any("request_contact" in str(markup) for markup in markups)

    def test_start_with_vacancy_uuid_deep_link_requires_onboarding_first(self, vacancy):
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
        sent_text = "".join(str(call.kwargs.get("json", {}).get("text", "")) for call in post_mock.call_args_list)
        assert "Let's register you first" in sent_text

    def test_vacancy_deep_link_resumes_after_required_onboarding(self, vacancy):
        with (
            patch("apps.integrations.telegram_bot.client.requests.post") as post_mock,
            patch("apps.integrations.telegram_bot.client.requests.get"),
        ):
            post_mock.return_value.json.return_value = {"ok": True, "result": {}}
            handle_update(_make_message_update(f"/start vac_{vacancy.id}"))
            handle_update(_make_contact_update("+998901234567"))
            handle_update(_make_callback_update("cand:lang:en"))

        sent_text = "".join(str(call.kwargs.get("json", {}).get("text", "")) for call in post_mock.call_args_list)
        assert vacancy.title in sent_text

    def test_start_with_vacancy_telegram_code_deep_link(self, vacancy):
        _create_onboarded_candidate()
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
        user = _create_onboarded_candidate()
        application = Application.objects.create(
            vacancy=vacancy,
            candidate=user,
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
        session = get_session(role=ROLE_CANDIDATE, telegram_id=TG_USER["id"])
        assert session.get(SK_VACANCY_ID) == str(vacancy.id)

    def test_start_with_prescan_token_overrides_code_prompt_state(self, vacancy):
        user = _create_onboarded_candidate()
        application = Application.objects.create(
            vacancy=vacancy,
            candidate=user,
            candidate_name="Alex Tester",
            candidate_email=user.email,
        )
        interview = Interview.objects.create(
            application=application,
            session_type=Interview.SessionType.PRESCANNING,
            screening_mode=Interview.ScreeningMode.CHAT,
            status=Interview.Status.PENDING,
            language="en",
        )
        update_session(role=ROLE_CANDIDATE, telegram_id=TG_USER["id"], state=STATE_PS_CODE)

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

        interview.refresh_from_db()
        assert interview.status == Interview.Status.IN_PROGRESS
        session = get_session(role=ROLE_CANDIDATE, telegram_id=TG_USER["id"])
        assert session.get(SK_VACANCY_ID) == str(vacancy.id)
        sent_text = "".join(str(call.kwargs.get("json", {}).get("text", "")) for call in post_mock.call_args_list)
        assert "6-digit" not in sent_text

    def test_start_with_link_token_requires_confirmation_without_autosignup(self, candidate_user):
        link = TelegramLinkCode.generate(user=candidate_user)

        with (
            patch(
                "apps.integrations.telegram_bot.client.requests.post",
            ) as post_mock,
            patch(
                "apps.integrations.telegram_bot.client.requests.get",
            ),
        ):
            post_mock.return_value.json.return_value = {"ok": True, "result": {}}
            handle_update(_make_message_update(f"/start link_{link.code}"))

        candidate_user.refresh_from_db()
        link.refresh_from_db()
        assert candidate_user.telegram_id is None
        assert link.is_used is False
        assert not User.objects.filter(email=f"tg_{TG_USER['id']}@telegram.local").exists()
        sent_text = "".join(str(call.kwargs.get("json", {}).get("text", "")) for call in post_mock.call_args_list)
        assert "Connect this Telegram account" in sent_text

    def test_link_confirmation_links_existing_candidate_without_autosignup(self, candidate_user):
        link = TelegramLinkCode.generate(user=candidate_user)

        with (
            patch(
                "apps.integrations.telegram_bot.client.requests.post",
            ) as post_mock,
            patch(
                "apps.integrations.telegram_bot.client.requests.get",
            ),
        ):
            post_mock.return_value.json.return_value = {"ok": True, "result": {}}
            handle_update(_make_callback_update(f"cand:link:ok:{link.code}"))

        candidate_user.refresh_from_db()
        link.refresh_from_db()
        assert candidate_user.telegram_id == TG_USER["id"]
        assert candidate_user.telegram_username == TG_USER["username"]
        assert link.is_used is True
        assert not User.objects.filter(email=f"tg_{TG_USER['id']}@telegram.local").exists()

    def test_link_confirmation_merges_telegram_placeholder_candidate(self, candidate_user, vacancy):
        placeholder = get_or_create_candidate_user(
            telegram_id=TG_USER["id"],
            telegram_username=TG_USER["username"],
            first_name=TG_USER["first_name"],
            last_name=TG_USER["last_name"],
            language=User.Language.RU,
        )
        application = Application.objects.create(
            vacancy=vacancy,
            candidate=placeholder,
            candidate_name=placeholder.full_name,
            candidate_email=placeholder.email,
        )
        link = TelegramLinkCode.generate(user=candidate_user)

        with (
            patch(
                "apps.integrations.telegram_bot.client.requests.post",
            ) as post_mock,
            patch(
                "apps.integrations.telegram_bot.client.requests.get",
            ),
        ):
            post_mock.return_value.json.return_value = {"ok": True, "result": {}}
            handle_update(_make_callback_update(f"cand:link:ok:{link.code}"))

        placeholder.refresh_from_db()
        candidate_user.refresh_from_db()
        application.refresh_from_db()
        link.refresh_from_db()
        assert placeholder.is_active is False
        assert placeholder.telegram_id is None
        assert candidate_user.telegram_id == TG_USER["id"]
        assert candidate_user.language == User.Language.RU
        assert application.candidate == candidate_user
        assert link.is_used is True


class TestCandidateLanguageSettings:
    def test_menu_exposes_candidate_action_buttons(self):
        _create_onboarded_candidate()
        with (
            patch(
                "apps.integrations.telegram_bot.client.requests.post",
            ) as post_mock,
            patch(
                "apps.integrations.telegram_bot.client.requests.get",
            ),
        ):
            post_mock.return_value.json.return_value = {"ok": True, "result": {}}
            handle_update(_make_message_update("/menu"))

        markups = [call.kwargs.get("json", {}).get("reply_markup", {}) for call in post_mock.call_args_list]
        assert any("cand:lang" in str(markup) for markup in markups)
        assert any(CB_JOB_SEARCH in str(markup) for markup in markups)
        assert any("cand:ps:start" in str(markup) for markup in markups)
        assert any(CB_CV_ASSISTANT in str(markup) for markup in markups)

    def test_language_callback_updates_stored_language(self):
        _create_onboarded_candidate(language=User.Language.EN)

        with (
            patch(
                "apps.integrations.telegram_bot.client.requests.post",
            ) as post_mock,
            patch(
                "apps.integrations.telegram_bot.client.requests.get",
            ),
        ):
            post_mock.return_value.json.return_value = {"ok": True, "result": {}}
            handle_update(_make_callback_update("cand:lang:ru"))

        user = User.objects.get(telegram_id=TG_USER["id"])
        sent_text = " ".join(str(call.kwargs.get("json", {}).get("text", "")) for call in post_mock.call_args_list)
        assert user.language == User.Language.RU
        assert "Язык сохранён" in sent_text

    def test_language_callback_finishes_phone_first_onboarding(self):
        user = get_or_create_candidate_user(
            telegram_id=TG_USER["id"],
            telegram_username=TG_USER["username"],
            first_name=TG_USER["first_name"],
            last_name=TG_USER["last_name"],
            language=User.Language.EN,
        )
        user.phone = "+998901234567"
        user.onboarding_completed = False
        user.save(update_fields=["phone", "onboarding_completed", "updated_at"])

        with (
            patch("apps.integrations.telegram_bot.client.requests.post") as post_mock,
            patch("apps.integrations.telegram_bot.client.requests.get"),
        ):
            post_mock.return_value.json.return_value = {"ok": True, "result": {}}
            handle_update(_make_callback_update("cand:lang:ru"))

        user.refresh_from_db()
        sent_text = " ".join(str(call.kwargs.get("json", {}).get("text", "")) for call in post_mock.call_args_list)
        assert user.language == User.Language.RU
        assert user.onboarding_completed is True
        assert "Теперь можно пользоваться ботом" in sent_text


class TestCandidateAssistantButtons:
    def test_search_jobs_button_routes_to_candidate_assistant(self):
        _create_onboarded_candidate()
        with (
            patch("apps.integrations.telegram_bot.client.requests.post") as post_mock,
            patch("apps.integrations.telegram_bot.client.requests.get"),
            patch(
                "apps.integrations.telegram_bot.candidate.assistant.process_candidate_ai_command",
                return_value={"message": "Found jobs"},
            ) as assistant_mock,
        ):
            post_mock.return_value.json.return_value = {"ok": True, "result": {}}
            handle_update(_make_callback_update(CB_JOB_SEARCH))

        assistant_mock.assert_called_once()
        assert assistant_mock.call_args.kwargs["message"] == "Show me available jobs."

    def test_create_cv_button_routes_to_candidate_assistant(self):
        _create_onboarded_candidate()
        with (
            patch("apps.integrations.telegram_bot.client.requests.post") as post_mock,
            patch("apps.integrations.telegram_bot.client.requests.get"),
            patch(
                "apps.integrations.telegram_bot.candidate.assistant.process_candidate_ai_command",
                return_value={"message": "Let's create your CV"},
            ) as assistant_mock,
        ):
            post_mock.return_value.json.return_value = {"ok": True, "result": {}}
            handle_update(_make_callback_update(CB_CV_ASSISTANT))

        assistant_mock.assert_called_once()
        assert assistant_mock.call_args.kwargs["message"] == "Help me create my CV."


class TestPrescreeningLanguageAndCv:
    def test_vacancy_code_switches_bot_ui_to_prescreening_language(self, vacancy):
        vacancy.prescanning_language = User.Language.RU
        vacancy.save(update_fields=["prescanning_language"])
        _create_onboarded_candidate(language=User.Language.EN)
        update_session(role=ROLE_CANDIDATE, telegram_id=TG_USER["id"], state=STATE_PS_CODE)

        with (
            patch("apps.integrations.telegram_bot.client.requests.post") as post_mock,
            patch("apps.integrations.telegram_bot.client.requests.get"),
        ):
            post_mock.return_value.json.return_value = {"ok": True, "result": {}}
            handle_update(_make_message_update(str(vacancy.telegram_code)))

        user = User.objects.get(telegram_id=TG_USER["id"])
        sent_text = " ".join(str(call.kwargs.get("json", {}).get("text", "")) for call in post_mock.call_args_list)
        assert user.language == User.Language.RU
        assert "Ваше имя" in sent_text

    def test_missing_phone_asks_for_phone_instead_of_confirming_placeholder(self, vacancy):
        user = _create_onboarded_candidate(language=User.Language.RU)
        user.phone = ""
        user.save(update_fields=["phone", "updated_at"])
        update_session(
            role=ROLE_CANDIDATE,
            telegram_id=TG_USER["id"],
            state="ps_confirm_name",
            **{SK_VACANCY_ID: str(vacancy.id)},
        )

        with (
            patch("apps.integrations.telegram_bot.client.requests.post") as post_mock,
            patch("apps.integrations.telegram_bot.client.requests.get"),
        ):
            post_mock.return_value.json.return_value = {"ok": True, "result": {}}
            handle_update(_make_callback_update("cand:ps:name_confirm"))

        session = get_session(role=ROLE_CANDIDATE, telegram_id=TG_USER["id"])
        sent_text = " ".join(str(call.kwargs.get("json", {}).get("text", "")) for call in post_mock.call_args_list)
        assert session["state"] == STATE_ONBOARD_PHONE
        assert "Отправьте номер телефона" in sent_text
        assert "—" not in sent_text

    def test_can_select_existing_cv_for_prescreening_application(self, vacancy):
        user = _create_onboarded_candidate(language=User.Language.EN)
        profile, _ = CandidateProfile.objects.get_or_create(user=user)
        cv = CandidateCV.objects.create(
            profile=profile, name="Backend CV", file="cv-generated/test.pdf", is_active=True
        )
        update_session(
            role=ROLE_CANDIDATE,
            telegram_id=TG_USER["id"],
            state=STATE_PS_CV,
            **{
                SK_VACANCY_ID: str(vacancy.id),
                SK_NAME: user.full_name,
                SK_PHONE: user.phone,
            },
        )

        with (
            patch("apps.integrations.telegram_bot.client.requests.post") as post_mock,
            patch("apps.integrations.telegram_bot.client.requests.get"),
        ):
            post_mock.return_value.json.return_value = {"ok": True, "result": {}}
            handle_update(_make_callback_update(f"{CB_PS_CV_SELECT_PREFIX}{cv.id}"))

        application = Application.objects.get(vacancy=vacancy, candidate=user)
        sent_text = " ".join(str(call.kwargs.get("json", {}).get("text", "")) for call in post_mock.call_args_list)
        assert application.cv_file == cv.file
        assert "Selected CV" in sent_text


class TestApplyFlow:
    def test_apply_callback_without_cv_when_required_prompts_for_cv(self, vacancy):
        _create_onboarded_candidate()
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
        _create_onboarded_candidate()
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

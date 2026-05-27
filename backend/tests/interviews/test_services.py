from decimal import Decimal
from unittest.mock import patch

from django.test import override_settings

from apps.accounts.models import User
from apps.applications.models import Application
from apps.interviews.chat_service.evaluation_prompt import derive_ai_decision_from_evaluation
from apps.interviews.chat_service.prompts import build_system_prompt
from apps.interviews.models import Interview
from apps.interviews.services import (
    cancel_interview,
    complete_session,
    reset_interview,
    start_interview,
)
from apps.notifications.models import Message, Notification
from tests.factories import ApplicationFactory, InterviewFactory, UserFactory


class TestStartSession:
    @patch("apps.interviews.services.interview_livekit.generate_candidate_token", return_value="mock-token")
    def test_start_session_sets_in_progress(self, _mock_token, vacancy):
        """Starting a session sets status to IN_PROGRESS and records started_at."""
        app = ApplicationFactory(vacancy=vacancy, status=Application.Status.APPLIED)
        session = InterviewFactory(
            application=app,
            session_type=Interview.SessionType.PRESCANNING,
            screening_mode=Interview.ScreeningMode.CHAT,
            status=Interview.Status.PENDING,
        )

        with patch("apps.interviews.chat_service.generate_greeting", return_value="Hello!"):
            started = start_interview(interview=session)

        assert started.status == Interview.Status.IN_PROGRESS
        assert started.started_at is not None

    def test_interview_meet_prompt_falls_back_from_uzbek_to_russian(self, vacancy):
        app = ApplicationFactory(vacancy=vacancy, status=Application.Status.PRESCANNED)
        session = InterviewFactory(
            application=app,
            session_type=Interview.SessionType.INTERVIEW,
            screening_mode=Interview.ScreeningMode.MEET,
            status=Interview.Status.PENDING,
            language="uz",
        )

        prompt = build_system_prompt(session)

        assert "You MUST respond ONLY in Russian" in prompt

    def test_prescanning_prompt_allows_clarification_when_answer_is_unclear(self, vacancy):
        app = ApplicationFactory(vacancy=vacancy, status=Application.Status.APPLIED)
        session = InterviewFactory(
            application=app,
            session_type=Interview.SessionType.PRESCANNING,
            screening_mode=Interview.ScreeningMode.CHAT,
            status=Interview.Status.PENDING,
        )

        prompt = build_system_prompt(session)

        assert "cannot evaluate their answer with reasonable confidence" in prompt
        assert "one concise clarification question tied to the current prescanning topic" in prompt

    def test_interview_prompt_allows_clarification_when_answer_is_unclear(self, vacancy):
        app = ApplicationFactory(vacancy=vacancy, status=Application.Status.PRESCANNED)
        session = InterviewFactory(
            application=app,
            session_type=Interview.SessionType.INTERVIEW,
            screening_mode=Interview.ScreeningMode.MEET,
            status=Interview.Status.PENDING,
        )

        prompt = build_system_prompt(session)

        assert "cannot evaluate their answer with reasonable confidence" in prompt
        assert "ask a targeted clarification or practical follow-up" in prompt


class TestCompleteSession:
    def test_complete_prescanning_advances_to_shortlisted_when_final_step(self, vacancy):
        """Completing prescanning with 'advance' decision shortlists if interview is disabled."""
        app = ApplicationFactory(vacancy=vacancy, status=Application.Status.APPLIED)
        session = InterviewFactory(
            application=app,
            session_type=Interview.SessionType.PRESCANNING,
            status=Interview.Status.IN_PROGRESS,
        )

        completed = complete_session(
            interview=session,
            overall_score=Decimal("7.50"),
            ai_summary="Good candidate.",
            transcript=[{"role": "ai", "text": "Q1"}, {"role": "candidate", "text": "A1"}],
            ai_decision="advance",
        )

        assert completed.status == Interview.Status.COMPLETED
        assert completed.overall_score == Decimal("7.50")

        app.refresh_from_db()
        assert app.status == Application.Status.SHORTLISTED

    def test_complete_prescanning_rejects(self, vacancy):
        """Completing prescanning with 'reject' decision moves app to REJECTED."""
        app = ApplicationFactory(vacancy=vacancy, status=Application.Status.APPLIED)
        session = InterviewFactory(
            application=app,
            session_type=Interview.SessionType.PRESCANNING,
            status=Interview.Status.IN_PROGRESS,
        )

        complete_session(
            interview=session,
            overall_score=Decimal("3.00"),
            ai_summary="Not a good fit.",
            transcript=[],
            ai_decision="reject",
        )

        app.refresh_from_db()
        assert app.status == Application.Status.REJECTED

    def test_complete_prescanning_creates_interview_if_enabled(self, vacancy):
        """Advancing from prescanning auto-creates an interview session if enabled."""
        vacancy.interview_enabled = True
        vacancy.save(update_fields=["interview_enabled"])

        app = ApplicationFactory(vacancy=vacancy, status=Application.Status.APPLIED)
        session = InterviewFactory(
            application=app,
            session_type=Interview.SessionType.PRESCANNING,
            status=Interview.Status.IN_PROGRESS,
        )

        complete_session(
            interview=session,
            overall_score=Decimal("8.00"),
            ai_summary="Strong candidate.",
            transcript=[],
            ai_decision="advance",
        )

        # An interview session should have been auto-created
        interview_session = app.sessions.filter(
            session_type=Interview.SessionType.INTERVIEW,
            status=Interview.Status.PENDING,
        ).first()
        assert interview_session is not None

    @override_settings(
        FRONTEND_URL="https://app.hrprescan.test",
        TELEGRAM_CANDIDATE_BOT_TOKEN="test-candidate-token",
        TELEGRAM_CANDIDATE_BOT_USERNAME="TestCandidateBot",
    )
    def test_complete_prescanning_sends_interview_link_to_joined_telegram_candidate(self, vacancy):
        vacancy.interview_enabled = True
        vacancy.save(update_fields=["interview_enabled"])
        candidate = UserFactory(company=None, role=User.Role.CANDIDATE, telegram_id=556677)
        app = ApplicationFactory(vacancy=vacancy, candidate=candidate, status=Application.Status.APPLIED)
        session = InterviewFactory(
            application=app,
            session_type=Interview.SessionType.PRESCANNING,
            status=Interview.Status.IN_PROGRESS,
        )

        with patch("apps.integrations.telegram_bot.client.requests.post") as post_mock:
            post_mock.return_value.json.return_value = {"ok": True, "result": {"message_id": 78}}
            complete_session(
                interview=session,
                overall_score=Decimal("8.00"),
                ai_summary="Strong candidate.",
                transcript=[],
                ai_decision="advance",
            )

        interview_session = app.sessions.get(session_type=Interview.SessionType.INTERVIEW)
        payload = post_mock.call_args.kwargs["json"]
        assert payload["chat_id"] == candidate.telegram_id
        assert "parse_mode" not in payload
        assert f"https://app.hrprescan.test/interview/{interview_session.interview_token}" in payload["text"]

        notification = Notification.objects.get(user=candidate, type=Notification.Type.SYSTEM)
        assert notification.data["kind"] == "interview_ready"
        assert notification.data["delivery_channel"] == Message.DeliveryChannel.TELEGRAM
        assert notification.data["delivery_status"] == Message.DeliveryStatus.DELIVERED

    @override_settings(
        FRONTEND_URL="https://app.hrprescan.test",
        TELEGRAM_CANDIDATE_BOT_TOKEN="test-candidate-token",
        TELEGRAM_CANDIDATE_BOT_USERNAME="TestCandidateBot",
    )
    def test_complete_prescanning_sends_interview_link_to_internal_inbox_when_candidate_has_not_joined_bot(
        self,
        vacancy,
    ):
        vacancy.interview_enabled = True
        vacancy.save(update_fields=["interview_enabled"])
        candidate = UserFactory(company=None, role=User.Role.CANDIDATE, telegram_id=None)
        app = ApplicationFactory(vacancy=vacancy, candidate=candidate, status=Application.Status.APPLIED)
        session = InterviewFactory(
            application=app,
            session_type=Interview.SessionType.PRESCANNING,
            status=Interview.Status.IN_PROGRESS,
        )

        with patch("apps.integrations.telegram_bot.client.requests.post") as post_mock:
            complete_session(
                interview=session,
                overall_score=Decimal("8.00"),
                ai_summary="Strong candidate.",
                transcript=[],
                ai_decision="advance",
            )

        post_mock.assert_not_called()
        interview_session = app.sessions.get(session_type=Interview.SessionType.INTERVIEW)
        notification = Notification.objects.get(user=candidate, type=Notification.Type.SYSTEM)
        assert notification.data["kind"] == "interview_ready"
        assert notification.data["delivery_channel"] == Message.DeliveryChannel.WEB
        assert notification.data["delivery_status"] == Message.DeliveryStatus.DELIVERED
        assert notification.data["link"] == f"https://app.hrprescan.test/interview/{interview_session.interview_token}"

    def test_evaluation_negative_recommendation_overrides_live_advance_marker(self):
        """A negative evaluator recommendation must reject even if chat ended with advance."""
        result = {
            "overall_score": 6.0,
            "summary": (
                "\u041d\u0435 \u0440\u0435\u043a\u043e\u043c\u0435\u043d\u0434\u0443\u0435\u0442\u0441\u044f "
                "\u043a \u043f\u0440\u043e\u0434\u0432\u0438\u0436\u0435\u043d\u0438\u044e. "
                "\u041a\u0430\u043d\u0434\u0438\u0434\u0430\u0442 \u043f\u0440\u043e\u044f\u0432"
                "\u043b\u044f\u0435\u0442 \u043d\u0438\u0437\u043a\u0438\u0439 "
                "\u0443\u0440\u043e\u0432\u0435\u043d\u044c."
            ),
        }

        assert derive_ai_decision_from_evaluation(result, fallback="advance") == "reject"

    def test_evaluation_structured_recommendation_overrides_summary(self):
        result = {
            "overall_score": 6.0,
            "summary": "Candidate has some experience but gave short answers.",
            "recommendation": "reject",
        }

        assert derive_ai_decision_from_evaluation(result, fallback="advance") == "reject"


class TestCancelInterview:
    def test_cancel_prescanning_reverts_to_applied(self, vacancy):
        """Cancelling a prescanning session reverts app status to APPLIED."""
        app = ApplicationFactory(vacancy=vacancy, status=Application.Status.APPLIED)
        session = InterviewFactory(
            application=app,
            session_type=Interview.SessionType.PRESCANNING,
            status=Interview.Status.PENDING,
        )

        cancel_interview(interview=session)

        session.refresh_from_db()
        assert session.status == Interview.Status.CANCELLED

        app.refresh_from_db()
        assert app.status == Application.Status.APPLIED

    def test_cancel_interview_reverts_to_prescanned(self, vacancy):
        """Cancelling an interview session reverts app status to PRESCANNED."""
        app = ApplicationFactory(vacancy=vacancy, status=Application.Status.PRESCANNED)
        session = InterviewFactory(
            application=app,
            session_type=Interview.SessionType.INTERVIEW,
            status=Interview.Status.PENDING,
        )

        cancel_interview(interview=session)

        session.refresh_from_db()
        assert session.status == Interview.Status.CANCELLED

        app.refresh_from_db()
        assert app.status == Application.Status.PRESCANNED


class TestResetInterview:
    def test_reset_creates_new_session(self, vacancy):
        """Resetting creates a fresh session with the same type and a new token."""
        app = ApplicationFactory(vacancy=vacancy, status=Application.Status.APPLIED)
        old_session = InterviewFactory(
            application=app,
            session_type=Interview.SessionType.PRESCANNING,
            screening_mode=Interview.ScreeningMode.CHAT,
            status=Interview.Status.IN_PROGRESS,
        )
        old_token = old_session.interview_token

        new_session = reset_interview(interview=old_session)

        # Old session should be cancelled
        old_session.refresh_from_db()
        assert old_session.status == Interview.Status.CANCELLED

        # New session should be pending with a different token
        assert new_session.status == Interview.Status.PENDING
        assert new_session.session_type == Interview.SessionType.PRESCANNING
        assert new_session.interview_token != old_token
        assert new_session.id != old_session.id

    def test_reset_meet_session_uses_interview_id_room_name(self, vacancy):
        app = ApplicationFactory(vacancy=vacancy, status=Application.Status.PRESCANNED)
        old_session = InterviewFactory(
            application=app,
            session_type=Interview.SessionType.INTERVIEW,
            screening_mode=Interview.ScreeningMode.MEET,
            status=Interview.Status.IN_PROGRESS,
        )

        new_session = reset_interview(interview=old_session)

        assert new_session.livekit_room_name == f"interview-{new_session.id}"

    def test_reset_interview_preserves_runtime_language_policy(self, vacancy):
        app = ApplicationFactory(vacancy=vacancy, status=Application.Status.PRESCANNED)
        old_session = InterviewFactory(
            application=app,
            session_type=Interview.SessionType.INTERVIEW,
            screening_mode=Interview.ScreeningMode.MEET,
            status=Interview.Status.IN_PROGRESS,
            language="uz",
        )

        new_session = reset_interview(interview=old_session)

        assert new_session.language == "ru"

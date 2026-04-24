from unittest.mock import patch

from apps.accounts.models import User
from apps.applications.models import Application
from apps.integrations.telegram_bot.bots import ROLE_CANDIDATE
from apps.integrations.telegram_bot.candidate.interview_flow import handle_interview_answer
from apps.integrations.telegram_bot.candidate.states import SK_INTERVIEW_ID, STATE_PS_INTERVIEW
from apps.integrations.telegram_bot.sessions import clear_session, get_session, update_session
from apps.interviews.models import Interview


class FakeTelegramClient:
    def __init__(self):
        self.messages = []

    def send_message(self, **kwargs):
        self.messages.append(kwargs)


def _candidate_user():
    return User.objects.create(
        email="candidate-telegram-flow@example.com",
        first_name="Alex",
        last_name="Tester",
        role=User.Role.CANDIDATE,
        telegram_id=99887766,
        language=User.Language.EN,
    )


def _interview(vacancy, user):
    application = Application.objects.create(
        vacancy=vacancy,
        candidate=user,
        candidate_name=user.full_name,
        candidate_email=user.email,
    )
    return Interview.objects.create(
        application=application,
        session_type=Interview.SessionType.PRESCANNING,
        screening_mode=Interview.ScreeningMode.CHAT,
        status=Interview.Status.IN_PROGRESS,
        channel=Interview.Channel.TELEGRAM,
        chat_history=[{"role": "ai", "text": "Tell me about yourself.", "timestamp": "now"}],
    )


def test_telegram_prescreening_uses_conversational_ai(vacancy):
    user = _candidate_user()
    interview = _interview(vacancy, user)
    client = FakeTelegramClient()

    with patch(
        "apps.interviews.chat_service.process_candidate_message",
        return_value={"ai_message": "Thanks. Can you share a concrete example?", "is_complete": False},
    ) as process_mock:
        handle_interview_answer(
            client=client,
            chat_id=user.telegram_id,
            user=user,
            text="I have relevant experience.",
            session={SK_INTERVIEW_ID: str(interview.id)},
            lang="en",
        )

    process_mock.assert_called_once()
    assert process_mock.call_args.args[1] == "I have relevant experience."
    assert client.messages[-1]["text"] == "Thanks. Can you share a concrete example?"


def test_telegram_prescreening_clears_session_on_completion(vacancy):
    user = _candidate_user()
    interview = _interview(vacancy, user)
    client = FakeTelegramClient()
    update_session(
        role=ROLE_CANDIDATE,
        telegram_id=user.telegram_id,
        state=STATE_PS_INTERVIEW,
        **{SK_INTERVIEW_ID: str(interview.id)},
    )

    with patch(
        "apps.interviews.chat_service.process_candidate_message",
        return_value={"ai_message": "Thank you, we have enough information.", "is_complete": True},
    ):
        handle_interview_answer(
            client=client,
            chat_id=user.telegram_id,
            user=user,
            text="Final answer.",
            session=get_session(role=ROLE_CANDIDATE, telegram_id=user.telegram_id),
            lang="en",
        )

    assert any(message["text"] == "Thank you, we have enough information." for message in client.messages)
    assert get_session(role=ROLE_CANDIDATE, telegram_id=user.telegram_id) == {}
    clear_session(role=ROLE_CANDIDATE, telegram_id=user.telegram_id)

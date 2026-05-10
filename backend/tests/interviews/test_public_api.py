from django.test import override_settings
from rest_framework.test import APIClient

from apps.applications.models import Application
from apps.interviews.models import Interview
from tests.factories import ApplicationFactory, InterviewFactory


class TestPublicInterviewApi:
    def test_interview_cannot_start_before_prescanning_is_completed(self, vacancy):
        app = ApplicationFactory(vacancy=vacancy, status=Application.Status.APPLIED)
        interview = InterviewFactory(
            application=app,
            session_type=Interview.SessionType.INTERVIEW,
            screening_mode=Interview.ScreeningMode.CHAT,
            status=Interview.Status.PENDING,
        )

        response = APIClient().post(f"/api/public/interview/{interview.interview_token}/start/")

        assert response.status_code == 400
        assert "after prescanning" in response.data["detail"]


class TestInternalInterviewApi:
    @override_settings(INTERNAL_API_KEY="test-internal-key")
    def test_agent_can_fetch_interview_context(self, vacancy):
        app = ApplicationFactory(vacancy=vacancy, status=Application.Status.PRESCANNED)
        interview = InterviewFactory(
            application=app,
            session_type=Interview.SessionType.INTERVIEW,
            screening_mode=Interview.ScreeningMode.MEET,
            status=Interview.Status.IN_PROGRESS,
        )

        response = APIClient().get(
            f"/api/internal/interviews/{interview.id}/context/",
            HTTP_X_INTERNAL_KEY="test-internal-key",
            HTTP_X_FORWARDED_PROTO="https",
        )

        assert response.status_code == 200
        assert response.data["interview_id"] == str(interview.id)
        assert response.data["vacancy_title"] == vacancy.title

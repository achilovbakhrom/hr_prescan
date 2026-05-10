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

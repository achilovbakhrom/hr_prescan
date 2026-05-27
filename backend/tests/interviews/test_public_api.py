from io import BytesIO

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
            screening_mode=Interview.ScreeningMode.MEET,
            status=Interview.Status.PENDING,
        )

        response = APIClient().post(f"/api/public/interview/{interview.interview_token}/start/")

        assert response.status_code == 400
        assert "after prescanning" in response.data["detail"]

    @override_settings(ALLOW_INTERVIEW_WITHOUT_PRESCREENING=True)
    def test_dev_bypass_allows_interview_before_prescanning_is_completed(self, vacancy):
        app = ApplicationFactory(vacancy=vacancy, status=Application.Status.APPLIED)
        interview = InterviewFactory(
            application=app,
            session_type=Interview.SessionType.INTERVIEW,
            screening_mode=Interview.ScreeningMode.MEET,
            status=Interview.Status.PENDING,
        )

        response = APIClient().get(f"/api/public/interview/{interview.interview_token}/")

        assert response.status_code == 200
        assert response.data["id"] == str(interview.id)


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

    @override_settings(INTERNAL_API_KEY="test-internal-key")
    def test_agent_context_falls_back_from_uzbek_to_russian(self, vacancy):
        app = ApplicationFactory(vacancy=vacancy, status=Application.Status.PRESCANNED)
        interview = InterviewFactory(
            application=app,
            session_type=Interview.SessionType.INTERVIEW,
            screening_mode=Interview.ScreeningMode.MEET,
            status=Interview.Status.IN_PROGRESS,
            language="uz",
        )

        response = APIClient().get(
            f"/api/internal/interviews/{interview.id}/context/",
            HTTP_X_INTERNAL_KEY="test-internal-key",
            HTTP_X_FORWARDED_PROTO="https",
        )

        assert response.status_code == 200
        assert response.data["language"] == "ru"


class TestVoiceMessageAudioApi:
    @override_settings(S3_KEY_PREFIX="", AWS_STORAGE_BUCKET_NAME="test-bucket")
    def test_streams_unprefixed_voice_message_audio(self, vacancy, monkeypatch):
        requested_keys = []

        class FakeS3:
            def get_object(self, **kwargs):
                requested_keys.append((kwargs["Bucket"], kwargs["Key"]))
                return {"Body": BytesIO(b"audio-bytes"), "ContentType": "audio/webm"}

        monkeypatch.setattr(
            "apps.interviews.transcription_service._get_s3_client",
            lambda: FakeS3(),
        )
        app = ApplicationFactory(vacancy=vacancy, status=Application.Status.APPLIED)
        audio_key = "voice-messages/interview-1/message.webm"
        interview = InterviewFactory(
            application=app,
            session_type=Interview.SessionType.PRESCANNING,
            screening_mode=Interview.ScreeningMode.CHAT,
            status=Interview.Status.IN_PROGRESS,
            chat_history=[
                {"role": "ai", "text": "Hello", "timestamp": "2026-05-26T00:00:00Z"},
                {
                    "role": "candidate",
                    "text": "Answer",
                    "timestamp": "2026-05-26T00:00:01Z",
                    "message_type": "voice",
                    "audio_url": audio_key,
                    "duration": 2,
                },
            ],
        )

        response = APIClient().get(f"/api/public/interview/{interview.interview_token}/chat/voice/1/audio/")

        assert response.status_code == 200
        assert response.content == b"audio-bytes"
        assert requested_keys == [("test-bucket", audio_key)]

    @override_settings(S3_KEY_PREFIX="local", AWS_STORAGE_BUCKET_NAME="test-bucket")
    def test_streams_prefixed_voice_message_audio(self, vacancy, monkeypatch):
        requested_keys = []

        class FakeS3:
            def get_object(self, **kwargs):
                requested_keys.append((kwargs["Bucket"], kwargs["Key"]))
                return {"Body": BytesIO(b"prefixed-audio"), "ContentType": "audio/webm"}

        monkeypatch.setattr(
            "apps.interviews.transcription_service._get_s3_client",
            lambda: FakeS3(),
        )
        app = ApplicationFactory(vacancy=vacancy, status=Application.Status.APPLIED)
        audio_key = "local/voice-messages/interview-1/message.webm"
        interview = InterviewFactory(
            application=app,
            session_type=Interview.SessionType.PRESCANNING,
            screening_mode=Interview.ScreeningMode.CHAT,
            status=Interview.Status.IN_PROGRESS,
            chat_history=[
                {"role": "ai", "text": "Hello", "timestamp": "2026-05-26T00:00:00Z"},
                {
                    "role": "candidate",
                    "text": "Answer",
                    "timestamp": "2026-05-26T00:00:01Z",
                    "message_type": "voice",
                    "audio_url": audio_key,
                    "duration": 2,
                },
            ],
        )

        response = APIClient().get(f"/api/public/interview/{interview.interview_token}/chat/voice/1/audio/")

        assert response.status_code == 200
        assert response.content == b"prefixed-audio"
        assert requested_keys == [("test-bucket", audio_key)]

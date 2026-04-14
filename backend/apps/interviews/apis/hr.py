from django.conf import settings
from django.http import HttpResponse
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdmin, IsHRManager
from apps.applications.selectors import get_application_by_id
from apps.common.exceptions import ApplicationError
from apps.common.messages import (
    MSG_APPLICATION_NOT_FOUND,
    MSG_AUDIO_NOT_FOUND,
    MSG_INTERVIEW_NOT_FOUND,
    MSG_INVALID_AUDIO_URL,
    MSG_MESSAGE_INDEX_OUT_OF_RANGE,
    MSG_NO_AUDIO_FILE,
    MSG_NO_RECORDING,
    MSG_NO_SESSION_FOUND,
    MSG_NOT_IN_COMPANY,
    MSG_RECORDING_ONLY_COMPLETED,
    MSG_TRANSCRIPT_ONLY_COMPLETED,
)
from apps.interviews.models import Interview
from apps.interviews.selectors import (
    get_company_interviews,
    get_integrity_flags,
    get_interview_by_id,
)
from apps.interviews.serializers import (
    IntegrityFlagOutputSerializer,
    InterviewDetailOutputSerializer,
    InterviewOutputSerializer,
)
from apps.interviews.services import (
    cancel_interview,
    generate_observer_token,
    reset_interview,
    schedule_human_interview,
)


class HRApplicationInterviewApi(APIView):
    """GET /api/hr/candidates/{application_id}/interview/ — get session data for a candidate.

    Returns the most recent non-cancelled session. Accepts an optional
    ``session_type`` query parameter ("prescanning" or "interview") to
    retrieve a specific session.
    """

    permission_classes = [IsHRManager | IsAdmin]

    def get(self, request: Request, application_id: str) -> Response:
        company = request.user.company
        if company is None:
            return Response(
                {"detail": str(MSG_NOT_IN_COMPANY)},
                status=status.HTTP_404_NOT_FOUND,
            )

        application = get_application_by_id(
            application_id=application_id,
            company=company,
        )
        if application is None:
            return Response(
                {"detail": str(MSG_APPLICATION_NOT_FOUND)},
                status=status.HTTP_404_NOT_FOUND,
            )

        sessions_qs = (
            Interview.objects.filter(application=application)
            .exclude(status=Interview.Status.CANCELLED)
            .select_related("application__vacancy__company")
            .prefetch_related("scores__criteria", "integrity_flags")
            .order_by("-created_at")
        )

        session_type = request.query_params.get("session_type")
        if session_type in (
            Interview.SessionType.PRESCANNING,
            Interview.SessionType.INTERVIEW,
        ):
            sessions_qs = sessions_qs.filter(session_type=session_type)

        interview = sessions_qs.first()
        if interview is None:
            return Response(
                {"detail": str(MSG_NO_SESSION_FOUND)},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            InterviewDetailOutputSerializer(interview).data,
            status=status.HTTP_200_OK,
        )


class ScheduleHumanInterviewApi(APIView):
    """POST /api/hr/candidates/{application_id}/schedule-human-interview/"""

    permission_classes = [IsHRManager | IsAdmin]

    class InputSerializer(serializers.Serializer):
        scheduled_at = serializers.DateTimeField()
        interviewer_name = serializers.CharField(max_length=255)
        meeting_link = serializers.URLField(required=False, default="", allow_blank=True)

    def post(self, request: Request, application_id: str) -> Response:
        company = request.user.company
        if company is None:
            return Response(
                {"detail": str(MSG_NOT_IN_COMPANY)},
                status=status.HTTP_404_NOT_FOUND,
            )

        application = get_application_by_id(
            application_id=application_id,
            company=company,
        )
        if application is None:
            return Response(
                {"detail": str(MSG_APPLICATION_NOT_FOUND)},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = schedule_human_interview(
            application=application,
            scheduled_at=serializer.validated_data["scheduled_at"],
            interviewer_name=serializer.validated_data["interviewer_name"],
            meeting_link=serializer.validated_data.get("meeting_link", ""),
        )

        return Response(data, status=status.HTTP_201_CREATED)


class HRInterviewListApi(APIView):
    """GET /api/hr/interviews/"""

    permission_classes = [IsHRManager | IsAdmin]

    class FilterSerializer(serializers.Serializer):
        status = serializers.ChoiceField(
            choices=Interview.Status.choices,
            required=False,
        )

    def get(self, request: Request) -> Response:
        company = request.user.company
        if company is None:
            return Response(
                {"detail": str(MSG_NOT_IN_COMPANY)},
                status=status.HTTP_404_NOT_FOUND,
            )

        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        interviews = get_company_interviews(
            company=company,
            status=filter_serializer.validated_data.get("status"),
        )

        return Response(
            InterviewOutputSerializer(interviews, many=True).data,
            status=status.HTTP_200_OK,
        )


class HRInterviewDetailApi(APIView):
    """GET /api/hr/interviews/{id}/"""

    permission_classes = [IsHRManager | IsAdmin]

    def get(self, request: Request, interview_id: str) -> Response:
        company = request.user.company
        if company is None:
            return Response(
                {"detail": str(MSG_NOT_IN_COMPANY)},
                status=status.HTTP_404_NOT_FOUND,
            )

        interview = get_interview_by_id(
            interview_id=interview_id,
            company=company,
        )
        if interview is None:
            return Response(
                {"detail": str(MSG_INTERVIEW_NOT_FOUND)},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            InterviewDetailOutputSerializer(interview).data,
            status=status.HTTP_200_OK,
        )


class CancelInterviewApi(APIView):
    """POST /api/hr/interviews/{id}/cancel/"""

    permission_classes = [IsHRManager | IsAdmin]

    def post(self, request: Request, interview_id: str) -> Response:
        company = request.user.company
        if company is None:
            return Response(
                {"detail": str(MSG_NOT_IN_COMPANY)},
                status=status.HTTP_404_NOT_FOUND,
            )

        interview = get_interview_by_id(
            interview_id=interview_id,
            company=company,
        )
        if interview is None:
            return Response(
                {"detail": str(MSG_INTERVIEW_NOT_FOUND)},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            interview = cancel_interview(interview=interview)
        except ApplicationError as e:
            return Response(
                {"detail": e.message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            InterviewDetailOutputSerializer(interview).data,
            status=status.HTTP_200_OK,
        )


class ResetInterviewApi(APIView):
    """POST /api/hr/interviews/{id}/reset/

    Reset an abandoned interview. Creates a new interview with a fresh token
    and cancels the old one.
    """

    permission_classes = [IsHRManager | IsAdmin]

    def post(self, request: Request, interview_id: str) -> Response:
        company = request.user.company
        if company is None:
            return Response(
                {"detail": str(MSG_NOT_IN_COMPANY)},
                status=status.HTTP_404_NOT_FOUND,
            )

        interview = get_interview_by_id(
            interview_id=interview_id,
            company=company,
        )
        if interview is None:
            return Response(
                {"detail": str(MSG_INTERVIEW_NOT_FOUND)},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            new_interview = reset_interview(interview=interview)
        except ApplicationError as e:
            return Response(
                {"detail": e.message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            InterviewDetailOutputSerializer(new_interview).data,
            status=status.HTTP_200_OK,
        )


class ObserverTokenApi(APIView):
    """GET /api/hr/interviews/{id}/observer-token/"""

    permission_classes = [IsHRManager | IsAdmin]

    def get(self, request: Request, interview_id: str) -> Response:
        company = request.user.company
        if company is None:
            return Response(
                {"detail": str(MSG_NOT_IN_COMPANY)},
                status=status.HTTP_404_NOT_FOUND,
            )

        interview = get_interview_by_id(
            interview_id=interview_id,
            company=company,
        )
        if interview is None:
            return Response(
                {"detail": str(MSG_INTERVIEW_NOT_FOUND)},
                status=status.HTTP_404_NOT_FOUND,
            )

        token = generate_observer_token(interview=interview)

        return Response(
            {
                "token": token,
                "room_name": interview.livekit_room_name,
            },
            status=status.HTTP_200_OK,
        )


class InterviewTranscriptApi(APIView):
    """GET /api/hr/interviews/{id}/transcript/ — timestamped transcript."""

    permission_classes = [IsHRManager | IsAdmin]

    def get(self, request: Request, interview_id: str) -> Response:
        company = request.user.company
        if company is None:
            return Response(
                {"detail": str(MSG_NOT_IN_COMPANY)},
                status=status.HTTP_404_NOT_FOUND,
            )

        interview = get_interview_by_id(
            interview_id=interview_id,
            company=company,
        )
        if interview is None:
            return Response(
                {"detail": str(MSG_INTERVIEW_NOT_FOUND)},
                status=status.HTTP_404_NOT_FOUND,
            )

        if interview.status != Interview.Status.COMPLETED:
            return Response(
                {"detail": str(MSG_TRANSCRIPT_ONLY_COMPLETED)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "interview_id": str(interview.id),
                "transcript": interview.transcript,
            },
            status=status.HTTP_200_OK,
        )


class InterviewRecordingApi(APIView):
    """GET /api/hr/interviews/{id}/recording/ — recording path / presigned URL."""

    permission_classes = [IsHRManager | IsAdmin]

    def get(self, request: Request, interview_id: str) -> Response:
        company = request.user.company
        if company is None:
            return Response(
                {"detail": str(MSG_NOT_IN_COMPANY)},
                status=status.HTTP_404_NOT_FOUND,
            )

        interview = get_interview_by_id(
            interview_id=interview_id,
            company=company,
        )
        if interview is None:
            return Response(
                {"detail": str(MSG_INTERVIEW_NOT_FOUND)},
                status=status.HTTP_404_NOT_FOUND,
            )

        if interview.status != Interview.Status.COMPLETED:
            return Response(
                {"detail": str(MSG_RECORDING_ONLY_COMPLETED)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not interview.recording_path:
            return Response(
                {"detail": str(MSG_NO_RECORDING)},
                status=status.HTTP_404_NOT_FOUND,
            )

        # TODO: Generate presigned URL from MinIO/S3 instead of raw path
        return Response(
            {
                "interview_id": str(interview.id),
                "recording_url": interview.recording_path,
            },
            status=status.HTTP_200_OK,
        )


class IntegrityFlagsApi(APIView):
    """GET /api/hr/interviews/{id}/integrity-flags/

    Returns all anti-cheating integrity flags detected during an interview.
    Only available for HR managers and admins scoped to their company.
    """

    permission_classes = [IsHRManager | IsAdmin]

    def get(self, request: Request, interview_id: str) -> Response:
        company = request.user.company
        if company is None:
            return Response(
                {"detail": str(MSG_NOT_IN_COMPANY)},
                status=status.HTTP_404_NOT_FOUND,
            )

        flags = get_integrity_flags(interview_id=interview_id, company=company)
        if flags is None:
            return Response(
                {"detail": str(MSG_INTERVIEW_NOT_FOUND)},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "interview_id": str(interview_id),
                "flags": IntegrityFlagOutputSerializer(flags, many=True).data,
                "total_flags": flags.count(),
            },
            status=status.HTTP_200_OK,
        )


class HRVoiceMessageAudioApi(APIView):
    """GET /api/hr/interviews/{interview_id}/voice/{message_index}/audio/ — HR plays voice message."""

    permission_classes = [IsHRManager | IsAdmin]

    def get(self, request: Request, interview_id: str, message_index: int) -> Response:
        company = request.user.company
        interview = get_interview_by_id(interview_id=interview_id, company=company)
        if interview is None:
            return Response(
                {"detail": str(MSG_INTERVIEW_NOT_FOUND)},
                status=status.HTTP_404_NOT_FOUND,
            )

        chat_history = interview.chat_history or []

        if message_index < 0 or message_index >= len(chat_history):
            return Response(
                {"detail": str(MSG_MESSAGE_INDEX_OUT_OF_RANGE)},
                status=status.HTTP_404_NOT_FOUND,
            )

        message = chat_history[message_index]

        if message.get("message_type") != "voice" or not message.get("audio_url"):
            return Response(
                {"detail": str(MSG_NO_AUDIO_FILE)},
                status=status.HTTP_404_NOT_FOUND,
            )

        audio_url = message["audio_url"]
        if not audio_url.startswith("voice-messages/"):
            return Response(
                {"detail": str(MSG_INVALID_AUDIO_URL)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from apps.interviews.transcription_service import _get_s3_client

        s3 = _get_s3_client()
        try:
            s3_response = s3.get_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=audio_url,
            )
        except Exception:
            return Response(
                {"detail": str(MSG_AUDIO_NOT_FOUND)},
                status=status.HTTP_404_NOT_FOUND,
            )

        audio_bytes = s3_response["Body"].read()
        content_type = s3_response.get("ContentType", "audio/webm")

        response = HttpResponse(audio_bytes, content_type=content_type)
        response["Content-Disposition"] = "inline"
        response["Cache-Control"] = "private, max-age=3600"
        return response

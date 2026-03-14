from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdmin, IsHRManager
from apps.applications.selectors import get_application_by_id
from apps.common.exceptions import ApplicationError
from apps.interviews.models import Interview
from apps.interviews.selectors import get_company_interviews, get_interview_by_id
from apps.interviews.serializers import (
    InterviewDetailOutputSerializer,
    InterviewOutputSerializer,
)
from apps.interviews.services import cancel_interview, generate_observer_token, schedule_interview


class ScheduleInterviewApi(APIView):
    """POST /api/hr/candidates/{application_id}/schedule-interview/"""

    permission_classes = [IsHRManager | IsAdmin]

    class InputSerializer(serializers.Serializer):
        scheduled_at = serializers.DateTimeField()

    def post(self, request: Request, application_id: str) -> Response:
        company = request.user.company
        if company is None:
            return Response(
                {"detail": "You are not associated with a company."},
                status=status.HTTP_404_NOT_FOUND,
            )

        application = get_application_by_id(
            application_id=application_id, company=company,
        )
        if application is None:
            return Response(
                {"detail": "Application not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            interview = schedule_interview(
                application=application,
                scheduled_at=serializer.validated_data["scheduled_at"],
            )
        except ApplicationError as e:
            return Response(
                {"detail": e.message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            InterviewDetailOutputSerializer(interview).data,
            status=status.HTTP_201_CREATED,
        )


class HRInterviewListApi(APIView):
    """GET /api/hr/interviews/"""

    permission_classes = [IsHRManager | IsAdmin]

    class FilterSerializer(serializers.Serializer):
        status = serializers.ChoiceField(
            choices=Interview.Status.choices, required=False,
        )

    def get(self, request: Request) -> Response:
        company = request.user.company
        if company is None:
            return Response(
                {"detail": "You are not associated with a company."},
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
                {"detail": "You are not associated with a company."},
                status=status.HTTP_404_NOT_FOUND,
            )

        interview = get_interview_by_id(
            interview_id=interview_id, company=company,
        )
        if interview is None:
            return Response(
                {"detail": "Interview not found."},
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
                {"detail": "You are not associated with a company."},
                status=status.HTTP_404_NOT_FOUND,
            )

        interview = get_interview_by_id(
            interview_id=interview_id, company=company,
        )
        if interview is None:
            return Response(
                {"detail": "Interview not found."},
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


class ObserverTokenApi(APIView):
    """GET /api/hr/interviews/{id}/observer-token/"""

    permission_classes = [IsHRManager | IsAdmin]

    def get(self, request: Request, interview_id: str) -> Response:
        company = request.user.company
        if company is None:
            return Response(
                {"detail": "You are not associated with a company."},
                status=status.HTTP_404_NOT_FOUND,
            )

        interview = get_interview_by_id(
            interview_id=interview_id, company=company,
        )
        if interview is None:
            return Response(
                {"detail": "Interview not found."},
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
                {"detail": "You are not associated with a company."},
                status=status.HTTP_404_NOT_FOUND,
            )

        interview = get_interview_by_id(
            interview_id=interview_id, company=company,
        )
        if interview is None:
            return Response(
                {"detail": "Interview not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if interview.status != Interview.Status.COMPLETED:
            return Response(
                {"detail": "Transcript is only available for completed interviews."},
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
                {"detail": "You are not associated with a company."},
                status=status.HTTP_404_NOT_FOUND,
            )

        interview = get_interview_by_id(
            interview_id=interview_id, company=company,
        )
        if interview is None:
            return Response(
                {"detail": "Interview not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if interview.status != Interview.Status.COMPLETED:
            return Response(
                {"detail": "Recording is only available for completed interviews."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not interview.recording_path:
            return Response(
                {"detail": "No recording available for this interview."},
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

from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.applications.models import Application
from apps.common.exceptions import ApplicationError
from apps.common.messages import (
    MSG_INTERVIEW_NOT_FOUND,
    MSG_VACANCY_NOT_ACCEPTING_INTERVIEWS,
)
from apps.interviews.models import Interview
from apps.interviews.selectors import (
    get_interview_by_token,
    get_interview_for_candidate,
)
from apps.interviews.serializers import (
    CandidateInterviewOutputSerializer,
    PublicInterviewOutputSerializer,
)
from apps.interviews.services import generate_candidate_token, start_interview


def _interview_step_is_available(interview: Interview) -> bool:
    if interview.session_type != Interview.SessionType.INTERVIEW:
        return True
    return interview.application.status in (Application.Status.PRESCANNED, Application.Status.INTERVIEWED)


def _not_ready_response() -> Response:
    return Response(
        {"detail": "The interview link is prepared, but it opens only after prescanning is completed."},
        status=status.HTTP_400_BAD_REQUEST,
    )


class CandidateInterviewApi(APIView):
    permission_classes = [AllowAny]

    class InputSerializer(serializers.Serializer):
        candidate_email = serializers.EmailField()

    def get(self, request: Request, interview_id: str) -> Response:
        serializer = self.InputSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        candidate_email = serializer.validated_data["candidate_email"]

        interview = get_interview_for_candidate(
            interview_id=interview_id,
            candidate_email=candidate_email,
        )
        if interview is None:
            return Response(
                {"detail": str(MSG_INTERVIEW_NOT_FOUND)},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            CandidateInterviewOutputSerializer(interview).data,
            status=status.HTTP_200_OK,
        )


class InterviewRoomJoinApi(APIView):
    permission_classes = [AllowAny]

    def get(self, request: Request, token: str) -> Response:
        interview = get_interview_by_token(interview_token=token)
        if interview is None:
            return Response(
                {"detail": str(MSG_INTERVIEW_NOT_FOUND)},
                status=status.HTTP_404_NOT_FOUND,
            )

        if interview.screening_mode != Interview.ScreeningMode.MEET:
            return Response(
                {"detail": "Video room is only available for meet-mode interviews."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if interview.status not in (
            Interview.Status.PENDING,
            Interview.Status.IN_PROGRESS,
        ):
            return Response(
                {"detail": f"Interview is {interview.status}. Cannot join."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not _interview_step_is_available(interview):
            return _not_ready_response()

        if interview.status == Interview.Status.PENDING:
            vacancy = interview.application.vacancy
            if vacancy.status == "archived":
                return Response(
                    {"detail": str(MSG_VACANCY_NOT_ACCEPTING_INTERVIEWS)},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                interview = start_interview(interview=interview)
            except ApplicationError as e:
                return Response(
                    {"detail": e.message},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if not interview.livekit_room_name:
            interview.livekit_room_name = f"interview-{interview.id}"
            interview.save(update_fields=["livekit_room_name", "updated_at"])

        try:
            token = generate_candidate_token(interview=interview)
        except ApplicationError as e:
            return Response(
                {"detail": e.message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        response_data = {
            "id": str(interview.id),
            "vacancy_title": interview.application.vacancy.title,
            "candidate_name": interview.application.candidate_name,
            "session_type": interview.session_type,
            "screening_mode": interview.screening_mode,
            "started_at": interview.started_at.isoformat() if interview.started_at else None,
            "duration_minutes": interview.duration_minutes,
            "status": interview.status,
            "livekit_room_name": interview.livekit_room_name,
            "candidate_token": token,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class PublicInterviewApi(APIView):
    permission_classes = [AllowAny]

    def get(self, request: Request, token: str) -> Response:
        interview = get_interview_by_token(interview_token=token)
        if interview is None:
            return Response(
                {"detail": str(MSG_INTERVIEW_NOT_FOUND)},
                status=status.HTTP_404_NOT_FOUND,
            )
        if not _interview_step_is_available(interview):
            return _not_ready_response()

        return Response(
            PublicInterviewOutputSerializer(interview).data,
            status=status.HTTP_200_OK,
        )


class StartInterviewApi(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request, token: str) -> Response:
        interview = get_interview_by_token(interview_token=token)
        if interview is None:
            return Response(
                {"detail": str(MSG_INTERVIEW_NOT_FOUND)},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not _interview_step_is_available(interview):
            return _not_ready_response()

        try:
            interview = start_interview(interview=interview)
        except ApplicationError as e:
            return Response(
                {"detail": e.message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            PublicInterviewOutputSerializer(interview).data,
            status=status.HTTP_200_OK,
        )

from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.applications.selectors import get_application_by_id
from apps.common.exceptions import ApplicationError
from apps.interviews.selectors import get_interview_for_candidate
from apps.interviews.serializers import CandidateInterviewOutputSerializer
from apps.interviews.services import schedule_interview


class CandidateScheduleApi(APIView):
    """POST /api/candidate/schedule/{application_id}/

    Candidate picks a time slot for their interview.
    Token-based access (AllowAny — real auth via token in later phase).
    """

    permission_classes = [AllowAny]

    class InputSerializer(serializers.Serializer):
        scheduled_at = serializers.DateTimeField()
        candidate_email = serializers.EmailField()

    def post(self, request: Request, application_id: str) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        candidate_email = serializer.validated_data["candidate_email"]

        application = get_application_by_id(application_id=application_id)
        if application is None:
            return Response(
                {"detail": "Application not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Verify the candidate owns this application
        if application.candidate_email != candidate_email:
            return Response(
                {"detail": "Application not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

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
            CandidateInterviewOutputSerializer(interview).data,
            status=status.HTTP_201_CREATED,
        )


class CandidateInterviewApi(APIView):
    """GET /api/candidate/interview/{interview_id}/

    Returns room link and token for joining the interview.
    Token-based access (AllowAny — real auth via token in later phase).
    """

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
                {"detail": "Interview not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            CandidateInterviewOutputSerializer(interview).data,
            status=status.HTTP_200_OK,
        )

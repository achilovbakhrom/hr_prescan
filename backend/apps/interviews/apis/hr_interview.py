from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import HasHRPermission, HRPermissions
from apps.accounts.selectors import get_user_live_company_ids
from apps.applications.selectors import get_application_by_id
from apps.common.exceptions import ApplicationError
from apps.common.messages import (
    MSG_APPLICATION_NOT_FOUND,
    MSG_INTERVIEW_NOT_FOUND,
    MSG_NO_SESSION_FOUND,
    MSG_NOT_IN_COMPANY,
)
from apps.interviews.models import Interview
from apps.interviews.selectors import (
    get_interview_by_id,
    get_user_interviews,
)
from apps.interviews.serializers import (
    InterviewDetailOutputSerializer,
    InterviewOutputSerializer,
)
from apps.interviews.services import cancel_interview


class HRApplicationInterviewApi(APIView):
    """GET /api/hr/candidates/{application_id}/interview/ — get session data for a candidate.

    Returns the most recent non-cancelled session. Accepts an optional
    ``session_type`` query parameter ("prescanning" or "interview") to
    retrieve a specific session.
    """

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_INTERVIEWS

    def get(self, request: Request, application_id: str) -> Response:
        if not get_user_live_company_ids(user=request.user):
            return Response(
                {"detail": str(MSG_NOT_IN_COMPANY)},
                status=status.HTTP_404_NOT_FOUND,
            )

        application = get_application_by_id(
            application_id=application_id,
            user=request.user,
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


class HRInterviewListApi(APIView):
    """GET /api/hr/interviews/"""

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_INTERVIEWS

    class FilterSerializer(serializers.Serializer):
        status = serializers.ChoiceField(
            choices=Interview.Status.choices,
            required=False,
        )

    def get(self, request: Request) -> Response:
        if not get_user_live_company_ids(user=request.user):
            return Response(
                {"detail": str(MSG_NOT_IN_COMPANY)},
                status=status.HTTP_404_NOT_FOUND,
            )

        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        interviews = get_user_interviews(
            user=request.user,
            status=filter_serializer.validated_data.get("status"),
        )

        return Response(
            InterviewOutputSerializer(interviews, many=True).data,
            status=status.HTTP_200_OK,
        )


class HRInterviewDetailApi(APIView):
    """GET /api/hr/interviews/{id}/"""

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_INTERVIEWS

    def get(self, request: Request, interview_id: str) -> Response:
        if not get_user_live_company_ids(user=request.user):
            return Response(
                {"detail": str(MSG_NOT_IN_COMPANY)},
                status=status.HTTP_404_NOT_FOUND,
            )

        interview = get_interview_by_id(
            interview_id=interview_id,
            user=request.user,
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

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_INTERVIEWS

    def post(self, request: Request, interview_id: str) -> Response:
        if not get_user_live_company_ids(user=request.user):
            return Response(
                {"detail": str(MSG_NOT_IN_COMPANY)},
                status=status.HTTP_404_NOT_FOUND,
            )

        interview = get_interview_by_id(
            interview_id=interview_id,
            user=request.user,
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

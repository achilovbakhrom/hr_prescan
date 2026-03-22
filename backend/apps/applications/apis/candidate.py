from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.messages import MSG_APPLICATION_NOT_FOUND
from apps.applications.selectors import (
    get_candidate_application_by_id,
    get_candidate_applications,
)
from apps.applications.serializers import (
    CandidateApplicationDetailOutputSerializer,
    CandidateApplicationListOutputSerializer,
)


class CandidateApplicationListApi(APIView):
    """GET /api/candidate/applications/ — list candidate's own applications."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        applications = get_candidate_applications(
            candidate_email=request.user.email,
        )
        return Response(
            CandidateApplicationListOutputSerializer(applications, many=True).data,
            status=status.HTTP_200_OK,
        )


class CandidateApplicationDetailApi(APIView):
    """GET /api/candidate/applications/{id}/ — candidate's application detail."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, application_id: str) -> Response:
        application = get_candidate_application_by_id(
            application_id=application_id,
            candidate_email=request.user.email,
        )
        if application is None:
            return Response(
                {"detail": str(MSG_APPLICATION_NOT_FOUND)},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            CandidateApplicationDetailOutputSerializer(application).data,
            status=status.HTTP_200_OK,
        )

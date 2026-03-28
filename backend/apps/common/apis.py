from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import HasHRPermission, IsAdmin, IsHRManager
from apps.common.messages import MSG_NOT_IN_COMPANY
from apps.applications.serializers import ApplicationListOutputSerializer
from apps.common.selectors import (
    get_dashboard_stats,
    get_recent_applications,
    get_pending_company_interviews,
)
from apps.interviews.serializers import InterviewOutputSerializer


class HRDashboardApi(APIView):
    """GET /api/hr/dashboard/ — dashboard stats for HR."""

    permission_classes = [HasHRPermission]

    def get(self, request: Request) -> Response:
        company = request.user.company
        if company is None:
            return Response(
                {"detail": str(MSG_NOT_IN_COMPANY)},
                status=status.HTTP_404_NOT_FOUND,
            )

        stats = get_dashboard_stats(company=company)

        recent_applications = get_recent_applications(company=company, limit=5)
        upcoming_interviews = get_pending_company_interviews(
            company=company, limit=5,
        )

        return Response(
            {
                **stats,
                "recent_applications": ApplicationListOutputSerializer(
                    recent_applications, many=True,
                ).data,
                "upcoming_interviews": InterviewOutputSerializer(
                    upcoming_interviews, many=True,
                ).data,
            },
            status=status.HTTP_200_OK,
        )

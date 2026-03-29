from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import HasHRPermission, HRPermissions
from apps.common.messages import MSG_NOT_IN_COMPANY
from apps.common.selectors import get_company_analytics


class HRAnalyticsApi(APIView):
    """GET /api/hr/analytics/ — company-level hiring analytics for HR."""

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.VIEW_ANALYTICS

    def get(self, request: Request) -> Response:
        company = request.user.company
        if company is None:
            return Response(
                {"detail": str(MSG_NOT_IN_COMPANY)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = get_company_analytics(company=company)
        return Response(data, status=status.HTTP_200_OK)

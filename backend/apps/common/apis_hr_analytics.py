from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import HasHRPermission, HRPermissions
from apps.accounts.selectors import get_user_live_company_ids
from apps.common.analytics_selectors import get_user_analytics
from apps.common.messages import MSG_NOT_IN_COMPANY


class HRAnalyticsApi(APIView):
    """GET /api/hr/analytics/ — company-level hiring analytics for HR."""

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.VIEW_ANALYTICS

    def get(self, request: Request) -> Response:
        if not get_user_live_company_ids(user=request.user):
            return Response(
                {"detail": str(MSG_NOT_IN_COMPANY)},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = get_user_analytics(user=request.user)
        return Response(data, status=status.HTTP_200_OK)

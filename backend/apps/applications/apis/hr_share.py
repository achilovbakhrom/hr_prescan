from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import HasHRPermission, HRPermissions
from apps.accounts.selectors import get_user_live_company_ids
from apps.applications.selectors import get_application_by_id
from apps.applications.services import rotate_hiring_manager_token
from apps.common.messages import MSG_APPLICATION_NOT_FOUND, MSG_NOT_IN_COMPANY


class HRApplicationShareTokenRotateApi(APIView):
    """POST /api/hr/candidates/{id}/share-token/rotate/ — revoke old review link."""

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_CANDIDATES

    def post(self, request, application_id: str) -> Response:
        if not get_user_live_company_ids(user=request.user):
            return Response({"detail": str(MSG_NOT_IN_COMPANY)}, status=status.HTTP_404_NOT_FOUND)

        application = get_application_by_id(application_id=application_id, user=request.user)
        if application is None:
            return Response({"detail": str(MSG_APPLICATION_NOT_FOUND)}, status=status.HTTP_404_NOT_FOUND)

        application = rotate_hiring_manager_token(
            application=application,
            actor_name=getattr(request.user, "email", ""),
        )
        return Response(
            {"hiring_manager_token": str(application.hiring_manager_token)},
            status=status.HTTP_200_OK,
        )

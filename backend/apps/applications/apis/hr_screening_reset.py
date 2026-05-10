from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import HasHRPermission, HRPermissions
from apps.accounts.selectors import get_user_live_company_ids
from apps.applications.selectors import get_application_by_id
from apps.applications.serializers import ApplicationDetailOutputSerializer
from apps.applications.services.screening_reset import reset_application_screening
from apps.common.messages import MSG_APPLICATION_NOT_FOUND, MSG_NOT_IN_COMPANY
from apps.interviews.models import Interview


class HRApplicationScreeningResetApi(APIView):
    """POST /api/hr/candidates/{id}/screening/{session_type}/reset/."""

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_CANDIDATES

    class InputSerializer(serializers.Serializer):
        session_type = serializers.ChoiceField(
            choices=[
                Interview.SessionType.PRESCANNING,
                Interview.SessionType.INTERVIEW,
            ],
        )

    def post(self, request: Request, application_id: str, session_type: str) -> Response:
        if not get_user_live_company_ids(user=request.user):
            return Response(
                {"detail": str(MSG_NOT_IN_COMPANY)},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.InputSerializer(data={"session_type": session_type})
        serializer.is_valid(raise_exception=True)

        application = get_application_by_id(
            application_id=application_id,
            user=request.user,
        )
        if application is None:
            return Response(
                {"detail": str(MSG_APPLICATION_NOT_FOUND)},
                status=status.HTTP_404_NOT_FOUND,
            )

        application = reset_application_screening(
            application=application,
            session_type=serializer.validated_data["session_type"],
        )
        return Response(
            ApplicationDetailOutputSerializer(application).data,
            status=status.HTTP_200_OK,
        )

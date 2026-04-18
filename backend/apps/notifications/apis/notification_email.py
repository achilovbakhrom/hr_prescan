from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import HasHRPermission, HRPermissions
from apps.applications.models import Application
from apps.common.exceptions import ApplicationError
from apps.notifications.serializers import (
    BulkStatusUpdateInputSerializer,
    SendCandidateEmailInputSerializer,
)

# ---------------------------------------------------------------------------
# Send Email to Candidate
# ---------------------------------------------------------------------------


class SendCandidateEmailApi(APIView):
    """POST /api/hr/candidates/{application_id}/email/ — send email to candidate."""

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_CANDIDATES

    def post(self, request: Request, application_id: str) -> Response:
        try:
            application = Application.objects.select_related("vacancy").get(
                id=application_id,
                vacancy__company=request.user.company,
            )
        except Application.DoesNotExist:
            return Response(
                {"detail": "Application not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SendCandidateEmailInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from apps.notifications.tasks import send_candidate_email

        send_candidate_email.delay(
            str(application.id),
            serializer.validated_data["subject"],
            serializer.validated_data["body"],
        )

        return Response({"status": "Email queued."}, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# Bulk Actions
# ---------------------------------------------------------------------------


class BulkStatusUpdateApi(APIView):
    """POST /api/hr/candidates/bulk-status/ — update multiple applications at once."""

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_CANDIDATES

    def post(self, request: Request) -> Response:
        serializer = BulkStatusUpdateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from apps.applications.services import bulk_update_status

        try:
            count = bulk_update_status(
                application_ids=serializer.validated_data["application_ids"],
                status=serializer.validated_data["status"],
                updated_by=request.user,
            )
        except ApplicationError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"updated": count},
            status=status.HTTP_200_OK,
        )

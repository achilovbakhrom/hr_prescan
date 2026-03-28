from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import HasHRPermission, HRPermissions, IsAdmin, IsHRManager
from apps.applications.models import Application
from apps.common.exceptions import ApplicationError
from apps.notifications.models import Notification
from apps.notifications.selectors import get_unread_count, get_user_notifications
from apps.notifications.serializers import (
    BulkStatusUpdateInputSerializer,
    MessageOutputSerializer,
    NotificationOutputSerializer,
    SendCandidateEmailInputSerializer,
    SendMessageInputSerializer,
)
from apps.notifications.services import (
    get_message_thread,
    mark_all_as_read,
    mark_as_read,
    mark_messages_as_read,
    send_message,
)


# ---------------------------------------------------------------------------
# Notification APIs
# ---------------------------------------------------------------------------


class NotificationListApi(APIView):
    """GET /api/notifications/ — list notifications for the authenticated user."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        unread_only = request.query_params.get("unread", "").lower() in ("true", "1")
        notifications = get_user_notifications(
            user=request.user,
            unread_only=unread_only,
        )
        data = NotificationOutputSerializer(notifications[:100], many=True).data
        return Response(data, status=status.HTTP_200_OK)


class NotificationReadApi(APIView):
    """PATCH /api/notifications/{id}/read/ — mark a single notification as read."""

    permission_classes = [IsAuthenticated]

    def patch(self, request: Request, notification_id: str) -> Response:
        try:
            notification = Notification.objects.get(
                id=notification_id, user=request.user,
            )
        except Notification.DoesNotExist:
            return Response(
                {"detail": "Notification not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        mark_as_read(notification=notification)
        return Response({"status": "ok"}, status=status.HTTP_200_OK)


class NotificationReadAllApi(APIView):
    """POST /api/notifications/read-all/ — mark all notifications as read."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        count = mark_all_as_read(user=request.user)
        return Response({"updated": count}, status=status.HTTP_200_OK)


class NotificationUnreadCountApi(APIView):
    """GET /api/notifications/unread-count/ — return the unread count."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        count = get_unread_count(user=request.user)
        return Response({"unread_count": count}, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# Messaging APIs
# ---------------------------------------------------------------------------


class HRMessageListApi(APIView):
    """
    GET  /api/hr/candidates/{application_id}/messages/ — message thread for an application
    POST /api/hr/candidates/{application_id}/messages/ — send a message to candidate
    """

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_CANDIDATES

    def get(self, request: Request, application_id: str) -> Response:
        application = self._get_application(request, application_id)
        if application is None:
            return Response(
                {"detail": "Application not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if application.candidate is None:
            return Response([], status=status.HTTP_200_OK)

        messages = get_message_thread(
            user=request.user,
            other_user=application.candidate,
            application=application,
        )

        # Mark messages from candidate as read
        mark_messages_as_read(user=request.user, other_user=application.candidate)

        data = MessageOutputSerializer(messages, many=True).data
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request: Request, application_id: str) -> Response:
        application = self._get_application(request, application_id)
        if application is None:
            return Response(
                {"detail": "Application not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if application.candidate is None:
            return Response(
                {"detail": "Candidate does not have an account."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = SendMessageInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        message = send_message(
            sender=request.user,
            recipient=application.candidate,
            content=serializer.validated_data["content"],
            application=application,
        )

        data = MessageOutputSerializer(message).data
        return Response(data, status=status.HTTP_201_CREATED)

    @staticmethod
    def _get_application(request: Request, application_id: str) -> Application | None:
        try:
            return Application.objects.select_related(
                "candidate", "vacancy",
            ).get(
                id=application_id,
                vacancy__company=request.user.company,
            )
        except Application.DoesNotExist:
            return None


class CandidateMessageListApi(APIView):
    """GET /api/candidate/messages/ — all message threads for the candidate."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        from apps.notifications.models import Message
        from django.db.models import Q

        messages = (
            Message.objects.filter(
                Q(sender=request.user) | Q(recipient=request.user),
            )
            .select_related("sender", "recipient", "application")
            .order_by("-created_at")[:100]
        )

        data = MessageOutputSerializer(messages, many=True).data
        return Response(data, status=status.HTTP_200_OK)


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

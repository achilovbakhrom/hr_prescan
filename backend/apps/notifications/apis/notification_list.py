from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import HasHRPermission, HRPermissions
from apps.applications.models import Application
from apps.applications.selectors import get_application_by_id
from apps.notifications.models import Notification
from apps.notifications.selectors import get_unread_count, get_user_notifications
from apps.notifications.serializers import (
    MessageOutputSerializer,
    NotificationOutputSerializer,
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
                id=notification_id,
                user=request.user,
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
        return get_application_by_id(application_id=application_id, user=request.user)


class CandidateMessageListApi(APIView):
    """GET /api/candidate/messages/ — all message threads for the candidate."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        from django.db.models import Q

        from apps.notifications.models import Message

        messages = (
            Message.objects.filter(
                Q(sender=request.user) | Q(recipient=request.user),
            )
            .select_related("sender", "recipient", "application")
            .order_by("-created_at")[:100]
        )

        data = MessageOutputSerializer(messages, many=True).data
        return Response(data, status=status.HTTP_200_OK)

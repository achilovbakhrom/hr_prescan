from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import HasHRPermission


class TelegramWebhookApi(APIView):
    """POST /api/telegram/webhook/ — receive updates from Telegram."""

    permission_classes = [AllowAny]

    def post(self, request):
        # Verify webhook secret
        secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if settings.TELEGRAM_WEBHOOK_SECRET and secret != settings.TELEGRAM_WEBHOOK_SECRET:
            return Response(status=status.HTTP_403_FORBIDDEN)

        # Dispatch to Celery for async processing
        from apps.integrations.tasks import process_telegram_update

        process_telegram_update.delay(request.data)

        return Response({"ok": True}, status=status.HTTP_200_OK)


class TelegramLinkCodeApi(APIView):
    """GET /api/hr/telegram/link-code/ — generate a deep link for Telegram."""

    permission_classes = [HasHRPermission]

    def get(self, request):
        from apps.integrations.models import TelegramLinkCode

        link = TelegramLinkCode.generate(user=request.user)
        bot_username = settings.TELEGRAM_BOT_USERNAME.lstrip("@")
        link_url = f"https://t.me/{bot_username}?start={link.code}"
        return Response({
            "link_url": link_url,
            "expires_at": link.expires_at.isoformat(),
        })


class TelegramStatusApi(APIView):
    """GET /api/hr/telegram/status/ — check Telegram connection status."""

    permission_classes = [HasHRPermission]

    def get(self, request):
        user = request.user
        return Response({
            "linked": bool(user.telegram_id),
            "telegram_username": user.telegram_username or None,
        })


class TelegramUnlinkApi(APIView):
    """POST /api/hr/telegram/unlink/ — disconnect Telegram account."""

    permission_classes = [HasHRPermission]

    def post(self, request):
        user = request.user
        user.telegram_id = None
        user.telegram_username = ""
        user.save(update_fields=["telegram_id", "telegram_username", "updated_at"])
        return Response({"detail": "Telegram account disconnected."})

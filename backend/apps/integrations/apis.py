from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import HasHRPermission
from apps.integrations.telegram_bot.bots import (
    ROLE_CANDIDATE,
    ROLE_HR,
    VALID_ROLES,
    get_bot_config,
)


class TelegramWebhookApi(APIView):
    """POST /api/telegram/<role>/webhook/ — receive updates from a Telegram bot.

    The ``role`` URL kwarg distinguishes the HR bot from the candidate bot so
    each can verify its own secret token and dispatch to its own handler.
    """

    permission_classes = [AllowAny]

    def post(self, request, role: str):
        if role not in VALID_ROLES:
            return Response(status=status.HTTP_404_NOT_FOUND)

        config = get_bot_config(role=role)
        if not config.token:
            # Bot isn't configured on this deployment — fail loudly so the
            # operator notices instead of silently dropping updates.
            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)

        secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if config.webhook_secret and secret != config.webhook_secret:
            return Response(status=status.HTTP_403_FORBIDDEN)

        from apps.integrations.tasks import process_telegram_update

        process_telegram_update.delay(request.data, role)
        return Response({"ok": True}, status=status.HTTP_200_OK)


class TelegramLinkCodeApi(APIView):
    """GET /api/hr/telegram/link-code/ — generate a deep link for HRs to connect Telegram."""

    permission_classes = [HasHRPermission]

    def get(self, request):
        from apps.integrations.models import TelegramLinkCode

        link = TelegramLinkCode.generate(user=request.user)
        bot_username = settings.TELEGRAM_HR_BOT_USERNAME.lstrip("@")
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
        return Response(
            {
                "linked": bool(user.telegram_id),
                "telegram_username": user.telegram_username or None,
            }
        )


class TelegramUnlinkApi(APIView):
    """POST /api/hr/telegram/unlink/ — disconnect Telegram account."""

    permission_classes = [HasHRPermission]

    def post(self, request):
        user = request.user
        user.telegram_id = None
        user.telegram_username = ""
        user.save(update_fields=["telegram_id", "telegram_username", "updated_at"])
        return Response({"detail": "Telegram account disconnected."})


# Re-exported here for clarity in URL routing.
__all__ = [
    "ROLE_CANDIDATE",
    "ROLE_HR",
    "TelegramLinkCodeApi",
    "TelegramStatusApi",
    "TelegramUnlinkApi",
    "TelegramWebhookApi",
]

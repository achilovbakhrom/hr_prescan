from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.permissions import IsAdmin, IsHRManager
from apps.accounts.serializers import UserOutputSerializer


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


class TelegramAuthRequestApi(APIView):
    """POST /api/telegram/auth/request/ — generate a login code for bot-based auth."""

    permission_classes = [AllowAny]

    def post(self, request):
        from apps.integrations.models import TelegramAuthCode

        auth_code = TelegramAuthCode.generate()
        bot_username = settings.TELEGRAM_BOT_USERNAME.lstrip("@")
        link_url = f"https://t.me/{bot_username}?start=login_{auth_code.code}"
        return Response({
            "code": auth_code.code,
            "link_url": link_url,
            "expires_at": auth_code.expires_at.isoformat(),
        })


class TelegramAuthCheckApi(APIView):
    """GET /api/telegram/auth/check/<code>/ — poll to check if auth is complete."""

    permission_classes = [AllowAny]

    def get(self, request, code):
        from django.utils import timezone

        from apps.integrations.models import TelegramAuthCode

        auth_code = TelegramAuthCode.objects.filter(code=code).first()

        if auth_code is None:
            return Response(
                {"detail": "Invalid code."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if auth_code.is_expired and not auth_code.is_authenticated:
            return Response(
                {"detail": "Code expired."},
                status=status.HTTP_410_GONE,
            )

        if not auth_code.is_authenticated:
            return Response({"status": "pending"})

        # Authenticated — return JWT tokens
        user = auth_code.authenticated_user
        refresh = RefreshToken.for_user(user)

        # Delete the used code
        auth_code.delete()

        return Response({
            "status": "authenticated",
            "tokens": {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            "user": UserOutputSerializer(user).data,
        })


class TelegramLinkCodeApi(APIView):
    """GET /api/hr/telegram/link-code/ — generate a deep link for Telegram."""

    permission_classes = [IsHRManager | IsAdmin]

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

    permission_classes = [IsHRManager | IsAdmin]

    def get(self, request):
        user = request.user
        return Response({
            "linked": bool(user.telegram_id),
            "telegram_username": user.telegram_username or None,
        })


class TelegramUnlinkApi(APIView):
    """POST /api/hr/telegram/unlink/ — disconnect Telegram account."""

    permission_classes = [IsHRManager | IsAdmin]

    def post(self, request):
        user = request.user
        user.telegram_id = None
        user.telegram_username = ""
        user.save(update_fields=["telegram_id", "telegram_username", "updated_at"])
        return Response({"detail": "Telegram account disconnected."})

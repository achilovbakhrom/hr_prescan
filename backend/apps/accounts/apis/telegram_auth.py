import hashlib
import hmac
import logging
import time

from django.conf import settings
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User
from apps.accounts.serializers import UserOutputSerializer
from apps.applications.services import bind_existing_applications
from apps.common.messages import MSG_ACCOUNT_DEACTIVATED

logger = logging.getLogger(__name__)

# Telegram auth data must be no older than 1 day
MAX_AUTH_AGE_SECONDS = 86400


class TelegramAuthApi(APIView):
    """POST /api/auth/telegram/ — authenticate with Telegram Login Widget data.

    The frontend uses the Telegram Login Widget which provides user data
    signed with HMAC-SHA-256. We verify the hash, find or create the user,
    and return JWT tokens.
    """

    permission_classes = [AllowAny]

    class InputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        first_name = serializers.CharField(required=False, default="")
        last_name = serializers.CharField(required=False, default="")
        username = serializers.CharField(required=False, default="")
        photo_url = serializers.URLField(required=False, default="")
        auth_date = serializers.IntegerField()
        hash = serializers.CharField()

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Verify the hash
        if not self._verify_telegram_hash(data):
            return Response(
                {"detail": "Invalid Telegram authentication data."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Check auth_date is recent
        if time.time() - data["auth_date"] > MAX_AUTH_AGE_SECONDS:
            return Response(
                {"detail": "Telegram authentication has expired."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        telegram_id = data["id"]
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
        username = data.get("username", "")

        # Find user by telegram_id
        user = User.objects.filter(telegram_id=telegram_id).first()

        if user is None:
            # Create new candidate user (no email — Telegram doesn't provide one)
            user = User.objects.create_user(
                email=f"tg_{telegram_id}@telegram.local",
                password=None,
                first_name=first_name,
                last_name=last_name,
                role=User.Role.CANDIDATE,
                email_verified=True,
            )
            user.telegram_id = telegram_id
            user.telegram_username = username
            user.onboarding_completed = False
            user.save(update_fields=["telegram_id", "telegram_username", "onboarding_completed", "updated_at"])
            logger.info("Created new user via Telegram auth: tg_id=%s", telegram_id)
            bind_existing_applications(user=user)
        elif not user.is_active:
            return Response(
                {"detail": str(MSG_ACCOUNT_DEACTIVATED)},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Update username if changed
        if user.telegram_username != username and username:
            user.telegram_username = username
            user.save(update_fields=["telegram_username", "updated_at"])

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                "user": UserOutputSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _verify_telegram_hash(data: dict) -> bool:
        """Verify Telegram Login data using HMAC-SHA-256.

        Algorithm from https://core.telegram.org/widgets/login#checking-authorization
        1. Sort data fields alphabetically (excluding 'hash')
        2. Build data_check_string as key=value lines joined by \\n
        3. secret_key = SHA256(bot_token)
        4. hash = HMAC-SHA-256(secret_key, data_check_string)
        5. Compare with provided hash
        """
        received_hash = data["hash"]
        check_data = {k: v for k, v in data.items() if k != "hash" and v != ""}
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(check_data.items()))

        bot_token = settings.TELEGRAM_LOGIN_WIDGET_TOKEN
        if not bot_token:
            return False
        secret_key = hashlib.sha256(bot_token.encode()).digest()
        computed_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(computed_hash, received_hash)

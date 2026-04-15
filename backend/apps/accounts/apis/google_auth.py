import logging

from django.conf import settings
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User
from apps.accounts.serializers import UserOutputSerializer
from apps.applications.services import bind_existing_applications
from apps.common.messages import (
    MSG_ACCOUNT_DEACTIVATED,
    MSG_GOOGLE_NO_EMAIL,
    MSG_INVALID_GOOGLE_TOKEN,
)

logger = logging.getLogger(__name__)


def _verify_google_credential(credential: str) -> dict | None:
    """Return the verified idinfo dict, or None if the token is invalid."""
    try:
        return id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
    except ValueError:
        return None


class GoogleAuthApi(APIView):
    """POST /api/auth/google/ — authenticate with Google ID token.

    Always returns JWT tokens + user. For first-time Google sign-ins we
    create the user with a placeholder role (candidate) and
    onboarding_completed=False — the frontend router sees that flag and
    redirects to /choose-role, where the user picks candidate or hr via
    /auth/complete-onboarding/. Social identities skip email verification
    (email_verified=True) because Google has already verified the email.
    """

    permission_classes = [AllowAny]

    class InputSerializer(serializers.Serializer):
        credential = serializers.CharField(help_text="Google ID token (JWT)")

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        credential = serializer.validated_data["credential"]

        idinfo = _verify_google_credential(credential)
        if idinfo is None:
            return Response(
                {"detail": str(MSG_INVALID_GOOGLE_TOKEN)},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        email = idinfo.get("email")
        if not email:
            return Response(
                {"detail": str(MSG_GOOGLE_NO_EMAIL)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(email=email).first()

        if user is None:
            user = User.objects.create_user(
                email=email,
                password=None,
                first_name=idinfo.get("given_name", ""),
                last_name=idinfo.get("family_name", ""),
                role=User.Role.CANDIDATE,
                email_verified=True,
            )
            user.onboarding_completed = False
            user.save(update_fields=["onboarding_completed", "updated_at"])
            logger.info("Created new user via Google auth: %s", email)
            bind_existing_applications(user=user)
        else:
            if not user.is_active:
                return Response(
                    {"detail": str(MSG_ACCOUNT_DEACTIVATED)},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            if not user.email_verified:
                user.email_verified = True
                user.save(update_fields=["email_verified", "updated_at"])

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

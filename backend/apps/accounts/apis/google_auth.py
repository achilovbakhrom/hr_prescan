import logging

from django.conf import settings
from django.db import transaction
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import Company, User
from apps.accounts.serializers import CompanyOutputSerializer, UserOutputSerializer
from apps.accounts.services import create_company_with_admin
from apps.applications.services import bind_existing_applications
from apps.common.exceptions import ApplicationError
from apps.common.messages import (
    MSG_ACCOUNT_DEACTIVATED,
    MSG_GOOGLE_NO_EMAIL,
    MSG_INVALID_GOOGLE_TOKEN,
    MSG_USER_EXISTS,
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

    Flow for new (unregistered) users:
      1. Frontend sends `credential` only.
      2. Server verifies the token, sees no user exists, responds with
         `{needs_role: true, email, first_name, last_name}` (HTTP 200, no JWT).
      3. Frontend shows a role picker (candidate / hr). User picks.
      4. If candidate: frontend re-POSTs with `credential` + `role=candidate`.
         Server creates the user and returns JWT tokens.
      5. If hr: frontend redirects to the company-creation flow, which calls
         a different endpoint with the Google credential; the HR user is
         then created together with the company.

    Existing users: `role` is ignored; normal login.
    """

    permission_classes = [AllowAny]

    class InputSerializer(serializers.Serializer):
        credential = serializers.CharField(help_text="Google ID token (JWT)")
        role = serializers.ChoiceField(
            choices=[User.Role.CANDIDATE, User.Role.HR],
            required=False,
            help_text="Role to assign on first-time registration. Omit to probe.",
        )

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        credential = serializer.validated_data["credential"]
        requested_role = serializer.validated_data.get("role")

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

        first_name = idinfo.get("given_name", "")
        last_name = idinfo.get("family_name", "")

        user = User.objects.filter(email=email).first()

        # New user — no role yet: probe response, frontend shows role picker.
        if user is None and not requested_role:
            return Response(
                {
                    "needs_role": True,
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                },
                status=status.HTTP_200_OK,
            )

        # New user picking "hr" — they must complete company creation first.
        # We don't create the HR user here; frontend routes them to the
        # company-creation form which will POST to /api/auth/google/register-company/.
        if user is None and requested_role == User.Role.HR:
            return Response(
                {
                    "needs_company": True,
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                },
                status=status.HTTP_200_OK,
            )

        # New candidate — create and return tokens.
        if user is None:
            user = User.objects.create_user(
                email=email,
                password=None,
                first_name=first_name,
                last_name=last_name,
                role=User.Role.CANDIDATE,
                email_verified=True,
            )
            logger.info("Created new candidate via Google auth: %s", email)
            bind_existing_applications(user=user)

        elif not user.is_active:
            return Response(
                {"detail": str(MSG_ACCOUNT_DEACTIVATED)},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Mark email as verified if not already
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


class GoogleCompanyRegisterApi(APIView):
    """POST /api/auth/google/register-company/

    Completes the "sign in with Google → I'm hiring" flow. Verifies the
    Google credential, creates a Company + HR admin user tied to that
    Google identity in one transaction, and returns JWT tokens.

    This mirrors CompanyRegisterApi but replaces the email+password pair
    with a Google ID token. No password is stored on the user.
    """

    permission_classes = [AllowAny]

    class InputSerializer(serializers.Serializer):
        credential = serializers.CharField(help_text="Google ID token (JWT)")
        company_name = serializers.CharField(max_length=255)
        industry = serializers.CharField(max_length=255)
        size = serializers.ChoiceField(choices=Company.Size.choices)
        country = serializers.CharField(max_length=100)
        website = serializers.URLField(max_length=500, required=False, allow_blank=True)
        description = serializers.CharField(required=False, allow_blank=True)

    @transaction.atomic
    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        credential = serializer.validated_data.pop("credential")
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

        if User.objects.filter(email=email).exists():
            return Response(
                {"detail": str(MSG_USER_EXISTS)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            company, user = create_company_with_admin(
                **serializer.validated_data,
                admin_email=email,
                admin_password=None,
                admin_first_name=idinfo.get("given_name", ""),
                admin_last_name=idinfo.get("family_name", ""),
            )
        except ApplicationError as exc:
            return Response({"detail": exc.message}, status=status.HTTP_400_BAD_REQUEST)

        # Google identity → email already verified.
        user.email_verified = True
        user.save(update_fields=["email_verified", "updated_at"])

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                "company": CompanyOutputSerializer(company).data,
                "user": UserOutputSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )

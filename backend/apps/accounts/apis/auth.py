from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.selectors import get_pending_invitations_for_email, get_user_by_email
from apps.accounts.serializers import PendingInvitationOutputSerializer, UserOutputSerializer
from apps.accounts.models import Company, User
from apps.accounts.services import (
    accept_invitation_existing_user,
    complete_company_setup,
    complete_onboarding,
    register_user,
    verify_email,
)
from apps.common.exceptions import ApplicationError
from apps.common.messages import (
    MSG_ACCOUNT_DEACTIVATED,
    MSG_EMAIL_VERIFIED,
    MSG_INVALID_CREDENTIALS,
    MSG_INVALID_TOKEN,
    MSG_INVALID_REFRESH_TOKEN,
    MSG_INVITATION_ACCEPTED_COMPANY,
    MSG_LOGOUT_SUCCESS,
    MSG_REGISTRATION_SUCCESS,
)


class RegisterApi(APIView):
    """POST /api/auth/register/ — create a candidate user."""

    permission_classes = [AllowAny]

    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField()
        password = serializers.CharField(min_length=8)
        first_name = serializers.CharField(max_length=150)
        last_name = serializers.CharField(max_length=150)

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = register_user(**serializer.validated_data)
        except ApplicationError as e:
            return Response({"detail": e.message}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"detail": str(MSG_REGISTRATION_SUCCESS), "user": UserOutputSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )


class LoginApi(APIView):
    """POST /api/auth/login/ — authenticate and return JWT tokens."""

    permission_classes = [AllowAny]

    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField()
        password = serializers.CharField()

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = get_user_by_email(email=serializer.validated_data["email"])

        if user is None or not user.check_password(serializer.validated_data["password"]):
            return Response(
                {"detail": str(MSG_INVALID_CREDENTIALS)},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {"detail": str(MSG_ACCOUNT_DEACTIVATED)},
                status=status.HTTP_401_UNAUTHORIZED,
            )

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


class LogoutApi(APIView):
    """POST /api/auth/logout/ — blacklist the refresh token."""

    permission_classes = [IsAuthenticated]

    class InputSerializer(serializers.Serializer):
        refresh = serializers.CharField()

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            token = RefreshToken(serializer.validated_data["refresh"])
            token.blacklist()
        except (TokenError, InvalidToken):
            return Response(
                {"detail": str(MSG_INVALID_TOKEN)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"detail": str(MSG_LOGOUT_SUCCESS)}, status=status.HTTP_200_OK)


class TokenRefreshApi(APIView):
    """POST /api/auth/token/refresh/ — refresh the access token."""

    permission_classes = [AllowAny]

    class InputSerializer(serializers.Serializer):
        refresh = serializers.CharField()

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            refresh = RefreshToken(serializer.validated_data["refresh"])
        except (TokenError, InvalidToken):
            return Response(
                {"detail": str(MSG_INVALID_REFRESH_TOKEN)},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )


class VerifyEmailApi(APIView):
    """POST /api/auth/verify-email/ — verify email with token."""

    permission_classes = [AllowAny]

    class InputSerializer(serializers.Serializer):
        token = serializers.CharField()

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            verify_email(token=serializer.validated_data["token"])
        except ApplicationError as e:
            return Response({"detail": e.message}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": str(MSG_EMAIL_VERIFIED)}, status=status.HTTP_200_OK)


class MeApi(APIView):
    """GET /api/auth/me/ — get current user profile."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        user = get_user_by_email(email=request.user.email)
        return Response(UserOutputSerializer(user).data, status=status.HTTP_200_OK)


class MyInvitationsApi(APIView):
    """GET /api/auth/my-invitations/ — list pending invitations for the current user."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        invitations = get_pending_invitations_for_email(email=request.user.email)
        return Response(
            PendingInvitationOutputSerializer(invitations, many=True).data,
            status=status.HTTP_200_OK,
        )


class AcceptCompanyInvitationApi(APIView):
    """POST /api/auth/accept-company-invitation/ — accept invitation and switch company."""

    permission_classes = [IsAuthenticated]

    class InputSerializer(serializers.Serializer):
        token = serializers.UUIDField()

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = accept_invitation_existing_user(
                user=request.user,
                token=serializer.validated_data["token"],
            )
        except ApplicationError as e:
            return Response(
                {"detail": e.message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "detail": str(MSG_INVITATION_ACCEPTED_COMPANY),
                "user": UserOutputSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class CompleteCompanySetupApi(APIView):
    """POST /api/auth/complete-company-setup/ — upgrade social auth user to company admin."""

    permission_classes = [IsAuthenticated]

    class InputSerializer(serializers.Serializer):
        company_name = serializers.CharField(max_length=255)
        industries = serializers.ListField(
            child=serializers.SlugField(max_length=50),
            required=False, default=list,
        )
        size = serializers.ChoiceField(choices=Company.Size.choices)
        country = serializers.CharField(max_length=2)
        email = serializers.EmailField(required=False)

    def post(self, request: Request) -> Response:
        if request.user.role != User.Role.CANDIDATE or request.user.company is not None:
            return Response(
                {"detail": "Only candidates without a company can use this."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Require email if user has synthetic telegram email
        if request.user.email.endswith("@telegram.local") and not data.get("email"):
            return Response(
                {"detail": "Email is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            company = complete_company_setup(user=request.user, **data)
        except ApplicationError as e:
            return Response({"detail": e.message}, status=status.HTTP_400_BAD_REQUEST)

        request.user.refresh_from_db()
        refresh = RefreshToken.for_user(request.user)

        return Response(
            {
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                "user": UserOutputSerializer(request.user).data,
            },
        )


class CompleteOnboardingApi(APIView):
    """POST /api/auth/complete-onboarding/ — mark onboarding as done (stay as candidate)."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        complete_onboarding(user=request.user)
        return Response({"user": UserOutputSerializer(request.user).data})

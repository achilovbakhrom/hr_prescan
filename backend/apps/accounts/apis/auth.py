from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.selectors import get_pending_invitations_for_email, get_user_by_email
from apps.accounts.serializers import PendingInvitationOutputSerializer, UserOutputSerializer
from apps.accounts.services import accept_invitation_existing_user, register_user, verify_email
from apps.common.exceptions import ApplicationError


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

        user = register_user(**serializer.validated_data)

        return Response(
            {"detail": "Registration successful. Please verify your email.", "user": UserOutputSerializer(user).data},
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
                {"detail": "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {"detail": "Account is deactivated."},
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
                {"detail": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"detail": "Logout successful."}, status=status.HTTP_200_OK)


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
                {"detail": "Invalid or expired refresh token."},
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

        return Response({"detail": "Email verified successfully."}, status=status.HTTP_200_OK)


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
                "detail": "Invitation accepted. You are now part of the company.",
                "user": UserOutputSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )

from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.selectors import get_pending_invitations_for_email, get_user_by_email
from apps.accounts.serializers import PendingInvitationOutputSerializer, UserOutputSerializer
from apps.common.messages import (
    MSG_ACCOUNT_DEACTIVATED,
    MSG_INVALID_CREDENTIALS,
    MSG_INVALID_REFRESH_TOKEN,
    MSG_INVALID_TOKEN,
    MSG_LOGOUT_SUCCESS,
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
        except TokenError, InvalidToken:
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
        except TokenError, InvalidToken:
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

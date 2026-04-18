from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.serializers import UserOutputSerializer
from apps.accounts.services import register_user, verify_email
from apps.common.exceptions import ApplicationError
from apps.common.messages import MSG_EMAIL_VERIFIED, MSG_REGISTRATION_SUCCESS


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

from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import Company, User
from apps.accounts.serializers import UserOutputSerializer
from apps.accounts.services import (
    accept_invitation_existing_user,
    complete_company_setup,
    complete_onboarding,
)
from apps.common.exceptions import ApplicationError
from apps.common.messages import MSG_INVITATION_ACCEPTED_COMPANY


class CheckInvitationApi(APIView):
    """GET /api/auth/check-invitation/?token=... — check if invitation is for existing user."""

    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        token = request.query_params.get("token")
        if not token:
            return Response({"detail": "Token is required."}, status=status.HTTP_400_BAD_REQUEST)

        from apps.accounts.models import Invitation

        try:
            invitation = Invitation.objects.select_related("company").get(token=token)
        except Invitation.DoesNotExist, ValueError:
            return Response({"detail": "Invalid invitation."}, status=status.HTTP_404_NOT_FOUND)

        if invitation.is_accepted:
            return Response({"detail": "Invitation already accepted."}, status=status.HTTP_400_BAD_REQUEST)

        if invitation.is_expired:
            return Response({"detail": "Invitation expired."}, status=status.HTTP_400_BAD_REQUEST)

        existing_user = User.objects.filter(email=invitation.email).exists()

        return Response(
            {
                "email": invitation.email,
                "company_name": invitation.company.name,
                "existing_user": existing_user,
            }
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
            required=False,
            default=list,
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
            company = complete_company_setup(user=request.user, **data)  # noqa: F841
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
    """POST /api/auth/complete-onboarding/ — choose role and complete onboarding."""

    permission_classes = [IsAuthenticated]

    class InputSerializer(serializers.Serializer):
        role = serializers.ChoiceField(choices=["candidate", "hr"])

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        complete_onboarding(user=request.user, role=serializer.validated_data["role"])
        request.user.refresh_from_db()
        refresh = RefreshToken.for_user(request.user)

        return Response(
            {
                "tokens": {"access": str(refresh.access_token), "refresh": str(refresh)},
                "user": UserOutputSerializer(request.user).data,
            }
        )

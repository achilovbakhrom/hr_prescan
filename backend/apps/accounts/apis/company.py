from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdmin, IsHRManager
from apps.accounts.selectors import get_company_invitations, get_company_users, get_user_by_id
from apps.accounts.serializers import (
    AcceptInvitationInputSerializer,
    CompanyOutputSerializer,
    CompanyProfileInputSerializer,
    CompanyRegisterInputSerializer,
    InvitationOutputSerializer,
    InviteHRInputSerializer,
    TeamMemberUpdateSerializer,
    UserOutputSerializer,
)
from apps.accounts.services import (
    accept_invitation,
    activate_user,
    create_company_with_admin,
    deactivate_user,
    invite_hr,
    update_company_profile,
)


class CompanyRegisterApi(APIView):
    """POST /api/auth/company-register/ — create company + admin user."""

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = CompanyRegisterInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        company, user = create_company_with_admin(**serializer.validated_data)

        return Response(
            {
                "detail": "Company registered successfully. Please verify your email.",
                "company": CompanyOutputSerializer(company).data,
                "user": UserOutputSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class CompanyProfileApi(APIView):
    """
    GET  /api/hr/company/profile/ — get company profile
    PUT  /api/hr/company/profile/ — update company profile
    """

    permission_classes = [IsHRManager | IsAdmin]

    def get(self, request: Request) -> Response:
        company = request.user.company
        if company is None:
            return Response(
                {"detail": "You are not associated with a company."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(CompanyOutputSerializer(company).data, status=status.HTTP_200_OK)

    def put(self, request: Request) -> Response:
        company = request.user.company
        if company is None:
            return Response(
                {"detail": "You are not associated with a company."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CompanyProfileInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        company = update_company_profile(company=company, data=serializer.validated_data)

        return Response(CompanyOutputSerializer(company).data, status=status.HTTP_200_OK)


class InviteHRApi(APIView):
    """POST /api/hr/company/invite/ — invite an HR manager."""

    permission_classes = [IsAdmin]

    def post(self, request: Request) -> Response:
        serializer = InviteHRInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        invitation = invite_hr(
            company=request.user.company,
            email=serializer.validated_data["email"],
            invited_by=request.user,
        )

        return Response(
            {
                "detail": "Invitation sent successfully.",
                "invitation": InvitationOutputSerializer(invitation).data,
            },
            status=status.HTTP_201_CREATED,
        )

    def get(self, request: Request) -> Response:
        """List all invitations for the company."""
        invitations = get_company_invitations(company=request.user.company)
        return Response(
            InvitationOutputSerializer(invitations, many=True).data,
            status=status.HTTP_200_OK,
        )


class AcceptInvitationApi(APIView):
    """POST /api/auth/accept-invitation/ — accept an HR invitation."""

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = AcceptInvitationInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = accept_invitation(**serializer.validated_data)

        return Response(
            {
                "detail": "Invitation accepted. You can now log in.",
                "user": UserOutputSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class TeamListApi(APIView):
    """GET /api/hr/company/team/ — list team members."""

    permission_classes = [IsAdmin]

    def get(self, request: Request) -> Response:
        company = request.user.company
        if company is None:
            return Response(
                {"detail": "You are not associated with a company."},
                status=status.HTTP_404_NOT_FOUND,
            )

        users = get_company_users(company=company)
        return Response(
            UserOutputSerializer(users, many=True).data,
            status=status.HTTP_200_OK,
        )


class TeamMemberDetailApi(APIView):
    """PATCH /api/hr/company/team/<user_id>/ — activate/deactivate a team member."""

    permission_classes = [IsAdmin]

    def patch(self, request: Request, user_id: str) -> Response:
        serializer = TeamMemberUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        target_user = get_user_by_id(user_id=user_id)
        if target_user is None:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if serializer.validated_data["is_active"]:
            target_user = activate_user(user=target_user, activated_by=request.user)
        else:
            target_user = deactivate_user(user=target_user, deactivated_by=request.user)

        return Response(UserOutputSerializer(target_user).data, status=status.HTTP_200_OK)

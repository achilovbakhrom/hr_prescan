from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import CompanyMembership
from apps.accounts.permissions import HasHRPermission, HRPermissions, IsAdmin, IsHRManager
from apps.common.exceptions import ApplicationError
from apps.common.messages import (
    MSG_COMPANY_REGISTERED,
    MSG_INVITATION_ACCEPTED,
    MSG_INVITATION_SENT,
    MSG_NOT_IN_COMPANY,
    MSG_USER_NOT_FOUND,
)
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
    switch_company,
    update_company_profile,
)


class CompanyRegisterApi(APIView):
    """POST /api/auth/company-register/ — create company + admin user."""

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = CompanyRegisterInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            company, user = create_company_with_admin(**serializer.validated_data)
        except ApplicationError as e:
            return Response({"detail": e.message}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "detail": str(MSG_COMPANY_REGISTERED),
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

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_SETTINGS

    def get(self, request: Request) -> Response:
        company = request.user.company
        if company is None:
            return Response(
                {"detail": str(MSG_NOT_IN_COMPANY)},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(CompanyOutputSerializer(company).data, status=status.HTTP_200_OK)

    def put(self, request: Request) -> Response:
        company = request.user.company
        if company is None:
            return Response(
                {"detail": str(MSG_NOT_IN_COMPANY)},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CompanyProfileInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        company = update_company_profile(company=company, data=serializer.validated_data)

        return Response(CompanyOutputSerializer(company).data, status=status.HTTP_200_OK)


class InviteHRApi(APIView):
    """POST /api/hr/company/invite/ — invite an HR manager."""

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_TEAM

    def post(self, request: Request) -> Response:
        serializer = InviteHRInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            invitation = invite_hr(
                company=request.user.company,
                email=serializer.validated_data["email"],
                invited_by=request.user,
                permissions=serializer.validated_data.get("permissions", []),
            )
        except ApplicationError as e:
            return Response({"detail": e.message}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "detail": str(MSG_INVITATION_SENT),
                "invitation": InvitationOutputSerializer(invitation).data,
            },
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request: Request) -> Response:
        """DELETE /api/hr/company/invite/ — cancel a pending invitation."""
        invitation_id = request.data.get("invitation_id")
        if not invitation_id:
            return Response(
                {"detail": "invitation_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        from apps.accounts.models import Invitation
        try:
            invitation = Invitation.objects.get(
                id=invitation_id,
                company=request.user.company,
                is_accepted=False,
            )
        except Invitation.DoesNotExist:
            return Response(
                {"detail": "Invitation not found or already accepted."},
                status=status.HTTP_404_NOT_FOUND,
            )
        invitation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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

        try:
            user = accept_invitation(**serializer.validated_data)
        except ApplicationError as e:
            return Response({"detail": e.message}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "detail": str(MSG_INVITATION_ACCEPTED),
                "user": UserOutputSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class TeamListApi(APIView):
    """GET /api/hr/company/team/ — list team members."""

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_TEAM

    def get(self, request: Request) -> Response:
        company = request.user.company
        if company is None:
            return Response(
                {"detail": str(MSG_NOT_IN_COMPANY)},
                status=status.HTTP_404_NOT_FOUND,
            )

        users = get_company_users(company=company)
        return Response(
            UserOutputSerializer(users, many=True).data,
            status=status.HTTP_200_OK,
        )


class TeamMemberDetailApi(APIView):
    """PATCH /api/hr/company/team/<user_id>/ — update team member (status, permissions)."""

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_TEAM

    def patch(self, request: Request, user_id: str) -> Response:
        serializer = TeamMemberUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        target_user = get_user_by_id(user_id=user_id)
        if target_user is None:
            return Response(
                {"detail": str(MSG_USER_NOT_FOUND)},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            if "is_active" in serializer.validated_data:
                if serializer.validated_data["is_active"]:
                    target_user = activate_user(user=target_user, activated_by=request.user)
                else:
                    target_user = deactivate_user(user=target_user, deactivated_by=request.user)

            if "hr_permissions" in serializer.validated_data:
                target_user.hr_permissions = serializer.validated_data["hr_permissions"]
                target_user.save(update_fields=["hr_permissions", "updated_at"])
        except ApplicationError as e:
            return Response({"detail": e.message}, status=status.HTTP_400_BAD_REQUEST)

        return Response(UserOutputSerializer(target_user).data, status=status.HTTP_200_OK)


class MyCompaniesApi(APIView):
    """GET /api/auth/my-companies/ — list companies the user belongs to."""

    permission_classes = [IsAuthenticated]

    class OutputSerializer(serializers.ModelSerializer):
        company = CompanyOutputSerializer(read_only=True)

        class Meta:
            model = CompanyMembership
            fields = ["company", "role", "hr_permissions", "created_at"]
            read_only_fields = fields

    def get(self, request: Request) -> Response:
        memberships = (
            CompanyMembership.objects
            .filter(user=request.user)
            .select_related("company")
        )
        return Response(
            self.OutputSerializer(memberships, many=True).data,
            status=status.HTTP_200_OK,
        )


class SwitchCompanyApi(APIView):
    """POST /api/auth/switch-company/ — switch active company."""

    permission_classes = [IsAuthenticated]

    class InputSerializer(serializers.Serializer):
        company_id = serializers.UUIDField()

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = switch_company(
                user=request.user,
                company_id=serializer.validated_data["company_id"],
            )
        except ApplicationError as e:
            return Response({"detail": e.message}, status=status.HTTP_400_BAD_REQUEST)

        return Response(UserOutputSerializer(user).data, status=status.HTTP_200_OK)

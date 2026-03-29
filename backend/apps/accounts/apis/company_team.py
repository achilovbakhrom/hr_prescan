from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import HasHRPermission, HRPermissions
from apps.accounts.selectors import get_company_users, get_user_by_id
from apps.accounts.serializers import (
    TeamMemberUpdateSerializer,
    UserOutputSerializer,
)
from apps.accounts.services import (
    activate_user,
    deactivate_user,
    switch_company,
    switch_to_personal,
)
from apps.common.exceptions import ApplicationError
from apps.common.messages import MSG_NOT_IN_COMPANY, MSG_USER_NOT_FOUND


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


class SwitchToPersonalApi(APIView):
    """POST /api/auth/switch-personal/ — switch back to personal/candidate context."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        user = switch_to_personal(user=request.user)
        return Response(UserOutputSerializer(user).data, status=status.HTTP_200_OK)

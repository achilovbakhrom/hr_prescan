from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import HasHRPermission, HRPermissions
from apps.applications.models import Application
from apps.applications.selectors import get_company_applications_filtered
from apps.applications.serializers import ApplicationListOutputSerializer
from apps.common.messages import MSG_NOT_IN_COMPANY


class HRAllCandidatesListApi(APIView):
    """GET /api/hr/candidates/ — list applications across all vacancies of the company."""

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_CANDIDATES

    class FilterSerializer(serializers.Serializer):
        status = serializers.ChoiceField(
            choices=Application.Status.choices, required=False,
        )
        vacancy_id = serializers.UUIDField(required=False)
        ordering = serializers.ChoiceField(
            choices=[
                ("-created_at", "Newest first"),
                ("created_at", "Oldest first"),
                ("-match_score", "Highest match"),
                ("match_score", "Lowest match"),
                ("-candidate_name", "Name Z-A"),
                ("candidate_name", "Name A-Z"),
            ],
            required=False,
            default="-created_at",
        )
        min_score = serializers.DecimalField(
            max_digits=5, decimal_places=2, required=False,
        )
        max_score = serializers.DecimalField(
            max_digits=5, decimal_places=2, required=False,
        )
        search = serializers.CharField(required=False)

    def get(self, request: Request) -> Response:
        company = request.user.company
        if company is None:
            return Response(
                {"detail": str(MSG_NOT_IN_COMPANY)},
                status=status.HTTP_404_NOT_FOUND,
            )

        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        data = filter_serializer.validated_data

        applications = get_company_applications_filtered(
            company=company,
            status=data.get("status"),
            vacancy_id=data.get("vacancy_id"),
            ordering=data.get("ordering", "-created_at"),
            min_score=data.get("min_score"),
            max_score=data.get("max_score"),
            search=data.get("search"),
        )

        return Response(
            ApplicationListOutputSerializer(applications, many=True).data,
            status=status.HTTP_200_OK,
        )

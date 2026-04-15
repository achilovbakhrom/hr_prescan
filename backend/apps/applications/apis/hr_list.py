from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import HasHRPermission, HRPermissions
from apps.applications.models import Application
from apps.applications.selectors import (
    get_application_by_id,
    get_vacancy_applications_filtered,
)
from apps.applications.serializers import (
    ApplicationDetailOutputSerializer,
    ApplicationListOutputSerializer,
)
from apps.applications.services import generate_cv_download_url
from apps.common.messages import (
    MSG_APPLICATION_NOT_FOUND,
    MSG_NO_CV_UPLOADED,
    MSG_NOT_IN_COMPANY,
    MSG_VACANCY_NOT_FOUND,
)
from apps.vacancies.selectors import get_vacancy_by_id


class HRApplicationListApi(APIView):
    """GET /api/hr/vacancies/{vacancy_id}/candidates/ — list applications for a vacancy."""

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_CANDIDATES

    class FilterSerializer(serializers.Serializer):
        status = serializers.ChoiceField(
            choices=Application.Status.choices, required=False,
        )
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

    def get(self, request: Request, vacancy_id: str) -> Response:
        company = request.user.company
        if company is None:
            return Response(
                {"detail": str(MSG_NOT_IN_COMPANY)},
                status=status.HTTP_404_NOT_FOUND,
            )

        vacancy = get_vacancy_by_id(vacancy_id=vacancy_id, company=company)
        if vacancy is None:
            return Response(
                {"detail": str(MSG_VACANCY_NOT_FOUND)},
                status=status.HTTP_404_NOT_FOUND,
            )

        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        data = filter_serializer.validated_data

        applications = get_vacancy_applications_filtered(
            vacancy=vacancy,
            status=data.get("status"),
            ordering=data.get("ordering", "-created_at"),
            min_score=data.get("min_score"),
            max_score=data.get("max_score"),
            search=data.get("search"),
        )

        return Response(
            ApplicationListOutputSerializer(applications, many=True).data,
            status=status.HTTP_200_OK,
        )


class HRApplicationDetailApi(APIView):
    """GET /api/hr/candidates/{id}/ — application detail for HR."""

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_CANDIDATES

    def get(self, request: Request, application_id: str) -> Response:
        company = request.user.company
        if company is None:
            return Response(
                {"detail": str(MSG_NOT_IN_COMPANY)},
                status=status.HTTP_404_NOT_FOUND,
            )

        application = get_application_by_id(
            application_id=application_id, company=company,
        )
        if application is None:
            return Response(
                {"detail": str(MSG_APPLICATION_NOT_FOUND)},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            ApplicationDetailOutputSerializer(application).data,
            status=status.HTTP_200_OK,
        )


class HRCvDownloadApi(APIView):
    """GET /api/hr/candidates/{id}/cv-download/ — get presigned URL for CV download."""

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_CANDIDATES

    def get(self, request: Request, application_id: str) -> Response:
        company = request.user.company
        if company is None:
            return Response(
                {"detail": str(MSG_NOT_IN_COMPANY)},
                status=status.HTTP_404_NOT_FOUND,
            )

        application = get_application_by_id(
            application_id=application_id, company=company,
        )
        if application is None:
            return Response(
                {"detail": str(MSG_APPLICATION_NOT_FOUND)},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not application.cv_file:
            return Response(
                {"detail": str(MSG_NO_CV_UPLOADED)},
                status=status.HTTP_404_NOT_FOUND,
            )

        url = generate_cv_download_url(cv_file_path=application.cv_file)
        return Response(
            {"url": url, "filename": application.cv_original_filename},
            status=status.HTTP_200_OK,
        )

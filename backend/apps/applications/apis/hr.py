from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdmin, IsHRManager
from apps.applications.models import Application
from apps.applications.selectors import (
    get_application_by_id,
    get_vacancy_applications_filtered,
)
from apps.applications.serializers import (
    ApplicationDetailOutputSerializer,
    ApplicationListOutputSerializer,
)
from apps.applications.services import (
    add_hr_note,
    bulk_move_by_filter,
    bulk_update_status,
    generate_cv_download_url,
    soft_delete_applications,
    update_application_status,
)
from apps.common.exceptions import ApplicationError
from apps.common.messages import (
    MSG_APPLICATION_NOT_FOUND,
    MSG_NO_CV_UPLOADED,
    MSG_NOT_IN_COMPANY,
    MSG_VACANCY_NOT_FOUND,
)
from apps.vacancies.selectors import get_vacancy_by_id


class HRApplicationListApi(APIView):
    """GET /api/hr/vacancies/{vacancy_id}/candidates/ — list applications for a vacancy."""

    permission_classes = [IsHRManager | IsAdmin]

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

    permission_classes = [IsHRManager | IsAdmin]

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


class HRApplicationStatusApi(APIView):
    """PATCH /api/hr/candidates/{id}/status/ — update application status."""

    permission_classes = [IsHRManager | IsAdmin]

    class InputSerializer(serializers.Serializer):
        status = serializers.ChoiceField(choices=Application.Status.choices)

    def patch(self, request: Request, application_id: str) -> Response:
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

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            application = update_application_status(
                application=application,
                status=serializer.validated_data["status"],
                updated_by=request.user,
            )
        except ApplicationError as e:
            return Response(
                {"detail": e.message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            ApplicationDetailOutputSerializer(application).data,
            status=status.HTTP_200_OK,
        )


class HRApplicationNotesApi(APIView):
    """POST /api/hr/candidates/{id}/notes/ — add HR note to application."""

    permission_classes = [IsHRManager | IsAdmin]

    class InputSerializer(serializers.Serializer):
        note = serializers.CharField()

    def post(self, request: Request, application_id: str) -> Response:
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

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        application = add_hr_note(
            application=application,
            note=serializer.validated_data["note"],
        )

        return Response(
            ApplicationDetailOutputSerializer(application).data,
            status=status.HTTP_200_OK,
        )


class HRCvDownloadApi(APIView):
    """GET /api/hr/candidates/{id}/cv-download/ — get presigned URL for CV download."""

    permission_classes = [IsHRManager | IsAdmin]

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


class HRBulkStatusApi(APIView):
    """PATCH /api/hr/candidates/bulk-status — bulk update status by IDs."""

    permission_classes = [IsHRManager | IsAdmin]

    class InputSerializer(serializers.Serializer):
        application_ids = serializers.ListField(child=serializers.UUIDField())
        status = serializers.ChoiceField(choices=Application.Status.choices)

    def patch(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        count = bulk_update_status(
            application_ids=serializer.validated_data["application_ids"],
            status=serializer.validated_data["status"],
            updated_by=request.user,
        )
        return Response({"updated": count}, status=status.HTTP_200_OK)


class HRBatchMoveApi(APIView):
    """POST /api/hr/vacancies/{vacancy_id}/candidates/batch-move — filtered batch move."""

    permission_classes = [IsHRManager | IsAdmin]

    class InputSerializer(serializers.Serializer):
        from_status = serializers.ChoiceField(choices=Application.Status.choices)
        to_status = serializers.ChoiceField(choices=Application.Status.choices)
        max_score = serializers.FloatField(required=False)
        min_score = serializers.FloatField(required=False)
        score_field = serializers.ChoiceField(
            choices=["match_score", "prescanning_score", "interview_score"],
            default="match_score",
            required=False,
        )
        has_cv = serializers.BooleanField(required=False, allow_null=True)
        days_since_applied = serializers.IntegerField(required=False, min_value=1)

    def post(self, request: Request, vacancy_id: str) -> Response:
        vacancy = get_vacancy_by_id(vacancy_id=vacancy_id, company=request.user.company)
        if vacancy is None:
            return Response({"detail": str(MSG_VACANCY_NOT_FOUND)}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            count = bulk_move_by_filter(
                vacancy_id=vacancy.id,
                from_status=data["from_status"],
                to_status=data["to_status"],
                updated_by=request.user,
                max_score=data.get("max_score"),
                min_score=data.get("min_score"),
                score_field=data.get("score_field", "match_score"),
                has_cv=data.get("has_cv"),
                days_since_applied=data.get("days_since_applied"),
            )
        except ApplicationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"moved": count}, status=status.HTTP_200_OK)


class HRSoftDeleteApi(APIView):
    """POST /api/hr/candidates/soft-delete — soft delete archived candidates."""

    permission_classes = [IsHRManager | IsAdmin]

    class InputSerializer(serializers.Serializer):
        application_ids = serializers.ListField(child=serializers.UUIDField())

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        count = soft_delete_applications(
            application_ids=serializer.validated_data["application_ids"],
            updated_by=request.user,
        )
        return Response({"deleted": count}, status=status.HTTP_200_OK)

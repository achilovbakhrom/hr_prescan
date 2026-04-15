from rest_framework import serializers, status
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import HasHRPermission, HRPermissions
from apps.common.exceptions import ApplicationError
from apps.common.messages import (
    MSG_FILE_TOO_LARGE,
    MSG_NO_FILE_UPLOADED,
    MSG_NOT_IN_COMPANY,
    MSG_UNSUPPORTED_FILE_TYPE,
)
from apps.vacancies.serializers import EmployerCompanyOutputSerializer
from apps.vacancies.services import (
    create_employer_from_file,
    create_employer_from_url,
)


class ParseEmployerFileApi(APIView):
    """POST /api/hr/employers/parse-file/ — create employer from uploaded file."""

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_VACANCIES
    parser_classes = [MultiPartParser]

    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=255)

    def post(self, request: Request) -> Response:
        company = request.user.company
        if company is None:
            return Response(
                {"detail": str(MSG_NOT_IN_COMPANY)},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response(
                {"detail": str(MSG_NO_FILE_UPLOADED)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        allowed_extensions = {"pdf", "docx", "doc", "txt"}
        ext = file_obj.name.rsplit(".", 1)[-1].lower() if "." in file_obj.name else ""
        if ext not in allowed_extensions:
            return Response(
                {"detail": str(MSG_UNSUPPORTED_FILE_TYPE)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if file_obj.size > 10 * 1024 * 1024:  # 10MB limit
            return Response(
                {"detail": str(MSG_FILE_TOO_LARGE)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            employer = create_employer_from_file(
                company=company,
                name=serializer.validated_data["name"],
                file_obj=file_obj,
            )
        except ApplicationError as e:
            return Response({"detail": e.message}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            EmployerCompanyOutputSerializer(employer).data,
            status=status.HTTP_201_CREATED,
        )


class ParseEmployerUrlApi(APIView):
    """POST /api/hr/employers/parse-url/ — create employer from website URL."""

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_VACANCIES

    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=255)
        url = serializers.URLField()

    def post(self, request: Request) -> Response:
        company = request.user.company
        if company is None:
            return Response(
                {"detail": str(MSG_NOT_IN_COMPANY)},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            employer = create_employer_from_url(
                company=company,
                name=serializer.validated_data["name"],
                url=serializer.validated_data["url"],
            )
        except ApplicationError as e:
            return Response({"detail": e.message}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            EmployerCompanyOutputSerializer(employer).data,
            status=status.HTTP_201_CREATED,
        )

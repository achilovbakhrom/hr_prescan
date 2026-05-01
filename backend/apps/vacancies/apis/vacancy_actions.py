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
    MSG_UNSUPPORTED_FILE_TYPE,
    MSG_VACANCY_NOT_FOUND,
)
from apps.vacancies.selectors import get_user_vacancy_by_id
from apps.vacancies.serializers import VacancyDetailOutputSerializer
from apps.vacancies.services import (
    archive_vacancy,
    parse_company_info_from_file,
    parse_company_info_from_url,
    pause_vacancy,
    publish_vacancy,
)


class VacancyStatusApi(APIView):
    """PATCH /api/hr/vacancies/{id}/status/ — change vacancy status."""

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_VACANCIES

    class InputSerializer(serializers.Serializer):
        action = serializers.ChoiceField(choices=["publish", "pause", "archive"])

    def patch(self, request: Request, vacancy_id: str) -> Response:
        vacancy = get_user_vacancy_by_id(vacancy_id=vacancy_id, user=request.user)
        if vacancy is None:
            return Response({"detail": str(MSG_VACANCY_NOT_FOUND)}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action = serializer.validated_data["action"]
        action_map = {
            "publish": publish_vacancy,
            "pause": pause_vacancy,
            "archive": archive_vacancy,
        }

        try:
            vacancy = action_map[action](vacancy=vacancy)
        except ApplicationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(VacancyDetailOutputSerializer(vacancy).data, status=status.HTTP_200_OK)


class ParseCompanyFileApi(APIView):
    """POST /api/hr/vacancies/parse-company-file/ — extract company info from uploaded file."""

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_VACANCIES
    parser_classes = [MultiPartParser]

    def post(self, request: Request) -> Response:
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
            company_info = parse_company_info_from_file(file_obj=file_obj)
        except ApplicationError as e:
            return Response({"detail": e.message}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"company_info": company_info}, status=status.HTTP_200_OK)


class ParseCompanyUrlApi(APIView):
    """POST /api/hr/vacancies/parse-company-url/ — extract company info from a website URL."""

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_VACANCIES

    class InputSerializer(serializers.Serializer):
        url = serializers.URLField()

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            company_info = parse_company_info_from_url(url=serializer.validated_data["url"])
        except ApplicationError as e:
            return Response({"detail": e.message}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"company_info": company_info}, status=status.HTTP_200_OK)


class VacancyRegenerateKeywordsApi(APIView):
    """POST /api/hr/vacancies/{id}/regenerate-keywords/ — regenerate AI search keywords."""

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_VACANCIES

    def post(self, request: Request, vacancy_id: str) -> Response:
        vacancy = get_user_vacancy_by_id(vacancy_id=vacancy_id, user=request.user)
        if vacancy is None:
            return Response({"detail": str(MSG_VACANCY_NOT_FOUND)}, status=status.HTTP_404_NOT_FOUND)

        from apps.vacancies.tasks import generate_keywords_task

        generate_keywords_task.delay(str(vacancy.id))

        return Response({"detail": "Keyword regeneration started."}, status=status.HTTP_202_ACCEPTED)

from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import HasHRPermission, HRPermissions
from apps.common.exceptions import ApplicationError
from apps.job_parser.models import ParsedVacancy
from apps.job_parser.selectors import get_user_parsed_vacancies, get_user_parsed_vacancy_by_id, get_user_source_by_id
from apps.job_parser.serializers import ParsedVacancyOutputSerializer, TelegramMessageInputSerializer
from apps.job_parser.services import import_parsed_vacancy, parse_telegram_job_message
from apps.vacancies.serializers import VacancyDetailOutputSerializer


class ParsedVacancyListApi(APIView):
    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_VACANCIES

    class FilterSerializer(serializers.Serializer):
        status = serializers.ChoiceField(choices=ParsedVacancy.Status.choices, required=False)
        source_id = serializers.UUIDField(required=False)

    def get(self, request: Request) -> Response:
        serializer = self.FilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        vacancies = get_user_parsed_vacancies(
            user=request.user,
            status=serializer.validated_data.get("status"),
            source_id=serializer.validated_data.get("source_id"),
        )
        return Response(ParsedVacancyOutputSerializer(vacancies, many=True).data)


class ParsedVacancyImportApi(APIView):
    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_VACANCIES

    def post(self, request: Request, vacancy_id) -> Response:
        parsed_vacancy = get_user_parsed_vacancy_by_id(user=request.user, vacancy_id=vacancy_id)
        if parsed_vacancy is None:
            return Response({"detail": "Parsed vacancy not found."}, status=status.HTTP_404_NOT_FOUND)
        try:
            vacancy = import_parsed_vacancy(parsed_vacancy=parsed_vacancy, created_by=request.user)
        except ApplicationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(VacancyDetailOutputSerializer(vacancy).data, status=status.HTTP_201_CREATED)


class TelegramMessageParseApi(APIView):
    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_VACANCIES

    def post(self, request: Request, source_id) -> Response:
        source = get_user_source_by_id(user=request.user, source_id=source_id)
        if source is None:
            return Response({"detail": "Source not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = TelegramMessageInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            vacancy = parse_telegram_job_message(source=source, **serializer.validated_data)
        except ApplicationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(ParsedVacancyOutputSerializer(vacancy).data, status=status.HTTP_201_CREATED)

from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import HasHRPermission, HRPermissions
from apps.common.exceptions import ApplicationError
from apps.common.messages import MSG_VACANCY_NOT_FOUND
from apps.vacancies.models import Vacancy
from apps.vacancies.selectors import get_user_vacancy_by_id
from apps.vacancies.serializers import VacancyDetailOutputSerializer
from apps.vacancies.services import (
    soft_delete_vacancy,
    update_vacancy,
)


class VacancyDetailApi(APIView):
    """
    GET    /api/hr/vacancies/{id}/ — vacancy detail with criteria + questions
    PUT    /api/hr/vacancies/{id}/ — update vacancy
    DELETE /api/hr/vacancies/{id}/ — soft-delete an archived vacancy

    Scoped to vacancies under any of the user's (non-deleted) companies.
    """

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_VACANCIES

    class InputSerializer(serializers.Serializer):
        title = serializers.CharField(max_length=255, required=False)
        description = serializers.CharField(required=False)
        requirements = serializers.CharField(required=False, allow_blank=True)
        responsibilities = serializers.CharField(required=False, allow_blank=True)
        skills = serializers.ListField(child=serializers.CharField(), required=False)
        salary_min = serializers.DecimalField(
            max_digits=12,
            decimal_places=2,
            required=False,
            allow_null=True,
        )
        salary_max = serializers.DecimalField(
            max_digits=12,
            decimal_places=2,
            required=False,
            allow_null=True,
        )
        salary_currency = serializers.CharField(max_length=3, required=False)
        location = serializers.CharField(max_length=255, required=False, allow_blank=True)
        is_remote = serializers.BooleanField(required=False)
        employment_type = serializers.ChoiceField(
            choices=Vacancy.EmploymentType.choices,
            required=False,
        )
        experience_level = serializers.ChoiceField(
            choices=Vacancy.ExperienceLevel.choices,
            required=False,
        )
        deadline = serializers.DateField(required=False, allow_null=True)
        visibility = serializers.ChoiceField(choices=Vacancy.Visibility.choices, required=False)
        interview_mode = serializers.ChoiceField(
            choices=Vacancy.InterviewMode.choices,
            required=False,
        )
        interview_enabled = serializers.BooleanField(required=False)
        cv_required = serializers.BooleanField(required=False)
        interview_duration = serializers.IntegerField(required=False)
        company_info = serializers.CharField(required=False, allow_blank=True)
        prescanning_prompt = serializers.CharField(required=False, allow_blank=True)
        interview_prompt = serializers.CharField(required=False, allow_blank=True)
        prescanning_language = serializers.ChoiceField(
            choices=[("en", "English"), ("ru", "Russian"), ("uz", "Uzbek")],
            required=False,
        )

    def get(self, request: Request, vacancy_id: str) -> Response:
        vacancy = get_user_vacancy_by_id(vacancy_id=vacancy_id, user=request.user)
        if vacancy is None:
            return Response({"detail": str(MSG_VACANCY_NOT_FOUND)}, status=status.HTTP_404_NOT_FOUND)
        return Response(VacancyDetailOutputSerializer(vacancy).data, status=status.HTTP_200_OK)

    def put(self, request: Request, vacancy_id: str) -> Response:
        vacancy = get_user_vacancy_by_id(vacancy_id=vacancy_id, user=request.user)
        if vacancy is None:
            return Response({"detail": str(MSG_VACANCY_NOT_FOUND)}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        vacancy = update_vacancy(vacancy=vacancy, data=serializer.validated_data)
        return Response(VacancyDetailOutputSerializer(vacancy).data, status=status.HTTP_200_OK)

    def delete(self, request: Request, vacancy_id: str) -> Response:
        vacancy = get_user_vacancy_by_id(vacancy_id=vacancy_id, user=request.user)
        if vacancy is None:
            return Response({"detail": str(MSG_VACANCY_NOT_FOUND)}, status=status.HTTP_404_NOT_FOUND)
        try:
            soft_delete_vacancy(vacancy=vacancy)
        except ApplicationError as e:
            return Response({"detail": e.message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

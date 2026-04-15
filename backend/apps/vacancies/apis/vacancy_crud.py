from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import HasHRPermission, HRPermissions
from apps.common.messages import (
    MSG_EMPLOYER_NOT_FOUND,
    MSG_NOT_IN_COMPANY,
)
from apps.vacancies.models import Vacancy
from apps.vacancies.selectors import get_company_vacancies, get_employer_by_id
from apps.vacancies.serializers import VacancyDetailOutputSerializer, VacancyListOutputSerializer
from apps.vacancies.services import create_vacancy


class VacancyListCreateApi(APIView):
    """
    GET  /api/hr/vacancies/ — list company vacancies
    POST /api/hr/vacancies/ — create a vacancy
    """

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_VACANCIES

    class InputSerializer(serializers.Serializer):
        title = serializers.CharField(max_length=255)
        description = serializers.CharField()
        requirements = serializers.CharField(required=False, allow_blank=True, default="")
        responsibilities = serializers.CharField(required=False, allow_blank=True, default="")
        skills = serializers.ListField(child=serializers.CharField(), required=False, default=list)
        salary_min = serializers.DecimalField(
            max_digits=12, decimal_places=2, required=False, allow_null=True,
        )
        salary_max = serializers.DecimalField(
            max_digits=12, decimal_places=2, required=False, allow_null=True,
        )
        salary_currency = serializers.CharField(max_length=3, required=False, default="USD")
        location = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
        is_remote = serializers.BooleanField(required=False, default=False)
        employment_type = serializers.ChoiceField(
            choices=Vacancy.EmploymentType.choices,
            required=False,
            default=Vacancy.EmploymentType.FULL_TIME,
        )
        experience_level = serializers.ChoiceField(
            choices=Vacancy.ExperienceLevel.choices,
            required=False,
            default=Vacancy.ExperienceLevel.MIDDLE,
        )
        deadline = serializers.DateField(required=False, allow_null=True)
        visibility = serializers.ChoiceField(
            choices=Vacancy.Visibility.choices,
            required=False,
            default=Vacancy.Visibility.PUBLIC,
        )
        interview_mode = serializers.ChoiceField(
            choices=Vacancy.InterviewMode.choices,
            required=False,
            default=Vacancy.InterviewMode.CHAT,
        )
        interview_enabled = serializers.BooleanField(required=False, default=False)
        cv_required = serializers.BooleanField(required=False, default=False)
        interview_duration = serializers.IntegerField(required=False, default=30)
        company_info = serializers.CharField(required=False, allow_blank=True, default="")
        prescanning_prompt = serializers.CharField(required=False, allow_blank=True, default="")
        interview_prompt = serializers.CharField(required=False, allow_blank=True, default="")
        prescanning_language = serializers.ChoiceField(
            choices=[("en", "English"), ("ru", "Russian"), ("uz", "Uzbek")],
            required=False,
            default="en",
        )
        employer_id = serializers.UUIDField(required=False, allow_null=True)

    class FilterSerializer(serializers.Serializer):
        status = serializers.ChoiceField(choices=Vacancy.Status.choices, required=False)

    def get(self, request: Request) -> Response:
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        company = request.user.company
        if company is None:
            return Response(
                {"detail": str(MSG_NOT_IN_COMPANY)},
                status=status.HTTP_404_NOT_FOUND,
            )

        vacancies = get_company_vacancies(
            company=company,
            status=filter_serializer.validated_data.get("status"),
        )
        return Response(
            VacancyListOutputSerializer(vacancies, many=True).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        company = request.user.company
        if company is None:
            return Response(
                {"detail": str(MSG_NOT_IN_COMPANY)},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = serializer.validated_data
        employer_id = data.pop("employer_id", None)

        # Validate employer belongs to the same company
        employer = None
        if employer_id is not None:
            employer = get_employer_by_id(employer_id=employer_id, company=company)
            if employer is None:
                return Response(
                    {"detail": str(MSG_EMPLOYER_NOT_FOUND)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        vacancy = create_vacancy(
            company=company,
            created_by=request.user,
            employer=employer,
            **data,
        )

        return Response(
            VacancyDetailOutputSerializer(vacancy).data,
            status=status.HTTP_201_CREATED,
        )

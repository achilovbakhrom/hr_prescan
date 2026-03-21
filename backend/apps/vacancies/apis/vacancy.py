from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdmin, IsHRManager
from apps.common.exceptions import ApplicationError
from apps.vacancies.models import Vacancy
from apps.vacancies.selectors import get_company_vacancies, get_vacancy_by_id
from apps.vacancies.serializers import VacancyDetailOutputSerializer, VacancyListOutputSerializer
from apps.vacancies.services import (
    close_vacancy,
    create_vacancy,
    pause_vacancy,
    publish_vacancy,
    update_vacancy,
)


class VacancyListCreateApi(APIView):
    """
    GET  /api/hr/vacancies/ — list company vacancies
    POST /api/hr/vacancies/ — create a vacancy
    """

    permission_classes = [IsHRManager | IsAdmin]

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
        screening_mode = serializers.ChoiceField(
            choices=Vacancy.ScreeningMode.choices,
            required=False,
            default=Vacancy.ScreeningMode.CHAT,
        )
        cv_required = serializers.BooleanField(required=False, default=False)
        interview_duration = serializers.IntegerField(required=False, default=30)
        company_info = serializers.CharField(required=False, allow_blank=True, default="")

    class FilterSerializer(serializers.Serializer):
        status = serializers.ChoiceField(choices=Vacancy.Status.choices, required=False)

    def get(self, request: Request) -> Response:
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        company = request.user.company
        if company is None:
            return Response(
                {"detail": "You are not associated with a company."},
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
                {"detail": "You are not associated with a company."},
                status=status.HTTP_404_NOT_FOUND,
            )

        vacancy = create_vacancy(
            company=company,
            created_by=request.user,
            **serializer.validated_data,
        )

        return Response(
            VacancyDetailOutputSerializer(vacancy).data,
            status=status.HTTP_201_CREATED,
        )


class VacancyDetailApi(APIView):
    """
    GET /api/hr/vacancies/{id}/ — vacancy detail with criteria + questions
    PUT /api/hr/vacancies/{id}/ — update vacancy
    """

    permission_classes = [IsHRManager | IsAdmin]

    class InputSerializer(serializers.Serializer):
        title = serializers.CharField(max_length=255, required=False)
        description = serializers.CharField(required=False)
        requirements = serializers.CharField(required=False, allow_blank=True)
        responsibilities = serializers.CharField(required=False, allow_blank=True)
        skills = serializers.ListField(child=serializers.CharField(), required=False)
        salary_min = serializers.DecimalField(
            max_digits=12, decimal_places=2, required=False, allow_null=True,
        )
        salary_max = serializers.DecimalField(
            max_digits=12, decimal_places=2, required=False, allow_null=True,
        )
        salary_currency = serializers.CharField(max_length=3, required=False)
        location = serializers.CharField(max_length=255, required=False, allow_blank=True)
        is_remote = serializers.BooleanField(required=False)
        employment_type = serializers.ChoiceField(
            choices=Vacancy.EmploymentType.choices, required=False,
        )
        experience_level = serializers.ChoiceField(
            choices=Vacancy.ExperienceLevel.choices, required=False,
        )
        deadline = serializers.DateField(required=False, allow_null=True)
        visibility = serializers.ChoiceField(choices=Vacancy.Visibility.choices, required=False)
        screening_mode = serializers.ChoiceField(
            choices=Vacancy.ScreeningMode.choices, required=False,
        )
        cv_required = serializers.BooleanField(required=False)
        interview_duration = serializers.IntegerField(required=False)
        company_info = serializers.CharField(required=False, allow_blank=True)

    def get(self, request: Request, vacancy_id: str) -> Response:
        vacancy = get_vacancy_by_id(vacancy_id=vacancy_id, company=request.user.company)
        if vacancy is None:
            return Response({"detail": "Vacancy not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(VacancyDetailOutputSerializer(vacancy).data, status=status.HTTP_200_OK)

    def put(self, request: Request, vacancy_id: str) -> Response:
        vacancy = get_vacancy_by_id(vacancy_id=vacancy_id, company=request.user.company)
        if vacancy is None:
            return Response({"detail": "Vacancy not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        vacancy = update_vacancy(vacancy=vacancy, data=serializer.validated_data)
        return Response(VacancyDetailOutputSerializer(vacancy).data, status=status.HTTP_200_OK)


class VacancyStatusApi(APIView):
    """PATCH /api/hr/vacancies/{id}/status/ — change vacancy status."""

    permission_classes = [IsHRManager | IsAdmin]

    class InputSerializer(serializers.Serializer):
        action = serializers.ChoiceField(choices=["publish", "pause", "close"])

    def patch(self, request: Request, vacancy_id: str) -> Response:
        vacancy = get_vacancy_by_id(vacancy_id=vacancy_id, company=request.user.company)
        if vacancy is None:
            return Response({"detail": "Vacancy not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action = serializer.validated_data["action"]
        action_map = {
            "publish": publish_vacancy,
            "pause": pause_vacancy,
            "close": close_vacancy,
        }

        try:
            vacancy = action_map[action](vacancy=vacancy)
        except ApplicationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(VacancyDetailOutputSerializer(vacancy).data, status=status.HTTP_200_OK)

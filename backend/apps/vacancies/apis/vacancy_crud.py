from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import CompanyMembership
from apps.accounts.permissions import HasHRPermission, HRPermissions
from apps.common.messages import MSG_NOT_IN_COMPANY
from apps.vacancies.models import Vacancy
from apps.vacancies.selectors import get_user_vacancies
from apps.vacancies.serializers import VacancyDetailOutputSerializer, VacancyListOutputSerializer
from apps.vacancies.services import create_vacancy

MSG_COMPANY_NOT_FOUND_OR_NOT_MEMBER = "Company not found or you are not a member."


class VacancyListCreateApi(APIView):
    """
    GET  /api/hr/vacancies/ — list vacancies across the user's non-deleted companies
    POST /api/hr/vacancies/ — create a vacancy under a chosen company (defaults to user's default)
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
        # Optional; falls back to the user's default company.
        company_id = serializers.UUIDField(required=False, allow_null=True)

    class FilterSerializer(serializers.Serializer):
        status = serializers.ChoiceField(choices=Vacancy.Status.choices, required=False)

    def get(self, request: Request) -> Response:
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        vacancies = get_user_vacancies(
            user=request.user,
            status=filter_serializer.validated_data.get("status"),
        )
        return Response(
            VacancyListOutputSerializer(vacancies, many=True).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        company_id = data.pop("company_id", None)
        if company_id is not None:
            membership = (
                CompanyMembership.objects.filter(
                    user=request.user,
                    company_id=company_id,
                    company__is_deleted=False,
                )
                .select_related("company")
                .first()
            )
            if membership is None:
                return Response(
                    {"detail": MSG_COMPANY_NOT_FOUND_OR_NOT_MEMBER},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            company = membership.company
        else:
            default_membership = (
                CompanyMembership.objects.filter(
                    user=request.user,
                    is_default=True,
                    company__is_deleted=False,
                )
                .select_related("company")
                .first()
            )
            if default_membership is None:
                return Response(
                    {"detail": str(MSG_NOT_IN_COMPANY)},
                    status=status.HTTP_404_NOT_FOUND,
                )
            company = default_membership.company

        vacancy = create_vacancy(
            company=company,
            created_by=request.user,
            **data,
        )

        return Response(
            VacancyDetailOutputSerializer(vacancy).data,
            status=status.HTTP_201_CREATED,
        )

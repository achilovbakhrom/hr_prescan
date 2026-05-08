from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import HasHRPermission, HRPermissions
from apps.common.exceptions import ApplicationError
from apps.vacancies.models import Vacancy
from apps.vacancies.services import generate_vacancy_content


class GenerateVacancyContentApi(APIView):
    """Generate draft vacancy description, requirements, and responsibilities."""

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_VACANCIES

    class InputSerializer(serializers.Serializer):
        title = serializers.CharField(max_length=255, min_length=5)
        employment_type = serializers.ChoiceField(
            choices=Vacancy.EmploymentType.choices,
            required=False,
            allow_blank=True,
        )
        experience_level = serializers.ChoiceField(
            choices=Vacancy.ExperienceLevel.choices,
            required=False,
            allow_blank=True,
        )
        skills = serializers.ListField(child=serializers.CharField(), required=False, default=list)
        salary_min = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
        salary_max = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
        salary_currency = serializers.CharField(max_length=3, required=False, default="USD")
        location = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
        is_remote = serializers.BooleanField(required=False, allow_null=True)

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            content = generate_vacancy_content(
                language=getattr(request.user, "language", "en") or "en",
                **serializer.validated_data,
            )
        except ApplicationError as exc:
            return Response({"detail": exc.message}, status=status.HTTP_502_BAD_GATEWAY)

        return Response(content, status=status.HTTP_200_OK)

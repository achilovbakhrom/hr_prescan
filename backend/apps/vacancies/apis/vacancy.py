from rest_framework import serializers, status
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdmin, IsHRManager
from apps.common.exceptions import ApplicationError
from apps.common.messages import (
    MSG_EMPLOYER_NOT_FOUND,
    MSG_FILE_TOO_LARGE,
    MSG_NO_FILE_UPLOADED,
    MSG_NOT_IN_COMPANY,
    MSG_UNSUPPORTED_FILE_TYPE,
    MSG_VACANCY_NOT_FOUND,
)
from apps.vacancies.models import Vacancy
from apps.vacancies.selectors import get_company_vacancies, get_employer_by_id, get_vacancy_by_id
from apps.vacancies.serializers import VacancyDetailOutputSerializer, VacancyListOutputSerializer
from apps.vacancies.services import (
    archive_vacancy,
    create_vacancy,
    parse_company_info_from_file,
    parse_company_info_from_url,
    pause_vacancy,
    publish_vacancy,
    soft_delete_vacancy,
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


class VacancyDetailApi(APIView):
    """
    GET    /api/hr/vacancies/{id}/ — vacancy detail with criteria + questions
    PUT    /api/hr/vacancies/{id}/ — update vacancy
    DELETE /api/hr/vacancies/{id}/ — soft-delete an archived vacancy
    """

    permission_classes = [IsHRManager | IsAdmin]

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
        employer_id = serializers.UUIDField(required=False, allow_null=True)

    def get(self, request: Request, vacancy_id: str) -> Response:
        vacancy = get_vacancy_by_id(vacancy_id=vacancy_id, company=request.user.company)
        if vacancy is None:
            return Response({"detail": str(MSG_VACANCY_NOT_FOUND)}, status=status.HTTP_404_NOT_FOUND)

        return Response(VacancyDetailOutputSerializer(vacancy).data, status=status.HTTP_200_OK)

    def put(self, request: Request, vacancy_id: str) -> Response:
        vacancy = get_vacancy_by_id(vacancy_id=vacancy_id, company=request.user.company)
        if vacancy is None:
            return Response({"detail": str(MSG_VACANCY_NOT_FOUND)}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        # Handle employer_id separately — validate and set on vacancy directly
        if "employer_id" in data:
            employer_id = data.pop("employer_id")
            if employer_id is None:
                vacancy.employer = None
                vacancy.save(update_fields=["employer", "updated_at"])
            else:
                employer = get_employer_by_id(employer_id=employer_id, company=request.user.company)
                if employer is None:
                    return Response(
                        {"detail": str(MSG_EMPLOYER_NOT_FOUND)},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                vacancy.employer = employer
                vacancy.save(update_fields=["employer", "updated_at"])

        vacancy = update_vacancy(vacancy=vacancy, data=data)
        return Response(VacancyDetailOutputSerializer(vacancy).data, status=status.HTTP_200_OK)

    def delete(self, request: Request, vacancy_id: str) -> Response:
        vacancy = get_vacancy_by_id(vacancy_id=vacancy_id, company=request.user.company)
        if vacancy is None:
            return Response({"detail": str(MSG_VACANCY_NOT_FOUND)}, status=status.HTTP_404_NOT_FOUND)
        try:
            soft_delete_vacancy(vacancy=vacancy)
        except ApplicationError as e:
            return Response({"detail": e.message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class VacancyStatusApi(APIView):
    """PATCH /api/hr/vacancies/{id}/status/ — change vacancy status."""

    permission_classes = [IsHRManager | IsAdmin]

    class InputSerializer(serializers.Serializer):
        action = serializers.ChoiceField(choices=["publish", "pause", "archive"])

    def patch(self, request: Request, vacancy_id: str) -> Response:
        vacancy = get_vacancy_by_id(vacancy_id=vacancy_id, company=request.user.company)
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

    permission_classes = [IsHRManager | IsAdmin]
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

    permission_classes = [IsHRManager | IsAdmin]

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

    permission_classes = [IsHRManager | IsAdmin]

    def post(self, request: Request, vacancy_id: str) -> Response:
        vacancy = get_vacancy_by_id(vacancy_id=vacancy_id, company=request.user.company)
        if vacancy is None:
            return Response({"detail": str(MSG_VACANCY_NOT_FOUND)}, status=status.HTTP_404_NOT_FOUND)

        from apps.vacancies.tasks import generate_keywords_task

        generate_keywords_task.delay(str(vacancy.id))

        return Response({"detail": "Keyword regeneration started."}, status=status.HTTP_202_ACCEPTED)

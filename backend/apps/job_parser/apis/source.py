from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import CompanyMembership
from apps.accounts.permissions import HasHRPermission, HRPermissions
from apps.common.exceptions import ApplicationError
from apps.job_parser.models import ParsedVacancySource
from apps.job_parser.selectors import get_user_source_by_id, get_user_sources
from apps.job_parser.serializers import ParsedVacancySourceInputSerializer, ParsedVacancySourceOutputSerializer
from apps.job_parser.services import sync_hh_source
from apps.job_parser.tasks import sync_parsed_vacancy_source_task

MSG_COMPANY_NOT_FOUND_OR_NOT_MEMBER = "Company not found or you are not a member."


class ParsedVacancySourceListCreateApi(APIView):
    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_VACANCIES

    class FilterSerializer(serializers.Serializer):
        source_type = serializers.ChoiceField(choices=ParsedVacancySource.Type.choices, required=False)

    def get(self, request: Request) -> Response:
        serializer = self.FilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        sources = get_user_sources(
            user=request.user,
            source_type=serializer.validated_data.get("source_type"),
        )
        return Response(ParsedVacancySourceOutputSerializer(sources, many=True).data)

    def post(self, request: Request) -> Response:
        serializer = ParsedVacancySourceInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        company = _resolve_company(user=request.user, company_id=data.pop("company_id", None))
        if company is None:
            return Response({"detail": MSG_COMPANY_NOT_FOUND_OR_NOT_MEMBER}, status=status.HTTP_400_BAD_REQUEST)
        source = ParsedVacancySource.objects.create(company=company, created_by=request.user, **data)
        return Response(ParsedVacancySourceOutputSerializer(source).data, status=status.HTTP_201_CREATED)


class ParsedVacancySourceSyncApi(APIView):
    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_VACANCIES

    def post(self, request: Request, source_id) -> Response:
        source = get_user_source_by_id(user=request.user, source_id=source_id)
        if source is None:
            return Response({"detail": "Source not found."}, status=status.HTTP_404_NOT_FOUND)
        if request.query_params.get("async") == "1":
            sync_parsed_vacancy_source_task.delay(str(source.id))
            return Response({"detail": "Sync scheduled."}, status=status.HTTP_202_ACCEPTED)
        try:
            result = sync_hh_source(source=source)
        except ApplicationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(result, status=status.HTTP_200_OK)


def _resolve_company(*, user, company_id):
    filters = {"user": user, "company__is_deleted": False}
    if company_id is not None:
        filters["company_id"] = company_id
    else:
        filters["is_default"] = True
    membership = CompanyMembership.objects.filter(**filters).select_related("company").first()
    return membership.company if membership else None

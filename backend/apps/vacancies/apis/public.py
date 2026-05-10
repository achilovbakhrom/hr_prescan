from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.utils.urls import remove_query_param, replace_query_param
from rest_framework.views import APIView

from apps.common.messages import MSG_VACANCY_NOT_FOUND
from apps.common.pagination import StandardPagination
from apps.job_parser.selectors import (
    get_public_parsed_vacancies,
    get_public_parsed_vacancy_by_id,
    get_public_reachable_parsed_vacancies,
)
from apps.job_parser.serializers_public import (
    PublicParsedVacancyDetailOutputSerializer,
    PublicParsedVacancyListOutputSerializer,
)
from apps.job_parser.services.contact_detection import parsed_vacancy_is_publicly_usable
from apps.vacancies.selectors import get_public_vacancies, get_vacancy_by_id, get_vacancy_by_share_token
from apps.vacancies.serializers import PublicVacancyDetailOutputSerializer, PublicVacancyListOutputSerializer

LEGACY_PUBLIC_LIST_LIMIT = 100


class PublicVacancyListApi(APIView):
    """GET /api/public/vacancies/ — public job board."""

    permission_classes = [AllowAny]

    class FilterSerializer(serializers.Serializer):
        search = serializers.CharField(required=False)
        location = serializers.CharField(required=False)
        is_remote = serializers.BooleanField(required=False, default=None, allow_null=True)
        employment_type = serializers.CharField(required=False)
        experience_level = serializers.CharField(required=False)
        salary_min = serializers.IntegerField(required=False)
        salary_max = serializers.IntegerField(required=False)
        page = serializers.IntegerField(required=False, min_value=1)
        page_size = serializers.IntegerField(required=False, min_value=1, max_value=100)

    def get(self, request: Request) -> Response:
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        filters = filter_serializer.validated_data
        pagination_requested = "page" in request.query_params or "page_size" in request.query_params
        filters.pop("page", None)
        filters.pop("page_size", None)
        vacancies = get_public_vacancies(**filters)
        if pagination_requested:
            return _get_paginated_public_vacancies(request=request, filters=filters, vacancies=vacancies)

        internal_qs = vacancies.order_by("-created_at")[:LEGACY_PUBLIC_LIST_LIMIT]
        items = _with_apply_flag(PublicVacancyListOutputSerializer(internal_qs, many=True).data, can_apply=True)

        if filters.get("is_remote") is not True and filters.get("experience_level") in (None, "middle"):
            parsed_vacancies = _get_filtered_public_parsed_vacancies(filters=filters).order_by("-created_at")[
                :LEGACY_PUBLIC_LIST_LIMIT
            ]
            items.extend(PublicParsedVacancyListOutputSerializer(parsed_vacancies, many=True).data)

        return Response(items, status=status.HTTP_200_OK)


class PublicVacancyDetailApi(APIView):
    """
    GET /api/public/vacancies/{id}/ — public vacancy detail
    GET /api/public/vacancies/share/{token}/ — vacancy via share link
    """

    permission_classes = [AllowAny]

    def get(self, request: Request, vacancy_id: str | None = None, share_token: str | None = None) -> Response:
        parsed_vacancy = None
        if share_token:
            vacancy = get_vacancy_by_share_token(share_token=share_token)
        else:
            vacancy = get_vacancy_by_id(vacancy_id=vacancy_id)
            if vacancy is None:
                parsed_vacancy = get_public_parsed_vacancy_by_id(vacancy_id=vacancy_id)
                if parsed_vacancy is not None and not parsed_vacancy_is_publicly_usable(parsed_vacancy):
                    parsed_vacancy = None

        if vacancy is None and parsed_vacancy is None:
            return Response({"detail": str(MSG_VACANCY_NOT_FOUND)}, status=status.HTTP_404_NOT_FOUND)

        # For non-share-token access, only show published + public vacancies
        if not share_token and vacancy is not None:
            from apps.vacancies.models import Vacancy

            if vacancy.status != Vacancy.Status.PUBLISHED or vacancy.visibility != Vacancy.Visibility.PUBLIC:
                return Response({"detail": str(MSG_VACANCY_NOT_FOUND)}, status=status.HTTP_404_NOT_FOUND)

        if parsed_vacancy is not None:
            return Response(
                PublicParsedVacancyDetailOutputSerializer(parsed_vacancy).data,
                status=status.HTTP_200_OK,
            )
        return Response(
            _with_apply_flag(PublicVacancyDetailOutputSerializer(vacancy).data, can_apply=True),
            status=status.HTTP_200_OK,
        )


def _with_apply_flag(data, *, can_apply: bool):
    if isinstance(data, list):
        return [_with_apply_flag(item, can_apply=can_apply) for item in data]
    data["can_apply"] = can_apply
    data["content_source"] = "internal"
    return data


def _get_paginated_public_vacancies(*, request: Request, filters: dict, vacancies) -> Response:
    internal_qs = vacancies.order_by("-created_at")
    parsed_qs = _get_filtered_public_parsed_vacancies(filters=filters).order_by("-created_at")
    internal_count = internal_qs.count()

    paginator = StandardPagination()
    page_size = paginator.get_page_size(request) or paginator.page_size
    page_number = int(request.query_params.get(paginator.page_query_param, 1))
    start = (page_number - 1) * page_size
    end = start + page_size

    internal_items = []
    if start < internal_count:
        internal_items = list(internal_qs[start : min(end, internal_count)])

    remaining = page_size - len(internal_items)
    parsed_items = []
    has_next = end < internal_count
    if remaining > 0:
        parsed_start = max(start - internal_count, 0)
        parsed_page = list(parsed_qs[parsed_start : parsed_start + remaining + 1])
        parsed_items = parsed_page[:remaining]
        has_next = len(parsed_page) > remaining
    elif end == internal_count:
        has_next = parsed_qs.exists()

    serialized_items = []
    for item in [*internal_items, *parsed_items]:
        if item.__class__.__name__ == "Vacancy":
            serialized_items.append(
                _with_apply_flag(PublicVacancyListOutputSerializer(item).data, can_apply=True),
            )
        else:
            serialized_items.append(PublicParsedVacancyListOutputSerializer(item).data)

    loaded_count = start + len(serialized_items)
    count = loaded_count + 1 if has_next else loaded_count
    return Response(
        {
            "count": count,
            "next": _page_url(request=request, page_number=page_number + 1) if has_next else None,
            "previous": _page_url(request=request, page_number=page_number - 1) if page_number > 1 else None,
            "results": serialized_items,
        },
        status=status.HTTP_200_OK,
    )


def _page_url(*, request: Request, page_number: int) -> str:
    url = request.build_absolute_uri()
    if page_number <= 1:
        return remove_query_param(url, StandardPagination.page_query_param)
    return replace_query_param(url, StandardPagination.page_query_param, page_number)


def _get_filtered_public_parsed_vacancies(*, filters: dict):
    if filters.get("is_remote") is True or filters.get("experience_level") not in (None, "middle"):
        return get_public_parsed_vacancies().none()
    return get_public_reachable_parsed_vacancies(
        search=filters.get("search"),
        location=filters.get("location"),
        employment_type=filters.get("employment_type"),
        salary_min=filters.get("salary_min"),
        salary_max=filters.get("salary_max"),
    )

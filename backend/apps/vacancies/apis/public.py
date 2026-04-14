from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.messages import MSG_VACANCY_NOT_FOUND
from apps.vacancies.selectors import get_public_vacancies, get_vacancy_by_id, get_vacancy_by_share_token
from apps.vacancies.serializers import PublicVacancyDetailOutputSerializer, PublicVacancyListOutputSerializer


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

    def get(self, request: Request) -> Response:
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)

        vacancies = get_public_vacancies(**filter_serializer.validated_data)
        return Response(
            PublicVacancyListOutputSerializer(vacancies, many=True).data,
            status=status.HTTP_200_OK,
        )


class PublicVacancyDetailApi(APIView):
    """
    GET /api/public/vacancies/{id}/ — public vacancy detail
    GET /api/public/vacancies/share/{token}/ — vacancy via share link
    """

    permission_classes = [AllowAny]

    def get(self, request: Request, vacancy_id: str | None = None, share_token: str | None = None) -> Response:
        if share_token:
            vacancy = get_vacancy_by_share_token(share_token=share_token)
        else:
            vacancy = get_vacancy_by_id(vacancy_id=vacancy_id)

        if vacancy is None:
            return Response({"detail": str(MSG_VACANCY_NOT_FOUND)}, status=status.HTTP_404_NOT_FOUND)

        # For non-share-token access, only show published + public vacancies
        if not share_token:
            from apps.vacancies.models import Vacancy

            if vacancy.status != Vacancy.Status.PUBLISHED or vacancy.visibility != Vacancy.Visibility.PUBLIC:
                return Response({"detail": str(MSG_VACANCY_NOT_FOUND)}, status=status.HTTP_404_NOT_FOUND)

        return Response(
            PublicVacancyDetailOutputSerializer(vacancy).data,
            status=status.HTTP_200_OK,
        )

from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import HasHRPermission, HRPermissions
from apps.common.exceptions import ApplicationError
from apps.common.messages import MSG_CRITERIA_NOT_FOUND, MSG_VACANCY_NOT_FOUND
from apps.vacancies.models import ScreeningStep
from apps.vacancies.selectors import get_vacancy_by_id, get_vacancy_criteria
from apps.vacancies.serializers import VacancyCriteriaOutputSerializer
from apps.vacancies.services import (
    add_vacancy_criteria,
    delete_vacancy_criteria,
    update_vacancy_criteria,
)


class VacancyCriteriaListCreateApi(APIView):
    """
    GET  /api/hr/vacancies/{id}/criteria/?step=prescanning — list criteria
    POST /api/hr/vacancies/{id}/criteria/ — add criteria
    """

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_VACANCIES

    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=255)
        description = serializers.CharField(required=False, allow_blank=True, default="")
        weight = serializers.IntegerField(required=False, default=1, min_value=1, max_value=5)
        step = serializers.ChoiceField(
            choices=ScreeningStep.choices,
            required=False,
            default=ScreeningStep.PRESCANNING,
        )

    def get(self, request: Request, vacancy_id: str) -> Response:
        vacancy = get_vacancy_by_id(vacancy_id=vacancy_id, company=request.user.company)
        if vacancy is None:
            return Response({"detail": str(MSG_VACANCY_NOT_FOUND)}, status=status.HTTP_404_NOT_FOUND)

        step = request.query_params.get("step")
        criteria = get_vacancy_criteria(vacancy=vacancy, step=step)
        return Response(
            VacancyCriteriaOutputSerializer(criteria, many=True).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request: Request, vacancy_id: str) -> Response:
        vacancy = get_vacancy_by_id(vacancy_id=vacancy_id, company=request.user.company)
        if vacancy is None:
            return Response({"detail": str(MSG_VACANCY_NOT_FOUND)}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        criteria = add_vacancy_criteria(vacancy=vacancy, **serializer.validated_data)
        return Response(
            VacancyCriteriaOutputSerializer(criteria).data,
            status=status.HTTP_201_CREATED,
        )


class VacancyCriteriaDetailApi(APIView):
    """
    PUT    /api/hr/vacancies/{id}/criteria/{criteria_id}/ — update
    DELETE /api/hr/vacancies/{id}/criteria/{criteria_id}/ — delete
    """

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_VACANCIES

    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=255, required=False)
        description = serializers.CharField(required=False, allow_blank=True)
        weight = serializers.IntegerField(required=False, min_value=1, max_value=5)
        order = serializers.IntegerField(required=False)

    def put(self, request: Request, vacancy_id: str, criteria_id: str) -> Response:
        vacancy = get_vacancy_by_id(vacancy_id=vacancy_id, company=request.user.company)
        if vacancy is None:
            return Response({"detail": str(MSG_VACANCY_NOT_FOUND)}, status=status.HTTP_404_NOT_FOUND)

        criteria = vacancy.criteria.filter(id=criteria_id).first()
        if criteria is None:
            return Response({"detail": str(MSG_CRITERIA_NOT_FOUND)}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        criteria = update_vacancy_criteria(criteria=criteria, **serializer.validated_data)
        return Response(
            VacancyCriteriaOutputSerializer(criteria).data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request: Request, vacancy_id: str, criteria_id: str) -> Response:
        vacancy = get_vacancy_by_id(vacancy_id=vacancy_id, company=request.user.company)
        if vacancy is None:
            return Response({"detail": str(MSG_VACANCY_NOT_FOUND)}, status=status.HTTP_404_NOT_FOUND)

        criteria = vacancy.criteria.filter(id=criteria_id).first()
        if criteria is None:
            return Response({"detail": str(MSG_CRITERIA_NOT_FOUND)}, status=status.HTTP_404_NOT_FOUND)

        try:
            delete_vacancy_criteria(criteria=criteria)
        except ApplicationError as e:
            return Response({"detail": e.message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

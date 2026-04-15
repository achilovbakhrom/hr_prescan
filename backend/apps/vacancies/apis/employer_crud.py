from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import HasHRPermission, HRPermissions
from apps.common.exceptions import ApplicationError
from apps.common.messages import (
    MSG_EMPLOYER_NOT_FOUND,
    MSG_NOT_IN_COMPANY,
)
from apps.vacancies.selectors import get_company_employers, get_employer_by_id
from apps.vacancies.serializers import EmployerCompanyOutputSerializer
from apps.vacancies.services import (
    create_employer,
    delete_employer,
    update_employer,
)


class EmployerCompanyListCreateApi(APIView):
    """
    GET  /api/hr/employers/ — list employer companies for the tenant
    POST /api/hr/employers/ — create an employer company (manual)
    """

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_VACANCIES

    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=255)
        industry = serializers.CharField(required=False, allow_blank=True, default="")
        website = serializers.URLField(required=False, allow_blank=True, default="")
        description = serializers.CharField(required=False, allow_blank=True, default="")

    def get(self, request: Request) -> Response:
        company = request.user.company
        if company is None:
            return Response(
                {"detail": str(MSG_NOT_IN_COMPANY)},
                status=status.HTTP_404_NOT_FOUND,
            )

        employers = get_company_employers(company=company)
        return Response(
            EmployerCompanyOutputSerializer(employers, many=True).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request: Request) -> Response:
        company = request.user.company
        if company is None:
            return Response(
                {"detail": str(MSG_NOT_IN_COMPANY)},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        employer = create_employer(company=company, **serializer.validated_data)
        return Response(
            EmployerCompanyOutputSerializer(employer).data,
            status=status.HTTP_201_CREATED,
        )


class EmployerCompanyDetailApi(APIView):
    """
    GET    /api/hr/employers/{id}/ — employer detail
    PUT    /api/hr/employers/{id}/ — update employer
    DELETE /api/hr/employers/{id}/ — delete employer (only if no linked vacancies)
    """

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_VACANCIES

    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=255, required=False)
        industry = serializers.CharField(required=False, allow_blank=True)
        logo = serializers.URLField(required=False, allow_blank=True)
        website = serializers.URLField(required=False, allow_blank=True)
        description = serializers.CharField(required=False, allow_blank=True)

    def get(self, request: Request, employer_id: str) -> Response:
        company = request.user.company
        if company is None:
            return Response(
                {"detail": str(MSG_NOT_IN_COMPANY)},
                status=status.HTTP_404_NOT_FOUND,
            )

        employer = get_employer_by_id(employer_id=employer_id, company=company)
        if employer is None:
            return Response(
                {"detail": str(MSG_EMPLOYER_NOT_FOUND)},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            EmployerCompanyOutputSerializer(employer).data,
            status=status.HTTP_200_OK,
        )

    def put(self, request: Request, employer_id: str) -> Response:
        company = request.user.company
        if company is None:
            return Response(
                {"detail": str(MSG_NOT_IN_COMPANY)},
                status=status.HTTP_404_NOT_FOUND,
            )

        employer = get_employer_by_id(employer_id=employer_id, company=company)
        if employer is None:
            return Response(
                {"detail": str(MSG_EMPLOYER_NOT_FOUND)},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        employer = update_employer(employer=employer, data=serializer.validated_data)
        return Response(
            EmployerCompanyOutputSerializer(employer).data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request: Request, employer_id: str) -> Response:
        company = request.user.company
        if company is None:
            return Response(
                {"detail": str(MSG_NOT_IN_COMPANY)},
                status=status.HTTP_404_NOT_FOUND,
            )

        employer = get_employer_by_id(employer_id=employer_id, company=company)
        if employer is None:
            return Response(
                {"detail": str(MSG_EMPLOYER_NOT_FOUND)},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            delete_employer(employer=employer)
        except ApplicationError as e:
            return Response({"detail": e.message}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)

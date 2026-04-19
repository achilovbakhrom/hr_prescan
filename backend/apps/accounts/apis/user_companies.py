from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import Company, CompanyMembership
from apps.accounts.serializers import CompanyOutputSerializer
from apps.accounts.services import (
    create_user_company,
    set_default_company,
    soft_delete_company,
    update_user_company,
)
from apps.common.exceptions import ApplicationError


class UserCompanyListOutputSerializer(serializers.Serializer):
    id = serializers.UUIDField(source="company.id")
    name = serializers.CharField(source="company.name")
    industries = serializers.SlugRelatedField(
        source="company.industries",
        many=True,
        read_only=True,
        slug_field="slug",
    )
    custom_industry = serializers.CharField(source="company.custom_industry")
    size = serializers.CharField(source="company.size")
    country = serializers.CharField(source="company.country")
    logo = serializers.CharField(source="company.logo", allow_null=True)
    website = serializers.CharField(source="company.website", allow_null=True)
    description = serializers.CharField(source="company.description", allow_null=True)
    is_default = serializers.BooleanField()
    is_deleted = serializers.BooleanField(source="company.is_deleted")
    role = serializers.CharField()
    created_at = serializers.DateTimeField(source="company.created_at")
    updated_at = serializers.DateTimeField(source="company.updated_at")


class UserCompanyListCreateApi(APIView):
    """
    GET  /api/hr/companies/ — list the authenticated user's non-deleted companies
    POST /api/hr/companies/ — create a new company (current user becomes admin)
    """

    permission_classes = [IsAuthenticated]

    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=255)
        size = serializers.ChoiceField(choices=Company.Size.choices)
        country = serializers.CharField(max_length=100)
        industries = serializers.ListField(
            child=serializers.SlugField(max_length=50),
            required=False,
            default=list,
        )
        custom_industry = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
        website = serializers.URLField(max_length=500, required=False, allow_blank=True, default="")
        description = serializers.CharField(required=False, allow_blank=True, default="")

    def get(self, request: Request) -> Response:
        memberships = (
            CompanyMembership.objects.filter(user=request.user, company__is_deleted=False)
            .select_related("company")
            .prefetch_related("company__industries")
            .order_by("-is_default", "company__created_at")
        )
        return Response(
            UserCompanyListOutputSerializer(memberships, many=True).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        company = create_user_company(user=request.user, **serializer.validated_data)
        return Response(
            CompanyOutputSerializer(company).data,
            status=status.HTTP_201_CREATED,
        )


class UserCompanyDetailApi(APIView):
    """
    GET    /api/hr/companies/<id>/ — detail
    PATCH  /api/hr/companies/<id>/ — update (admin only)
    DELETE /api/hr/companies/<id>/ — soft delete
    """

    permission_classes = [IsAuthenticated]

    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=255, required=False)
        industries = serializers.ListField(
            child=serializers.SlugField(max_length=50),
            required=False,
        )
        custom_industry = serializers.CharField(max_length=255, required=False, allow_blank=True)
        size = serializers.ChoiceField(choices=Company.Size.choices, required=False)
        country = serializers.CharField(max_length=100, required=False)
        website = serializers.URLField(max_length=500, required=False, allow_blank=True)
        description = serializers.CharField(required=False, allow_blank=True)
        logo = serializers.CharField(max_length=500, required=False, allow_blank=True)

    def _get_membership(self, request: Request, pk: str) -> CompanyMembership | None:
        return (
            CompanyMembership.objects.filter(
                user=request.user,
                company_id=pk,
                company__is_deleted=False,
            )
            .select_related("company")
            .first()
        )

    def get(self, request: Request, pk: str) -> Response:
        membership = self._get_membership(request, pk)
        if membership is None:
            return Response({"detail": "Company not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(CompanyOutputSerializer(membership.company).data, status=status.HTTP_200_OK)

    def patch(self, request: Request, pk: str) -> Response:
        membership = self._get_membership(request, pk)
        if membership is None:
            return Response({"detail": "Company not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.InputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        try:
            company = update_user_company(
                user=request.user,
                company=membership.company,
                data=dict(serializer.validated_data),
            )
        except ApplicationError as exc:
            return Response({"detail": exc.message}, status=status.HTTP_403_FORBIDDEN)
        return Response(CompanyOutputSerializer(company).data, status=status.HTTP_200_OK)

    def delete(self, request: Request, pk: str) -> Response:
        membership = self._get_membership(request, pk)
        if membership is None:
            return Response({"detail": "Company not found."}, status=status.HTTP_404_NOT_FOUND)
        try:
            soft_delete_company(user=request.user, company=membership.company)
        except ApplicationError as exc:
            return Response({"detail": exc.message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserCompanySetDefaultApi(APIView):
    """POST /api/hr/companies/<id>/set-default/ — mark the company as the user's default."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, pk: str) -> Response:
        try:
            membership = set_default_company(user=request.user, company_id=pk)
        except ApplicationError as exc:
            return Response({"detail": exc.message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {
                "company_id": str(membership.company_id),
                "is_default": membership.is_default,
            },
            status=status.HTTP_200_OK,
        )

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import Company, User
from apps.accounts.permissions import IsPlatformAdmin
from apps.common.pagination import StandardPagination
from apps.common.selectors_admin import get_all_companies, get_all_users, get_platform_analytics
from apps.common.serializers_admin import (
    AdminCompanyDetailOutputSerializer,
    AdminCompanyListOutputSerializer,
    AdminCompanyUpdateInputSerializer,
    AdminUserDetailOutputSerializer,
    AdminUserListOutputSerializer,
    AdminUserUpdateInputSerializer,
)


class AdminCompanyListApi(APIView):
    """GET /api/admin/companies/ — list all companies with stats."""

    permission_classes = [IsPlatformAdmin]

    def get(self, request: Request) -> Response:
        search = request.query_params.get("search")
        status_filter = request.query_params.get("status")

        companies = get_all_companies(search=search, status=status_filter)

        paginator = StandardPagination()
        page = paginator.paginate_queryset(companies, request)
        serializer = AdminCompanyListOutputSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class AdminCompanyDetailApi(APIView):
    """
    GET   /api/admin/companies/{id}/ — company detail
    PATCH /api/admin/companies/{id}/ — update company (activate/block)
    """

    permission_classes = [IsPlatformAdmin]

    def get(self, request: Request, company_id) -> Response:
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response(
                {"detail": "Company not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminCompanyDetailOutputSerializer(company)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request: Request, company_id) -> Response:
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response(
                {"detail": "Company not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        input_serializer = AdminCompanyUpdateInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        update_fields = ["updated_at"]
        for field, value in input_serializer.validated_data.items():
            setattr(company, field, value)
            update_fields.append(field)

        company.save(update_fields=update_fields)

        serializer = AdminCompanyDetailOutputSerializer(company)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminUserListApi(APIView):
    """GET /api/admin/users/ — list all users."""

    permission_classes = [IsPlatformAdmin]

    def get(self, request: Request) -> Response:
        search = request.query_params.get("search")
        role = request.query_params.get("role")

        users = get_all_users(search=search, role=role)

        paginator = StandardPagination()
        page = paginator.paginate_queryset(users, request)
        serializer = AdminUserListOutputSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class AdminUserDetailApi(APIView):
    """
    GET   /api/admin/users/{id}/ — user detail
    PATCH /api/admin/users/{id}/ — activate/block user
    """

    permission_classes = [IsPlatformAdmin]

    def get(self, request: Request, user_id) -> Response:
        try:
            user = User.objects.select_related("company").get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminUserDetailOutputSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request: Request, user_id) -> Response:
        try:
            user = User.objects.select_related("company").get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        input_serializer = AdminUserUpdateInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        update_fields = ["updated_at"]
        for field, value in input_serializer.validated_data.items():
            setattr(user, field, value)
            update_fields.append(field)

        user.save(update_fields=update_fields)

        serializer = AdminUserDetailOutputSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminAnalyticsApi(APIView):
    """GET /api/admin/analytics/ — platform-wide statistics."""

    permission_classes = [IsPlatformAdmin]

    def get(self, request: Request) -> Response:
        analytics = get_platform_analytics()
        return Response(analytics, status=status.HTTP_200_OK)

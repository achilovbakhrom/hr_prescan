from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import Company, User
from apps.accounts.permissions import IsPlatformAdmin
from apps.common.pagination import StandardPagination
from apps.common.selectors_admin import get_all_companies, get_all_users, get_platform_analytics
from apps.subscriptions.models import SubscriptionPlan
from apps.subscriptions.selectors import get_all_plans

# ---------------------------------------------------------------------------
# Serializers
# ---------------------------------------------------------------------------


class AdminCompanyListOutputSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    industry = serializers.CharField()
    size = serializers.CharField()
    country = serializers.CharField()
    subscription_status = serializers.CharField()
    user_count = serializers.IntegerField()
    vacancy_count = serializers.IntegerField()
    created_at = serializers.DateTimeField()


class AdminCompanyDetailOutputSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    industry = serializers.CharField()
    size = serializers.CharField()
    country = serializers.CharField()
    website = serializers.URLField(allow_null=True)
    description = serializers.CharField(allow_null=True)
    subscription_status = serializers.CharField()
    trial_ends_at = serializers.DateTimeField(allow_null=True)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


class AdminCompanyUpdateInputSerializer(serializers.Serializer):
    subscription_status = serializers.ChoiceField(
        choices=Company.SubscriptionStatus.choices,
        required=False,
    )


class AdminUserListOutputSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    role = serializers.CharField()
    is_active = serializers.BooleanField()
    is_staff = serializers.BooleanField()
    company_name = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField()

    def get_company_name(self, obj: User) -> str | None:
        return obj.company.name if obj.company else None


class AdminUserDetailOutputSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone = serializers.CharField(allow_null=True)
    role = serializers.CharField()
    is_active = serializers.BooleanField()
    is_staff = serializers.BooleanField()
    email_verified = serializers.BooleanField()
    company_name = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

    def get_company_name(self, obj: User) -> str | None:
        return obj.company.name if obj.company else None


class AdminUserUpdateInputSerializer(serializers.Serializer):
    is_active = serializers.BooleanField(required=False)
    is_staff = serializers.BooleanField(required=False)


class AdminPlanInputSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    tier = serializers.ChoiceField(choices=SubscriptionPlan.Tier.choices)
    description = serializers.CharField(required=False, allow_blank=True)
    price_monthly = serializers.DecimalField(max_digits=10, decimal_places=2)
    price_yearly = serializers.DecimalField(max_digits=10, decimal_places=2)
    max_vacancies = serializers.IntegerField(min_value=0)
    max_interviews_per_month = serializers.IntegerField(min_value=0)
    max_hr_users = serializers.IntegerField(min_value=0)
    max_storage_gb = serializers.IntegerField(min_value=0)
    is_active = serializers.BooleanField(default=True)


class AdminPlanOutputSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    tier = serializers.CharField()
    description = serializers.CharField()
    price_monthly = serializers.DecimalField(max_digits=10, decimal_places=2)
    price_yearly = serializers.DecimalField(max_digits=10, decimal_places=2)
    max_vacancies = serializers.IntegerField()
    max_interviews_per_month = serializers.IntegerField()
    max_hr_users = serializers.IntegerField()
    max_storage_gb = serializers.IntegerField()
    is_active = serializers.BooleanField()
    created_at = serializers.DateTimeField()


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------


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


class AdminPlanManagementApi(APIView):
    """
    GET  /api/admin/plans/      — list all plans
    POST /api/admin/plans/      — create a plan
    """

    permission_classes = [IsPlatformAdmin]

    def get(self, request: Request) -> Response:
        plans = get_all_plans(active_only=False)
        serializer = AdminPlanOutputSerializer(plans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        input_serializer = AdminPlanInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        plan = SubscriptionPlan.objects.create(**input_serializer.validated_data)

        serializer = AdminPlanOutputSerializer(plan)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AdminPlanDetailApi(APIView):
    """PUT /api/admin/plans/{id}/ — update a plan."""

    permission_classes = [IsPlatformAdmin]

    def put(self, request: Request, plan_id) -> Response:
        try:
            plan = SubscriptionPlan.objects.get(id=plan_id)
        except SubscriptionPlan.DoesNotExist:
            return Response(
                {"detail": "Plan not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        input_serializer = AdminPlanInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        for field, value in input_serializer.validated_data.items():
            setattr(plan, field, value)
        plan.save()

        serializer = AdminPlanOutputSerializer(plan)
        return Response(serializer.data, status=status.HTTP_200_OK)

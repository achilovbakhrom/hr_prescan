from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import HasHRPermission, HRPermissions, IsAdmin, IsHRManager
from apps.subscriptions.models import CompanySubscription, SubscriptionPlan
from apps.subscriptions.selectors import get_all_plans, get_company_subscription, get_plan_by_tier
from apps.subscriptions.services import (
    cancel_subscription,
    get_subscription_usage,
    subscribe_company,
)


# ---------------------------------------------------------------------------
# Serializers
# ---------------------------------------------------------------------------


class PlanOutputSerializer(serializers.Serializer):
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


class CompanySubscriptionOutputSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    plan = PlanOutputSerializer()
    billing_period = serializers.CharField()
    current_period_start = serializers.DateTimeField()
    current_period_end = serializers.DateTimeField()
    is_active = serializers.BooleanField()
    created_at = serializers.DateTimeField()


class SubscribeInputSerializer(serializers.Serializer):
    plan_tier = serializers.ChoiceField(choices=SubscriptionPlan.Tier.choices)
    billing_period = serializers.ChoiceField(
        choices=CompanySubscription.BillingPeriod.choices,
        default=CompanySubscription.BillingPeriod.MONTHLY,
    )


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------


class PlanListApi(APIView):
    """GET /api/subscriptions/plans/ — list all active plans (public)."""

    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        plans = get_all_plans(active_only=True)
        serializer = PlanOutputSerializer(plans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CompanySubscriptionApi(APIView):
    """
    GET  /api/hr/subscription/ — current subscription
    POST /api/hr/subscription/ — subscribe or change plan
    """

    permission_classes = [IsAdmin]

    def get(self, request: Request) -> Response:
        company = request.user.company
        if company is None:
            return Response(
                {"detail": "You are not associated with a company."},
                status=status.HTTP_404_NOT_FOUND,
            )

        subscription = get_company_subscription(company=company)
        if subscription is None:
            return Response(
                {"detail": "No active subscription."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CompanySubscriptionOutputSerializer(subscription)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        company = request.user.company
        if company is None:
            return Response(
                {"detail": "You are not associated with a company."},
                status=status.HTTP_404_NOT_FOUND,
            )

        input_serializer = SubscribeInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        plan = get_plan_by_tier(tier=input_serializer.validated_data["plan_tier"])
        if plan is None:
            return Response(
                {"detail": "Plan not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        subscription = subscribe_company(
            company=company,
            plan=plan,
            billing_period=input_serializer.validated_data["billing_period"],
        )

        serializer = CompanySubscriptionOutputSerializer(subscription)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CancelSubscriptionApi(APIView):
    """POST /api/hr/subscription/cancel/ — cancel subscription."""

    permission_classes = [IsAdmin]

    def post(self, request: Request) -> Response:
        company = request.user.company
        if company is None:
            return Response(
                {"detail": "You are not associated with a company."},
                status=status.HTTP_404_NOT_FOUND,
            )

        subscription = get_company_subscription(company=company)
        if subscription is None:
            return Response(
                {"detail": "No active subscription to cancel."},
                status=status.HTTP_404_NOT_FOUND,
            )

        subscription = cancel_subscription(subscription=subscription)
        serializer = CompanySubscriptionOutputSerializer(subscription)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubscriptionUsageApi(APIView):
    """GET /api/hr/subscription/usage/ — current usage vs limits."""

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_SETTINGS

    def get(self, request: Request) -> Response:
        company = request.user.company
        if company is None:
            return Response(
                {"detail": "You are not associated with a company."},
                status=status.HTTP_404_NOT_FOUND,
            )

        usage = get_subscription_usage(company=company)
        return Response(usage, status=status.HTTP_200_OK)

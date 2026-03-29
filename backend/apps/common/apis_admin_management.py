from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsPlatformAdmin
from apps.subscriptions.models import SubscriptionPlan
from apps.subscriptions.selectors import get_all_plans

# ---------------------------------------------------------------------------
# Serializers
# ---------------------------------------------------------------------------


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

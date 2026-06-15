import logging
from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from apps.accounts.models import User
from apps.subscriptions.models import SubscriptionPlan, UserSubscription

logger = logging.getLogger(__name__)


def create_default_plans() -> list[SubscriptionPlan]:
    """Create the four default subscription plans (idempotent)."""
    defaults = [
        {
            "tier": SubscriptionPlan.Tier.FREE,
            "name": "Free",
            "description": "Get started with basic features",
            "price_monthly": Decimal("0.00"),
            "price_yearly": Decimal("0.00"),
            "max_vacancies": 2,
            "max_interviews_per_month": 10,
            "max_hr_users": 1,
            "max_storage_gb": 1,
        },
        {
            "tier": SubscriptionPlan.Tier.STARTER,
            "name": "Starter",
            "description": "For small teams getting started with AI interviews",
            "price_monthly": Decimal("49.00"),
            "price_yearly": Decimal("470.00"),
            "max_vacancies": 10,
            "max_interviews_per_month": 50,
            "max_hr_users": 3,
            "max_storage_gb": 10,
        },
        {
            "tier": SubscriptionPlan.Tier.PROFESSIONAL,
            "name": "Professional",
            "description": "For growing teams with advanced needs",
            "price_monthly": Decimal("149.00"),
            "price_yearly": Decimal("1430.00"),
            "max_vacancies": 50,
            "max_interviews_per_month": 200,
            "max_hr_users": 10,
            "max_storage_gb": 50,
        },
        {
            "tier": SubscriptionPlan.Tier.ENTERPRISE,
            "name": "Enterprise",
            "description": "Unlimited access for large organisations",
            "price_monthly": Decimal("399.00"),
            "price_yearly": Decimal("3830.00"),
            "max_vacancies": 0,
            "max_interviews_per_month": 0,
            "max_hr_users": 0,
            "max_storage_gb": 500,
        },
    ]

    plans: list[SubscriptionPlan] = []
    for data in defaults:
        plan, _created = SubscriptionPlan.objects.update_or_create(
            tier=data.pop("tier"),
            defaults=data,
        )
        plans.append(plan)

    return plans


def subscribe_user(
    *,
    user: User,
    plan: SubscriptionPlan,
    billing_period: str,
) -> UserSubscription:
    """Create or update a user's subscription."""
    now = timezone.now()

    if billing_period == UserSubscription.BillingPeriod.YEARLY:
        period_end = now + timedelta(days=365)
    else:
        period_end = now + timedelta(days=30)

    subscription, _created = UserSubscription.objects.update_or_create(
        user=user,
        defaults={
            "plan": plan,
            "billing_period": billing_period,
            "current_period_start": now,
            "current_period_end": period_end,
            "is_active": True,
        },
    )

    user.subscription_plan = plan
    user.subscription_status = User.SubscriptionStatus.ACTIVE
    user.save(update_fields=["subscription_plan", "subscription_status", "updated_at"])

    return subscription


def cancel_subscription(*, subscription: UserSubscription) -> UserSubscription:
    """Cancel an active subscription (remains active until period end)."""
    subscription.is_active = False
    subscription.save(update_fields=["is_active", "updated_at"])

    subscription.user.subscription_status = User.SubscriptionStatus.CANCELLED
    subscription.user.save(update_fields=["subscription_status", "updated_at"])

    return subscription

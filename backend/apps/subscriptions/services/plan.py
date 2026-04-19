import logging
from datetime import timedelta
from decimal import Decimal

from django.db import transaction
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


@transaction.atomic
def expire_trial(*, user: User) -> None:
    """Downgrade a user from trial to the Free plan."""
    free_plan = SubscriptionPlan.objects.filter(
        tier=SubscriptionPlan.Tier.FREE,
        is_active=True,
    ).first()

    if free_plan is None:
        logger.error(
            "Free plan not found — cannot downgrade user %s (%s) from trial.",
            user.email,
            user.id,
        )
        return

    now = timezone.now()

    UserSubscription.objects.update_or_create(
        user=user,
        defaults={
            "plan": free_plan,
            "billing_period": UserSubscription.BillingPeriod.MONTHLY,
            "current_period_start": now,
            "current_period_end": now + timedelta(days=30),
            "is_active": True,
        },
    )

    user.subscription_plan = free_plan
    user.subscription_status = User.SubscriptionStatus.ACTIVE
    user.save(update_fields=["subscription_plan", "subscription_status", "updated_at"])

    logger.info(
        "Trial expired for user %s (%s) — downgraded to Free plan.",
        user.email,
        user.id,
    )


def check_and_expire_trials() -> int:
    """Check all trial users and downgrade expired ones. Returns count of expired trials."""
    now = timezone.now()
    expired_users = User.objects.filter(
        subscription_status=User.SubscriptionStatus.TRIAL,
        trial_ends_at__lte=now,
    )

    count = 0
    for user in expired_users:
        expire_trial(user=user)
        count += 1

    if count:
        logger.info("Expired %d trial(s).", count)

    return count

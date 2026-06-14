import logging
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.subscriptions.models import SubscriptionPlan, UserSubscription

logger = logging.getLogger(__name__)

TRIAL_DURATION_DAYS = 14


@transaction.atomic
def grant_trial(*, user: User) -> None:
    """Start a 14-day Professional trial on the user.

    Idempotent: if the user already has a UserSubscription, this is a no-op so we
    never create a second subscription. The trial is granted regardless of billing
    state — creating an HR space must work even for users without a paid plan.
    """
    if UserSubscription.objects.filter(user=user).exists():
        return

    now = timezone.now()
    pro_plan = SubscriptionPlan.objects.filter(
        tier=SubscriptionPlan.Tier.PROFESSIONAL,
        is_active=True,
    ).first()

    user.subscription_plan = pro_plan
    user.subscription_status = User.SubscriptionStatus.TRIAL
    user.trial_ends_at = now + timedelta(days=TRIAL_DURATION_DAYS)
    user.save(update_fields=["subscription_plan", "subscription_status", "trial_ends_at", "updated_at"])

    if pro_plan is None:
        logger.warning(
            "Professional plan not found — user %s (%s) created without trial subscription.",
            user.email,
            user.id,
        )
        return

    UserSubscription.objects.create(
        user=user,
        plan=pro_plan,
        billing_period=UserSubscription.BillingPeriod.MONTHLY,
        current_period_start=now,
        current_period_end=now + timedelta(days=TRIAL_DURATION_DAYS),
        is_active=True,
    )


@transaction.atomic
def expire_trial(*, user: User) -> None:
    """Downgrade a user from trial to the Free plan."""
    if not settings.BILLING_ENABLED:
        return

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
    if not settings.BILLING_ENABLED:
        return 0

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

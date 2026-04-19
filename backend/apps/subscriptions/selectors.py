from django.db.models import QuerySet

from apps.accounts.models import User
from apps.subscriptions.models import SubscriptionPlan, UserSubscription


def get_all_plans(*, active_only: bool = True) -> QuerySet[SubscriptionPlan]:
    """Return all subscription plans, optionally filtered to active ones."""
    qs = SubscriptionPlan.objects.all()
    if active_only:
        qs = qs.filter(is_active=True)
    return qs


def get_user_subscription(*, user: User) -> UserSubscription | None:
    """Return the active subscription for a user, or None."""
    try:
        return UserSubscription.objects.select_related("plan").get(
            user=user,
            is_active=True,
        )
    except UserSubscription.DoesNotExist:
        return None


def get_plan_by_tier(*, tier: str) -> SubscriptionPlan | None:
    """Return the active plan for a given tier, or None."""
    try:
        return SubscriptionPlan.objects.get(tier=tier, is_active=True)
    except SubscriptionPlan.DoesNotExist:
        return None

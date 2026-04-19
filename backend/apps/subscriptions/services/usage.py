from django.utils import timezone

from apps.accounts.models import User
from apps.interviews.models import Interview
from apps.subscriptions.selectors import get_user_subscription
from apps.vacancies.models import Vacancy


def _live_company_ids(user: User) -> list:
    """Company IDs the user belongs to, excluding soft-deleted ones."""
    return list(user.memberships.filter(company__is_deleted=False).values_list("company_id", flat=True))


def check_vacancy_quota(*, user: User) -> bool:
    """Return True if the user can create more vacancies across their companies."""
    subscription = get_user_subscription(user=user)
    if subscription is None:
        return False

    limit = subscription.plan.max_vacancies
    if limit == 0:
        return True  # unlimited

    current_count = Vacancy.objects.filter(
        company_id__in=_live_company_ids(user),
        status__in=[Vacancy.Status.DRAFT, Vacancy.Status.PUBLISHED, Vacancy.Status.PAUSED],
    ).count()

    return current_count < limit


def check_interview_quota(*, user: User) -> bool:
    """Return True if the user has not exceeded the monthly interview limit."""
    subscription = get_user_subscription(user=user)
    if subscription is None:
        return False

    limit = subscription.plan.max_interviews_per_month
    if limit == 0:
        return True  # unlimited

    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    current_count = Interview.objects.filter(
        application__vacancy__company_id__in=_live_company_ids(user),
        created_at__gte=month_start,
    ).count()

    return current_count < limit


def check_hr_user_quota(*, user: User) -> bool:
    """Return True if the user's companies can add more HR users in total."""
    subscription = get_user_subscription(user=user)
    if subscription is None:
        return False

    limit = subscription.plan.max_hr_users
    if limit == 0:
        return True  # unlimited

    company_ids = _live_company_ids(user)
    # Distinct users with HR/admin role who have an active membership in any of this user's companies.
    current_count = (
        User.objects.filter(
            memberships__company_id__in=company_ids,
            memberships__role__in=[User.Role.HR, User.Role.ADMIN],
            is_active=True,
        )
        .distinct()
        .count()
    )

    return current_count < limit


def get_subscription_usage(*, user: User) -> dict:
    """Return current usage vs plan limits for a user (aggregated across their companies)."""
    subscription = get_user_subscription(user=user)
    if subscription is None:
        return {
            "has_subscription": False,
            "plan": None,
            "vacancies": {"used": 0, "limit": 0},
            "interviews_this_month": {"used": 0, "limit": 0},
            "hr_users": {"used": 0, "limit": 0},
        }

    plan = subscription.plan
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    company_ids = _live_company_ids(user)

    vacancy_count = Vacancy.objects.filter(
        company_id__in=company_ids,
        status__in=[Vacancy.Status.DRAFT, Vacancy.Status.PUBLISHED, Vacancy.Status.PAUSED],
    ).count()

    interview_count = Interview.objects.filter(
        application__vacancy__company_id__in=company_ids,
        created_at__gte=month_start,
    ).count()

    hr_user_count = (
        User.objects.filter(
            memberships__company_id__in=company_ids,
            memberships__role__in=[User.Role.HR, User.Role.ADMIN],
            is_active=True,
        )
        .distinct()
        .count()
    )

    is_trial = user.subscription_status == User.SubscriptionStatus.TRIAL
    trial_ends_at = user.trial_ends_at.isoformat() if user.trial_ends_at else None

    return {
        "has_subscription": True,
        "plan": {
            "name": plan.name,
            "tier": plan.tier,
        },
        "billing_period": subscription.billing_period,
        "current_period_end": subscription.current_period_end.isoformat(),
        "is_trial": is_trial,
        "trial_ends_at": trial_ends_at,
        "vacancies": {
            "used": vacancy_count,
            "limit": plan.max_vacancies,
        },
        "interviews_this_month": {
            "used": interview_count,
            "limit": plan.max_interviews_per_month,
        },
        "hr_users": {
            "used": hr_user_count,
            "limit": plan.max_hr_users,
        },
    }

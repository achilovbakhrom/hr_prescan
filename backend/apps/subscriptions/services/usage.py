from django.utils import timezone

from apps.accounts.models import Company, User
from apps.interviews.models import Interview
from apps.subscriptions.selectors import get_company_subscription
from apps.vacancies.models import Vacancy


def check_vacancy_quota(*, company: Company) -> bool:
    """Return True if the company can create more vacancies."""
    subscription = get_company_subscription(company=company)
    if subscription is None:
        return False

    limit = subscription.plan.max_vacancies
    if limit == 0:
        return True  # unlimited

    current_count = Vacancy.objects.filter(
        company=company,
        status__in=[Vacancy.Status.DRAFT, Vacancy.Status.PUBLISHED, Vacancy.Status.PAUSED],
    ).count()

    return current_count < limit


def check_interview_quota(*, company: Company) -> bool:
    """Return True if the company has not exceeded the monthly interview limit."""
    subscription = get_company_subscription(company=company)
    if subscription is None:
        return False

    limit = subscription.plan.max_interviews_per_month
    if limit == 0:
        return True  # unlimited

    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    current_count = Interview.objects.filter(
        application__vacancy__company=company,
        created_at__gte=month_start,
    ).count()

    return current_count < limit


def check_hr_user_quota(*, company: Company) -> bool:
    """Return True if the company can add more HR users."""
    subscription = get_company_subscription(company=company)
    if subscription is None:
        return False

    limit = subscription.plan.max_hr_users
    if limit == 0:
        return True  # unlimited

    current_count = User.objects.filter(
        company=company,
        role__in=[User.Role.HR, User.Role.ADMIN],
        is_active=True,
    ).count()

    return current_count < limit


def get_subscription_usage(*, company: Company) -> dict:
    """Return current usage vs plan limits for a company."""
    subscription = get_company_subscription(company=company)
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

    vacancy_count = Vacancy.objects.filter(
        company=company,
        status__in=[Vacancy.Status.DRAFT, Vacancy.Status.PUBLISHED, Vacancy.Status.PAUSED],
    ).count()

    interview_count = Interview.objects.filter(
        application__vacancy__company=company,
        created_at__gte=month_start,
    ).count()

    hr_user_count = User.objects.filter(
        company=company,
        role__in=[User.Role.HR, User.Role.ADMIN],
        is_active=True,
    ).count()

    # Trial info
    is_trial = company.subscription_status == Company.SubscriptionStatus.TRIAL
    trial_ends_at = company.trial_ends_at.isoformat() if company.trial_ends_at else None

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

from datetime import timedelta
from decimal import Decimal

from django.db.models import Count, Q
from django.utils import timezone

from apps.accounts.models import Company, User
from apps.interviews.models import Interview
from apps.subscriptions.models import CompanySubscription, SubscriptionPlan
from apps.subscriptions.selectors import get_company_subscription
from apps.vacancies.models import Vacancy


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
            "max_vacancies": 0,  # unlimited
            "max_interviews_per_month": 0,  # unlimited
            "max_hr_users": 0,  # unlimited
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


def subscribe_company(
    *,
    company: Company,
    plan: SubscriptionPlan,
    billing_period: str,
) -> CompanySubscription:
    """Create or update a company's subscription."""
    now = timezone.now()

    if billing_period == CompanySubscription.BillingPeriod.YEARLY:
        period_end = now + timedelta(days=365)
    else:
        period_end = now + timedelta(days=30)

    subscription, created = CompanySubscription.objects.update_or_create(
        company=company,
        defaults={
            "plan": plan,
            "billing_period": billing_period,
            "current_period_start": now,
            "current_period_end": period_end,
            "is_active": True,
        },
    )

    # Update company status
    company.subscription_status = Company.SubscriptionStatus.ACTIVE
    company.save(update_fields=["subscription_status", "updated_at"])

    return subscription


def cancel_subscription(*, subscription: CompanySubscription) -> CompanySubscription:
    """Cancel an active subscription (remains active until period end)."""
    subscription.is_active = False
    subscription.save(update_fields=["is_active", "updated_at"])

    subscription.company.subscription_status = Company.SubscriptionStatus.CANCELLED
    subscription.company.save(update_fields=["subscription_status", "updated_at"])

    return subscription


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

    return {
        "has_subscription": True,
        "plan": {
            "name": plan.name,
            "tier": plan.tier,
        },
        "billing_period": subscription.billing_period,
        "current_period_end": subscription.current_period_end.isoformat(),
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

from django.db.models import Count, Q, QuerySet, Sum
from django.utils import timezone

from apps.accounts.models import Company, User
from apps.applications.models import Application
from apps.interviews.models import Interview
from apps.subscriptions.models import CompanySubscription
from apps.vacancies.models import Vacancy


def get_all_companies(
    *,
    search: str | None = None,
    status: str | None = None,
) -> QuerySet[Company]:
    """Return all companies with optional search and status filter."""
    qs = Company.objects.annotate(
        user_count=Count("users"),
        vacancy_count=Count("vacancies"),
    )

    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(industry__icontains=search))

    if status:
        qs = qs.filter(subscription_status=status)

    return qs.order_by("-created_at")


def get_all_users(
    *,
    search: str | None = None,
    role: str | None = None,
) -> QuerySet[User]:
    """Return all users with optional search and role filter."""
    qs = User.objects.select_related("company")

    if search:
        qs = qs.filter(Q(email__icontains=search) | Q(first_name__icontains=search) | Q(last_name__icontains=search))

    if role:
        qs = qs.filter(role=role)

    return qs.order_by("-created_at")


def get_platform_analytics() -> dict:
    """Aggregate platform-wide statistics."""
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    total_companies = Company.objects.count()
    total_users = User.objects.count()
    total_vacancies = Vacancy.objects.count()
    total_interviews = Interview.objects.count()
    total_applications = Application.objects.count()

    active_subscriptions = CompanySubscription.objects.filter(is_active=True).count()

    # Monthly revenue estimate (from active subscriptions)
    monthly_revenue = (
        CompanySubscription.objects.filter(
            is_active=True,
            billing_period=CompanySubscription.BillingPeriod.MONTHLY,
        ).aggregate(
            total=Sum("plan__price_monthly"),
        )["total"]
        or 0
    )

    yearly_revenue_monthly = (
        CompanySubscription.objects.filter(
            is_active=True,
            billing_period=CompanySubscription.BillingPeriod.YEARLY,
        ).aggregate(
            total=Sum("plan__price_yearly"),
        )["total"]
        or 0
    )

    # Convert yearly to monthly equivalent
    monthly_revenue = float(monthly_revenue) + float(yearly_revenue_monthly) / 12

    # New this month
    new_companies_this_month = Company.objects.filter(
        created_at__gte=month_start,
    ).count()

    new_users_this_month = User.objects.filter(
        created_at__gte=month_start,
    ).count()

    interviews_this_month = Interview.objects.filter(
        created_at__gte=month_start,
    ).count()

    # Subscription tier breakdown
    tier_breakdown = (
        CompanySubscription.objects.filter(is_active=True)
        .values("plan__tier", "plan__name")
        .annotate(count=Count("id"))
        .order_by("plan__tier")
    )

    return {
        "total_companies": total_companies,
        "total_users": total_users,
        "total_vacancies": total_vacancies,
        "total_interviews": total_interviews,
        "total_applications": total_applications,
        "active_subscriptions": active_subscriptions,
        "estimated_monthly_revenue": round(monthly_revenue, 2),
        "new_companies_this_month": new_companies_this_month,
        "new_users_this_month": new_users_this_month,
        "interviews_this_month": interviews_this_month,
        "subscription_tier_breakdown": list(tier_breakdown),
    }

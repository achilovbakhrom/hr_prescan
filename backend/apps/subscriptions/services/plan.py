import logging
from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import Company
from apps.subscriptions.models import CompanySubscription, SubscriptionPlan

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

    subscription, _created = CompanySubscription.objects.update_or_create(
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


@transaction.atomic
def expire_trial(*, company: Company) -> None:
    """Downgrade a company from trial to the Free plan."""
    free_plan = SubscriptionPlan.objects.filter(
        tier=SubscriptionPlan.Tier.FREE,
        is_active=True,
    ).first()

    if free_plan is None:
        logger.error(
            "Free plan not found — cannot downgrade company %s (%s) from trial.",
            company.name,
            company.id,
        )
        return

    now = timezone.now()

    # Update or create subscription with the free plan
    CompanySubscription.objects.update_or_create(
        company=company,
        defaults={
            "plan": free_plan,
            "billing_period": CompanySubscription.BillingPeriod.MONTHLY,
            "current_period_start": now,
            "current_period_end": now + timedelta(days=30),
            "is_active": True,
        },
    )

    company.subscription_status = Company.SubscriptionStatus.ACTIVE
    company.save(update_fields=["subscription_status", "updated_at"])

    logger.info(
        "Trial expired for company %s (%s) — downgraded to Free plan.",
        company.name,
        company.id,
    )


def check_and_expire_trials() -> int:
    """Check all trial companies and downgrade expired ones. Returns count of expired trials."""
    now = timezone.now()
    expired_companies = Company.objects.filter(
        subscription_status=Company.SubscriptionStatus.TRIAL,
        trial_ends_at__lte=now,
    )

    count = 0
    for company in expired_companies:
        expire_trial(company=company)
        count += 1

    if count:
        logger.info("Expired %d trial(s).", count)

    return count

import logging
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import Company, CompanyMembership, User
from apps.accounts.services.auth import create_user
from apps.accounts.tasks import send_verification_email
from apps.common.exceptions import ApplicationError

logger = logging.getLogger(__name__)

TRIAL_DURATION_DAYS = 14


def _create_company(
    *,
    name: str,
    industries: list[str] | None = None,
    custom_industry: str = "",
    size: str,
    country: str,
    website: str | None = None,
    description: str | None = None,
) -> Company:
    """Create a Company row. No subscription/trial side-effects."""
    from apps.common.models import Industry

    company = Company.objects.create(
        name=name,
        size=size,
        country=country,
        custom_industry=custom_industry,
        website=website or "",
        description=description or "",
    )

    if industries:
        industry_objs = Industry.objects.filter(slug__in=industries)
        company.industries.set(industry_objs)

    return company


def _grant_trial_to_user(user: User) -> None:
    """Start a 14-day Professional trial on the user. Idempotent — no-op if already subscribed."""
    from apps.subscriptions.models import SubscriptionPlan, UserSubscription

    now = timezone.now()

    pro_plan = SubscriptionPlan.objects.filter(
        tier=SubscriptionPlan.Tier.PROFESSIONAL,
        is_active=True,
    ).first()

    user.subscription_plan = pro_plan
    user.subscription_status = User.SubscriptionStatus.TRIAL
    user.trial_ends_at = now + timedelta(days=TRIAL_DURATION_DAYS)
    user.save(update_fields=["subscription_plan", "subscription_status", "trial_ends_at", "updated_at"])

    if pro_plan is not None:
        UserSubscription.objects.update_or_create(
            user=user,
            defaults={
                "plan": pro_plan,
                "billing_period": UserSubscription.BillingPeriod.MONTHLY,
                "current_period_start": now,
                "current_period_end": now + timedelta(days=TRIAL_DURATION_DAYS),
                "is_active": True,
            },
        )
    else:
        logger.warning(
            "Professional plan not found — user %s (%s) created without trial subscription.",
            user.email,
            user.id,
        )


@transaction.atomic
def create_company_with_admin(
    *,
    company_name: str,
    industries: list[str] | None = None,
    size: str,
    country: str,
    admin_email: str,
    admin_password: str,
    admin_first_name: str,
    admin_last_name: str,
    website: str | None = None,
    description: str | None = None,
) -> tuple[Company, User]:
    """Create a company and its admin user in one transaction, starting a 14-day user trial."""
    company = _create_company(
        name=company_name,
        industries=industries,
        size=size,
        country=country,
        website=website,
        description=description,
    )

    user = create_user(
        email=admin_email,
        password=admin_password,
        first_name=admin_first_name,
        last_name=admin_last_name,
        role=User.Role.ADMIN,
        company=company,
    )

    _grant_trial_to_user(user)

    CompanyMembership.objects.create(
        user=user,
        company=company,
        role=User.Role.ADMIN,
        is_default=True,
    )

    send_verification_email.delay(user_id=str(user.id))

    return company, user


@transaction.atomic
def complete_company_setup(
    *,
    user: User,
    company_name: str,
    industries: list[str] | None = None,
    size: str,
    country: str,
    email: str | None = None,
) -> Company:
    """Upgrade a social-auth candidate to company admin, granting them a trial."""
    if email:
        if User.objects.filter(email=email).exclude(id=user.id).exists():
            raise ApplicationError("A user with this email already exists.")
        user.email = email

    company = _create_company(
        name=company_name,
        industries=industries,
        size=size,
        country=country,
    )

    user.role = User.Role.ADMIN
    user.company = company
    user.onboarding_completed = True
    user.save(update_fields=["email", "role", "company", "onboarding_completed", "updated_at"])

    _grant_trial_to_user(user)

    CompanyMembership.objects.create(
        user=user,
        company=company,
        role=User.Role.ADMIN,
        is_default=True,
    )

    return company

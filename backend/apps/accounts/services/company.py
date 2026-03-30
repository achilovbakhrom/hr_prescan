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


def _create_company_with_trial(
    *,
    company_name: str,
    industries: list[str] | None = None,
    custom_industry: str = "",
    size: str,
    country: str,
    website: str | None = None,
    description: str | None = None,
) -> Company:
    """Create a Company with a 14-day Professional trial."""
    from apps.common.models import Industry
    from apps.subscriptions.models import CompanySubscription, SubscriptionPlan

    now = timezone.now()

    company = Company.objects.create(
        name=company_name,
        size=size,
        country=country,
        custom_industry=custom_industry,
        website=website or "",
        description=description or "",
    )

    if industries:
        industry_objs = Industry.objects.filter(slug__in=industries)
        company.industries.set(industry_objs)

    # Activate 14-day trial
    company.trial_ends_at = now + timedelta(days=TRIAL_DURATION_DAYS)
    company.subscription_status = Company.SubscriptionStatus.TRIAL
    company.save(update_fields=["trial_ends_at", "subscription_status", "updated_at"])

    # Grant Professional-tier limits during trial
    pro_plan = SubscriptionPlan.objects.filter(
        tier=SubscriptionPlan.Tier.PROFESSIONAL,
        is_active=True,
    ).first()

    if pro_plan is not None:
        CompanySubscription.objects.create(
            company=company,
            plan=pro_plan,
            billing_period=CompanySubscription.BillingPeriod.MONTHLY,
            current_period_start=now,
            current_period_end=now + timedelta(days=TRIAL_DURATION_DAYS),
            is_active=True,
        )
    else:
        logger.warning(
            "Professional plan not found — company %s (%s) created without trial subscription.",
            company.name,
            company.id,
        )

    return company


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
    """Create a company and its admin user in a single transaction.

    The company starts on a 14-day free trial with Professional-tier limits.
    """
    company = _create_company_with_trial(
        company_name=company_name,
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

    CompanyMembership.objects.create(user=user, company=company, role=User.Role.ADMIN)

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
    """Upgrade a social-auth candidate to company admin."""
    if email:
        if User.objects.filter(email=email).exclude(id=user.id).exists():
            raise ApplicationError("A user with this email already exists.")
        user.email = email

    company = _create_company_with_trial(
        company_name=company_name,
        industries=industries,
        size=size,
        country=country,
    )

    user.role = User.Role.ADMIN
    user.company = company
    user.onboarding_completed = True
    user.save(update_fields=["email", "role", "company", "onboarding_completed", "updated_at"])

    CompanyMembership.objects.create(user=user, company=company, role=User.Role.ADMIN)

    return company


def update_company_profile(*, company: Company, data: dict) -> Company:
    """Update company fields (name, industries, size, country, website, description, logo)."""
    from apps.common.models import Industry

    allowed_fields = {"name", "size", "country", "website", "description", "logo", "custom_industry"}
    update_fields = []

    # Handle M2M industries separately
    if "industries" in data:
        industry_slugs = data.pop("industries")
        industry_objs = Industry.objects.filter(slug__in=industry_slugs)
        company.industries.set(industry_objs)

    for field, value in data.items():
        if field in allowed_fields:
            setattr(company, field, value)
            update_fields.append(field)

    if not update_fields:
        return company

    update_fields.append("updated_at")
    company.save(update_fields=update_fields)
    return company

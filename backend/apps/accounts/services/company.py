from django.db import transaction

from apps.accounts.models import Company, CompanyMembership, User
from apps.accounts.services.auth import create_user
from apps.accounts.tasks import send_verification_email
from apps.common.exceptions import ApplicationError


def _create_company(
    *,
    account_owner: User,
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
        account_owner=account_owner,
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
    from apps.subscriptions.services import grant_trial

    grant_trial(user=user)


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
    user = create_user(
        email=admin_email,
        password=admin_password,
        first_name=admin_first_name,
        last_name=admin_last_name,
        role=User.Role.ADMIN,
    )

    company = _create_company(
        account_owner=user,
        name=company_name,
        industries=industries,
        size=size,
        country=country,
        website=website,
        description=description,
    )
    user.company = company
    user.save(update_fields=["company", "updated_at"])

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
        account_owner=user,
        name=company_name,
        industries=industries,
        size=size,
        country=country,
    )

    user.role = User.Role.ADMIN
    user.active_mode = User.ActiveMode.HR
    user.company = company
    user.onboarding_completed = True
    user.save(update_fields=["email", "role", "active_mode", "company", "onboarding_completed", "updated_at"])

    _grant_trial_to_user(user)

    CompanyMembership.objects.create(
        user=user,
        company=company,
        role=User.Role.ADMIN,
        is_default=True,
    )

    return company

import logging
from datetime import timedelta
from uuid import UUID

from django.core import signing
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import Company, Invitation, User
from apps.accounts.tasks import send_invitation_email, send_verification_email
from apps.common.exceptions import ApplicationError
from apps.common.messages import (
    MSG_CANNOT_DEACTIVATE_SELF,
    MSG_EMAIL_ALREADY_VERIFIED,
    MSG_INVALID_INVITATION,
    MSG_INVALID_VERIFICATION_TOKEN,
    MSG_INVITATION_ALREADY_ACCEPTED,
    MSG_INVITATION_EXISTS,
    MSG_INVITATION_EXPIRED,
    MSG_INVITATION_WRONG_EMAIL,
    MSG_MANAGE_OWN_COMPANY,
    MSG_ONLY_ADMINS_ACTIVATE,
    MSG_ONLY_ADMINS_DEACTIVATE,
    MSG_USER_ALREADY_ACTIVE,
    MSG_USER_ALREADY_DEACTIVATED,
    MSG_USER_EXISTS,
)

logger = logging.getLogger(__name__)

TRIAL_DURATION_DAYS = 14

EMAIL_VERIFICATION_SALT = "email-verification"
EMAIL_VERIFICATION_MAX_AGE = 60 * 60 * 24 * 3  # 3 days


def generate_email_verification_token(*, user_id: str) -> str:
    """Generate a signed, time-limited token for email verification."""
    return signing.dumps(user_id, salt=EMAIL_VERIFICATION_SALT)


def decode_email_verification_token(*, token: str) -> str:
    """Decode and validate a signed email verification token. Returns user_id."""
    try:
        return signing.loads(token, salt=EMAIL_VERIFICATION_SALT, max_age=EMAIL_VERIFICATION_MAX_AGE)
    except signing.BadSignature as exc:
        raise ApplicationError(str(MSG_INVALID_VERIFICATION_TOKEN)) from exc


def create_user(
    *,
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    role: str,
    company: Company | None = None,
) -> User:
    """Create a user with hashed password."""
    if User.objects.filter(email=email).exists():
        raise ApplicationError(str(MSG_USER_EXISTS))

    user = User.objects.create_user(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        role=role,
        company=company,
    )
    return user


def register_user(
    *,
    email: str,
    password: str,
    first_name: str,
    last_name: str,
) -> User:
    """Register a candidate user and trigger verification email."""
    user = create_user(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        role=User.Role.CANDIDATE,
    )
    send_verification_email.delay(user_id=str(user.id))
    return user


def verify_email(*, token: str) -> User:
    """Verify a user's email address using a signed token."""
    user_id = decode_email_verification_token(token=token)

    try:
        user = User.objects.get(id=user_id)
    except (User.DoesNotExist, ValueError) as exc:
        raise ApplicationError(str(MSG_INVALID_VERIFICATION_TOKEN)) from exc

    if user.email_verified:
        raise ApplicationError(str(MSG_EMAIL_ALREADY_VERIFIED))

    user.email_verified = True
    user.save(update_fields=["email_verified", "updated_at"])
    return user


@transaction.atomic
def create_company_with_admin(
    *,
    company_name: str,
    industry: str,
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
    from apps.subscriptions.models import CompanySubscription, SubscriptionPlan

    now = timezone.now()

    company = Company.objects.create(
        name=company_name,
        industry=industry,
        size=size,
        country=country,
        website=website or "",
        description=description or "",
    )

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

    user = create_user(
        email=admin_email,
        password=admin_password,
        first_name=admin_first_name,
        last_name=admin_last_name,
        role=User.Role.ADMIN,
        company=company,
    )

    send_verification_email.delay(user_id=str(user.id))

    return company, user


def update_company_profile(*, company: Company, data: dict) -> Company:
    """Update company fields (name, industry, size, country, website, description, logo)."""
    allowed_fields = {"name", "industry", "size", "country", "website", "description", "logo"}
    update_fields = []

    for field, value in data.items():
        if field in allowed_fields:
            setattr(company, field, value)
            update_fields.append(field)

    if not update_fields:
        return company

    update_fields.append("updated_at")
    company.save(update_fields=update_fields)
    return company


def invite_hr(*, company: Company, email: str, invited_by: User) -> Invitation:
    """Create an HR invitation and send the invitation email."""
    if User.objects.filter(email=email).exists():
        raise ApplicationError(str(MSG_USER_EXISTS))

    if Invitation.objects.filter(company=company, email=email, is_accepted=False).exists():
        raise ApplicationError(str(MSG_INVITATION_EXISTS))

    invitation = Invitation.objects.create(
        company=company,
        email=email,
        invited_by=invited_by,
    )

    send_invitation_email.delay(invitation_id=str(invitation.id))

    return invitation


@transaction.atomic
def accept_invitation(
    *,
    token: UUID,
    password: str,
    first_name: str,
    last_name: str,
) -> User:
    """Accept an invitation: validate token, create HR user, mark invitation accepted."""
    try:
        invitation = Invitation.objects.select_related("company").get(token=token)
    except Invitation.DoesNotExist as exc:
        raise ApplicationError(str(MSG_INVALID_INVITATION)) from exc

    if invitation.is_accepted:
        raise ApplicationError(str(MSG_INVITATION_ALREADY_ACCEPTED))

    if invitation.is_expired:
        raise ApplicationError(str(MSG_INVITATION_EXPIRED))

    user = create_user(
        email=invitation.email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        role=User.Role.HR,
        company=invitation.company,
    )

    invitation.is_accepted = True
    invitation.save(update_fields=["is_accepted", "updated_at"])

    return user


@transaction.atomic
def accept_invitation_existing_user(
    *,
    user: User,
    token: UUID,
) -> User:
    """Accept an invitation for an existing user — switches their company and role."""
    try:
        invitation = Invitation.objects.select_related("company").get(token=token)
    except Invitation.DoesNotExist as exc:
        raise ApplicationError(str(MSG_INVALID_INVITATION)) from exc

    if invitation.is_accepted:
        raise ApplicationError(str(MSG_INVITATION_ALREADY_ACCEPTED))

    if invitation.is_expired:
        raise ApplicationError(str(MSG_INVITATION_EXPIRED))

    if invitation.email != user.email:
        raise ApplicationError(str(MSG_INVITATION_WRONG_EMAIL))

    # Switch user's company and role
    user.company = invitation.company
    user.role = User.Role.HR
    user.save(update_fields=["company", "role", "updated_at"])

    invitation.is_accepted = True
    invitation.save(update_fields=["is_accepted", "updated_at"])

    return user


def deactivate_user(*, user: User, deactivated_by: User) -> User:
    """Deactivate a user. Only admins of the same company can deactivate."""
    if deactivated_by.role != User.Role.ADMIN:
        raise ApplicationError(str(MSG_ONLY_ADMINS_DEACTIVATE))

    if deactivated_by.company_id != user.company_id:
        raise ApplicationError(str(MSG_MANAGE_OWN_COMPANY))

    if user.id == deactivated_by.id:
        raise ApplicationError(str(MSG_CANNOT_DEACTIVATE_SELF))

    if not user.is_active:
        raise ApplicationError(str(MSG_USER_ALREADY_DEACTIVATED))

    user.is_active = False
    user.save(update_fields=["is_active", "updated_at"])
    return user


def activate_user(*, user: User, activated_by: User) -> User:
    """Activate a user. Only admins of the same company can activate."""
    if activated_by.role != User.Role.ADMIN:
        raise ApplicationError(str(MSG_ONLY_ADMINS_ACTIVATE))

    if activated_by.company_id != user.company_id:
        raise ApplicationError(str(MSG_MANAGE_OWN_COMPANY))

    if user.is_active:
        raise ApplicationError(str(MSG_USER_ALREADY_ACTIVE))

    user.is_active = True
    user.save(update_fields=["is_active", "updated_at"])
    return user

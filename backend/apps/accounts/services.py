from django.db import transaction

from apps.accounts.models import Company, User
from apps.accounts.tasks import send_verification_email
from apps.common.exceptions import ApplicationError


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
        raise ApplicationError("User with this email already exists.")

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
    """Verify a user's email address using the provided token."""
    # In a full implementation, this would decode a signed token.
    # For now, we treat the token as the user ID (placeholder logic).
    try:
        user = User.objects.get(id=token)
    except (User.DoesNotExist, ValueError) as exc:
        raise ApplicationError("Invalid or expired verification token.") from exc

    if user.email_verified:
        raise ApplicationError("Email is already verified.")

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
) -> tuple[Company, User]:
    """Create a company and its admin user in a single transaction."""
    company = Company.objects.create(
        name=company_name,
        industry=industry,
        size=size,
        country=country,
    )

    user = create_user(
        email=admin_email,
        password=admin_password,
        first_name=admin_first_name,
        last_name=admin_last_name,
        role=User.Role.ADMIN,
        company=company,
    )

    return company, user

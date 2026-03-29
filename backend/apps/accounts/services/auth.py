import logging

from django.core import signing

from apps.accounts.models import Company, User
from apps.accounts.tasks import send_verification_email
from apps.common.exceptions import ApplicationError
from apps.common.messages import (
    MSG_EMAIL_ALREADY_VERIFIED,
    MSG_INVALID_VERIFICATION_TOKEN,
    MSG_USER_EXISTS,
)

logger = logging.getLogger(__name__)

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


def complete_onboarding(*, user: User) -> User:
    """Mark onboarding as completed (user chose to stay as candidate)."""
    user.onboarding_completed = True
    user.save(update_fields=["onboarding_completed", "updated_at"])
    return user

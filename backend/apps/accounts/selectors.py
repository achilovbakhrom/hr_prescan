from uuid import UUID

from django.db.models import QuerySet

from apps.accounts.models import Company, Invitation, User


def get_user_by_email(*, email: str) -> User | None:
    """Retrieve a user by email, with company pre-loaded."""
    return User.objects.select_related("company").filter(email=email).first()


def get_company_users(*, company: Company) -> QuerySet[User]:
    """Return all users belonging to a company."""
    return User.objects.filter(company=company).select_related("company").order_by("-created_at")


def get_user_by_id(*, user_id: UUID) -> User | None:
    """Retrieve a user by ID, with company pre-loaded."""
    return User.objects.select_related("company").filter(id=user_id).first()


def get_company_by_id(*, company_id: UUID) -> Company | None:
    """Retrieve a company by ID."""
    return Company.objects.filter(id=company_id).first()


def get_company_invitations(*, company: Company) -> QuerySet[Invitation]:
    """Return all invitations for a company."""
    return (
        Invitation.objects
        .filter(company=company)
        .select_related("invited_by")
        .order_by("-created_at")
    )


def get_pending_invitations_for_email(*, email: str) -> QuerySet[Invitation]:
    """Return all pending (not accepted, not expired) invitations for an email."""
    from django.utils import timezone

    return (
        Invitation.objects
        .filter(
            email=email,
            is_accepted=False,
            expires_at__gt=timezone.now(),
        )
        .select_related("company", "invited_by")
        .order_by("-created_at")
    )


def get_invitation_by_token(*, token: UUID) -> Invitation | None:
    """Retrieve an invitation by its token, with company pre-loaded."""
    return (
        Invitation.objects
        .select_related("company", "invited_by")
        .filter(token=token)
        .first()
    )

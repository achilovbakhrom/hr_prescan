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


def get_user_live_company_ids(*, user: User) -> list[UUID]:
    """Return IDs of non-deleted companies the user belongs to."""
    company_ids = list(user.memberships.filter(company__is_deleted=False).values_list("company_id", flat=True))
    if (
        user.company_id
        and user.company_id not in company_ids
        and Company.objects.filter(id=user.company_id, is_deleted=False).exists()
    ):
        company_ids.append(user.company_id)
    return company_ids


def get_account_invitations(*, account_owner: User) -> QuerySet[Invitation]:
    """Return all invitations for an account (across all its companies)."""
    return (
        Invitation.objects.filter(account_owner=account_owner)
        .select_related("invited_by")
        .prefetch_related("companies")
        .order_by("-created_at")
    )


def get_pending_invitations_for_email(*, email: str) -> QuerySet[Invitation]:
    """Return all pending (not accepted, not expired) invitations for an email."""
    from django.utils import timezone

    return (
        Invitation.objects.filter(
            email=email,
            is_accepted=False,
            expires_at__gt=timezone.now(),
        )
        .select_related("account_owner", "invited_by")
        .prefetch_related("companies")
        .order_by("-created_at")
    )


def get_invitation_by_token(*, token: UUID) -> Invitation | None:
    """Retrieve an invitation by its token, with account and companies pre-loaded."""
    return (
        Invitation.objects.select_related("account_owner", "invited_by")
        .prefetch_related("companies")
        .filter(token=token)
        .first()
    )

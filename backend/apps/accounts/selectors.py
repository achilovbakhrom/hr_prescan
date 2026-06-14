from uuid import UUID

from django.db.models import F, QuerySet

from apps.accounts.models import Company, Invitation, User


def get_user_by_email(*, email: str) -> User | None:
    """Retrieve a user by email, with company pre-loaded."""
    return User.objects.select_related("company").filter(email=email).first()


def get_company_users(*, company: Company) -> QuerySet[User]:
    """Return all users who hold a membership in a company.

    Membership is the source of truth — this includes members currently switched
    into a different company or candidate mode, not just those whose active-company
    pointer (``User.company``) happens to be this company.

    Each row is annotated with the member's ``role`` and ``hr_permissions`` for the
    *queried* company (``membership_role`` / ``membership_hr_permissions``), so the
    team read path reflects the queried company's membership rather than the member's
    live active-company pointer. ``select_related`` covers
    ``UserOutputSerializer.account_owner_name``/``is_account_owner`` traversals.
    """
    return (
        User.objects.filter(memberships__company=company)
        .select_related("company", "account_owner")
        .annotate(
            membership_role=F("memberships__role"),
            membership_hr_permissions=F("memberships__hr_permissions"),
        )
        .order_by("-created_at")
    )


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

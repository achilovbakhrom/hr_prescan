from uuid import UUID

from django.db import transaction

from apps.accounts.models import Company, CompanyMembership, Invitation, User
from apps.accounts.services.auth import create_user
from apps.accounts.tasks import send_invitation_email
from apps.common.exceptions import ApplicationError
from apps.common.messages import (
    MSG_INVALID_INVITATION,
    MSG_INVITATION_ALREADY_ACCEPTED,
    MSG_INVITATION_EXISTS,
    MSG_INVITATION_EXPIRED,
    MSG_INVITATION_WRONG_EMAIL,
)


def invite_hr(
    *,
    invited_by: User,
    email: str,
    companies: list[Company] | None = None,
    permissions: list[str] | None = None,
) -> Invitation:
    """Create an HR invitation scoped to the inviter's account and one or more companies.

    If ``companies`` is None/empty, the invitation grants access to every non-deleted
    company currently owned by the inviter's account. If the target email already has
    a membership covering every requested company, the invitation is rejected.
    """
    account_owner = invited_by.effective_account_owner
    owned_qs = Company.objects.filter(account_owner=account_owner, is_deleted=False)

    if companies:
        selected = list(owned_qs.filter(id__in=[c.id for c in companies]))
        if len(selected) != len({c.id for c in companies}):
            raise ApplicationError("One or more selected companies do not belong to your account.")
    else:
        selected = list(owned_qs)

    if not selected:
        raise ApplicationError("No companies available to invite into.")

    existing_user = User.objects.filter(email=email).first()
    if existing_user:
        existing_company_ids = set(
            CompanyMembership.objects.filter(
                user=existing_user,
                company_id__in=[c.id for c in selected],
            ).values_list("company_id", flat=True),
        )
        if existing_company_ids == {c.id for c in selected}:
            raise ApplicationError("User is already a member of the selected companies.")

    if Invitation.objects.filter(account_owner=account_owner, email=email, is_accepted=False).exists():
        raise ApplicationError(str(MSG_INVITATION_EXISTS))

    invitation = Invitation.objects.create(
        account_owner=account_owner,
        email=email,
        invited_by=invited_by,
        permissions=permissions or [],
    )
    invitation.companies.set(selected)

    send_invitation_email.delay(invitation_id=str(invitation.id))

    return invitation


def _create_membership_from_invitation(user: User, invitation: Invitation) -> None:
    """Grant the user memberships to every company in the invitation and link them to the account.

    Existing default membership is preserved — re-accepting never demotes the current default.
    """
    perms = invitation.permissions or []
    companies = list(invitation.companies.filter(is_deleted=False))
    if not companies:
        raise ApplicationError(str(MSG_INVALID_INVITATION))

    # If the user already operates under a different account (either as owner of
    # their own companies or as an invited member elsewhere), reject — we don't
    # support belonging to two accounts simultaneously.
    if user.owned_companies.exists():
        raise ApplicationError("You already own companies. Transfer or delete them before accepting this invitation.")
    if user.account_owner_id and user.account_owner_id != invitation.account_owner_id:
        raise ApplicationError("You already belong to another account. Leave it before accepting this invitation.")

    user.account_owner = invitation.account_owner
    has_default = CompanyMembership.objects.filter(user=user, is_default=True).exists()
    for company in companies:
        membership, created = CompanyMembership.objects.get_or_create(
            user=user,
            company=company,
            defaults={
                "role": User.Role.HR,
                "hr_permissions": perms,
                "is_default": not has_default,
            },
        )
        if membership.is_default:
            has_default = True
        if not created:
            membership.role = User.Role.HR
            membership.hr_permissions = perms
            membership.save(update_fields=["role", "hr_permissions"])

    user.company = companies[0]
    user.role = User.Role.HR
    user.hr_permissions = perms
    user.save(update_fields=["account_owner", "company", "role", "hr_permissions", "updated_at"])


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
        invitation = Invitation.objects.select_related("account_owner").get(token=token)
    except Invitation.DoesNotExist as exc:
        raise ApplicationError(str(MSG_INVALID_INVITATION)) from exc

    if invitation.is_accepted:
        raise ApplicationError(str(MSG_INVITATION_ALREADY_ACCEPTED))

    if invitation.is_expired:
        raise ApplicationError(str(MSG_INVITATION_EXPIRED))

    first_company = invitation.companies.filter(is_deleted=False).first()
    user = create_user(
        email=invitation.email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        role=User.Role.HR,
        company=first_company,
    )
    _create_membership_from_invitation(user, invitation)

    invitation.is_accepted = True
    invitation.save(update_fields=["is_accepted", "updated_at"])

    return user


@transaction.atomic
def accept_invitation_existing_user(*, user: User, token: UUID) -> User:
    """Accept an invitation for an existing user -- adds membership and switches."""
    try:
        invitation = Invitation.objects.select_related("account_owner").get(token=token)
    except Invitation.DoesNotExist as exc:
        raise ApplicationError(str(MSG_INVALID_INVITATION)) from exc

    if invitation.is_accepted:
        raise ApplicationError(str(MSG_INVITATION_ALREADY_ACCEPTED))

    if invitation.is_expired:
        raise ApplicationError(str(MSG_INVITATION_EXPIRED))

    if invitation.email != user.email:
        raise ApplicationError(str(MSG_INVITATION_WRONG_EMAIL))

    _create_membership_from_invitation(user, invitation)

    invitation.is_accepted = True
    invitation.save(update_fields=["is_accepted", "updated_at"])

    return user

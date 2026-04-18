from uuid import UUID

from django.db import transaction

from apps.accounts.models import Company, CompanyMembership, Invitation, User
from apps.accounts.services.auth import create_user
from apps.accounts.tasks import send_invitation_email
from apps.common.exceptions import ApplicationError
from apps.common.messages import (
    MSG_CANNOT_DEACTIVATE_SELF,
    MSG_INVALID_INVITATION,
    MSG_INVITATION_ALREADY_ACCEPTED,
    MSG_INVITATION_EXISTS,
    MSG_INVITATION_EXPIRED,
    MSG_INVITATION_WRONG_EMAIL,
    MSG_MANAGE_OWN_COMPANY,
    MSG_ONLY_ADMINS_ACTIVATE,
    MSG_ONLY_ADMINS_DEACTIVATE,
    MSG_USER_ALREADY_ACTIVE,
    MSG_USER_ALREADY_DEACTIVATED,
)


def invite_hr(
    *,
    company: Company,
    email: str,
    invited_by: User,
    permissions: list[str] | None = None,
) -> Invitation:
    """Create an HR invitation and send the invitation email.

    Works for both new and existing users. If the user already belongs
    to this company, the invitation is rejected.
    """
    existing_user = User.objects.filter(email=email).first()
    if existing_user and CompanyMembership.objects.filter(user=existing_user, company=company).exists():
        raise ApplicationError("User is already a member of this company.")

    if Invitation.objects.filter(company=company, email=email, is_accepted=False).exists():
        raise ApplicationError(str(MSG_INVITATION_EXISTS))

    invitation = Invitation.objects.create(
        company=company,
        email=email,
        invited_by=invited_by,
        permissions=permissions or [],
    )

    send_invitation_email.delay(invitation_id=str(invitation.id))

    return invitation


def _create_membership_from_invitation(user: User, invitation: Invitation) -> None:
    """Create a CompanyMembership from an invitation and switch the user to that company.

    If the user has no existing default membership, this one becomes default.
    """
    perms = invitation.permissions or []
    has_default = CompanyMembership.objects.filter(user=user, is_default=True).exists()

    CompanyMembership.objects.update_or_create(
        user=user,
        company=invitation.company,
        defaults={
            "role": User.Role.HR,
            "hr_permissions": perms,
            "is_default": not has_default,
        },
    )
    # Switch active company
    user.company = invitation.company
    user.role = User.Role.HR
    user.hr_permissions = perms
    user.save(update_fields=["company", "role", "hr_permissions", "updated_at"])


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
    _create_membership_from_invitation(user, invitation)

    invitation.is_accepted = True
    invitation.save(update_fields=["is_accepted", "updated_at"])

    return user


@transaction.atomic
def accept_invitation_existing_user(
    *,
    user: User,
    token: UUID,
) -> User:
    """Accept an invitation for an existing user -- adds company membership and switches."""
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

    _create_membership_from_invitation(user, invitation)

    invitation.is_accepted = True
    invitation.save(update_fields=["is_accepted", "updated_at"])

    return user


@transaction.atomic
def switch_company(*, user: User, company_id: UUID) -> User:
    """Switch the user's active company. Must have a membership."""
    try:
        membership = CompanyMembership.objects.select_related("company").get(
            user=user,
            company_id=company_id,
        )
    except CompanyMembership.DoesNotExist as exc:
        raise ApplicationError("You are not a member of this company.") from exc

    user.company = membership.company
    user.role = membership.role
    user.hr_permissions = membership.hr_permissions
    user.save(update_fields=["company", "role", "hr_permissions", "updated_at"])
    return user


def switch_to_personal(*, user: User) -> User:
    """Switch user back to personal/candidate context (no company)."""
    user.company = None
    user.role = User.Role.CANDIDATE
    user.hr_permissions = []
    user.save(update_fields=["company", "role", "hr_permissions", "updated_at"])
    return user


@transaction.atomic
def set_default_company(*, user: User, company_id: UUID) -> CompanyMembership:
    """Toggle the user's default flag onto one of their memberships.

    Unsets any previous default for the user in the same transaction. The caller is expected
    to have verified the user owns a membership to ``company_id`` (raises otherwise).
    """
    try:
        target = CompanyMembership.objects.get(user=user, company_id=company_id)
    except CompanyMembership.DoesNotExist as exc:
        raise ApplicationError("You are not a member of this company.") from exc

    if target.is_default:
        return target  # idempotent

    CompanyMembership.objects.filter(user=user, is_default=True).update(is_default=False)
    target.is_default = True
    target.save(update_fields=["is_default"])
    return target


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

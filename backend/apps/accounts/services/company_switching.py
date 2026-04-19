from uuid import UUID

from django.db import transaction

from apps.accounts.models import CompanyMembership, User
from apps.common.exceptions import ApplicationError


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

    Unsets any previous default for the user in the same transaction.
    """
    try:
        target = CompanyMembership.objects.get(user=user, company_id=company_id)
    except CompanyMembership.DoesNotExist as exc:
        raise ApplicationError("You are not a member of this company.") from exc

    if target.is_default:
        return target

    CompanyMembership.objects.filter(user=user, is_default=True).update(is_default=False)
    target.is_default = True
    target.save(update_fields=["is_default"])
    return target

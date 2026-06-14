from apps.accounts.models import Company, CompanyMembership, User
from apps.common.exceptions import ApplicationError
from apps.common.messages import (
    MSG_CANNOT_DEACTIVATE_SELF,
    MSG_MANAGE_OWN_COMPANY,
    MSG_ONLY_ADMINS_ACTIVATE,
    MSG_ONLY_ADMINS_DEACTIVATE,
    MSG_USER_ALREADY_ACTIVE,
    MSG_USER_ALREADY_DEACTIVATED,
)


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


def set_member_permissions(*, user: User, company: Company, permissions: list[str]) -> User:
    """Update an HR member's permissions for a company.

    The CompanyMembership is the source of truth — switch_company reloads
    User.hr_permissions from the membership on every switch, so the write must land
    on the membership. The live User.hr_permissions is updated only when the member
    is currently active in this company, so the change takes effect immediately.
    """
    try:
        membership = CompanyMembership.objects.get(user=user, company=company)
    except CompanyMembership.DoesNotExist as exc:
        raise ApplicationError(str(MSG_MANAGE_OWN_COMPANY)) from exc

    membership.hr_permissions = permissions
    membership.save(update_fields=["hr_permissions"])

    if user.company_id == company.id:
        user.hr_permissions = permissions
        user.save(update_fields=["hr_permissions", "updated_at"])

    return user

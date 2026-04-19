"""Services for user-owned Company CRUD + soft delete + default transfer."""

from uuid import UUID

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import Company, CompanyMembership, User
from apps.common.exceptions import ApplicationError


def _user_live_memberships(user: User):
    return user.memberships.filter(company__is_deleted=False).select_related("company")


@transaction.atomic
def create_user_company(
    *,
    user: User,
    name: str,
    size: str,
    country: str,
    custom_industry: str = "",
    website: str | None = None,
    description: str | None = None,
    industries: list[str] | None = None,
) -> Company:
    """Create a new Company and attach an ADMIN membership for the user.

    The new membership is default only if the user has no other default membership.
    """
    from apps.common.models import Industry

    company = Company.objects.create(
        name=name,
        size=size,
        country=country,
        custom_industry=custom_industry,
        website=website or "",
        description=description or "",
    )
    if industries:
        company.industries.set(Industry.objects.filter(slug__in=industries))

    has_default = CompanyMembership.objects.filter(user=user, is_default=True).exists()
    CompanyMembership.objects.create(
        user=user,
        company=company,
        role=User.Role.ADMIN,
        is_default=not has_default,
    )
    return company


def update_user_company(*, user: User, company: Company, data: dict) -> Company:
    """Update company fields. Raises if user isn't an admin of this company."""
    if not CompanyMembership.objects.filter(
        user=user,
        company=company,
        role=User.Role.ADMIN,
    ).exists():
        raise ApplicationError("Only company admins can update company details.")

    from apps.common.models import Industry

    allowed = {"name", "size", "country", "website", "description", "logo", "custom_industry"}
    update_fields: list[str] = []

    if "industries" in data:
        industry_slugs = data.pop("industries")
        company.industries.set(Industry.objects.filter(slug__in=industry_slugs))

    for field, value in data.items():
        if field in allowed:
            setattr(company, field, value)
            update_fields.append(field)

    if update_fields:
        update_fields.append("updated_at")
        company.save(update_fields=update_fields)
    return company


@transaction.atomic
def soft_delete_company(*, user: User, company: Company) -> Company:
    """Soft-delete a company.

    Rules:
      * The acting user cannot delete their last non-deleted membership.
      * After deletion, every user whose default was this company has their default
        transferred to another of their non-deleted memberships, ordered by created_at.
      * Users whose current active (user.company) was this company get switched to
        their new default company. Candidate-only users are untouched by construction
        because they have no company membership.
    """
    if company.is_deleted:
        return company

    actor_live_memberships = _user_live_memberships(user).exclude(company=company)
    if not actor_live_memberships.exists():
        raise ApplicationError("Cannot delete your only remaining company.")

    company.is_deleted = True
    company.deleted_at = timezone.now()
    company.save(update_fields=["is_deleted", "deleted_at", "updated_at"])

    affected = CompanyMembership.objects.filter(company=company).select_related("user")
    for membership in affected:
        if not membership.is_default:
            continue
        # Drop the deleted company's default first so the partial UNIQUE constraint
        # stays satisfied when we pick a replacement.
        membership.is_default = False
        membership.save(update_fields=["is_default"])

        next_default = (
            CompanyMembership.objects.filter(user=membership.user, company__is_deleted=False)
            .order_by("created_at")
            .first()
        )
        if next_default is None:
            continue
        next_default.is_default = True
        next_default.save(update_fields=["is_default"])

    # Reassign active-company pointer for any user whose active was this company.
    User.objects.filter(company=company).update(company=None)
    for user_obj in User.objects.filter(company__isnull=True, memberships__is_default=True).distinct():
        default_membership = user_obj.memberships.filter(is_default=True).first()
        if default_membership is not None:
            user_obj.company = default_membership.company
            user_obj.save(update_fields=["company", "updated_at"])

    return company


@transaction.atomic
def set_default_company_for_user(*, user: User, company_id: UUID) -> CompanyMembership:
    """Thin wrapper over services.membership.set_default_company for consistent naming."""
    from apps.accounts.services.membership import set_default_company

    return set_default_company(user=user, company_id=company_id)

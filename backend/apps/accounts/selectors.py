from uuid import UUID

from django.db.models import QuerySet

from apps.accounts.models import Company, User


def get_user_by_email(*, email: str) -> User | None:
    """Retrieve a user by email, with company pre-loaded."""
    return User.objects.select_related("company").filter(email=email).first()


def get_company_users(*, company: Company) -> QuerySet[User]:
    """Return all users belonging to a company."""
    return User.objects.filter(company=company).select_related("company").order_by("-created_at")


def get_user_by_id(*, user_id: UUID) -> User | None:
    """Retrieve a user by ID, with company pre-loaded."""
    return User.objects.select_related("company").filter(id=user_id).first()

from decimal import Decimal
from uuid import UUID

from django.db.models import Q, QuerySet

from apps.accounts.models import Company, User
from apps.accounts.selectors import get_user_live_company_ids
from apps.applications.models import Application
from apps.vacancies.models import Vacancy


def get_vacancy_applications(
    *,
    vacancy: Vacancy,
    status: str | None = None,
    ordering: str = "-created_at",
) -> QuerySet[Application]:
    """Return applications for a vacancy, optionally filtered by status."""
    allowed_orderings = {
        "-created_at",
        "created_at",
        "-match_score",
        "match_score",
    }
    if ordering not in allowed_orderings:
        ordering = "-created_at"

    qs = Application.objects.filter(vacancy=vacancy, is_deleted=False).select_related("candidate")
    if status:
        qs = qs.filter(status=status)
    return qs.order_by(ordering)


def get_vacancy_applications_filtered(
    *,
    vacancy: Vacancy,
    status: str | None = None,
    min_score: Decimal | None = None,
    max_score: Decimal | None = None,
    ordering: str = "-created_at",
    search: str | None = None,
) -> QuerySet[Application]:
    """Return filtered applications for a vacancy with score range and search."""
    allowed_orderings = {
        "-created_at",
        "created_at",
        "-match_score",
        "match_score",
        "-candidate_name",
        "candidate_name",
    }
    if ordering not in allowed_orderings:
        ordering = "-created_at"

    qs = (
        Application.objects.filter(vacancy=vacancy, is_deleted=False)
        .select_related("candidate")
        .prefetch_related("sessions")
    )

    if status:
        qs = qs.filter(status=status)

    if min_score is not None:
        qs = qs.filter(match_score__gte=min_score)

    if max_score is not None:
        qs = qs.filter(match_score__lte=max_score)

    if search:
        qs = qs.filter(Q(candidate_name__icontains=search) | Q(candidate_email__icontains=search))

    return qs.order_by(ordering)


def get_user_applications_filtered(
    *,
    user: User,
    status: str | None = None,
    vacancy_id: UUID | None = None,
    min_score: Decimal | None = None,
    max_score: Decimal | None = None,
    ordering: str = "-created_at",
    search: str | None = None,
) -> QuerySet[Application]:
    """Return filtered applications across every company the user belongs to."""
    allowed_orderings = {
        "-created_at",
        "created_at",
        "-match_score",
        "match_score",
        "-candidate_name",
        "candidate_name",
    }
    if ordering not in allowed_orderings:
        ordering = "-created_at"

    qs = (
        Application.objects.filter(
            vacancy__company_id__in=get_user_live_company_ids(user=user),
            is_deleted=False,
        )
        .select_related("candidate", "vacancy", "vacancy__company")
        .prefetch_related("sessions")
    )

    if vacancy_id:
        qs = qs.filter(vacancy_id=vacancy_id)
    if status:
        qs = qs.filter(status=status)
    if min_score is not None:
        qs = qs.filter(match_score__gte=min_score)
    if max_score is not None:
        qs = qs.filter(match_score__lte=max_score)
    if search:
        qs = qs.filter(
            Q(candidate_name__icontains=search)
            | Q(candidate_email__icontains=search)
            | Q(vacancy__title__icontains=search)
        )

    return qs.order_by(ordering)


def get_application_by_id(
    *,
    application_id: UUID,
    company: Company | None = None,
    user: User | None = None,
) -> Application | None:
    """Get a single application, scoped to a company or any company the user belongs to."""
    qs = Application.objects.select_related("vacancy", "vacancy__company", "candidate")
    if user:
        qs = qs.filter(vacancy__company_id__in=get_user_live_company_ids(user=user))
    elif company:
        qs = qs.filter(vacancy__company=company)
    return qs.filter(id=application_id).first()


def get_candidate_applications(
    *,
    candidate: User,
    candidate_email: str,
) -> QuerySet[Application]:
    """Return all applications bound to the candidate or matching their email."""
    return (
        Application.objects.filter(Q(candidate=candidate) | Q(candidate_email=candidate_email))
        .select_related("vacancy", "vacancy__company")
        .prefetch_related("sessions")
        .order_by("-created_at")
    )


def get_candidate_application_by_id(
    *,
    application_id: UUID,
    candidate: User,
    candidate_email: str,
) -> Application | None:
    """Get a single application for a candidate view."""
    return (
        Application.objects.select_related("vacancy", "vacancy__company")
        .filter(Q(candidate=candidate) | Q(candidate_email=candidate_email), id=application_id)
        .first()
    )

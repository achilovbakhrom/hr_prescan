from uuid import UUID

from django.db.models import QuerySet

from apps.accounts.models import Company
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

    qs = (
        Application.objects
        .filter(vacancy=vacancy)
        .select_related("candidate")
    )
    if status:
        qs = qs.filter(status=status)
    return qs.order_by(ordering)


def get_application_by_id(
    *,
    application_id: UUID,
    company: Company | None = None,
) -> Application | None:
    """Get a single application, optionally scoped to a company via vacancy."""
    qs = Application.objects.select_related("vacancy", "vacancy__company", "candidate")
    if company:
        qs = qs.filter(vacancy__company=company)
    return qs.filter(id=application_id).first()


def get_candidate_applications(
    *,
    candidate_email: str,
) -> QuerySet[Application]:
    """Return all applications by a candidate email for their dashboard."""
    return (
        Application.objects
        .filter(candidate_email=candidate_email)
        .select_related("vacancy", "vacancy__company")
        .order_by("-created_at")
    )


def get_candidate_application_by_id(
    *,
    application_id: UUID,
    candidate_email: str,
) -> Application | None:
    """Get a single application for a candidate view."""
    return (
        Application.objects
        .select_related("vacancy", "vacancy__company")
        .filter(id=application_id, candidate_email=candidate_email)
        .first()
    )

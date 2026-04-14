from django.db.models import Avg, QuerySet

from apps.accounts.models import Company
from apps.applications.models import Application
from apps.interviews.models import Interview
from apps.vacancies.models import Vacancy


def get_dashboard_stats(*, company: Company) -> dict:
    """Aggregate dashboard metrics for a company."""
    active_vacancies_count = Vacancy.objects.filter(
        company=company,
        status=Vacancy.Status.PUBLISHED,
    ).count()

    total_candidates_count = Application.objects.filter(
        vacancy__company=company,
        is_deleted=False,
    ).count()

    pending_interviews_count = Interview.objects.filter(
        application__vacancy__company=company,
        application__is_deleted=False,
        status=Interview.Status.PENDING,
    ).count()

    completed_interviews_count = Interview.objects.filter(
        application__vacancy__company=company,
        application__is_deleted=False,
        status=Interview.Status.COMPLETED,
    ).count()

    avg_match = Application.objects.filter(
        vacancy__company=company,
        is_deleted=False,
        match_score__isnull=False,
    ).aggregate(avg=Avg("match_score"))["avg"]

    average_match_score = float(avg_match) if avg_match is not None else None

    return {
        "active_vacancies_count": active_vacancies_count,
        "total_candidates_count": total_candidates_count,
        "pending_interviews_count": pending_interviews_count,
        "completed_interviews_count": completed_interviews_count,
        "average_match_score": average_match_score,
    }


def get_recent_applications(
    *,
    company: Company,
    limit: int = 5,
) -> QuerySet[Application]:
    """Return the most recent applications for a company."""
    return (
        Application.objects.filter(vacancy__company=company, is_deleted=False)
        .select_related("vacancy")
        .order_by("-created_at")[:limit]
    )


def get_pending_company_interviews(
    *,
    company: Company,
    limit: int = 5,
) -> QuerySet[Interview]:
    """Return pending interviews (awaiting candidate) for a company."""
    return (
        Interview.objects.filter(
            application__vacancy__company=company,
            status=Interview.Status.PENDING,
        )
        .select_related(
            "application",
            "application__vacancy",
        )
        .order_by("-created_at")[:limit]
    )

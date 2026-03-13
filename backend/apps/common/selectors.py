from django.db.models import Avg, Count, Q, QuerySet
from django.utils import timezone

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
    ).count()

    pending_interviews_count = Interview.objects.filter(
        application__vacancy__company=company,
        status=Interview.Status.SCHEDULED,
    ).count()

    completed_interviews_count = Interview.objects.filter(
        application__vacancy__company=company,
        status=Interview.Status.COMPLETED,
    ).count()

    avg_match = Application.objects.filter(
        vacancy__company=company,
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
        Application.objects
        .filter(vacancy__company=company)
        .select_related("vacancy")
        .order_by("-created_at")[:limit]
    )


def get_upcoming_company_interviews(
    *,
    company: Company,
    limit: int = 5,
) -> QuerySet[Interview]:
    """Return the next upcoming scheduled interviews for a company."""
    now = timezone.now()
    return (
        Interview.objects
        .filter(
            application__vacancy__company=company,
            status=Interview.Status.SCHEDULED,
            scheduled_at__gte=now,
        )
        .select_related(
            "application",
            "application__vacancy",
        )
        .order_by("scheduled_at")[:limit]
    )

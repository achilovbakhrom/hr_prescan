from django.db.models import Avg, Count, Q, QuerySet
from django.utils import timezone

from apps.accounts.models import Company, User
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
        Application.objects
        .filter(vacancy__company=company, is_deleted=False)
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
        Interview.objects
        .filter(
            application__vacancy__company=company,
            status=Interview.Status.PENDING,
        )
        .select_related(
            "application",
            "application__vacancy",
        )
        .order_by("-created_at")[:limit]
    )


def get_candidate_dashboard_stats(user: User) -> dict:
    """Return application counts by status for the candidate."""
    apps = Application.objects.filter(candidate=user, is_deleted=False)
    return {
        "total_applications": apps.count(),
        "applied": apps.filter(status=Application.Status.APPLIED).count(),
        "prescanned": apps.filter(status=Application.Status.PRESCANNED).count(),
        "interviewed": apps.filter(status=Application.Status.INTERVIEWED).count(),
        "shortlisted": apps.filter(status=Application.Status.SHORTLISTED).count(),
        "hired": apps.filter(status=Application.Status.HIRED).count(),
        "rejected": apps.filter(status=Application.Status.REJECTED).count(),
    }


def get_recommended_vacancies(user: User, limit: int = 5) -> QuerySet[Vacancy]:
    """Return recent published vacancies as recommendations for a candidate."""
    return (
        Vacancy.objects
        .filter(status=Vacancy.Status.PUBLISHED)
        .select_related("company")
        .order_by("-created_at")[:limit]
    )


def get_company_analytics(*, company: Company) -> dict:
    """Return company-level hiring analytics."""
    vacancies = Vacancy.objects.filter(company=company)
    applications = Application.objects.filter(
        vacancy__company=company, is_deleted=False,
    )
    interviews = Interview.objects.filter(
        application__vacancy__company=company,
    )

    # Hiring funnel
    funnel = {
        "applied": applications.filter(
            status=Application.Status.APPLIED,
        ).count(),
        "prescanned": applications.filter(
            status=Application.Status.PRESCANNED,
        ).count(),
        "interviewed": applications.filter(
            status=Application.Status.INTERVIEWED,
        ).count(),
        "shortlisted": applications.filter(
            status=Application.Status.SHORTLISTED,
        ).count(),
        "hired": applications.filter(
            status=Application.Status.HIRED,
        ).count(),
        "rejected": applications.filter(
            status=Application.Status.REJECTED,
        ).count(),
        "total": applications.count(),
    }

    # Vacancy performance (top 5 by application count)
    vacancy_performance = list(
        vacancies.filter(status=Vacancy.Status.PUBLISHED)
        .annotate(
            app_count=Count(
                "applications",
                filter=Q(applications__is_deleted=False),
            ),
            avg_score=Avg(
                "applications__match_score",
                filter=Q(applications__is_deleted=False),
            ),
        )
        .order_by("-app_count")[:5]
        .values("id", "title", "app_count", "avg_score")
    )

    # Interview insights
    total_interviews = interviews.count()
    completed_interviews = interviews.filter(
        status=Interview.Status.COMPLETED,
    ).count()
    avg_score = interviews.filter(
        status=Interview.Status.COMPLETED,
    ).aggregate(avg=Avg("overall_score"))["avg"]

    return {
        "funnel": funnel,
        "vacancy_performance": vacancy_performance,
        "interview_insights": {
            "total": total_interviews,
            "completed": completed_interviews,
            "completion_rate": (
                round(completed_interviews / total_interviews * 100)
                if total_interviews > 0
                else 0
            ),
            "average_score": (
                round(float(avg_score), 1) if avg_score else None
            ),
        },
    }

from datetime import timedelta
from uuid import UUID

from django.db.models import Avg, Count, DurationField, ExpressionWrapper, F, Q
from django.utils import timezone

from apps.accounts.models import Company, User
from apps.accounts.selectors import get_user_live_company_ids
from apps.applications.models import Application
from apps.interviews.models import Interview
from apps.vacancies.models import Vacancy


def _get_hiring_funnel(applications):
    return {
        "applied": applications.filter(status=Application.Status.APPLIED).count(),
        "prescanned": applications.filter(status=Application.Status.PRESCANNED).count(),
        "interviewed": applications.filter(status=Application.Status.INTERVIEWED).count(),
        "shortlisted": applications.filter(status=Application.Status.SHORTLISTED).count(),
        "hired": applications.filter(status=Application.Status.HIRED).count(),
        "rejected": applications.filter(status=Application.Status.REJECTED).count(),
        "total": applications.count(),
    }


def _get_vacancy_performance(vacancies):
    performance = list(
        vacancies.filter(status=Vacancy.Status.PUBLISHED)
        .annotate(
            app_count=Count("applications", filter=Q(applications__is_deleted=False)),
            interviewed_count=Count(
                "applications",
                filter=Q(
                    applications__is_deleted=False,
                    applications__status__in=[
                        Application.Status.INTERVIEWED,
                        Application.Status.SHORTLISTED,
                        Application.Status.HIRED,
                    ],
                ),
            ),
            hired_count=Count(
                "applications",
                filter=Q(
                    applications__is_deleted=False,
                    applications__status=Application.Status.HIRED,
                ),
            ),
            rejected_count=Count(
                "applications",
                filter=Q(
                    applications__is_deleted=False,
                    applications__status=Application.Status.REJECTED,
                ),
            ),
            avg_score=Avg(
                "applications__match_score",
                filter=Q(applications__is_deleted=False),
            ),
        )
        .order_by("-app_count")[:5]
        .values(
            "id",
            "title",
            "app_count",
            "interviewed_count",
            "hired_count",
            "rejected_count",
            "avg_score",
        )
    )
    for vacancy in performance:
        app_count = vacancy["app_count"] or 0
        vacancy["avg_score"] = round(float(vacancy["avg_score"]), 1) if vacancy["avg_score"] is not None else None
        vacancy["hire_rate"] = round(vacancy["hired_count"] / app_count * 100) if app_count else 0
        vacancy["rejection_rate"] = round(vacancy["rejected_count"] / app_count * 100) if app_count else 0
    return performance


def _get_interview_insights(interviews):
    total_interviews = interviews.count()
    completed_interviews = interviews.filter(status=Interview.Status.COMPLETED).count()
    avg_score = interviews.filter(status=Interview.Status.COMPLETED).aggregate(
        avg=Avg("overall_score"),
    )["avg"]
    return {
        "total": total_interviews,
        "completed": completed_interviews,
        "completion_rate": (round(completed_interviews / total_interviews * 100) if total_interviews > 0 else 0),
        "average_score": round(float(avg_score), 1) if avg_score else None,
    }


def _get_status_breakdown(applications):
    total = applications.count()
    counts = applications.values("status").annotate(count=Count("id"))
    by_status = {item["status"]: item["count"] for item in counts}
    return [
        {
            "status": status,
            "count": by_status.get(status, 0),
            "percentage": round(by_status.get(status, 0) / total * 100) if total else 0,
        }
        for status, _label in Application.Status.choices
    ]


def _get_score_distribution(applications):
    scored = applications.exclude(match_score__isnull=True)
    buckets = [
        ("low", scored.filter(match_score__lt=40).count()),
        ("medium", scored.filter(match_score__gte=40, match_score__lt=60).count()),
        ("good", scored.filter(match_score__gte=60, match_score__lt=80).count()),
        ("strong", scored.filter(match_score__gte=80).count()),
    ]
    return [{"bucket": bucket, "count": count} for bucket, count in buckets]


def _get_process_metrics(*, vacancies, applications, interviews):
    now = timezone.now()
    decided = applications.filter(
        status__in=[Application.Status.HIRED, Application.Status.REJECTED],
    )
    avg_decision_duration = decided.aggregate(
        average=Avg(
            ExpressionWrapper(
                F("updated_at") - F("created_at"),
                output_field=DurationField(),
            ),
        ),
    )["average"]
    return {
        "active_vacancies": vacancies.filter(
            status=Vacancy.Status.PUBLISHED,
            is_deleted=False,
        ).count(),
        "pending_interviews": interviews.filter(
            status__in=[Interview.Status.PENDING, Interview.Status.IN_PROGRESS],
        ).count(),
        "stale_applications": applications.filter(
            status__in=[Application.Status.APPLIED, Application.Status.PRESCANNED],
            updated_at__lt=now - timedelta(days=7),
        ).count(),
        "average_decision_days": (
            round(avg_decision_duration.total_seconds() / 86400, 1) if avg_decision_duration else None
        ),
    }


def get_company_analytics(*, company: Company) -> dict:
    """Return company-level hiring analytics."""
    return get_companies_analytics(company_ids=[company.id])


def get_user_analytics(*, user: User) -> dict:
    """Return hiring analytics across every live company the HR user can access."""
    return get_companies_analytics(company_ids=get_user_live_company_ids(user=user))


def get_companies_analytics(*, company_ids: list[UUID]) -> dict:
    """Return hiring analytics scoped to a set of company IDs."""
    vacancies = Vacancy.objects.filter(company_id__in=company_ids)
    applications = Application.objects.filter(
        vacancy__company_id__in=company_ids,
        is_deleted=False,
    )
    interviews = Interview.objects.filter(application__vacancy__company_id__in=company_ids)
    return {
        "funnel": _get_hiring_funnel(applications),
        "vacancy_performance": _get_vacancy_performance(vacancies),
        "interview_insights": _get_interview_insights(interviews),
        "status_breakdown": _get_status_breakdown(applications),
        "score_distribution": _get_score_distribution(applications),
        "process_metrics": _get_process_metrics(
            vacancies=vacancies,
            applications=applications,
            interviews=interviews,
        ),
    }

from django.db.models import Avg, Count, Q

from apps.accounts.models import Company
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
        "completion_rate": (
            round(completed_interviews / total_interviews * 100) if total_interviews > 0 else 0
        ),
        "average_score": round(float(avg_score), 1) if avg_score else None,
    }


def get_company_analytics(*, company: Company) -> dict:
    """Return company-level hiring analytics."""
    vacancies = Vacancy.objects.filter(company=company)
    applications = Application.objects.filter(vacancy__company=company, is_deleted=False)
    interviews = Interview.objects.filter(application__vacancy__company=company)
    return {
        "funnel": _get_hiring_funnel(applications),
        "vacancy_performance": _get_vacancy_performance(vacancies),
        "interview_insights": _get_interview_insights(interviews),
    }

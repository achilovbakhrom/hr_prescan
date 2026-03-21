from uuid import UUID

from django.db.models import Count, Q, QuerySet

from apps.accounts.models import Company
from apps.vacancies.models import InterviewQuestion, Vacancy, VacancyCriteria


def get_company_vacancies(
    *,
    company: Company,
    status: str | None = None,
) -> QuerySet[Vacancy]:
    """Return vacancies for a company, optionally filtered by status."""
    qs = (
        Vacancy.objects
        .filter(company=company)
        .select_related("created_by")
        .annotate(
            criteria_count=Count("criteria"),
            questions_count=Count("questions", filter=Q(questions__is_active=True)),
            candidates_total=Count("applications", distinct=True),
            candidates_interviewed=Count(
                "applications",
                filter=Q(applications__status__in=["prescanned", "interviewed", "shortlisted"]),
                distinct=True,
            ),
            candidates_shortlisted=Count(
                "applications",
                filter=Q(applications__status="shortlisted"),
                distinct=True,
            ),
            candidates_rejected=Count(
                "applications",
                filter=Q(applications__status="rejected"),
                distinct=True,
            ),
        )
    )
    if status:
        qs = qs.filter(status=status)
    return qs


def get_vacancy_by_id(
    *,
    vacancy_id: UUID,
    company: Company | None = None,
) -> Vacancy | None:
    """Get a single vacancy, optionally scoped to a company."""
    qs = Vacancy.objects.select_related("company", "created_by")
    if company:
        qs = qs.filter(company=company)
    return qs.filter(id=vacancy_id).first()


def get_vacancy_by_share_token(*, share_token: UUID) -> Vacancy | None:
    """Get a vacancy by its share token for public/private access."""
    return (
        Vacancy.objects
        .select_related("company", "created_by")
        .filter(share_token=share_token)
        .first()
    )


def get_public_vacancies(
    *,
    search: str | None = None,
    location: str | None = None,
    is_remote: bool | None = None,
    employment_type: str | None = None,
    experience_level: str | None = None,
) -> QuerySet[Vacancy]:
    """Return published, public vacancies for the job board."""
    qs = (
        Vacancy.objects
        .filter(
            status=Vacancy.Status.PUBLISHED,
            visibility=Vacancy.Visibility.PUBLIC,
        )
        .select_related("company")
    )
    if search:
        qs = qs.filter(
            Q(title__icontains=search)
            | Q(description__icontains=search)
            | Q(skills__icontains=search)
        )
    if location:
        qs = qs.filter(location__icontains=location)
    if is_remote is not None:
        qs = qs.filter(is_remote=is_remote)
    if employment_type:
        qs = qs.filter(employment_type=employment_type)
    if experience_level:
        qs = qs.filter(experience_level=experience_level)
    return qs


def get_vacancy_criteria(
    *,
    vacancy: Vacancy,
    step: str | None = None,
) -> QuerySet[VacancyCriteria]:
    """Return criteria for a vacancy, optionally filtered by step."""
    qs = VacancyCriteria.objects.filter(vacancy=vacancy)
    if step:
        qs = qs.filter(step=step)
    return qs


def get_vacancy_questions(
    *,
    vacancy: Vacancy,
    active_only: bool = True,
    step: str | None = None,
) -> QuerySet[InterviewQuestion]:
    """Return questions for a vacancy, optionally filtered by step and active status."""
    qs = InterviewQuestion.objects.filter(vacancy=vacancy)
    if active_only:
        qs = qs.filter(is_active=True)
    if step:
        qs = qs.filter(step=step)
    return qs

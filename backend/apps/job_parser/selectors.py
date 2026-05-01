from uuid import UUID

from django.db.models import Q, QuerySet

from apps.accounts.models import User
from apps.accounts.selectors import get_user_live_company_ids
from apps.job_parser.models import ParsedVacancy, ParsedVacancySource


def get_user_sources(*, user: User, source_type: str | None = None) -> QuerySet[ParsedVacancySource]:
    qs = ParsedVacancySource.objects.select_related("company", "created_by").filter(
        company_id__in=get_user_live_company_ids(user=user),
    )
    if source_type:
        qs = qs.filter(source_type=source_type)
    return qs


def get_user_source_by_id(*, user: User, source_id: UUID) -> ParsedVacancySource | None:
    return get_user_sources(user=user).filter(id=source_id).first()


def get_user_parsed_vacancies(
    *,
    user: User,
    status: str | None = None,
    source_id: UUID | None = None,
) -> QuerySet[ParsedVacancy]:
    qs = ParsedVacancy.objects.select_related("source", "source__company", "imported_vacancy").filter(
        source__company_id__in=get_user_live_company_ids(user=user),
    )
    if status:
        qs = qs.filter(status=status)
    if source_id:
        qs = qs.filter(source_id=source_id)
    return qs


def get_user_parsed_vacancy_by_id(*, user: User, vacancy_id: UUID) -> ParsedVacancy | None:
    return get_user_parsed_vacancies(user=user).filter(id=vacancy_id).first()


def get_public_parsed_vacancies(
    *,
    search: str | None = None,
    location: str | None = None,
    employment_type: str | None = None,
    salary_min: int | None = None,
    salary_max: int | None = None,
) -> QuerySet[ParsedVacancy]:
    qs = ParsedVacancy.objects.select_related("source", "source__company").filter(
        source__is_active=True,
        source__company__is_deleted=False,
        status=ParsedVacancy.Status.ACTIVE,
    )
    if search:
        qs = qs.filter(
            Q(title__icontains=search)
            | Q(description__icontains=search)
            | Q(requirements__icontains=search)
            | Q(responsibilities__icontains=search)
            | Q(company_name__icontains=search),
        )
    if location:
        qs = qs.filter(location__icontains=location)
    if employment_type:
        qs = qs.filter(employment_type__icontains=employment_type)
    if salary_min is not None:
        qs = qs.filter(salary_max__gte=salary_min)
    if salary_max is not None:
        qs = qs.filter(salary_min__lte=salary_max)
    return qs


def get_public_parsed_vacancy_by_id(*, vacancy_id: UUID) -> ParsedVacancy | None:
    return get_public_parsed_vacancies().filter(id=vacancy_id).first()

from uuid import UUID

from django.contrib.postgres.search import SearchQuery, SearchRank, TrigramSimilarity
from django.db.models import Count, F, Q, QuerySet
from django.db.models.functions import Greatest

from apps.accounts.models import Company
from apps.vacancies.models import EmployerCompany, InterviewQuestion, Vacancy, VacancyCriteria


def get_company_vacancies(
    *,
    company: Company,
    status: str | None = None,
    include_deleted: bool = False,
) -> QuerySet[Vacancy]:
    """Return vacancies for a company, optionally filtered by status."""
    qs = (
        Vacancy.objects
        .filter(company=company)
        .select_related("created_by", "employer")
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
            candidates_hired=Count(
                "applications",
                filter=Q(applications__status="hired"),
                distinct=True,
            ),
        )
    )
    if not include_deleted:
        qs = qs.filter(is_deleted=False)
    if status:
        qs = qs.filter(status=status)
    return qs


def get_vacancy_by_id(
    *,
    vacancy_id: UUID,
    company: Company | None = None,
) -> Vacancy | None:
    """Get a single vacancy, optionally scoped to a company. Excludes soft-deleted."""
    qs = Vacancy.objects.select_related("company", "created_by", "employer").filter(is_deleted=False)
    if company:
        qs = qs.filter(company=company)
    return qs.filter(id=vacancy_id).first()


def get_vacancy_by_share_token(*, share_token: UUID) -> Vacancy | None:
    """Get a vacancy by its share token for public/private access."""
    return (
        Vacancy.objects
        .select_related("company", "created_by", "employer")
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
    salary_min: int | None = None,
    salary_max: int | None = None,
) -> QuerySet[Vacancy]:
    """Return published, public vacancies for the job board.

    Uses full-text search with SearchVector + trigram similarity for fuzzy matching.
    """
    qs = (
        Vacancy.objects
        .filter(
            status=Vacancy.Status.PUBLISHED,
            visibility=Vacancy.Visibility.PUBLIC,
            is_deleted=False,
        )
        .select_related("company", "employer")
    )
    if search:
        # Both english (stemming: program→programming) and simple (exact: Russian words)
        query_en = SearchQuery(search, config="english", search_type="websearch")
        query_simple = SearchQuery(search, config="simple", search_type="websearch")
        query_combined = query_en | query_simple

        fts_rank = SearchRank(F("search_vector"), query_combined)
        trigram_sim = Greatest(
            TrigramSimilarity("title", search),
            TrigramSimilarity("requirements", search),
        )
        qs = qs.annotate(
            fts_rank=fts_rank,
            trigram_sim=trigram_sim,
        ).filter(
            Q(search_vector=query_combined) | Q(trigram_sim__gte=0.15)
        ).order_by("-fts_rank", "-trigram_sim")
    if location:
        qs = qs.filter(location__icontains=location)
    if is_remote is not None:
        qs = qs.filter(is_remote=is_remote)
    if employment_type:
        qs = qs.filter(employment_type=employment_type)
    if experience_level:
        qs = qs.filter(experience_level=experience_level)
    if salary_min is not None:
        qs = qs.filter(salary_max__gte=salary_min)
    if salary_max is not None:
        qs = qs.filter(salary_min__lte=salary_max)
    return qs


def get_company_employers(*, company: Company) -> QuerySet[EmployerCompany]:
    """Return employer companies for a tenant."""
    return EmployerCompany.objects.filter(company=company)


def get_employer_by_id(*, employer_id: UUID, company: Company) -> EmployerCompany | None:
    """Get a single employer company scoped to a tenant."""
    return EmployerCompany.objects.filter(id=employer_id, company=company).first()


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

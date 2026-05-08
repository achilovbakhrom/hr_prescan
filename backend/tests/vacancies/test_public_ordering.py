from datetime import timedelta

from django.utils import timezone
from rest_framework.test import APIClient

from apps.job_parser.models import ParsedVacancy, ParsedVacancySource
from apps.vacancies.models import Vacancy
from tests.factories import VacancyFactory


def _parsed_vacancy(company, hr_user, *, title: str) -> ParsedVacancy:
    source = ParsedVacancySource.objects.create(
        company=company,
        created_by=hr_user,
        name=f"{title} source",
        source_type=ParsedVacancySource.Type.HH_UZ,
        is_active=True,
    )
    return ParsedVacancy.objects.create(
        source=source,
        external_id="hh-1",
        external_url="https://hh.uz/vacancy/1",
        title=title,
        description="Build public APIs",
        requirements="Python",
        responsibilities="Develop services",
        skills=["Python"],
        location="Tashkent",
        company_name="External Co",
        status=ParsedVacancy.Status.ACTIVE,
        fingerprint=f"parsed-public-{title}",
    )


def _set_created_at(instance, value):
    instance.__class__.objects.filter(id=instance.id).update(created_at=value)
    instance.created_at = value


def _create_mixed_vacancies(company, hr_user):
    now = timezone.now()
    older_internal = VacancyFactory(
        company=company,
        created_by=hr_user,
        title="Older Internal Role",
        status=Vacancy.Status.PUBLISHED,
        visibility=Vacancy.Visibility.PUBLIC,
    )
    newer_internal = VacancyFactory(
        company=company,
        created_by=hr_user,
        title="Newer Internal Role",
        status=Vacancy.Status.PUBLISHED,
        visibility=Vacancy.Visibility.PUBLIC,
    )
    older_parsed = _parsed_vacancy(company, hr_user, title="Older Parsed Role")
    newer_parsed = _parsed_vacancy(company, hr_user, title="Newer Parsed Role")
    _set_created_at(older_internal, now - timedelta(days=4))
    _set_created_at(newer_internal, now - timedelta(days=3))
    _set_created_at(older_parsed, now - timedelta(days=2))
    _set_created_at(newer_parsed, now - timedelta(days=1))
    return newer_internal, older_internal, newer_parsed, older_parsed


def test_public_job_board_lists_internal_vacancies_before_parsed_vacancies(company, hr_user):
    expected = _create_mixed_vacancies(company, hr_user)

    response = APIClient().get("/api/public/vacancies/")

    assert response.status_code == 200
    assert [item["id"] for item in response.data] == [str(vacancy.id) for vacancy in expected]


def test_public_job_board_paginates_internal_vacancies_before_parsed_vacancies(company, hr_user):
    newer_internal, older_internal, newer_parsed, older_parsed = _create_mixed_vacancies(company, hr_user)

    first_page = APIClient().get("/api/public/vacancies/?page=1&page_size=2")
    second_page = APIClient().get("/api/public/vacancies/?page=2&page_size=2")

    assert first_page.status_code == 200
    assert second_page.status_code == 200
    assert [item["id"] for item in first_page.data["results"]] == [
        str(newer_internal.id),
        str(older_internal.id),
    ]
    assert [item["id"] for item in second_page.data["results"]] == [
        str(newer_parsed.id),
        str(older_parsed.id),
    ]

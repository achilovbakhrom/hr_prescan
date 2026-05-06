from rest_framework.test import APIClient

from apps.job_parser.models import ParsedVacancy, ParsedVacancySource
from apps.vacancies.models import Vacancy
from tests.factories import VacancyFactory


def _parsed_vacancy(company, hr_user) -> ParsedVacancy:
    source = ParsedVacancySource.objects.create(
        company=company,
        created_by=hr_user,
        name="HH content",
        source_type=ParsedVacancySource.Type.HH_UZ,
        is_active=True,
    )
    return ParsedVacancy.objects.create(
        source=source,
        external_id="hh-1",
        external_url="https://hh.uz/vacancy/1",
        title="External Python Developer",
        description="Build public APIs",
        requirements="Python",
        responsibilities="Develop services",
        skills=["Python"],
        salary_min=1000,
        salary_max=2000,
        salary_currency="USD",
        location="Tashkent",
        company_name="External Co",
        status=ParsedVacancy.Status.ACTIVE,
        fingerprint="parsed-public",
    )


def test_public_job_board_includes_parsed_vacancies_as_read_only_with_source_url(company, hr_user):
    internal = VacancyFactory(
        company=company,
        created_by=hr_user,
        title="Internal Product Manager",
        status=Vacancy.Status.PUBLISHED,
        visibility=Vacancy.Visibility.PUBLIC,
    )
    parsed = _parsed_vacancy(company, hr_user)

    response = APIClient().get("/api/public/vacancies/")

    assert response.status_code == 200
    by_id = {item["id"]: item for item in response.data}
    assert by_id[str(internal.id)]["can_apply"] is True
    assert by_id[str(internal.id)]["content_source"] == "internal"
    assert by_id[str(parsed.id)]["can_apply"] is False
    assert by_id[str(parsed.id)]["content_source"] == "parsed"
    assert by_id[str(parsed.id)]["external_url"] == "https://hh.uz/vacancy/1"
    assert by_id[str(parsed.id)]["has_contact_info"] is False


def test_public_job_board_excludes_unreachable_parsed_vacancies(company, hr_user):
    parsed = _parsed_vacancy(company, hr_user)
    parsed.external_url = ""
    parsed.save(update_fields=["external_url", "updated_at"])

    response = APIClient().get("/api/public/vacancies/")

    assert response.status_code == 200
    assert str(parsed.id) not in {item["id"] for item in response.data}


def test_public_parsed_vacancy_detail_is_read_only(company, hr_user):
    parsed = _parsed_vacancy(company, hr_user)

    response = APIClient().get(f"/api/public/vacancies/{parsed.id}/")

    assert response.status_code == 200
    assert response.data["id"] == str(parsed.id)
    assert response.data["title"] == "External Python Developer"
    assert response.data["company_name"] == "External Co"
    assert response.data["company"] is None
    assert response.data["can_apply"] is False
    assert response.data["cv_required"] is False
    assert response.data["interview_duration"] == 0
    assert response.data["telegram_code"] is None
    assert response.data["salary_min"] == "1000.00"
    assert response.data["salary_max"] == "2000.00"
    assert response.data["salary_currency"] == "USD"
    assert response.data["is_remote"] is False
    assert response.data["external_url"] == "https://hh.uz/vacancy/1"
    assert response.data["has_contact_info"] is False


def test_public_parsed_vacancy_detail_returns_404_when_no_contact_or_source_url(company, hr_user):
    parsed = _parsed_vacancy(company, hr_user)
    parsed.external_url = ""
    parsed.save(update_fields=["external_url", "updated_at"])

    response = APIClient().get(f"/api/public/vacancies/{parsed.id}/")

    assert response.status_code == 404

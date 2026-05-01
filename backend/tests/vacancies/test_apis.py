from unittest.mock import patch

from rest_framework.test import APIClient

from apps.accounts.permissions import HRPermissions
from apps.vacancies.models import InterviewQuestion, ScreeningStep, Vacancy, VacancyCriteria
from apps.vacancies.services import create_default_criteria
from tests.factories import CompanyFactory, CompanyMembershipFactory, UserFactory, VacancyFactory


def _member_vacancy_in_second_company():
    default_company = CompanyFactory()
    second_company = CompanyFactory()
    user = UserFactory(
        company=default_company,
        role="hr",
        hr_permissions=[HRPermissions.MANAGE_VACANCIES],
    )
    CompanyMembershipFactory(
        user=user,
        company=second_company,
        role="hr",
        hr_permissions=[HRPermissions.MANAGE_VACANCIES],
        is_default=False,
    )
    vacancy = VacancyFactory(company=second_company, created_by=user, status=Vacancy.Status.DRAFT)
    return user, vacancy


def test_status_update_uses_all_user_company_memberships():
    user, vacancy = _member_vacancy_in_second_company()
    create_default_criteria(vacancy=vacancy, step=ScreeningStep.PRESCANNING)
    InterviewQuestion.objects.create(
        vacancy=vacancy,
        text="Why are you interested in this role?",
        step=ScreeningStep.PRESCANNING,
        is_active=True,
        order=1,
    )

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.patch(
        f"/api/hr/vacancies/{vacancy.id}/status/",
        {"action": "publish"},
        format="json",
    )

    assert response.status_code == 200
    vacancy.refresh_from_db()
    assert vacancy.status == Vacancy.Status.PUBLISHED


def test_criteria_buttons_use_all_user_company_memberships():
    user, vacancy = _member_vacancy_in_second_company()
    client = APIClient()
    client.force_authenticate(user=user)

    create_response = client.post(
        f"/api/hr/vacancies/{vacancy.id}/criteria/",
        {"name": "API Design", "description": "Can design practical APIs", "weight": 3},
        format="json",
    )
    assert create_response.status_code == 201

    criteria_id = create_response.data["id"]
    update_response = client.put(
        f"/api/hr/vacancies/{vacancy.id}/criteria/{criteria_id}/",
        {"weight": 4},
        format="json",
    )
    assert update_response.status_code == 200
    assert update_response.data["weight"] == 4

    list_response = client.get(f"/api/hr/vacancies/{vacancy.id}/criteria/")
    assert list_response.status_code == 200
    assert any(item["id"] == criteria_id for item in list_response.data)


def test_question_buttons_use_all_user_company_memberships():
    user, vacancy = _member_vacancy_in_second_company()
    client = APIClient()
    client.force_authenticate(user=user)

    create_response = client.post(
        f"/api/hr/vacancies/{vacancy.id}/questions/",
        {"text": "How do you debug a slow API?", "category": "Hard Skill"},
        format="json",
    )
    assert create_response.status_code == 201

    question_id = create_response.data["id"]
    update_response = client.put(
        f"/api/hr/vacancies/{vacancy.id}/questions/{question_id}/",
        {"category": "Domain Knowledge"},
        format="json",
    )
    assert update_response.status_code == 200
    assert update_response.data["category"] == "Domain Knowledge"

    list_response = client.get(f"/api/hr/vacancies/{vacancy.id}/questions/")
    assert list_response.status_code == 200
    assert any(item["id"] == question_id for item in list_response.data)


def test_generate_and_regenerate_buttons_use_all_user_company_memberships():
    user, vacancy = _member_vacancy_in_second_company()
    VacancyCriteria.objects.create(
        vacancy=vacancy,
        name="API Design",
        weight=3,
        order=1,
        step=ScreeningStep.PRESCANNING,
    )
    client = APIClient()
    client.force_authenticate(user=user)

    with (
        patch("apps.vacancies.apis.questions.generate_interview_questions") as questions_mock,
        patch("apps.vacancies.tasks.generate_keywords_task.delay") as keywords_mock,
    ):
        questions_mock.return_value = [
            InterviewQuestion.objects.create(
                vacancy=vacancy,
                text="How do you debug a slow API?",
                category="Hard Skill",
                step=ScreeningStep.PRESCANNING,
                order=1,
            )
        ]

        generate_response = client.post(
            f"/api/hr/vacancies/{vacancy.id}/questions/generate/",
            {"step": "prescanning"},
            format="json",
        )
        regenerate_response = client.post(f"/api/hr/vacancies/{vacancy.id}/regenerate-keywords/")

    assert generate_response.status_code == 201
    assert regenerate_response.status_code == 202
    keywords_mock.assert_called_once_with(str(vacancy.id))

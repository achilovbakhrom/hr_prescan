from decimal import Decimal
from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.accounts.models import CompanyMembership, User
from apps.accounts.permissions import HRPermissions
from apps.applications.apis import (
    CandidateApplicationListApi,
    HRAllCandidatesListApi,
    HRApplicationDetailApi,
    HRApplicationListApi,
)
from apps.interviews.apis import HRApplicationInterviewApi
from apps.interviews.models import Interview
from apps.notifications.apis import HRMessageListApi, SendCandidateEmailApi
from tests.factories import ApplicationFactory, CompanyFactory, InterviewFactory, UserFactory, VacancyFactory


def _hr_user_with_two_companies(permissions: list[str] | None = None):
    permissions = permissions or [HRPermissions.MANAGE_CANDIDATES]
    default_company = CompanyFactory()
    second_company = CompanyFactory()
    user = UserFactory(
        company=default_company,
        role=User.Role.HR,
        hr_permissions=permissions,
    )
    CompanyMembership.objects.create(
        user=user,
        company=default_company,
        role=User.Role.HR,
        hr_permissions=permissions,
        is_default=True,
    )
    CompanyMembership.objects.create(
        user=user,
        company=second_company,
        role=User.Role.HR,
        hr_permissions=permissions,
    )
    return user, second_company


def test_vacancy_candidates_api_uses_user_memberships():
    user, second_company = _hr_user_with_two_companies()
    vacancy = VacancyFactory(company=second_company, created_by=user)
    application = ApplicationFactory(vacancy=vacancy, candidate_name="Jane Candidate")
    factory = APIRequestFactory()
    request = factory.get(f"/api/hr/vacancies/{vacancy.id}/candidates/", {"ordering": "-created_at"})
    force_authenticate(request, user=user)

    response = HRApplicationListApi.as_view()(request, vacancy_id=str(vacancy.id))

    assert response.status_code == status.HTTP_200_OK
    assert [item["id"] for item in response.data] == [str(application.id)]


def test_all_candidates_api_includes_all_user_membership_companies():
    user, second_company = _hr_user_with_two_companies()
    vacancy = VacancyFactory(company=second_company, created_by=user)
    application = ApplicationFactory(vacancy=vacancy, candidate_name="Jane Candidate")
    factory = APIRequestFactory()
    request = factory.get("/api/hr/candidates/", {"ordering": "-created_at"})
    force_authenticate(request, user=user)

    response = HRAllCandidatesListApi.as_view()(request)

    assert response.status_code == status.HTTP_200_OK
    assert [item["id"] for item in response.data] == [str(application.id)]


def test_candidate_detail_api_uses_user_memberships():
    user, second_company = _hr_user_with_two_companies()
    vacancy = VacancyFactory(company=second_company, created_by=user)
    application = ApplicationFactory(vacancy=vacancy, candidate_name="Jane Candidate")
    factory = APIRequestFactory()
    request = factory.get(f"/api/hr/candidates/{application.id}/")
    force_authenticate(request, user=user)

    response = HRApplicationDetailApi.as_view()(request, application_id=str(application.id))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == str(application.id)


def test_candidate_detail_api_includes_screening_scores():
    user, second_company = _hr_user_with_two_companies()
    vacancy = VacancyFactory(company=second_company, created_by=user)
    application = ApplicationFactory(vacancy=vacancy, candidate_name="Jane Candidate")
    InterviewFactory(
        application=application,
        session_type=Interview.SessionType.PRESCANNING,
        status=Interview.Status.COMPLETED,
        overall_score=Decimal("4.00"),
    )
    factory = APIRequestFactory()
    request = factory.get(f"/api/hr/candidates/{application.id}/")
    force_authenticate(request, user=user)

    response = HRApplicationDetailApi.as_view()(request, application_id=str(application.id))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["prescanning_score"] == 4.0
    assert response.data["interview_score"] is None


def test_candidate_applications_api_includes_scores(vacancy, candidate_user):
    application = ApplicationFactory(
        vacancy=vacancy,
        candidate=candidate_user,
        candidate_email=candidate_user.email,
        match_score=Decimal("85.00"),
    )
    InterviewFactory(
        application=application,
        session_type=Interview.SessionType.PRESCANNING,
        status=Interview.Status.COMPLETED,
        overall_score=Decimal("4.00"),
    )
    factory = APIRequestFactory()
    request = factory.get("/api/candidate/applications/")
    force_authenticate(request, user=candidate_user)

    response = CandidateApplicationListApi.as_view()(request)

    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]["match_score"] == "85.00"
    assert response.data[0]["prescanning_score"] == 4.0
    assert response.data[0]["interview_score"] is None


def test_candidate_interview_api_uses_user_memberships():
    user, second_company = _hr_user_with_two_companies([HRPermissions.MANAGE_INTERVIEWS])
    vacancy = VacancyFactory(company=second_company, created_by=user)
    application = ApplicationFactory(vacancy=vacancy, candidate_name="Jane Candidate")
    interview = InterviewFactory(
        application=application,
        session_type=Interview.SessionType.PRESCANNING,
        status=Interview.Status.PENDING,
    )
    factory = APIRequestFactory()
    request = factory.get(
        f"/api/hr/candidates/{application.id}/interview/",
        {"session_type": Interview.SessionType.PRESCANNING},
    )
    force_authenticate(request, user=user)

    response = HRApplicationInterviewApi.as_view()(request, application_id=str(application.id))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == str(interview.id)


def test_candidate_messages_api_uses_user_memberships():
    user, second_company = _hr_user_with_two_companies()
    candidate = UserFactory(company=None, role=User.Role.CANDIDATE)
    vacancy = VacancyFactory(company=second_company, created_by=user)
    application = ApplicationFactory(vacancy=vacancy, candidate=candidate)
    factory = APIRequestFactory()
    request = factory.get(f"/api/hr/candidates/{application.id}/messages/")
    force_authenticate(request, user=user)

    response = HRMessageListApi.as_view()(request, application_id=str(application.id))

    assert response.status_code == status.HTTP_200_OK


def test_candidate_email_api_uses_user_memberships():
    user, second_company = _hr_user_with_two_companies()
    vacancy = VacancyFactory(company=second_company, created_by=user)
    application = ApplicationFactory(vacancy=vacancy)
    factory = APIRequestFactory()
    request = factory.post(
        f"/api/hr/candidates/{application.id}/email/",
        {"subject": "Next step", "body": "Please check your email."},
        format="json",
    )
    force_authenticate(request, user=user)

    with patch("apps.notifications.tasks.send_candidate_email.delay") as delay:
        response = SendCandidateEmailApi.as_view()(request, application_id=str(application.id))

    assert response.status_code == status.HTTP_200_OK
    delay.assert_called_once()

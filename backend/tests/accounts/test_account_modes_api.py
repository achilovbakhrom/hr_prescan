from rest_framework.test import APIClient

from apps.accounts.models import CandidateProfile, CompanyMembership, User
from tests.factories import CompanyFactory, UserFactory


def _client_for(user: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def test_candidate_can_create_hr_space_without_losing_candidate_mode():
    user = UserFactory(company=None, role=User.Role.CANDIDATE)
    client = _client_for(user)

    response = client.post(
        "/api/auth/modes/hr-space/",
        {
            "company_name": "Acme Hiring",
            "industries": [],
            "size": "small",
            "country": "Uzbekistan",
        },
        format="json",
    )

    assert response.status_code == 201
    user.refresh_from_db()
    assert user.role == User.Role.ADMIN
    assert user.active_mode == User.ActiveMode.HR
    assert CandidateProfile.objects.filter(user=user).exists()
    assert set(response.data["available_modes"]) == {User.ActiveMode.HR, User.ActiveMode.CANDIDATE}

    switch_response = client.post("/api/auth/modes/switch/", {"mode": "candidate"}, format="json")

    assert switch_response.status_code == 200
    user.refresh_from_db()
    assert user.role == User.Role.ADMIN
    assert user.active_mode == User.ActiveMode.CANDIDATE
    assert user.company is None


def test_hr_can_create_candidate_space_and_switch_back_to_company():
    user = UserFactory(role=User.Role.ADMIN, active_mode=User.ActiveMode.HR)
    company = user.company
    CompanyMembership.objects.create(user=user, company=company, role=User.Role.ADMIN, is_default=True)
    client = _client_for(user)

    response = client.post(
        "/api/auth/modes/candidate-space/",
        {
            "first_name": "Admin",
            "last_name": "Candidate",
            "phone": "+998901234567",
            "headline": "Operations lead",
            "location": "Tashkent",
        },
        format="json",
    )

    assert response.status_code == 201
    user.refresh_from_db()
    assert user.role == User.Role.ADMIN
    assert user.active_mode == User.ActiveMode.CANDIDATE
    assert CandidateProfile.objects.filter(user=user, headline="Operations lead").exists()

    switch_response = client.post(
        "/api/auth/modes/switch/",
        {"mode": "hr", "company_id": str(company.id)},
        format="json",
    )

    assert switch_response.status_code == 200
    user.refresh_from_db()
    assert user.role == User.Role.ADMIN
    assert user.active_mode == User.ActiveMode.HR
    assert user.company_id == company.id


def test_cannot_switch_to_missing_candidate_space():
    user = UserFactory(role=User.Role.ADMIN, active_mode=User.ActiveMode.HR)
    client = _client_for(user)

    response = client.post("/api/auth/modes/switch/", {"mode": "candidate"}, format="json")

    assert response.status_code == 400
    assert "Create a candidate space" in response.data["detail"]


def test_hr_switch_can_target_specific_company():
    user = UserFactory(role=User.Role.ADMIN, active_mode=User.ActiveMode.CANDIDATE, company=None)
    first = CompanyFactory(account_owner=user, name="First")
    second = CompanyFactory(account_owner=user, name="Second")
    CompanyMembership.objects.create(user=user, company=first, role=User.Role.ADMIN, is_default=True)
    CompanyMembership.objects.create(user=user, company=second, role=User.Role.HR, is_default=False)
    CandidateProfile.objects.create(user=user)
    client = _client_for(user)

    response = client.post(
        "/api/auth/modes/switch/",
        {"mode": "hr", "company_id": str(second.id)},
        format="json",
    )

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.company_id == second.id
    assert user.role == User.Role.HR
    assert user.active_mode == User.ActiveMode.HR

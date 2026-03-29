"""HR permissions API E2E tests."""

import pytest

from helpers.api_client import ApiClient
from helpers.factories import (
    create_published_vacancy,
    invite_and_accept_hr,
    register_candidate,
    register_company,
    submit_application,
    unique_email,
)


@pytest.fixture()
def company_setup(api: ApiClient, request_context):
    """Set up a company with admin and HR users with different permissions."""
    admin_data = register_company(api)
    admin_token = admin_data["tokens"]["access"]
    api.set_token(admin_token)

    # HR with full permissions
    hr_full_api = ApiClient(request_context, api._base_url)
    hr_full = invite_and_accept_hr(api, hr_full_api, permissions=[
        "manage_vacancies", "manage_candidates", "manage_interviews",
        "manage_team", "view_analytics", "manage_settings",
    ])

    # HR with only manage_vacancies
    hr_limited_api = ApiClient(request_context, api._base_url)
    hr_limited = invite_and_accept_hr(api, hr_limited_api, permissions=["manage_vacancies"])

    return {
        "admin": admin_data,
        "hr_full": hr_full,
        "hr_limited": hr_limited,
    }


class TestAdminAccess:
    def test_admin_can_list_vacancies(self, api: ApiClient, company_setup):
        api.set_token(company_setup["admin"]["tokens"]["access"])
        resp = api.get("/hr/vacancies/")
        assert resp.status == 200

    def test_admin_can_access_team(self, api: ApiClient, company_setup):
        api.set_token(company_setup["admin"]["tokens"]["access"])
        resp = api.get("/hr/company/team/")
        assert resp.status == 200

    def test_admin_can_access_analytics(self, api: ApiClient, company_setup):
        api.set_token(company_setup["admin"]["tokens"]["access"])
        resp = api.get("/hr/analytics/")
        assert resp.status == 200


class TestHRPermissions:
    def test_hr_with_manage_vacancies_can_create(self, api: ApiClient, company_setup):
        api.set_token(company_setup["hr_full"]["tokens"]["access"])
        resp = api.post("/hr/vacancies/", data={
            "title": "HR Created",
            "description": "By HR.",
        })
        assert resp.status == 201

    def test_hr_without_manage_candidates_blocked(self, api: ApiClient, company_setup):
        """HR with only manage_vacancies cannot access candidate endpoints."""
        api.set_token(company_setup["hr_limited"]["tokens"]["access"])

        # Create vacancy first (allowed)
        vacancy = create_published_vacancy(api)

        resp = api.get(f"/hr/vacancies/{vacancy['id']}/candidates/")
        assert resp.status == 403

    def test_hr_without_manage_team_blocked(self, api: ApiClient, company_setup):
        api.set_token(company_setup["hr_limited"]["tokens"]["access"])
        resp = api.get("/hr/company/team/")
        assert resp.status == 403

    def test_hr_without_view_analytics_blocked(self, api: ApiClient, company_setup):
        api.set_token(company_setup["hr_limited"]["tokens"]["access"])
        resp = api.get("/hr/analytics/")
        assert resp.status == 403


class TestCandidateBlocked:
    def test_candidate_cannot_access_hr_endpoints(self, api: ApiClient):
        candidate = register_candidate(api)
        api.set_token(candidate["tokens"]["access"])

        resp = api.get("/hr/vacancies/")
        assert resp.status == 403

        resp = api.get("/hr/dashboard/")
        assert resp.status == 403


class TestCrossCompanyIsolation:
    def test_cannot_see_other_company_vacancies(self, api: ApiClient, request_context):
        """HR in company A should not see vacancies from company B."""
        # Company A
        company_a = register_company(api)
        api.set_token(company_a["tokens"]["access"])
        vacancy_a = create_published_vacancy(api)

        # Company B
        api_b = ApiClient(request_context, api._base_url)
        company_b = register_company(api_b)
        api_b.set_token(company_b["tokens"]["access"])

        resp = api_b.get("/hr/vacancies/")
        assert resp.status == 200
        data = resp.json()
        vacancies = data["results"] if isinstance(data, dict) else data
        vacancy_ids = [v["id"] for v in vacancies]
        assert vacancy_a["id"] not in vacancy_ids

"""Multi-company and invitation API E2E tests."""

import pytest

from helpers.api_client import ApiClient
from helpers.factories import (
    create_published_vacancy,
    invite_and_accept_hr,
    register_company,
    unique_email,
)


@pytest.fixture()
def two_companies(api: ApiClient, request_context):
    """Set up two companies with their admin users."""
    company_a = register_company(api)

    api_b = ApiClient(request_context, api._base_url)
    company_b = register_company(api_b)

    return {"a": company_a, "b": company_b}


class TestInvitations:
    def test_invite_hr(self, api: ApiClient, request_context):
        admin = register_company(api)
        api.set_token(admin["tokens"]["access"])

        email = unique_email("invite")
        resp = api.post("/hr/company/invite/", data={
            "email": email,
            "permissions": ["manage_vacancies", "manage_candidates"],
        })
        assert resp.status == 201
        body = resp.json()["invitation"]
        assert body["email"] == email
        assert "token" in body

    def test_accept_invitation_new_user(self, api: ApiClient, request_context):
        admin = register_company(api)
        api.set_token(admin["tokens"]["access"])

        hr_api = ApiClient(request_context, api._base_url)
        hr = invite_and_accept_hr(api, hr_api, permissions=["manage_vacancies"])

        assert hr["user"]["role"] == "hr"
        assert hr["user"]["company"]["id"] == admin["company"]["id"]

    def test_invite_existing_member_fails(self, api: ApiClient, request_context):
        admin = register_company(api)
        api.set_token(admin["tokens"]["access"])

        # Invite and accept first
        hr_api = ApiClient(request_context, api._base_url)
        hr = invite_and_accept_hr(api, hr_api)

        # Try to invite the same email again
        resp = api.post("/hr/company/invite/", data={
            "email": hr["email"],
        })
        assert resp.status == 400

    def test_cancel_invitation(self, api: ApiClient):
        admin = register_company(api)
        api.set_token(admin["tokens"]["access"])

        email = unique_email("cancel")
        invite_resp = api.post("/hr/company/invite/", data={"email": email})
        assert invite_resp.status == 201
        invitation_id = invite_resp.json()["invitation"]["id"]

        resp = api.delete("/hr/company/invite/", data={"invitation_id": invitation_id})
        assert resp.status == 204

    def test_list_invitations(self, api: ApiClient):
        admin = register_company(api)
        api.set_token(admin["tokens"]["access"])

        # Send two invitations
        api.post("/hr/company/invite/", data={"email": unique_email("a")})
        api.post("/hr/company/invite/", data={"email": unique_email("b")})

        resp = api.get("/hr/company/invite/")
        assert resp.status == 200
        assert len(resp.json()) >= 2


class TestSwitchCompany:
    def test_switch_company(self, api: ApiClient, request_context, two_companies):
        """User invited to company B can switch to it."""
        # Admin A invites a user
        api.set_token(two_companies["a"]["tokens"]["access"])
        hr_api = ApiClient(request_context, api._base_url)
        hr = invite_and_accept_hr(api, hr_api)

        # Now admin B invites the SAME user (existing user flow)
        api_b = ApiClient(request_context, api._base_url)
        api_b.set_token(two_companies["b"]["tokens"]["access"])

        invite_resp = api_b.post("/hr/company/invite/", data={
            "email": hr["email"],
        })
        assert invite_resp.status == 201
        invite_token = invite_resp.json()["invitation"]["token"]

        # HR user accepts company B invitation
        hr_api.set_token(hr["tokens"]["access"])
        resp = hr_api.post("/auth/accept-company-invitation/", data={
            "token": invite_token,
        })
        assert resp.status == 200

        # Verify user is now in company B
        me = hr_api.get("/auth/me/").json()
        assert me["company"]["id"] == two_companies["b"]["company"]["id"]

        # Switch back to company A
        resp = hr_api.post("/auth/switch-company/", data={
            "company_id": two_companies["a"]["company"]["id"],
        })
        assert resp.status == 200
        assert resp.json()["company"]["id"] == two_companies["a"]["company"]["id"]

    def test_my_companies(self, api: ApiClient, request_context, two_companies):
        """User with two memberships sees both in my-companies."""
        # Invite same user to both companies
        api.set_token(two_companies["a"]["tokens"]["access"])
        hr_api = ApiClient(request_context, api._base_url)
        hr = invite_and_accept_hr(api, hr_api)

        api_b = ApiClient(request_context, api._base_url)
        api_b.set_token(two_companies["b"]["tokens"]["access"])
        invite_resp = api_b.post("/hr/company/invite/", data={"email": hr["email"]})
        invite_token = invite_resp.json()["invitation"]["token"]

        hr_api.set_token(hr["tokens"]["access"])
        hr_api.post("/auth/accept-company-invitation/", data={"token": invite_token})

        resp = hr_api.get("/auth/my-companies/")
        assert resp.status == 200
        companies = resp.json()
        assert len(companies) >= 2

    def test_data_isolation_after_switch(self, api: ApiClient, request_context, two_companies):
        """Vacancy created in company A is not visible after switching to company B."""
        # Create vacancy in company A
        api.set_token(two_companies["a"]["tokens"]["access"])
        vacancy_a = create_published_vacancy(api)

        # Invite user to both companies
        hr_api = ApiClient(request_context, api._base_url)
        hr = invite_and_accept_hr(api, hr_api, permissions=[
            "manage_vacancies", "manage_candidates", "manage_interviews",
            "manage_team", "view_analytics", "manage_settings",
        ])

        api_b = ApiClient(request_context, api._base_url)
        api_b.set_token(two_companies["b"]["tokens"]["access"])
        invite_resp = api_b.post("/hr/company/invite/", data={
            "email": hr["email"],
            "permissions": [
                "manage_vacancies", "manage_candidates", "manage_interviews",
                "manage_team", "view_analytics", "manage_settings",
            ],
        })
        hr_api.set_token(hr["tokens"]["access"])
        hr_api.post("/auth/accept-company-invitation/", data={
            "token": invite_resp.json()["invitation"]["token"],
        })

        # Re-login to pick up updated company/permissions
        hr_api.login(hr["email"], hr["password"])

        # Now in company B — vacancy A should not be visible
        resp = hr_api.get("/hr/vacancies/")
        assert resp.status == 200
        data = resp.json()
        vacancies = data["results"] if isinstance(data, dict) else data
        ids = [v["id"] for v in vacancies]
        assert vacancy_a["id"] not in ids

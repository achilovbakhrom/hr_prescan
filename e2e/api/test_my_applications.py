"""Candidate My Applications API E2E tests — covers §8."""

import pytest

from conftest import register_vacancy_for_cleanup
from helpers.api_client import ApiClient
from helpers.factories import (
    create_published_vacancy,
    register_candidate,
    register_company,
    submit_application,
    unique_email,
)

pytestmark = pytest.mark.api


@pytest.fixture()
def vacancy(api: ApiClient) -> dict:
    company = register_company(api)
    api.set_token(company["tokens"]["access"])
    v = create_published_vacancy(api)
    register_vacancy_for_cleanup(api, v["id"])
    api.clear_token()
    return v


class TestCandidateApplications:
    def test_list_own_applications(self, api: ApiClient, vacancy, request_context):
        """Candidate sees their own application after registering with a matching email."""
        email = unique_email("mine")
        # Apply anonymously first
        apply_resp = api._request.post(
            api._url(f"/public/vacancies/{vacancy['id']}/apply/"),
            multipart={"candidate_name": "Mine", "candidate_email": email},
        )
        assert apply_resp.status == 201

        # Register with the SAME email to claim the application via bind_existing_applications
        cand_api = ApiClient(request_context, api._base_url)
        password = "TestPass123!"
        resp = cand_api.post("/auth/register/", data={
            "email": email, "password": password,
            "first_name": "Mine", "last_name": "User",
        })
        assert resp.status == 201
        cand_api.login(email, password)

        resp = cand_api.get("/candidate/applications/")
        assert resp.status == 200
        apps = resp.json()
        ids = [a["id"] for a in apps]
        assert apply_resp.json()["id"] in ids

    def test_detail_endpoint_has_status_and_match_score(self, api: ApiClient, vacancy, request_context):
        email = unique_email("detail")
        apply_resp = api._request.post(
            api._url(f"/public/vacancies/{vacancy['id']}/apply/"),
            multipart={"candidate_name": "Detail", "candidate_email": email},
        )
        app_id = apply_resp.json()["id"]

        cand_api = ApiClient(request_context, api._base_url)
        password = "TestPass123!"
        cand_api.post("/auth/register/", data={
            "email": email, "password": password,
            "first_name": "D", "last_name": "U",
        })
        cand_api.login(email, password)

        resp = cand_api.get(f"/candidate/applications/{app_id}/")
        assert resp.status == 200
        body = resp.json()
        assert "status" in body
        assert "match_score" in body
        # CV info field should be present (may be empty)
        assert "cv_original_filename" in body or "cv_file_path" in body or "cv" in body


class TestBindOnRegistration:
    def test_anonymous_apps_bound_after_registration(self, api: ApiClient, vacancy, request_context):
        """Apply anonymously, then register with same email — app appears in list."""
        email = unique_email("bind")
        apply_resp = api._request.post(
            api._url(f"/public/vacancies/{vacancy['id']}/apply/"),
            multipart={"candidate_name": "Bindy", "candidate_email": email},
        )
        assert apply_resp.status == 201
        app_id = apply_resp.json()["id"]

        cand_api = ApiClient(request_context, api._base_url)
        password = "TestPass123!"
        reg = cand_api.post("/auth/register/", data={
            "email": email, "password": password,
            "first_name": "B", "last_name": "U",
        })
        assert reg.status == 201
        cand_api.login(email, password)

        resp = cand_api.get("/candidate/applications/")
        assert resp.status == 200
        ids = [a["id"] for a in resp.json()]
        assert app_id in ids


class TestApplicationIsolation:
    def test_cannot_see_other_candidates_application(self, api: ApiClient, vacancy, request_context):
        """A candidate cannot fetch another candidate's application detail."""
        # Candidate A applies
        email_a = unique_email("a")
        apply_resp = api._request.post(
            api._url(f"/public/vacancies/{vacancy['id']}/apply/"),
            multipart={"candidate_name": "A", "candidate_email": email_a},
        )
        app_id = apply_resp.json()["id"]

        # Candidate B registers (different email) and tries to view A's application
        api_b = ApiClient(request_context, api._base_url)
        cand_b = register_candidate(api_b)
        api_b.set_token(cand_b["tokens"]["access"])

        resp = api_b.get(f"/candidate/applications/{app_id}/")
        assert resp.status in (403, 404)

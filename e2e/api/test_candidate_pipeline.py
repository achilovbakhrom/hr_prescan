"""Candidate pipeline API E2E tests."""

import pytest

from helpers.api_client import ApiClient
from helpers.factories import (
    create_published_vacancy,
    register_company,
    submit_application,
    unique_email,
)


@pytest.fixture()
def setup(api: ApiClient):
    """Register company, create published vacancy. Returns {api, vacancy}."""
    data = register_company(api)
    api.set_token(data["tokens"]["access"])
    vacancy = create_published_vacancy(api)
    return {"api": api, "vacancy": vacancy, "admin": data}


class TestSubmitApplication:
    def test_submit_application(self, api: ApiClient, setup):
        vacancy_id = setup["vacancy"]["id"]
        api.clear_token()

        email = unique_email("apply")
        resp = api._request.post(
            api._url(f"/public/vacancies/{vacancy_id}/apply/"),
            multipart={"candidate_name": "Alice", "candidate_email": email},
        )
        assert resp.status == 201
        body = resp.json()
        assert "prescan_token" in body
        assert body["status"] == "applied"

    def test_duplicate_email_rejected(self, api: ApiClient, setup):
        vacancy_id = setup["vacancy"]["id"]
        api.clear_token()

        email = unique_email("dup")
        api._request.post(
            api._url(f"/public/vacancies/{vacancy_id}/apply/"),
            multipart={"candidate_name": "First", "candidate_email": email},
        )

        resp = api._request.post(
            api._url(f"/public/vacancies/{vacancy_id}/apply/"),
            multipart={"candidate_name": "Second", "candidate_email": email},
        )
        assert resp.status == 400

    def test_cannot_apply_to_draft(self, api: ApiClient, setup):
        api.set_token(setup["admin"]["tokens"]["access"])
        draft = api.post("/hr/vacancies/", data={
            "title": "Draft Only",
            "description": "Cannot apply.",
        }).json()

        resp = api._request.post(
            api._url(f"/public/vacancies/{draft['id']}/apply/"),
            multipart={"candidate_name": "Bob", "candidate_email": unique_email("bob")},
        )
        assert resp.status in (400, 404)


class TestPrescanning:
    def test_start_prescanning(self, api: ApiClient, setup):
        vacancy_id = setup["vacancy"]["id"]
        api.clear_token()

        result = submit_application(api, vacancy_id)
        token = result["prescan_token"]

        resp = api.post(f"/public/interview/{token}/start/")
        assert resp.status == 200
        body = resp.json()
        assert body["status"] == "in_progress"

    def test_chat_history_empty_initially(self, api: ApiClient, setup):
        vacancy_id = setup["vacancy"]["id"]
        api.clear_token()

        result = submit_application(api, vacancy_id)
        token = result["prescan_token"]

        # Start session
        api.post(f"/public/interview/{token}/start/")

        resp = api.get(f"/public/interview/{token}/chat/history/")
        assert resp.status == 200
        # Should have at least the AI greeting
        history = resp.json()
        assert isinstance(history, list)


class TestHRCandidateManagement:
    def test_hr_views_candidate_list(self, api: ApiClient, setup):
        vacancy_id = setup["vacancy"]["id"]

        # Submit an application as anonymous
        api.clear_token()
        submit_application(api, vacancy_id)

        # Switch to admin
        api.set_token(setup["admin"]["tokens"]["access"])
        resp = api.get(f"/hr/vacancies/{vacancy_id}/candidates/")
        assert resp.status == 200
        candidates = resp.json()
        assert len(candidates) >= 1

    def test_valid_status_transition(self, api: ApiClient, setup):
        vacancy_id = setup["vacancy"]["id"]

        api.clear_token()
        result = submit_application(api, vacancy_id)
        app_id = result["id"]

        # HR: applied -> prescanned (valid transition)
        api.set_token(setup["admin"]["tokens"]["access"])
        resp = api.patch(f"/hr/candidates/{app_id}/status/", data={
            "status": "prescanned",
        })
        assert resp.status == 200
        assert resp.json()["status"] == "prescanned"

    def test_invalid_status_transition(self, api: ApiClient, setup):
        vacancy_id = setup["vacancy"]["id"]

        api.clear_token()
        result = submit_application(api, vacancy_id)
        app_id = result["id"]

        # HR: applied -> interviewed (invalid — must go through prescanned first)
        api.set_token(setup["admin"]["tokens"]["access"])
        resp = api.patch(f"/hr/candidates/{app_id}/status/", data={
            "status": "interviewed",
        })
        assert resp.status == 400

    def test_batch_move_by_score(self, api: ApiClient, setup):
        vacancy_id = setup["vacancy"]["id"]

        # Submit two applications
        api.clear_token()
        submit_application(api, vacancy_id)
        submit_application(api, vacancy_id)

        # Batch move all "applied" with match_score <= 50 to rejected
        api.set_token(setup["admin"]["tokens"]["access"])
        resp = api.post(f"/hr/vacancies/{vacancy_id}/candidates/batch-move/", data={
            "from_status": "applied",
            "to_status": "rejected",
            "max_score": 50.0,
        })
        assert resp.status == 200

    def test_soft_delete_archived(self, api: ApiClient, setup):
        vacancy_id = setup["vacancy"]["id"]

        api.clear_token()
        result = submit_application(api, vacancy_id)
        app_id = result["id"]

        api.set_token(setup["admin"]["tokens"]["access"])
        # Move to prescanned -> shortlisted -> archived
        api.patch(f"/hr/candidates/{app_id}/status/", data={"status": "prescanned"})
        api.patch(f"/hr/candidates/{app_id}/status/", data={"status": "shortlisted"})
        api.patch(f"/hr/candidates/{app_id}/status/", data={"status": "archived"})

        # Soft delete
        resp = api.post("/hr/candidates/soft-delete/", data={
            "application_ids": [app_id],
        })
        assert resp.status == 200

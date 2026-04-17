"""Application submission API E2E tests — covers §2 + §3 (non-LLM)."""

import pytest

from conftest import register_vacancy_for_cleanup
from helpers.api_client import ApiClient
from helpers.factories import (
    create_published_vacancy,
    register_company,
    unique_email,
)

pytestmark = pytest.mark.api


def _apply(api: ApiClient, vacancy_id: str, **fields) -> dict:
    return api._request.post(
        api._url(f"/public/vacancies/{vacancy_id}/apply/"),
        multipart=fields,
    )


@pytest.fixture()
def vacancy(api: ApiClient) -> dict:
    data = register_company(api)
    api.set_token(data["tokens"]["access"])
    v = create_published_vacancy(api)
    register_vacancy_for_cleanup(api, v["id"])
    return v


class TestAnonymousApply:
    def test_apply_without_account(self, api: ApiClient, vacancy):
        api.clear_token()
        resp = _apply(
            api,
            vacancy["id"],
            candidate_name="Anon User",
            candidate_email=unique_email("anon"),
        )
        assert resp.status == 201
        body = resp.json()
        assert "prescan_token" in body
        assert body["status"] == "applied"
        assert "screening_mode" in body

    def test_optional_phone_number(self, api: ApiClient, vacancy):
        api.clear_token()
        resp = _apply(
            api,
            vacancy["id"],
            candidate_name="Phoney",
            candidate_email=unique_email("phone"),
            candidate_phone="+15551234567",
        )
        assert resp.status == 201
        assert resp.json().get("candidate_phone") == "+15551234567"

    def test_apply_without_phone(self, api: ApiClient, vacancy):
        api.clear_token()
        resp = _apply(
            api,
            vacancy["id"],
            candidate_name="NoPhone",
            candidate_email=unique_email("nophone"),
        )
        assert resp.status == 201


class TestAuthenticatedApply:
    def test_apply_while_logged_in(self, persistent_candidate_api: ApiClient, api: ApiClient, vacancy):
        """Authenticated candidate: application is linked to the user account."""
        resp = persistent_candidate_api._request.post(
            persistent_candidate_api._url(f"/public/vacancies/{vacancy['id']}/apply/"),
            multipart={
                "candidate_name": "Persistent",
                "candidate_email": unique_email("pers"),
            },
            headers={"Authorization": f"Bearer {persistent_candidate_api._token}"},
        )
        assert resp.status == 201
        body = resp.json()
        assert "prescan_token" in body


class TestValidationErrors:
    def test_duplicate_email(self, api: ApiClient, vacancy):
        api.clear_token()
        email = unique_email("dup")
        r1 = _apply(api, vacancy["id"], candidate_name="First", candidate_email=email)
        assert r1.status == 201
        r2 = _apply(api, vacancy["id"], candidate_name="Second", candidate_email=email)
        assert r2.status == 400

    def test_invalid_email(self, api: ApiClient, vacancy):
        api.clear_token()
        resp = _apply(
            api,
            vacancy["id"],
            candidate_name="Bad Email",
            candidate_email="notanemail",
        )
        assert resp.status == 400

    def test_missing_name(self, api: ApiClient, vacancy):
        api.clear_token()
        resp = _apply(api, vacancy["id"], candidate_email=unique_email("noname"))
        assert resp.status == 400


class TestCannotApplyToClosedVacancy:
    def test_draft(self, api: ApiClient, vacancy):
        # reuse the session token already on `api`
        draft = api.post("/hr/vacancies/", data={
            "title": "Draft only", "description": "No.",
        }).json()
        register_vacancy_for_cleanup(api, draft["id"])

        api.clear_token()
        resp = _apply(
            api, draft["id"],
            candidate_name="X", candidate_email=unique_email("draft"),
        )
        assert resp.status in (400, 404)

    def test_paused(self, api: ApiClient, vacancy):
        api.patch(f"/hr/vacancies/{vacancy['id']}/status/", data={"action": "pause"})

        api.clear_token()
        resp = _apply(
            api, vacancy["id"],
            candidate_name="X", candidate_email=unique_email("paused"),
        )
        assert resp.status in (400, 404)

    def test_archived(self, api: ApiClient, vacancy):
        api.patch(f"/hr/vacancies/{vacancy['id']}/status/", data={"action": "archive"})

        api.clear_token()
        resp = _apply(
            api, vacancy["id"],
            candidate_name="X", candidate_email=unique_email("arch"),
        )
        assert resp.status in (400, 404)

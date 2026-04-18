"""Prescanning session lifecycle & gateway API tests — covers §4.1, §4.2, §6."""

import uuid

import pytest

from conftest import register_vacancy_for_cleanup
from helpers.api_client import ApiClient
from helpers.factories import (
    create_published_vacancy,
    register_company,
    submit_application,
)

pytestmark = pytest.mark.api


@pytest.fixture()
def token(api: ApiClient) -> str:
    """Create a fresh vacancy + application and return its prescan token."""
    company = register_company(api)
    api.set_token(company["tokens"]["access"])
    vacancy = create_published_vacancy(api)
    register_vacancy_for_cleanup(api, vacancy["id"])

    api.clear_token()
    result = submit_application(api, vacancy["id"])
    return result["prescan_token"]


class TestSessionLifecycle:
    def test_start_prescanning_transitions_to_in_progress(self, api: ApiClient, token):
        resp = api.post(f"/public/interview/{token}/start/")
        assert resp.status == 200
        body = resp.json()
        assert body["status"] == "in_progress"

    def test_get_interview_detail(self, api: ApiClient, token):
        resp = api.get(f"/public/interview/{token}/")
        assert resp.status == 200
        body = resp.json()
        assert body["status"] in ("pending", "in_progress")
        assert "screening_mode" in body

    def test_chat_history_returns_list(self, api: ApiClient, token):
        api.post(f"/public/interview/{token}/start/")

        resp = api.get(f"/public/interview/{token}/chat/history/")
        assert resp.status == 200
        assert isinstance(resp.json(), list)


class TestInvalidToken:
    def test_invalid_token_detail_returns_404(self, api: ApiClient):
        bogus = uuid.uuid4()
        resp = api.get(f"/public/interview/{bogus}/")
        assert resp.status == 404

    def test_invalid_token_start_returns_404(self, api: ApiClient):
        bogus = uuid.uuid4()
        resp = api.post(f"/public/interview/{bogus}/start/")
        assert resp.status == 404

    def test_invalid_token_chat_history_returns_404(self, api: ApiClient):
        bogus = uuid.uuid4()
        resp = api.get(f"/public/interview/{bogus}/chat/history/")
        assert resp.status == 404


class TestRestartStartedSession:
    def test_start_twice_is_idempotent_or_rejected(self, api: ApiClient, token):
        """Starting a session twice should succeed (idempotent) or fail with 400."""
        first = api.post(f"/public/interview/{token}/start/")
        assert first.status == 200

        second = api.post(f"/public/interview/{token}/start/")
        # Backend's start_interview either no-ops if already in_progress (200)
        # or raises ApplicationError for completed/cancelled (400).
        assert second.status in (200, 400)

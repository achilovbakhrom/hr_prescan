"""Notifications API E2E tests — covers §10."""

import pytest

from helpers.api_client import ApiClient
from helpers.factories import register_candidate

pytestmark = pytest.mark.api


@pytest.fixture()
def cand_api(api: ApiClient) -> ApiClient:
    data = register_candidate(api)
    api.set_token(data["tokens"]["access"])
    return api


class TestNotificationsList:
    def test_list_returns_array(self, cand_api: ApiClient):
        resp = cand_api.get("/notifications/")
        assert resp.status == 200
        assert isinstance(resp.json(), list)

    def test_unread_count_endpoint(self, cand_api: ApiClient):
        resp = cand_api.get("/notifications/unread-count/")
        assert resp.status == 200
        body = resp.json()
        assert "unread_count" in body
        assert isinstance(body["unread_count"], int)

    def test_unread_only_filter(self, cand_api: ApiClient):
        resp = cand_api.get("/notifications/", params={"unread": "true"})
        assert resp.status == 200
        assert isinstance(resp.json(), list)


class TestMarkAsRead:
    def test_mark_all_as_read(self, cand_api: ApiClient):
        resp = cand_api.post("/notifications/read-all/")
        assert resp.status == 200
        body = resp.json()
        assert "updated" in body
        # After mark-all, unread count should be 0
        count_resp = cand_api.get("/notifications/unread-count/")
        assert count_resp.status == 200
        assert count_resp.json()["unread_count"] == 0

    def test_mark_nonexistent_returns_404(self, cand_api: ApiClient):
        import uuid

        bogus = uuid.uuid4()
        resp = cand_api.patch(f"/notifications/{bogus}/read/")
        assert resp.status == 404

    def test_requires_authentication(self, api: ApiClient):
        api.clear_token()
        resp = api.get("/notifications/")
        assert resp.status == 401

"""HR candidate management API E2E tests — expands §4/§5 HR-side."""

import pytest

from conftest import register_vacancy_for_cleanup
from helpers.api_client import ApiClient
from helpers.factories import (
    create_published_vacancy,
    register_candidate,
    register_company,
    submit_application,
)

pytestmark = pytest.mark.api


@pytest.fixture()
def setup(api: ApiClient) -> dict:
    """Register a company + published vacancy. `api` is left authenticated as admin."""
    admin = register_company(api)
    api.set_token(admin["tokens"]["access"])
    vacancy = create_published_vacancy(api)
    register_vacancy_for_cleanup(api, vacancy["id"])
    return {"api": api, "admin": admin, "vacancy": vacancy}


def _set_status(api: ApiClient, app_id: str, status: str):
    return api.patch(f"/hr/candidates/{app_id}/status/", data={"status": status})


class TestValidStatusChain:
    def test_applied_to_prescanned_to_shortlisted_to_hired(self, api: ApiClient, setup):
        vacancy_id = setup["vacancy"]["id"]

        api.clear_token()
        app = submit_application(api, vacancy_id)
        app_id = app["id"]

        api.set_token(setup["admin"]["tokens"]["access"])

        r1 = _set_status(api, app_id, "prescanned")
        assert r1.status == 200 and r1.json()["status"] == "prescanned"

        r2 = _set_status(api, app_id, "shortlisted")
        assert r2.status == 200 and r2.json()["status"] == "shortlisted"

        r3 = _set_status(api, app_id, "hired")
        assert r3.status == 200 and r3.json()["status"] == "hired"


class TestInvalidTransition:
    def test_applied_to_hired_rejected(self, api: ApiClient, setup):
        vacancy_id = setup["vacancy"]["id"]

        api.clear_token()
        app = submit_application(api, vacancy_id)

        api.set_token(setup["admin"]["tokens"]["access"])
        resp = _set_status(api, app["id"], "hired")
        assert resp.status == 400


class TestSoftDelete:
    def test_soft_delete_archived(self, api: ApiClient, setup):
        vacancy_id = setup["vacancy"]["id"]

        api.clear_token()
        app = submit_application(api, vacancy_id)
        app_id = app["id"]

        api.set_token(setup["admin"]["tokens"]["access"])
        _set_status(api, app_id, "prescanned")
        _set_status(api, app_id, "shortlisted")
        _set_status(api, app_id, "rejected")
        _set_status(api, app_id, "archived")

        resp = api.post("/hr/candidates/soft-delete/", data={
            "application_ids": [app_id],
        })
        assert resp.status == 200
        assert resp.json()["deleted"] == 1

    def test_cannot_soft_delete_non_archived(self, api: ApiClient, setup):
        vacancy_id = setup["vacancy"]["id"]

        api.clear_token()
        app = submit_application(api, vacancy_id)

        # Application is still in `applied` status
        api.set_token(setup["admin"]["tokens"]["access"])
        resp = api.post("/hr/candidates/soft-delete/", data={
            "application_ids": [app["id"]],
        })
        # Service filters by status=ARCHIVED; returns 200 with deleted=0
        assert resp.status == 200
        assert resp.json()["deleted"] == 0


class TestBatchMove:
    def test_batch_move_by_max_score(self, api: ApiClient, setup):
        vacancy_id = setup["vacancy"]["id"]

        api.clear_token()
        submit_application(api, vacancy_id)
        submit_application(api, vacancy_id)

        api.set_token(setup["admin"]["tokens"]["access"])
        resp = api.post(f"/hr/vacancies/{vacancy_id}/candidates/batch-move/", data={
            "from_status": "applied",
            "to_status": "rejected",
            "max_score": 100.0,
        })
        assert resp.status == 200
        assert "moved" in resp.json()


class TestHROnlyAccessControl:
    def test_candidate_cannot_access_hr_candidates(self, api: ApiClient, setup):
        """HR candidate endpoints must reject a candidate token (403)."""
        vacancy_id = setup["vacancy"]["id"]

        # Make sure there's at least one applied candidate (not used by the test itself)
        admin_token = setup["admin"]["tokens"]["access"]
        api.clear_token()
        submit_application(api, vacancy_id)

        # Candidate token attempts to call HR endpoint
        cand = register_candidate(api)
        api.set_token(cand["tokens"]["access"])

        r1 = api.get(f"/hr/vacancies/{vacancy_id}/candidates/")
        assert r1.status == 403

        r2 = api.get("/hr/candidates/")
        assert r2.status == 403

        # Restore admin token so session-scope cleanup can archive the vacancy
        api.set_token(admin_token)

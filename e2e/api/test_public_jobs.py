"""Public job board API E2E tests — covers TEST_CASES_CANDIDATE.md §1."""

import uuid

import pytest

from conftest import register_vacancy_for_cleanup
from helpers.api_client import ApiClient
from helpers.factories import create_published_vacancy, register_company

pytestmark = pytest.mark.api


def _extract_results(data):
    return data["results"] if isinstance(data, dict) else data


@pytest.fixture()
def company(api: ApiClient) -> dict:
    """Register a company and authenticate `api`."""
    data = register_company(api)
    api.set_token(data["tokens"]["access"])
    return data


class TestBrowseJobs:
    def test_only_published_public_shown(self, api: ApiClient, company):
        published = create_published_vacancy(api)
        register_vacancy_for_cleanup(api, published["id"])

        draft = api.post("/hr/vacancies/", data={
            "title": f"Draft-{uuid.uuid4().hex[:6]}",
            "description": "Draft vacancy.",
        }).json()
        register_vacancy_for_cleanup(api, draft["id"])

        api.clear_token()
        resp = api.get("/public/vacancies/")
        assert resp.status == 200
        titles = [v["title"] for v in _extract_results(resp.json())]
        assert published["title"] in titles
        assert draft["title"] not in titles

    def test_empty_search_returns_empty(self, api: ApiClient, company):
        api.clear_token()
        resp = api.get(
            "/public/vacancies/",
            params={"search": f"zzz-no-match-{uuid.uuid4().hex}"},
        )
        assert resp.status == 200
        assert len(_extract_results(resp.json())) == 0


class TestFilters:
    def test_search_by_keyword(self, api: ApiClient, company):
        unique = f"Kwd{uuid.uuid4().hex[:6]}"
        vacancy = api.post("/hr/vacancies/", data={
            "title": f"{unique} Developer",
            "description": "Needs good Python.",
        }).json()
        api.post(f"/hr/vacancies/{vacancy['id']}/questions/", data={
            "text": "Tell me about yourself.", "category": "Behavioral", "step": "prescanning",
        })
        api.patch(f"/hr/vacancies/{vacancy['id']}/status/", data={"action": "publish"})
        register_vacancy_for_cleanup(api, vacancy["id"])

        api.clear_token()
        resp = api.get("/public/vacancies/", params={"search": unique})
        assert resp.status == 200
        titles = [v["title"] for v in _extract_results(resp.json())]
        assert any(unique in t for t in titles)

    def test_filter_is_remote(self, api: ApiClient, company):
        vacancy = create_published_vacancy(api)  # factory sets is_remote=True
        register_vacancy_for_cleanup(api, vacancy["id"])

        api.clear_token()
        resp = api.get("/public/vacancies/", params={"is_remote": "true"})
        assert resp.status == 200
        for v in _extract_results(resp.json()):
            assert v.get("is_remote") is True

    def test_filter_employment_and_experience(self, api: ApiClient, company):
        vacancy = create_published_vacancy(api)  # full_time / middle
        register_vacancy_for_cleanup(api, vacancy["id"])

        api.clear_token()
        resp = api.get(
            "/public/vacancies/",
            params={"employment_type": "full_time", "experience_level": "middle"},
        )
        assert resp.status == 200
        for v in _extract_results(resp.json()):
            assert v["employment_type"] == "full_time"
            assert v["experience_level"] == "middle"

    def test_filter_by_location(self, api: ApiClient, company):
        loc = f"Loc-{uuid.uuid4().hex[:6]}"
        vacancy = api.post("/hr/vacancies/", data={
            "title": "Located", "description": "Some desc.", "location": loc,
        }).json()
        api.post(f"/hr/vacancies/{vacancy['id']}/questions/", data={
            "text": "Hi?", "category": "Behavioral", "step": "prescanning",
        })
        api.patch(f"/hr/vacancies/{vacancy['id']}/status/", data={"action": "publish"})
        register_vacancy_for_cleanup(api, vacancy["id"])

        api.clear_token()
        resp = api.get("/public/vacancies/", params={"location": loc})
        assert resp.status == 200
        results = _extract_results(resp.json())
        assert len(results) >= 1
        assert all(loc in v["location"] for v in results)

    def test_combined_filters(self, api: ApiClient, company):
        vacancy = create_published_vacancy(api)
        register_vacancy_for_cleanup(api, vacancy["id"])

        api.clear_token()
        resp = api.get("/public/vacancies/", params={
            "is_remote": "true",
            "employment_type": "full_time",
            "experience_level": "middle",
        })
        assert resp.status == 200
        ids = [v["id"] for v in _extract_results(resp.json())]
        assert vacancy["id"] in ids


class TestVacancyDetail:
    def test_detail_by_id_published_public(self, api: ApiClient, company):
        vacancy = create_published_vacancy(api)
        register_vacancy_for_cleanup(api, vacancy["id"])

        api.clear_token()
        resp = api.get(f"/public/vacancies/{vacancy['id']}/")
        assert resp.status == 200
        assert resp.json()["id"] == vacancy["id"]

    def test_detail_by_share_token_bypasses_status(self, api: ApiClient, company):
        """Share link works even on PAUSED + PRIVATE vacancies."""
        vacancy = create_published_vacancy(api)
        register_vacancy_for_cleanup(api, vacancy["id"])
        # Make it private + paused
        api.patch(f"/hr/vacancies/{vacancy['id']}/", data={"visibility": "private"})
        api.patch(f"/hr/vacancies/{vacancy['id']}/status/", data={"action": "pause"})

        share_token = vacancy["share_token"]
        api.clear_token()
        resp = api.get(f"/public/vacancies/share/{share_token}/")
        assert resp.status == 200
        assert resp.json()["id"] == vacancy["id"]

    def test_detail_by_id_draft_returns_404(self, api: ApiClient, company):
        draft = api.post("/hr/vacancies/", data={
            "title": "Drafty", "description": "No.",
        }).json()
        register_vacancy_for_cleanup(api, draft["id"])

        api.clear_token()
        resp = api.get(f"/public/vacancies/{draft['id']}/")
        assert resp.status == 404

    def test_detail_by_id_private_visibility_returns_404(self, api: ApiClient, company):
        vacancy = create_published_vacancy(api)
        register_vacancy_for_cleanup(api, vacancy["id"])
        api.patch(f"/hr/vacancies/{vacancy['id']}/", data={"visibility": "private"})

        api.clear_token()
        resp = api.get(f"/public/vacancies/{vacancy['id']}/")
        assert resp.status == 404

"""Vacancy lifecycle API E2E tests."""

import uuid

import pytest

from helpers.api_client import ApiClient
from helpers.factories import create_published_vacancy, register_company, unique_email


@pytest.fixture()
def company_admin(api: ApiClient) -> dict:
    """Register a company and return {api, company, admin_data}."""
    data = register_company(api)
    api.set_token(data["tokens"]["access"])
    return data


class TestCreateVacancy:
    def test_create_draft_vacancy(self, api: ApiClient, company_admin):
        resp = api.post("/hr/vacancies/", data={
            "title": "Backend Developer",
            "description": "Build APIs.",
        })
        assert resp.status == 201
        vacancy = resp.json()
        assert vacancy["status"] == "draft"
        assert vacancy["title"] == "Backend Developer"

    def test_draft_has_default_criteria(self, api: ApiClient, company_admin):
        resp = api.post("/hr/vacancies/", data={
            "title": "Test Criteria",
            "description": "Check defaults.",
        })
        assert resp.status == 201
        vacancy_id = resp.json()["id"]

        detail = api.get(f"/hr/vacancies/{vacancy_id}/").json()
        criteria = detail["criteria"]
        assert len(criteria) == 5
        names = {c["name"] for c in criteria}
        assert "Technical Skills" in names
        assert "Communication" in names


class TestPublishVacancy:
    def test_publish_with_questions(self, api: ApiClient, company_admin):
        # Create draft
        vacancy = api.post("/hr/vacancies/", data={
            "title": "Publishable",
            "description": "Has questions.",
        }).json()

        # Add prescanning question
        api.post(f"/hr/vacancies/{vacancy['id']}/questions/", data={
            "text": "Tell me about yourself.",
            "category": "Behavioral",
            "step": "prescanning",
        })

        # Publish
        resp = api.patch(f"/hr/vacancies/{vacancy['id']}/status/", data={"action": "publish"})
        assert resp.status == 200
        assert resp.json()["status"] == "published"

    def test_publish_without_questions_fails(self, api: ApiClient, company_admin):
        vacancy = api.post("/hr/vacancies/", data={
            "title": "No Questions",
            "description": "Missing questions.",
        }).json()

        resp = api.patch(f"/hr/vacancies/{vacancy['id']}/status/", data={"action": "publish"})
        assert resp.status == 400


class TestVacancyStatusTransitions:
    def test_pause_published(self, api: ApiClient, company_admin):
        vacancy = create_published_vacancy(api)
        resp = api.patch(f"/hr/vacancies/{vacancy['id']}/status/", data={"action": "pause"})
        assert resp.status == 200
        assert resp.json()["status"] == "paused"

    def test_resume_paused(self, api: ApiClient, company_admin):
        vacancy = create_published_vacancy(api)
        api.patch(f"/hr/vacancies/{vacancy['id']}/status/", data={"action": "pause"})

        resp = api.patch(f"/hr/vacancies/{vacancy['id']}/status/", data={"action": "publish"})
        assert resp.status == 200
        assert resp.json()["status"] == "published"

    def test_archive_published(self, api: ApiClient, company_admin):
        vacancy = create_published_vacancy(api)
        resp = api.patch(f"/hr/vacancies/{vacancy['id']}/status/", data={"action": "archive"})
        assert resp.status == 200
        assert resp.json()["status"] == "archived"

    def test_cannot_publish_archived(self, api: ApiClient, company_admin):
        vacancy = create_published_vacancy(api)
        api.patch(f"/hr/vacancies/{vacancy['id']}/status/", data={"action": "archive"})

        resp = api.patch(f"/hr/vacancies/{vacancy['id']}/status/", data={"action": "publish"})
        assert resp.status == 400


class TestCrudCriteriaQuestions:
    def test_add_and_delete_criteria(self, api: ApiClient, company_admin):
        vacancy = api.post("/hr/vacancies/", data={
            "title": "CRUD Test",
            "description": "Test.",
        }).json()

        # Add custom criteria
        resp = api.post(f"/hr/vacancies/{vacancy['id']}/criteria/", data={
            "name": "Leadership",
            "description": "Ability to lead teams.",
            "weight": 3,
            "step": "prescanning",
        })
        assert resp.status == 201
        criteria_id = resp.json()["id"]

        # Delete it
        resp = api.delete(f"/hr/vacancies/{vacancy['id']}/criteria/{criteria_id}/")
        assert resp.status == 204

    def test_add_and_delete_question(self, api: ApiClient, company_admin):
        vacancy = api.post("/hr/vacancies/", data={
            "title": "Q CRUD",
            "description": "Test.",
        }).json()

        resp = api.post(f"/hr/vacancies/{vacancy['id']}/questions/", data={
            "text": "What is your biggest weakness?",
            "category": "Soft Skill",
            "step": "prescanning",
        })
        assert resp.status == 201
        question_id = resp.json()["id"]

        resp = api.delete(f"/hr/vacancies/{vacancy['id']}/questions/{question_id}/")
        assert resp.status == 204


class TestPublicVacancies:
    def test_public_list_shows_only_published(self, api: ApiClient, company_admin):
        # Create a published vacancy
        published = create_published_vacancy(api)

        # Create a draft (don't publish)
        api.post("/hr/vacancies/", data={
            "title": "Draft Only",
            "description": "Should not appear.",
        })

        api.clear_token()
        resp = api.get("/public/vacancies/")
        assert resp.status == 200
        data = resp.json()
        vacancies = data["results"] if isinstance(data, dict) else data
        titles = [v["title"] for v in vacancies]
        assert published["title"] in titles
        assert "Draft Only" not in titles

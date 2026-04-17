"""My Applications page UI E2E tests (candidate)."""

import os

import pytest
from playwright.sync_api import Page, expect

from helpers.factories import create_published_vacancy, register_company

pytestmark = pytest.mark.ui


CANDIDATE_EMAIL = os.getenv("E2E_CANDIDATE_EMAIL", "")
CANDIDATE_PASSWORD = os.getenv("E2E_CANDIDATE_PASSWORD", "")


def _inject_candidate_tokens(page: Page, api, frontend_url) -> None:
    """Log in the persistent candidate via API and seed localStorage."""
    assert CANDIDATE_EMAIL and CANDIDATE_PASSWORD, "candidate creds missing"
    resp = api.post(
        "/auth/login/",
        data={"email": CANDIDATE_EMAIL, "password": CANDIDATE_PASSWORD},
    )
    assert resp.status == 200, f"candidate login failed: {resp.text()}"
    tokens = resp.json()["tokens"]

    # Must be on the right origin before writing localStorage
    page.goto(f"{frontend_url}/login")
    page.evaluate(
        "(tokens) => localStorage.setItem('hr_prescan_tokens', JSON.stringify(tokens))",
        {"access": tokens["access"], "refresh": tokens["refresh"]},
    )


def _submit_anon_application(api, vacancy_id: str, email: str) -> None:
    """Submit an anonymous public application with a specific candidate email."""
    resp = api._request.post(
        api._url(f"/public/vacancies/{vacancy_id}/apply/"),
        multipart={"candidate_name": "Persistent Candidate", "candidate_email": email},
    )
    assert resp.status == 201, f"anon apply failed: {resp.text()}"


class TestMyApplications:
    def test_page_renders_for_logged_in_candidate(
        self, page: Page, api, frontend_url
    ):
        _inject_candidate_tokens(page, api, frontend_url)
        page.goto(f"{frontend_url}/my-applications")

        # DataTable or empty state — either is acceptable. Verify heading loads.
        heading = page.locator("h1").first
        expect(heading).to_be_visible(timeout=15_000)
        # No hard-error message visible
        assert "500" not in page.content()

    def test_new_application_appears_after_apply(
        self, page: Page, api, frontend_url
    ):
        # Create a fresh vacancy as a throwaway admin, then apply as the
        # persistent candidate (anonymous apply with their email).
        admin = register_company(api)
        api.set_token(admin["tokens"]["access"])
        vacancy = create_published_vacancy(api)

        api.clear_token()
        _submit_anon_application(api, vacancy["id"], CANDIDATE_EMAIL)

        _inject_candidate_tokens(page, api, frontend_url)
        page.goto(f"{frontend_url}/my-applications")

        # The vacancy title should appear in the list
        expect(page.get_by_text(vacancy["title"])).to_be_visible(timeout=15_000)

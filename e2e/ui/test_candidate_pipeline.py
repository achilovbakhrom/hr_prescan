"""Candidate pipeline UI E2E tests."""

import re

import pytest
from playwright.sync_api import Page, expect

from helpers.factories import (
    create_published_vacancy,
    register_company,
    submit_application,
    unique_email,
)



@pytest.fixture()
def published_vacancy(api):
    """Create a company with a published vacancy via API."""
    data = register_company(api)
    api.set_token(data["tokens"]["access"])
    vacancy = create_published_vacancy(api)
    return {"vacancy": vacancy, "admin": data}


class TestPublicApplication:
    def test_apply_to_vacancy(self, page: Page, published_vacancy, frontend_url):
        vacancy = published_vacancy["vacancy"]

        # Open the public vacancy page
        page.goto(f"{frontend_url}/jobs/{vacancy['id']}")
        expect(page.get_by_text(vacancy["title"])).to_be_visible(timeout=10_000)

        # Click apply button
        page.get_by_role("button", name=re.compile("apply", re.IGNORECASE)).click()

        # Fill the application form
        page.get_by_placeholder("John Doe").fill("E2E Applicant")
        page.get_by_placeholder("john@example.com").fill(unique_email("ui-apply"))

        # Submit
        page.get_by_role("button", name=re.compile("submit|apply", re.IGNORECASE)).click()

        # Should see success state — prescan link appears or URL changes
        page.wait_for_timeout(3_000)
        assert "/apply" not in page.url or page.locator("text=prescanning").count() > 0 or page.locator("[class*='prescan']").count() > 0


class TestHRCandidateView:
    def test_hr_sees_candidate_in_list(self, page: Page, api, published_vacancy, frontend_url):
        vacancy = published_vacancy["vacancy"]
        admin = published_vacancy["admin"]

        # Submit application via API
        api.clear_token()
        submit_application(api, vacancy["id"])

        # Login as admin through UI
        page.goto(f"{frontend_url}/login")
        page.get_by_placeholder(re.compile("email", re.IGNORECASE)).fill(admin["email"])
        page.get_by_placeholder(re.compile("password", re.IGNORECASE)).fill(admin["password"])
        page.get_by_role("button", name="Sign In", exact=True).click()
        expect(page).to_have_url(re.compile(r"/dashboard"), timeout=10_000)

        # Navigate to vacancy candidates
        page.goto(f"{frontend_url}/vacancies/{vacancy['id']}?tab=candidates")

        # Should see at least one candidate row in table
        page.wait_for_timeout(3_000)
        rows = page.locator("table tbody tr")
        expect(rows.first).to_be_attached(timeout=10_000)

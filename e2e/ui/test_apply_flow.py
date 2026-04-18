"""Public application flow UI E2E tests."""

import re

import pytest
from playwright.sync_api import Page, expect

from helpers.factories import (
    create_published_vacancy,
    register_company,
    unique_email,
)

pytestmark = pytest.mark.ui


@pytest.fixture()
def published_vacancy(api):
    data = register_company(api)
    api.set_token(data["tokens"]["access"])
    vacancy = create_published_vacancy(api)
    return vacancy


class TestApplyFlow:
    def test_full_apply_success(self, page: Page, published_vacancy, frontend_url):
        vacancy = published_vacancy
        page.goto(f"{frontend_url}/jobs/{vacancy['id']}")
        expect(page.get_by_text(vacancy["title"])).to_be_visible(timeout=15_000)

        page.get_by_role("button", name=re.compile("apply", re.IGNORECASE)).click()

        # On the application form — guest mode: name + email inputs
        name_input = page.get_by_placeholder("John Doe")
        email_input = page.get_by_placeholder("john@example.com")
        expect(name_input).to_be_visible(timeout=10_000)

        name_input.fill("E2E Applicant")
        email_input.fill(unique_email("ui-apply"))

        page.get_by_role("button", name=re.compile("submit|apply", re.IGNORECASE)).first.click()

        # Success: the ready step shows "Start Prescanning" / prescan link, OR
        # we navigate away from the /apply form.
        page.wait_for_timeout(3_000)
        start_btn = page.get_by_role("button", name=re.compile("prescan|start", re.IGNORECASE))
        prescan_link = page.locator("[class*='prescan'], a[href*='/interview/']")
        assert (
            start_btn.count() > 0
            or prescan_link.count() > 0
            or "/interview/" in page.url
        ), f"No success indicator after apply. URL={page.url}"

    def test_empty_name_shows_error(self, page: Page, published_vacancy, frontend_url):
        vacancy = published_vacancy
        page.goto(f"{frontend_url}/jobs/{vacancy['id']}")
        expect(page.get_by_text(vacancy["title"])).to_be_visible(timeout=15_000)
        page.get_by_role("button", name=re.compile("apply", re.IGNORECASE)).click()

        email_input = page.get_by_placeholder("john@example.com")
        expect(email_input).to_be_visible(timeout=10_000)
        email_input.fill(unique_email("ui-apply-noname"))

        page.get_by_role("button", name=re.compile("submit|apply", re.IGNORECASE)).first.click()

        # Inline error under the name field (<small class="text-red-500">)
        expect(page.locator("small.text-red-500").first).to_be_visible(timeout=5_000)

    def test_invalid_email_shows_error(self, page: Page, published_vacancy, frontend_url):
        vacancy = published_vacancy
        page.goto(f"{frontend_url}/jobs/{vacancy['id']}")
        expect(page.get_by_text(vacancy["title"])).to_be_visible(timeout=15_000)
        page.get_by_role("button", name=re.compile("apply", re.IGNORECASE)).click()

        page.get_by_placeholder("John Doe").fill("Somebody")
        page.get_by_placeholder("john@example.com").fill("not-an-email")

        page.get_by_role("button", name=re.compile("submit|apply", re.IGNORECASE)).first.click()
        expect(page.locator("small.text-red-500").first).to_be_visible(timeout=5_000)

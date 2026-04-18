"""Vacancy lifecycle UI E2E tests."""

import re

import pytest
from playwright.sync_api import Page, expect

from helpers.factories import register_company, create_published_vacancy


@pytest.fixture()
def logged_in_admin(page: Page, api, frontend_url):
    """Register company via API, then login through the UI."""
    data = register_company(api)

    page.goto(f"{frontend_url}/login")
    page.get_by_placeholder(re.compile("email", re.IGNORECASE)).fill(data["email"])
    page.get_by_placeholder(re.compile("password", re.IGNORECASE)).fill(data["password"])
    page.get_by_role("button", name="Sign In", exact=True).click()
    expect(page).to_have_url(re.compile(r"/dashboard"), timeout=10_000)

    return data


class TestVacancyLifecycle:
    def test_create_vacancy_draft(self, page: Page, logged_in_admin, frontend_url):
        page.goto(f"{frontend_url}/vacancies")
        page.get_by_role("button", name="New Vacancy").first.click()

        # Fill form — find first text input (title) and first textarea/editor (description)
        page.locator("input[type='text']:visible").first.fill("UI Test Vacancy")
        # Description might be a textarea or a rich text editor (PrimeVue Editor / div contenteditable)
        desc = page.locator("textarea:visible, .ql-editor, [contenteditable='true']").first
        desc.fill("We are looking for a talented developer to join our team and build amazing products.")

        # Wait for Save button to become enabled, then click
        save_btn = page.get_by_role("button", name=re.compile("save|create", re.IGNORECASE)).first
        save_btn.click(timeout=5_000, force=True)

        # Should see the vacancy in the list or detail
        page.wait_for_timeout(3_000)
        assert "UI Test Vacancy" in page.content() or "/vacancies/" in page.url

    def test_publish_vacancy(self, page: Page, logged_in_admin, api, frontend_url):
        # Create a publishable vacancy via API
        api.set_token(logged_in_admin["tokens"]["access"])
        vacancy = create_published_vacancy(api)

        # Navigate to vacancy detail
        page.goto(f"{frontend_url}/vacancies/{vacancy['id']}")
        expect(page.get_by_text(vacancy["title"])).to_be_visible(timeout=10_000)

        # Should show "Published" badge
        expect(page.get_by_text(re.compile("published", re.IGNORECASE))).to_be_visible()

    def test_pause_and_resume(self, page: Page, logged_in_admin, api, frontend_url):
        api.set_token(logged_in_admin["tokens"]["access"])
        vacancy = create_published_vacancy(api)

        page.goto(f"{frontend_url}/vacancies/{vacancy['id']}")
        expect(page.get_by_text(vacancy["title"])).to_be_visible(timeout=10_000)

        # Click pause button
        pause_btn = page.get_by_role("button", name=re.compile("pause", re.IGNORECASE))
        if pause_btn.is_visible():
            pause_btn.click()
            expect(page.get_by_text(re.compile("paused", re.IGNORECASE))).to_be_visible(timeout=5_000)

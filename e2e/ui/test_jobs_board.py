"""Public jobs board UI E2E tests."""

import re
import uuid

import pytest
from playwright.sync_api import Page, expect

from helpers.factories import create_published_vacancy, register_company

pytestmark = pytest.mark.ui


@pytest.fixture()
def published_vacancy(api):
    """Create a company + published vacancy via API (owned by a throwaway admin)."""
    data = register_company(api)
    api.set_token(data["tokens"]["access"])
    vacancy = create_published_vacancy(api)
    return vacancy


class TestJobsBoard:
    def test_job_board_renders_cards(self, page: Page, published_vacancy, frontend_url):
        page.goto(f"{frontend_url}/jobs")
        # Wait for at least one card to mount. Cards render job titles in <h2>.
        expect(page.locator("h2").first).to_be_visible(timeout=15_000)

    def test_search_filters_results(self, page: Page, api, frontend_url):
        # Create a vacancy with a unique, recognizable title
        data = register_company(api)
        api.set_token(data["tokens"]["access"])

        unique_marker = f"ZZEE{uuid.uuid4().hex[:8].upper()}"
        vacancy = create_published_vacancy(api)
        # Patch the title so it contains the marker
        resp = api.patch(
            f"/hr/vacancies/{vacancy['id']}/",
            data={"title": f"Marker {unique_marker} Role"},
        )
        assert resp.status == 200, f"Could not rename vacancy: {resp.text()}"

        page.goto(f"{frontend_url}/jobs")
        expect(page.locator("h2").first).to_be_visible(timeout=15_000)

        search = page.get_by_placeholder(re.compile("search jobs", re.IGNORECASE))
        expect(search).to_be_visible(timeout=10_000)
        search.fill(unique_marker)

        # Debounced fetch (~400ms) — wait for our title to appear
        expect(page.get_by_text(re.compile(unique_marker, re.IGNORECASE))).to_be_visible(
            timeout=15_000,
        )

    def test_click_card_opens_detail(self, page: Page, published_vacancy, frontend_url):
        vacancy = published_vacancy
        page.goto(f"{frontend_url}/jobs")
        # Click card whose title matches our vacancy
        card = page.get_by_text(vacancy["title"]).first
        expect(card).to_be_visible(timeout=15_000)
        card.click()

        expect(page).to_have_url(re.compile(r"/jobs/"), timeout=10_000)
        # Detail page shows title and an Apply button
        expect(page.get_by_text(vacancy["title"])).to_be_visible(timeout=10_000)
        expect(
            page.get_by_role("button", name=re.compile("apply", re.IGNORECASE))
        ).to_be_visible(timeout=10_000)

    def test_detail_page_direct_navigation(self, page: Page, published_vacancy, frontend_url):
        vacancy = published_vacancy
        page.goto(f"{frontend_url}/jobs/{vacancy['id']}")
        expect(page.get_by_text(vacancy["title"])).to_be_visible(timeout=15_000)
        # Description text should be visible somewhere on the page
        assert "test vacancy" in page.content().lower()

"""Mobile viewport UI E2E tests."""

import os

import pytest
from playwright.sync_api import Page, expect

pytestmark = [pytest.mark.ui, pytest.mark.mobile]


MOBILE_VIEWPORT = {"width": 375, "height": 812}

CANDIDATE_EMAIL = os.getenv("E2E_CANDIDATE_EMAIL", "")
CANDIDATE_PASSWORD = os.getenv("E2E_CANDIDATE_PASSWORD", "")


def _no_horizontal_scroll(page: Page) -> bool:
    return page.evaluate(
        "() => document.documentElement.scrollWidth <= window.innerWidth + 1"
    )


class TestMobileLayout:
    def test_jobs_board_fits_375(self, page: Page, frontend_url):
        page.set_viewport_size(MOBILE_VIEWPORT)
        page.goto(f"{frontend_url}/jobs")

        # A job card title (h2) should render
        expect(page.locator("h2").first).to_be_visible(timeout=15_000)
        # Allow layout to settle
        page.wait_for_timeout(500)
        assert _no_horizontal_scroll(page), (
            f"Horizontal scroll detected: scrollWidth="
            f"{page.evaluate('document.documentElement.scrollWidth')} "
            f"viewport={MOBILE_VIEWPORT['width']}"
        )

    def test_my_applications_fits_375(self, page: Page, api, frontend_url):
        if not (CANDIDATE_EMAIL and CANDIDATE_PASSWORD):
            pytest.skip("E2E_CANDIDATE_EMAIL / PASSWORD not configured")

        page.set_viewport_size(MOBILE_VIEWPORT)

        resp = api.post(
            "/auth/login/",
            data={"email": CANDIDATE_EMAIL, "password": CANDIDATE_PASSWORD},
        )
        assert resp.status == 200, resp.text()
        tokens = resp.json()["tokens"]

        page.goto(f"{frontend_url}/login")
        page.evaluate(
            "(tokens) => localStorage.setItem('hr_prescan_tokens', JSON.stringify(tokens))",
            {"access": tokens["access"], "refresh": tokens["refresh"]},
        )
        page.goto(f"{frontend_url}/my-applications")

        expect(page.locator("h1").first).to_be_visible(timeout=15_000)
        page.wait_for_timeout(500)
        # PrimeVue DataTable can overflow horizontally on mobile; that's
        # handled by the table's own scroll container, not the document.
        assert _no_horizontal_scroll(page), "Document has horizontal scroll"

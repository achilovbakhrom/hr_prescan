"""UI E2E tests for social-auth post-OAuth flows.

We bypass the real OAuth redirect dance by using the backend E2E hook
(`oauth_simulate`) to get JWT tokens for a user in a specific state, then
inject those tokens into the frontend's localStorage. From there we verify
the Vue router's guards behave correctly:

- `new_candidate` → forced to `/choose-role` regardless of destination.
- `onboarded_candidate` → `/dashboard` loads directly.
- `new_hr_needs_company` → forced to `/company-setup`.

The hook self-skips if `ALLOW_E2E_HOOKS` is disabled on the target server.
"""

from __future__ import annotations

import re
import uuid

import pytest
from playwright.sync_api import Page, expect

from helpers.factories import oauth_simulate


pytestmark = [pytest.mark.ui, pytest.mark.social_auth]


def _inject_tokens(page: Page, frontend_url: str, tokens: dict) -> None:
    """Put JWT tokens into localStorage under the frontend's origin.

    Must hit the origin first so localStorage is scoped correctly; navigating
    to `/login` is cheap, guaranteed to render, and does not require auth.
    """
    page.goto(f"{frontend_url}/login")
    page.evaluate(
        "(tokens) => localStorage.setItem('hr_prescan_tokens', JSON.stringify(tokens))",
        tokens,
    )


class TestNewCandidateFlow:
    """Brand-new social user → `/choose-role`, then picks candidate → dashboard."""

    def test_new_candidate_redirected_to_choose_role(
        self, page: Page, api, frontend_url
    ):
        data = oauth_simulate(api, state="new_candidate")
        _inject_tokens(page, frontend_url, data["tokens"])

        # Even though we ask for /dashboard, the router guard should force us
        # to /choose-role because onboarding_completed=False.
        page.goto(f"{frontend_url}/dashboard")
        expect(page).to_have_url(re.compile(r"/choose-role"), timeout=10_000)

    def test_choose_role_candidate_goes_to_dashboard(
        self, page: Page, api, frontend_url
    ):
        data = oauth_simulate(api, state="new_candidate")
        _inject_tokens(page, frontend_url, data["tokens"])

        page.goto(f"{frontend_url}/choose-role")
        expect(page).to_have_url(re.compile(r"/choose-role"), timeout=10_000)

        # The candidate button carries the i18n copy "I'm looking for a job".
        page.get_by_role("button", name=re.compile("looking for a job", re.IGNORECASE)).click()

        expect(page).to_have_url(re.compile(r"/dashboard"), timeout=10_000)


class TestNewHRFlow:
    """Social user picks HR → forced into `/company-setup` until form submitted."""

    def test_choose_role_hr_goes_to_company_setup(
        self, page: Page, api, frontend_url
    ):
        data = oauth_simulate(api, state="new_candidate")
        _inject_tokens(page, frontend_url, data["tokens"])

        page.goto(f"{frontend_url}/choose-role")
        expect(page).to_have_url(re.compile(r"/choose-role"), timeout=10_000)

        # The HR button carries the i18n copy "I'm hiring".
        page.get_by_role("button", name=re.compile("hiring", re.IGNORECASE)).click()

        expect(page).to_have_url(re.compile(r"/company-setup"), timeout=10_000)

    def test_complete_company_setup_form(self, page: Page, api, frontend_url):
        data = oauth_simulate(api, state="new_hr_needs_company")
        _inject_tokens(page, frontend_url, data["tokens"])

        # Landing anywhere inside the app funnels us to /company-setup.
        page.goto(f"{frontend_url}/dashboard")
        expect(page).to_have_url(re.compile(r"/company-setup"), timeout=10_000)

        # Fill the required fields.
        page.get_by_placeholder("Acme Inc.").fill(f"E2E OAuth Corp {uuid.uuid4().hex[:6]}")

        # Industries — type and pick the first suggestion.
        industries = page.locator(".p-autocomplete").first
        industries.locator("input").click()
        industries.locator("input").fill("tech")
        page.wait_for_timeout(500)
        # Pick whichever option surfaces first from the dropdown.
        first_option = page.locator(".p-autocomplete-option").first
        first_option.wait_for(state="visible", timeout=5_000)
        first_option.click()

        # Size — PrimeVue Select.
        page.locator("#size").click()
        page.get_by_role("option", name=re.compile("small", re.IGNORECASE)).first.click()

        # Country — autocomplete by typing.
        country_ac = page.locator(".p-autocomplete").last
        country_ac.locator("input").click()
        country_ac.locator("input").fill("Uzbek")
        page.wait_for_timeout(500)
        page.locator(".p-autocomplete-option").first.click()

        # Submit — the button label is "Continue".
        page.get_by_role("button", name=re.compile("continue", re.IGNORECASE)).click()

        expect(page).to_have_url(re.compile(r"/dashboard"), timeout=15_000)


class TestOnboardedCandidate:
    """Already-onboarded candidate → `/dashboard` loads with no redirect loop."""

    def test_dashboard_loads_directly(self, page: Page, api, frontend_url):
        data = oauth_simulate(api, state="onboarded_candidate")
        _inject_tokens(page, frontend_url, data["tokens"])

        page.goto(f"{frontend_url}/dashboard")
        expect(page).to_have_url(re.compile(r"/dashboard"), timeout=10_000)
        # Ensure we did NOT bounce into /choose-role or /company-setup.
        assert "/choose-role" not in page.url
        assert "/company-setup" not in page.url


class TestNewHRNeedsCompanyGuard:
    """HR user with no company is forced into `/company-setup` on every nav."""

    def test_dashboard_access_redirects_to_company_setup(
        self, page: Page, api, frontend_url
    ):
        data = oauth_simulate(api, state="new_hr_needs_company")
        _inject_tokens(page, frontend_url, data["tokens"])

        page.goto(f"{frontend_url}/dashboard")
        expect(page).to_have_url(re.compile(r"/company-setup"), timeout=10_000)

    def test_jobs_access_redirects_to_company_setup(
        self, page: Page, api, frontend_url
    ):
        data = oauth_simulate(api, state="new_hr_needs_company")
        _inject_tokens(page, frontend_url, data["tokens"])

        page.goto(f"{frontend_url}/jobs")
        expect(page).to_have_url(re.compile(r"/company-setup"), timeout=10_000)

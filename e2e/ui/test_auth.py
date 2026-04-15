"""Authentication UI E2E tests."""

import re

from playwright.sync_api import Page, expect

from helpers.factories import register_company, unique_email


class TestLogin:
    def test_login_redirects_to_dashboard(self, page: Page, api, frontend_url):
        # Register a user first via API
        data = register_company(api)

        page.goto(f"{frontend_url}/login")
        page.get_by_placeholder(re.compile("email", re.IGNORECASE)).fill(data["email"])
        page.get_by_placeholder(re.compile("password", re.IGNORECASE)).fill(data["password"])
        page.get_by_role("button", name="Sign In", exact=True).click()

        # Should redirect to dashboard
        expect(page).to_have_url(re.compile(r"/dashboard"), timeout=10_000)

    def test_login_invalid_shows_error(self, page: Page, frontend_url):
        page.goto(f"{frontend_url}/login")
        page.get_by_placeholder(re.compile("email", re.IGNORECASE)).fill("wrong@example.com")
        page.get_by_placeholder(re.compile("password", re.IGNORECASE)).fill("WrongPass1!")
        page.get_by_role("button", name="Sign In", exact=True).click()

        # Should see an error message (toast or inline)
        error = page.locator(".p-toast-message, [class*='error'], [class*='alert']")
        expect(error.first).to_be_visible(timeout=5_000)


class TestRegister:
    def test_register_candidate(self, page: Page, frontend_url):
        email = unique_email("ui-reg")

        page.goto(f"{frontend_url}/register")

        # Dismiss cookie consent if present
        accept_btn = page.get_by_role("button", name="Accept")
        if accept_btn.count() > 0 and accept_btn.is_visible():
            accept_btn.click()
            page.wait_for_timeout(500)

        page.get_by_placeholder("First name").fill("Test")
        page.get_by_placeholder("Last name").fill("User")
        page.get_by_placeholder("Enter your email").fill(email)
        page.get_by_placeholder("Minimum 8 characters").fill("TestPass123!")
        page.get_by_placeholder("Confirm your password").fill("TestPass123!")

        page.get_by_role("button", name="Create Account").click()

        # Verify registration succeeded — login with the new credentials via API
        page.wait_for_timeout(3_000)
        from helpers.api_client import ApiClient
        import os
        verify_api = ApiClient(page.context.request, os.getenv("API_URL", "http://localhost:8000/api"))
        resp = verify_api.post("/auth/login/", data={"email": email, "password": "TestPass123!"})
        assert resp.status == 200, "User was not created by registration"

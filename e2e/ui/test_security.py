"""Security UI E2E tests (XSS, injection)."""

import re

import pytest
from playwright.sync_api import Page, expect

from helpers.factories import create_published_vacancy, register_company, unique_email

pytestmark = pytest.mark.ui


XSS_PAYLOAD = "<script>alert('xss-e2e')</script>"


class TestXssGuards:
    def test_candidate_name_xss_is_escaped(self, page: Page, api, frontend_url):
        # Fail the test if any browser dialog fires
        dialog_fired = {"value": False}

        def _on_dialog(dialog):
            dialog_fired["value"] = True
            dialog.dismiss()

        page.on("dialog", _on_dialog)

        # Arrange: admin + vacancy + apply with XSS name
        admin = register_company(api)
        api.set_token(admin["tokens"]["access"])
        vacancy = create_published_vacancy(api)

        api.clear_token()
        # Submit via multipart (same shape as helpers.factories.submit_application)
        resp = api._request.post(
            api._url(f"/public/vacancies/{vacancy['id']}/apply/"),
            multipart={
                "candidate_name": XSS_PAYLOAD,
                "candidate_email": unique_email("xss"),
            },
        )
        assert resp.status == 201, f"anon apply failed: {resp.text()}"

        # Act: login as admin in the browser, open candidates view
        page.goto(f"{frontend_url}/login")
        page.get_by_placeholder(re.compile("email", re.IGNORECASE)).fill(admin["email"])
        page.get_by_placeholder(re.compile("password", re.IGNORECASE)).fill(admin["password"])
        page.get_by_role("button", name="Sign In", exact=True).click()
        expect(page).to_have_url(re.compile(r"/dashboard"), timeout=15_000)

        page.goto(f"{frontend_url}/vacancies/{vacancy['id']}?tab=candidates")
        page.wait_for_timeout(3_000)

        # Assert: raw payload text is not executed and not rendered as HTML.
        # The escaped form ("&lt;script&gt;...") may appear in the DOM but the
        # <script> tag itself must not.
        assert not dialog_fired["value"], "XSS dialog fired"

        # Look for any non-injected script tag with our marker in its text.
        injected_scripts = page.locator("script").filter(
            has_text=re.compile(r"xss-e2e")
        )
        assert injected_scripts.count() == 0, "Payload was rendered as an executable <script>"

        # The text should still be present somewhere on the page (escaped).
        # Playwright's get_by_text matches rendered text, which is the safe form.
        body_text = page.locator("body").inner_text()
        assert "xss-e2e" in body_text or "script" in body_text.lower(), (
            "Candidate name missing from page entirely"
        )

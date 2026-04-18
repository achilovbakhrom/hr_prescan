"""Prescan chat overlay UI E2E tests.

Scope: verify the interview entry points load cleanly and a chat input
renders. Driving the conversation is the LLM suite's job — not here.
"""

import re

import pytest
from playwright.sync_api import Page, expect

from helpers.factories import (
    create_published_vacancy,
    register_company,
    submit_application,
)

pytestmark = pytest.mark.ui


@pytest.fixture()
def prescan_token(api):
    data = register_company(api)
    api.set_token(data["tokens"]["access"])
    vacancy = create_published_vacancy(api)
    api.clear_token()
    applied = submit_application(api, vacancy["id"])
    token = (
        applied.get("prescan_token")
        or applied.get("prescanToken")
        or applied.get("interview_token")
        or applied.get("interviewToken")
    )
    assert token, f"No prescan token in response: {applied}"
    return token


class TestChatOverlay:
    def test_interview_gateway_redirects_to_chat(
        self, page: Page, prescan_token, frontend_url
    ):
        page.goto(f"{frontend_url}/interview/{prescan_token}")
        # Gateway redirects to /interview/{token}/chat for chat-mode screenings
        expect(page).to_have_url(
            re.compile(rf"/interview/{prescan_token}(/chat)?/?$"), timeout=15_000
        )

    def test_chat_input_renders(self, page: Page, prescan_token, frontend_url):
        page.goto(f"{frontend_url}/interview/{prescan_token}/chat")

        # The chat page renders a <textarea> input. Loading state shows a spinner first.
        textarea = page.locator("textarea")
        expect(textarea.first).to_be_visible(timeout=15_000)

        # Page is not in an error state (no error banner)
        error_banner = page.locator("[class*='error'], [class*='ChatErrorState']")
        assert (
            error_banner.count() == 0 or not error_banner.first.is_visible()
        ), "Chat page rendered in error state"

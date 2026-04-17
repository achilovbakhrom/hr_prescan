"""API-level tests for the E2E OAuth-simulation hook.

These verify that `POST /api/auth/debug/oauth-simulate/` puts a user in the
requested post-OAuth state, and that the standard onboarding/company-setup
endpoints continue to work for social-auth users created this way.

The hook is gated behind `ALLOW_E2E_HOOKS=true` on the server — if the flag
is off, `oauth_simulate` self-skips via `pytest.skip(...)` so these tests
are a no-op in environments where social-auth E2E isn't enabled.
"""

from __future__ import annotations

import uuid

import pytest

from helpers.api_client import ApiClient
from helpers.factories import oauth_simulate


pytestmark = [pytest.mark.api, pytest.mark.social_auth]


class TestOAuthSimulateStates:
    """The hook creates users in the three documented post-OAuth states."""

    def test_new_candidate_state(self, api: ApiClient):
        data = oauth_simulate(api, state="new_candidate")
        user = data["user"]

        assert user["role"] == "candidate"
        assert user["onboarding_completed"] is False
        assert user["company"] is None
        assert "access" in data["tokens"]
        assert "refresh" in data["tokens"]

    def test_onboarded_candidate_state(self, api: ApiClient):
        data = oauth_simulate(api, state="onboarded_candidate")
        user = data["user"]

        assert user["role"] == "candidate"
        assert user["onboarding_completed"] is True
        assert user["company"] is None

    def test_new_hr_needs_company_state(self, api: ApiClient):
        data = oauth_simulate(api, state="new_hr_needs_company")
        user = data["user"]

        assert user["role"] == "hr"
        assert user["company"] is None

    def test_telegram_provider_generates_telegram_email(self, api: ApiClient):
        data = oauth_simulate(api, state="new_candidate", provider="telegram")
        assert data["user"]["email"].endswith("@telegram.local")

    def test_explicit_email_is_respected(self, api: ApiClient):
        email = f"fixed+{uuid.uuid4().hex[:8]}@e2e.test"
        data = oauth_simulate(api, state="new_candidate", email=email)
        assert data["user"]["email"] == email


class TestCompleteOnboardingAfterOAuth:
    """Candidate picks the candidate role on `/choose-role` → onboarding done."""

    def test_candidate_completes_onboarding(self, api: ApiClient):
        data = oauth_simulate(api, state="new_candidate")
        api.set_token(data["tokens"]["access"])

        resp = api.post("/auth/complete-onboarding/", data={"role": "candidate"})
        assert resp.status == 200, f"complete-onboarding failed: {resp.text()}"

        body = resp.json()
        assert body["user"]["role"] == "candidate"
        assert body["user"]["onboarding_completed"] is True
        # Fresh tokens returned so the frontend can refresh its auth state.
        assert "access" in body["tokens"]

        # /auth/me/ reflects the new state
        api.set_token(body["tokens"]["access"])
        me = api.get("/auth/me/")
        assert me.status == 200
        assert me.json()["onboarding_completed"] is True


class TestCompleteCompanySetupAfterOAuth:
    """HR picks HR role → fills company setup → becomes company admin."""

    def test_hr_completes_company_setup(self, api: ApiClient):
        data = oauth_simulate(api, state="new_hr_needs_company")
        api.set_token(data["tokens"]["access"])

        resp = api.post(
            "/auth/complete-company-setup/",
            data={
                "company_name": f"OAuth Corp {uuid.uuid4().hex[:6]}",
                "size": "small",
                "country": "UZ",
                "industries": [],
            },
        )
        assert resp.status in (200, 201), (
            f"complete-company-setup failed: {resp.text()}"
        )

        body = resp.json()
        # After company setup the HR who created the company is the admin.
        assert body["user"]["role"] == "admin"
        assert body["user"]["company"] is not None
        assert body["user"]["company"]["name"].startswith("OAuth Corp")
        assert "access" in body["tokens"]

"""Test data factories that create objects via the real API.

Every factory returns all created data so tests can assert on it.
Uses unique emails per call to avoid collisions in parallel runs.
"""

from __future__ import annotations

import uuid
from typing import Any

from helpers.api_client import ApiClient


def unique_email(prefix: str = "test") -> str:
    return f"{prefix}+{uuid.uuid4().hex[:8]}@e2e.test"


def register_candidate(api: ApiClient) -> dict[str, Any]:
    """Register a candidate user and login. Returns {user, tokens, email, password}."""
    email = unique_email("candidate")
    password = "TestPass123!"
    resp = api.post("/auth/register/", data={
        "email": email,
        "first_name": "Test",
        "last_name": "Candidate",
        "password": password,
    })
    assert resp.status == 201, f"Register failed: {resp.text()}"
    # Register returns {detail, user} — no tokens. Must login separately.
    login_data = api.login(email, password)
    return {
        "user": login_data["user"],
        "tokens": login_data["tokens"],
        "email": email,
        "password": password,
    }


def register_company(api: ApiClient) -> dict[str, Any]:
    """Register a new company with an admin user by chaining the real public flow:
    register candidate → login → complete-company-setup. There's no single-shot
    "company-register" endpoint on the backend.

    Returns {company, user, tokens, email, password}.
    """
    email = unique_email("admin")
    password = "TestPass123!"

    resp = api.post("/auth/register/", data={
        "email": email,
        "password": password,
        "first_name": "Admin",
        "last_name": "User",
    })
    assert resp.status == 201, f"Register failed: {resp.text()}"

    login_data = api.login(email, password)

    resp = api.post("/auth/complete-company-setup/", data={
        "company_name": f"E2E Corp {uuid.uuid4().hex[:6]}",
        "size": "small",
        "country": "UZ",
        "industries": [],
    })
    assert resp.status in (200, 201), f"complete-company-setup failed: {resp.text()}"
    setup = resp.json()
    # Refresh tokens returned by the setup endpoint take the new ADMIN role into account
    api.set_token(setup["tokens"]["access"])

    return {
        "company": setup["user"]["company"],
        "user": setup["user"],
        "tokens": setup["tokens"],
        "email": email,
        "password": password,
    }


def invite_and_accept_hr(
    admin_api: ApiClient,
    new_api: ApiClient,
    permissions: list[str] | None = None,
) -> dict[str, Any]:
    """Invite an HR user and accept the invitation. Returns {user, tokens, email, password}."""
    email = unique_email("hr")
    password = "TestPass123!"

    # Invite
    resp = admin_api.post("/hr/company/invite/", data={
        "email": email,
        "permissions": permissions or [
            "manage_vacancies",
            "manage_candidates",
            "manage_interviews",
            "manage_team",
            "view_analytics",
            "manage_settings",
        ],
    })
    assert resp.status == 201, f"Invite failed: {resp.text()}"
    invitation = resp.json()["invitation"]

    # Accept invitation (new user)
    resp = new_api.post("/auth/accept-invitation/", data={
        "token": invitation["token"],
        "first_name": "HR",
        "last_name": "Manager",
        "password": password,
    })
    assert resp.status == 201, f"Accept failed: {resp.text()}"

    # Login as the new HR user
    login_data = new_api.login(email, password)
    return {
        "user": login_data["user"],
        "tokens": login_data["tokens"],
        "email": email,
        "password": password,
        "invitation": invitation,
    }


def create_published_vacancy(api: ApiClient) -> dict[str, Any]:
    """Create a vacancy with a prescanning question and publish it."""
    # Create draft
    resp = api.post("/hr/vacancies/", data={
        "title": f"E2E Test Vacancy {uuid.uuid4().hex[:6]}",
        "description": "A test vacancy for E2E testing.",
        "requirements": "Python, Django, REST APIs",
        "skills": ["python", "django"],
        "experience_level": "middle",
        "employment_type": "full_time",
        "location": "Remote",
        "is_remote": True,
        "prescanning_language": "en",
    })
    assert resp.status == 201, f"Create vacancy failed: {resp.text()}"
    vacancy = resp.json()
    vacancy_id = vacancy["id"]

    # Add a prescanning question
    resp = api.post(f"/hr/vacancies/{vacancy_id}/questions/", data={
        "text": "Tell me about your experience with Python and Django.",
        "category": "Hard Skill",
        "step": "prescanning",
    })
    assert resp.status == 201, f"Add question failed: {resp.text()}"

    # Publish
    resp = api.patch(f"/hr/vacancies/{vacancy_id}/status/", data={"action": "publish"})
    assert resp.status == 200, f"Publish failed: {resp.text()}"

    # Re-fetch detail
    resp = api.get(f"/hr/vacancies/{vacancy_id}/")
    assert resp.status == 200
    return resp.json()


def submit_application(api: ApiClient, vacancy_id: str) -> dict[str, Any]:
    """Submit a candidate application to a vacancy. Returns {application, prescan_token}."""
    email = unique_email("applicant")
    # Apply endpoint uses MultiPartParser — send as multipart, not JSON
    resp = api._request.post(
        api._url(f"/public/vacancies/{vacancy_id}/apply/"),
        multipart={
            "candidate_name": "Test Applicant",
            "candidate_email": email,
        },
    )
    assert resp.status == 201, f"Apply failed: {resp.text()}"
    return {**resp.json(), "candidate_email": email}


def oauth_simulate(
    api: ApiClient,
    state: str,
    provider: str = "google",
    email: str | None = None,
) -> dict[str, Any]:
    """Call the backend E2E hook to simulate a post-OAuth user in a given state.

    `state` is one of: "new_candidate", "onboarded_candidate", "new_hr_needs_company".
    Requires ALLOW_E2E_HOOKS=true on the server. Skips the calling test if the
    endpoint returns 404.
    """
    import pytest

    payload: dict[str, Any] = {"state": state, "provider": provider}
    if email:
        payload["email"] = email
    resp = api.post("/auth/debug/oauth-simulate/", data=payload)
    if resp.status == 404:
        pytest.skip("ALLOW_E2E_HOOKS not enabled on target server")
    assert resp.status == 200, f"oauth-simulate failed ({resp.status}): {resp.text()}"
    return resp.json()

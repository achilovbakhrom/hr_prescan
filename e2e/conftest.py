"""Root conftest — shared fixtures for all E2E tests.

Three fixture scopes:

- `api` (function) — unauthenticated, fresh per test. Used when a test creates
  its own throwaway company/candidate via `register_company` / `register_candidate`.
- `persistent_admin_api` / `persistent_candidate_api` (session) — pre-authenticated
  against permanent accounts on the target environment, reused across all tests.
  Use these when you don't need a brand-new company.
- `run_tag` (session) — short unique ID (e.g. `e2e-ab12cd`) to prefix per-run
  resources so they're easy to identify and clean up.
"""

from __future__ import annotations

import os
import uuid

import pytest
from dotenv import load_dotenv
from playwright.sync_api import Playwright

from helpers.api_client import ApiClient

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000/api")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
ADMIN_EMAIL = os.getenv("E2E_ADMIN_EMAIL", "")
ADMIN_PASSWORD = os.getenv("E2E_ADMIN_PASSWORD", "")
CANDIDATE_EMAIL = os.getenv("E2E_CANDIDATE_EMAIL", "")
CANDIDATE_PASSWORD = os.getenv("E2E_CANDIDATE_PASSWORD", "")


# ---------------------------------------------------------------------------
# Session-scoped target config
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def api_url() -> str:
    return API_URL


@pytest.fixture(scope="session")
def frontend_url() -> str:
    return FRONTEND_URL


@pytest.fixture(scope="session")
def run_tag() -> str:
    """Short unique prefix for this test run. Helps identify leftover resources."""
    return f"e2e-{uuid.uuid4().hex[:6]}"


# ---------------------------------------------------------------------------
# Function-scoped fresh API context (unauthenticated)
# ---------------------------------------------------------------------------


@pytest.fixture()
def request_context(playwright: Playwright):
    """A fresh Playwright APIRequestContext for each test."""
    context = playwright.request.new_context(base_url=API_URL)
    yield context
    context.dispose()


@pytest.fixture()
def api(request_context) -> ApiClient:
    """Unauthenticated ApiClient. Tests call api.login() or factories as needed."""
    return ApiClient(request_context, API_URL)


# ---------------------------------------------------------------------------
# Session-scoped permanent-account clients
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def _session_request_context(playwright: Playwright):
    context = playwright.request.new_context(base_url=API_URL)
    yield context
    context.dispose()


@pytest.fixture(scope="session")
def persistent_admin_api(_session_request_context) -> ApiClient:
    """ApiClient authenticated as the permanent dev admin (company owner).

    Skips the test if E2E_ADMIN_EMAIL/PASSWORD aren't set — lets you run the
    throwaway-account subset without needing permanent creds.
    """
    if not ADMIN_EMAIL or not ADMIN_PASSWORD:
        pytest.skip("E2E_ADMIN_EMAIL / E2E_ADMIN_PASSWORD not configured")
    client = ApiClient(_session_request_context, API_URL)
    client.login(ADMIN_EMAIL, ADMIN_PASSWORD)
    return client


@pytest.fixture(scope="session")
def persistent_candidate_api(_session_request_context) -> ApiClient:
    """ApiClient authenticated as the permanent dev candidate."""
    if not CANDIDATE_EMAIL or not CANDIDATE_PASSWORD:
        pytest.skip("E2E_CANDIDATE_EMAIL / E2E_CANDIDATE_PASSWORD not configured")
    client = ApiClient(_session_request_context, API_URL)
    client.login(CANDIDATE_EMAIL, CANDIDATE_PASSWORD)
    return client


# ---------------------------------------------------------------------------
# Per-run cleanup — best-effort archive vacancies created by this run
# ---------------------------------------------------------------------------

_created_vacancy_ids: list[tuple[ApiClient, str]] = []


def register_vacancy_for_cleanup(api: ApiClient, vacancy_id: str) -> None:
    """Call this after creating a vacancy to have it archived on session teardown."""
    _created_vacancy_ids.append((api, vacancy_id))


@pytest.fixture(scope="session", autouse=True)
def _cleanup_created_vacancies():
    """Archive vacancies created during the run to keep the dev DB tidy."""
    yield
    for client, vid in _created_vacancy_ids:
        try:
            client.patch(f"/hr/vacancies/{vid}/status/", data={"action": "archive"})
        except Exception:
            pass  # best effort — failures here should never break the run


# Re-export auth fixtures so they're available everywhere
from fixtures.auth import admin_company, admin_api, hr_user_data, hr_api  # noqa: F401, E402

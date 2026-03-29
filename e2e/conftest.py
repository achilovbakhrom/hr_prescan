"""Root conftest — shared fixtures for all E2E tests."""

from __future__ import annotations

import os

import pytest
from dotenv import load_dotenv
from playwright.sync_api import Playwright

from helpers.api_client import ApiClient

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000/api")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


@pytest.fixture(scope="session")
def api_url() -> str:
    return API_URL


@pytest.fixture(scope="session")
def frontend_url() -> str:
    return FRONTEND_URL


@pytest.fixture()
def request_context(playwright: Playwright):
    """A fresh Playwright APIRequestContext for each test."""
    context = playwright.request.new_context(base_url=API_URL)
    yield context
    context.dispose()


@pytest.fixture()
def api(request_context) -> ApiClient:
    """An unauthenticated ApiClient. Tests call api.login() as needed."""
    return ApiClient(request_context, API_URL)


# Re-export auth fixtures so they're available everywhere
from fixtures.auth import admin_company, admin_api, hr_user_data, hr_api  # noqa: F401, E402

"""Reusable pytest fixtures for authenticated API contexts."""

from __future__ import annotations

import os

import pytest

from helpers.api_client import ApiClient
from helpers.factories import register_company, invite_and_accept_hr

API_URL = os.getenv("API_URL", "http://localhost:8000/api")


@pytest.fixture()
def admin_company(api: ApiClient) -> dict:
    """Register a new company and admin user. Returns factory output."""
    return register_company(api)


@pytest.fixture()
def admin_api(api: ApiClient, admin_company: dict) -> ApiClient:
    """ApiClient authenticated as the company admin."""
    api.set_token(admin_company["tokens"]["access"])
    return api


@pytest.fixture()
def hr_user_data(admin_api: ApiClient, request_context) -> dict:
    """Invite and accept an HR user with full permissions. Returns factory output."""
    hr_api = ApiClient(request_context, admin_api._base_url)
    return invite_and_accept_hr(admin_api, hr_api)


@pytest.fixture()
def hr_api(request_context, hr_user_data: dict) -> ApiClient:
    """ApiClient authenticated as the HR user."""
    client = ApiClient(request_context, API_URL)
    client.set_token(hr_user_data["tokens"]["access"])
    return client

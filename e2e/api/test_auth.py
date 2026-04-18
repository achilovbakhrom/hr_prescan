"""Authentication API E2E tests."""

import pytest

from helpers.api_client import ApiClient
from helpers.factories import register_candidate, register_company, unique_email


class TestRegister:
    def test_register_candidate(self, api: ApiClient):
        email = unique_email("reg")
        resp = api.post("/auth/register/", data={
            "email": email,
            "first_name": "Jane",
            "last_name": "Doe",
            "password": "SecurePass1!",
        })
        assert resp.status == 201
        body = resp.json()
        assert body["user"]["email"] == email
        assert body["user"]["role"] == "candidate"

    def test_register_duplicate_email(self, api: ApiClient):
        email = unique_email("dup")
        api.post("/auth/register/", data={
            "email": email,
            "first_name": "First",
            "last_name": "User",
            "password": "SecurePass1!",
        })

        resp = api.post("/auth/register/", data={
            "email": email,
            "first_name": "Second",
            "last_name": "User",
            "password": "SecurePass1!",
        })
        assert resp.status == 400

    def test_register_company(self, api: ApiClient):
        data = register_company(api)
        assert data["user"]["role"] == "admin"
        assert data["company"] is not None
        assert data["company"]["name"].startswith("E2E Corp")


class TestLogin:
    def test_login_valid(self, api: ApiClient):
        data = register_company(api)
        api.clear_token()
        resp = api.post("/auth/login/", data={
            "email": data["email"],
            "password": data["password"],
        })
        assert resp.status == 200
        body = resp.json()
        assert body["user"]["email"] == data["email"]
        assert "access" in body["tokens"]

    def test_login_wrong_password(self, api: ApiClient):
        data = register_company(api)
        api.clear_token()
        resp = api.post("/auth/login/", data={
            "email": data["email"],
            "password": "WrongPassword!",
        })
        assert resp.status == 401

    def test_login_nonexistent_user(self, api: ApiClient):
        resp = api.post("/auth/login/", data={
            "email": "nonexistent@example.com",
            "password": "Whatever1!",
        })
        assert resp.status == 401


class TestTokenRefresh:
    def test_refresh_valid(self, api: ApiClient):
        data = register_company(api)
        refresh_token = data["tokens"]["refresh"]
        api.clear_token()

        resp = api.post("/auth/token/refresh/", data={"refresh": refresh_token})
        assert resp.status == 200
        assert "access" in resp.json()

    def test_refresh_invalid_token(self, api: ApiClient):
        resp = api.post("/auth/token/refresh/", data={"refresh": "invalid-token"})
        assert resp.status == 401


class TestMe:
    def test_get_me_authenticated(self, api: ApiClient):
        data = register_company(api)
        api.set_token(data["tokens"]["access"])

        resp = api.get("/auth/me/")
        assert resp.status == 200
        assert resp.json()["email"] == data["email"]

    def test_get_me_unauthenticated(self, api: ApiClient):
        api.clear_token()
        resp = api.get("/auth/me/")
        assert resp.status == 401

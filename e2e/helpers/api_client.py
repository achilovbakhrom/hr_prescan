"""Low-level API helpers for E2E tests.

Wraps Playwright's APIRequestContext to call the Django backend directly.
All payloads use snake_case (Django convention — no camelCase conversion).
"""

from __future__ import annotations

from typing import Any

from playwright.sync_api import APIRequestContext


class ApiClient:
    """Thin wrapper around Playwright APIRequestContext with auth support."""

    def __init__(self, request: APIRequestContext, base_url: str) -> None:
        self._request = request
        self._base_url = base_url.rstrip("/")
        self._token: str | None = None

    # -- auth ----------------------------------------------------------------

    def login(self, email: str, password: str) -> dict[str, Any]:
        """POST /auth/login/ and store the access token for subsequent calls."""
        resp = self.post("/auth/login/", data={"email": email, "password": password})
        assert resp.status == 200, f"Login failed ({resp.status}): {resp.text()}"
        body = resp.json()
        self._token = body["tokens"]["access"]
        return body

    def set_token(self, token: str) -> None:
        self._token = token

    def clear_token(self) -> None:
        self._token = None

    # -- HTTP verbs ----------------------------------------------------------

    def get(self, path: str, **kwargs: Any):
        return self._request.get(self._url(path), headers=self._headers(), **kwargs)

    def post(self, path: str, *, data: Any = None, **kwargs: Any):
        return self._request.post(self._url(path), data=data, headers=self._headers(), **kwargs)

    def patch(self, path: str, *, data: Any = None, **kwargs: Any):
        return self._request.patch(self._url(path), data=data, headers=self._headers(), **kwargs)

    def put(self, path: str, *, data: Any = None, **kwargs: Any):
        return self._request.put(self._url(path), data=data, headers=self._headers(), **kwargs)

    def delete(self, path: str, *, data: Any = None, **kwargs: Any):
        return self._request.delete(self._url(path), data=data, headers=self._headers(), **kwargs)

    # -- internals -----------------------------------------------------------

    def _url(self, path: str) -> str:
        path = path if path.startswith("/") else f"/{path}"
        # Ensure trailing slash (Django APPEND_SLASH)
        if not path.endswith("/"):
            path += "/"
        return f"{self._base_url}{path}"

    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

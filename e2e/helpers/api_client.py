"""Low-level API helpers for E2E tests.

Wraps Playwright's APIRequestContext to call the Django backend directly.
All payloads use snake_case (Django convention — no camelCase conversion).

Responses that return a 5xx are retried up to `_MAX_RETRIES` times with a
short backoff, because the dev server occasionally returns 502/503 during
rolling deploys or container cold starts.
"""

from __future__ import annotations

import time
from typing import Any

from playwright.sync_api import APIRequestContext, APIResponse


_MAX_RETRIES = 5
_BACKOFF_SECONDS = 1.0


class ApiClient:
    """Thin wrapper around Playwright APIRequestContext with auth + retry support."""

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

    def get(self, path: str, **kwargs: Any) -> APIResponse:
        return self._send("get", path, **kwargs)

    def post(self, path: str, *, data: Any = None, **kwargs: Any) -> APIResponse:
        return self._send("post", path, data=data, **kwargs)

    def patch(self, path: str, *, data: Any = None, **kwargs: Any) -> APIResponse:
        return self._send("patch", path, data=data, **kwargs)

    def put(self, path: str, *, data: Any = None, **kwargs: Any) -> APIResponse:
        return self._send("put", path, data=data, **kwargs)

    def delete(self, path: str, *, data: Any = None, **kwargs: Any) -> APIResponse:
        return self._send("delete", path, data=data, **kwargs)

    # -- internals -----------------------------------------------------------

    def _send(self, method: str, path: str, **kwargs: Any) -> APIResponse:
        url = self._url(path)
        headers = self._headers()
        fn = getattr(self._request, method)
        last: APIResponse | None = None
        for attempt in range(_MAX_RETRIES):
            last = fn(url, headers=headers, **kwargs)
            if last.status < 500:
                return last
            # Exponential backoff — dev nginx 503s under concurrent cold-start load
            time.sleep(_BACKOFF_SECONDS * (2 ** attempt))
        return last  # type: ignore[return-value]

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

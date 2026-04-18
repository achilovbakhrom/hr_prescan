"""One-time provisioning: create permanent E2E accounts on the target environment.

Run this once against dev.prescreen-app.com to create the persistent admin +
candidate. Credentials are printed at the end — copy them into `e2e/.env`.

Idempotent: if the target email already exists, the login path is used instead
of re-registering and the credentials are emitted unchanged.

Usage:
    cd e2e
    python -m helpers.register_permanent_accounts \
        --api-url https://dev.prescreen-app.com/api \
        --admin-email e2e-admin@prescreen-test.dev \
        --candidate-email e2e-candidate@prescreen-test.dev \
        --password 'StrongPass!123'

Safety: we intentionally hard-code non-obvious emails so these accounts stand
out in the dev admin UI. Update the company name below if you want something
different.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

import requests

COMPANY_NAME = "E2E Permanent Test Co — DO NOT DELETE"


def _post(
    api_url: str,
    path: str,
    payload: dict[str, Any],
    token: str | None = None,
) -> tuple[int, dict[str, Any]]:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    resp = requests.post(
        f"{api_url.rstrip('/')}{path}",
        json=payload,
        headers=headers,
        timeout=30,
    )
    try:
        body = resp.json()
    except ValueError:
        body = {"raw": resp.text}
    return resp.status_code, body


def ensure_admin(api_url: str, email: str, password: str) -> str:
    """Ensure a company admin exists with the given credentials.

    Flow: register → login → complete-company-setup. The backend has no
    single-shot "company-register" endpoint, so we chain the real public flow.

    Idempotent: if the account already exists as an admin with a company, the
    login succeeds and `me` reports role=admin and we short-circuit.
    """
    # 1. Try login first — idempotent path
    code, body = _post(api_url, "/auth/login/", {"email": email, "password": password})
    if code == 200:
        user = body.get("user", {})
        if user.get("role") == "admin" and user.get("company"):
            return f"[admin] Login OK ({email}) — already provisioned as admin."
        # User exists but isn't an admin yet — finish the company setup
        token = body["tokens"]["access"]
        return _finish_company_setup(api_url, email, token)

    # 2. Register as a candidate (the only public entry point)
    code, body = _post(
        api_url,
        "/auth/register/",
        {
            "email": email,
            "password": password,
            "first_name": "E2E",
            "last_name": "Admin",
        },
    )
    if code != 201:
        raise RuntimeError(f"Register failed for admin {email}: {code} {json.dumps(body)}")

    # 3. Login to get tokens (email verification is not required for login)
    code, body = _post(api_url, "/auth/login/", {"email": email, "password": password})
    if code != 200:
        raise RuntimeError(f"Login after register failed: {code} {json.dumps(body)}")
    token = body["tokens"]["access"]
    return _finish_company_setup(api_url, email, token)


def _finish_company_setup(api_url: str, email: str, access_token: str) -> str:
    code, body = _post(
        api_url,
        "/auth/complete-company-setup/",
        {
            "company_name": COMPANY_NAME,
            "size": "small",
            "country": "UZ",
            "industries": [],
        },
        token=access_token,
    )
    if code in (200, 201):
        return f"[admin] Created company {COMPANY_NAME!r} for {email}"
    raise RuntimeError(f"complete-company-setup failed: {code} {json.dumps(body)}")


def ensure_candidate(api_url: str, email: str, password: str) -> str:
    code, body = _post(api_url, "/auth/login/", {"email": email, "password": password})
    if code == 200:
        return f"[candidate] Login OK ({email}) — account already provisioned."

    code, body = _post(
        api_url,
        "/auth/register/",
        {
            "email": email,
            "first_name": "E2E",
            "last_name": "Candidate",
            "password": password,
        },
    )
    if code == 201:
        return f"[candidate] Registered {email}"
    raise RuntimeError(f"Unexpected candidate-provision response {code}: {json.dumps(body)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-url", required=True)
    parser.add_argument("--admin-email", required=True)
    parser.add_argument("--candidate-email", required=True)
    parser.add_argument("--password", required=True, help="Password used for BOTH accounts")
    args = parser.parse_args()

    print(f"Target: {args.api_url}")
    print(ensure_admin(args.api_url, args.admin_email, args.password))
    print(ensure_candidate(args.api_url, args.candidate_email, args.password))
    print()
    print("Paste these into e2e/.env:")
    print(f"E2E_ADMIN_EMAIL={args.admin_email}")
    print(f"E2E_ADMIN_PASSWORD={args.password}")
    print(f"E2E_CANDIDATE_EMAIL={args.candidate_email}")
    print(f"E2E_CANDIDATE_PASSWORD={args.password}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

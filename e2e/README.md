# E2E tests

Playwright + pytest suite targeting either local dev or `dev.prescreen-app.com`.

## Layers

| Path       | Scope                                                               |
|------------|---------------------------------------------------------------------|
| `api/`     | Backend contracts via Playwright's APIRequestContext. Fast, deterministic. |
| `ui/`      | Browser flows with Playwright. Critical P0 paths only.              |
| `llm/`     | Prescan AI end-to-end: drives the chat to completion and asserts on scores / summary. Marked `@pytest.mark.llm` — skipped by default, costs API credits. |

## Setup

```bash
cd e2e
uv venv && source .venv/bin/activate
uv pip install -e .
playwright install chromium
cp .env.example .env
# fill in E2E_* credentials
```

### Provision permanent accounts (one-time, per target env)

```bash
python -m helpers.register_permanent_accounts \
    --api-url https://dev.prescreen-app.com/api \
    --admin-email e2e-admin@prescreen-test.dev \
    --candidate-email e2e-candidate@prescreen-test.dev \
    --password 'StrongPass!123'
```

Copy the printed creds into `.env`. Idempotent — re-running just logs in.

### Enable OAuth test hook + suppress test emails on the target server

Social-auth tests use `/api/auth/debug/oauth-simulate/` to bypass real Google /
Telegram OAuth. Register + invite flows send real email by default, which
spams the dev admin inbox. Both are controlled via env vars read by the
backend container.

On the dev server, add to the deploy env file:

```
ALLOW_E2E_HOOKS=true
EMAIL_SUPPRESS_DOMAINS=e2e.test,prescreen-test.dev,telegram.local
```

Then redeploy (or `docker compose up -d django` if you only changed env).
Production must leave both unset.

- `ALLOW_E2E_HOOKS=true` — enables `/api/auth/debug/oauth-simulate/`.
- `EMAIL_SUPPRESS_DOMAINS` — comma-separated recipient domains to silently
  drop. The backend still logs `Email suppressed (test domain): ...` so you
  can confirm it's filtering.

## Running

```bash
# Default run — skips LLM tests
pytest

# Only API
pytest api/

# Only UI (headful is useful for debugging)
pytest ui/ --headed

# Include LLM tests (slow, costs credits)
pytest -m llm

# Everything including LLM
pytest -m "not _never_"   # any marker string that doesn't exclude llm
```

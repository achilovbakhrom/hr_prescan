---
name: test
description: Run QA tests — backend (pytest), frontend (vitest), E2E (playwright), or all. Can run specific tests or full suites.
user-invocable: true
---

# QA Test Runner

Run automated tests for the HR PreScan project. Supports backend, frontend, E2E, or all test suites.

## Usage

- `/test` — run all test suites (backend + frontend + e2e)
- `/test backend` — run backend tests only (pytest)
- `/test frontend` — run frontend unit tests only (vitest)
- `/test e2e` — run all E2E tests (playwright)
- `/test backend apps/applications` — run specific backend test module
- `/test e2e tests/e2e/candidate-pipeline.spec.ts` — run specific E2E test file
- `/test --fix` — run tests and auto-fix any failures found

## Steps

### 1. Parse Arguments

Determine which test suite(s) to run from the user's input:
- No args or "all" → run all suites sequentially
- "backend" → pytest only
- "frontend" → vitest only
- "e2e" → playwright only
- Additional path arg → pass to the test runner as target
- "--fix" flag → after running tests, attempt to fix failures

### 2. Backend Tests (pytest)

```bash
cd backend && ../.venv/bin/python -m pytest <target> -v --tb=short 2>&1
```

- Default target: `tests/` directory
- If a specific module is given (e.g., `apps/applications`), pass it directly
- Report: show passed/failed/errors count
- On failure: show the failing test name, assertion error, and relevant code

### 3. Frontend Tests (vitest)

```bash
cd frontend && npx vitest run <target> --reporter=verbose 2>&1
```

- Default: run all tests
- If a specific file is given, pass it as target
- Report: show passed/failed count

### 4. E2E Tests (playwright)

```bash
cd frontend && npx playwright test <target> --reporter=list 2>&1
```

- Default: run all E2E tests in `tests/e2e/`
- If a specific file is given, pass it as target
- Requires the app to be running (check first with a curl to localhost)
- If app is not running, warn the user: "Start the app first with `make local-dev` or `make dev`"

### 5. Report Results

For each suite that was run, output:
- Total / Passed / Failed / Skipped counts
- List of failed tests with error messages
- If `--fix` flag was provided and there are failures:
  - Read the failing test and the source code it tests
  - Determine if the issue is in the test or the source code
  - Fix the issue and re-run that specific test to verify

### 6. Summary

At the end, output a summary table:

```
Suite      | Passed | Failed | Skipped
-----------|--------|--------|--------
Backend    |   42   |   0    |   2
Frontend   |   18   |   1    |   0
E2E        |   12   |   0    |   0
```

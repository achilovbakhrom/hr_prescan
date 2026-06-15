---
name: test
description: Run the AUTOMATED test suites — backend (pytest), frontend (vitest), E2E (playwright), or all; specific tests or full suites. This is code-level automated testing, NOT driving the live app (that's /qa). Delegates to the test-runner subagent.
user-invocable: true
---

# QA Test Runner

Thin wrapper that delegates to the **`test-runner`** subagent (full methodology in `.claude/agents/test-runner.md`).

When invoked:
1. Spawn the `test-runner` agent via the Agent tool (`subagent_type: "test-runner"`), passing the user's arguments verbatim (no args → all suites; `backend`/`frontend`/`e2e`; a trailing path; `--fix`).
2. Relay the agent's pass/fail summary table. The agent reports BLOCKED (not passed/failed) when the test DB or app isn't reachable, and fixes failures only when `--fix` is passed.

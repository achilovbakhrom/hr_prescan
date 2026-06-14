---
name: review
description: Review code before committing/pushing — fans out two subagents in parallel, code-reviewer (quality, security, performance, architecture) and business-reviewer (consistency with docs/BUSINESS_LOGIC.md), and merges their findings. Supports full codebase, specific features, or changed files.
user-invocable: true
---

# Review

Thin wrapper that runs **two reviewers in parallel** and merges their reports:
- **`code-reviewer`** — quality, security, performance, architecture, conventions (`.claude/agents/code-reviewer.md`).
- **`business-reviewer`** — consistency with `docs/BUSINESS_LOGIC.md`: flows, statuses, permissions, multi-tenancy, doc-sync (`.claude/agents/business-reviewer.md`).

When invoked:
1. Spawn **both** agents in a single message so they run concurrently (Agent tool, `subagent_type: "code-reviewer"` and `"business-reviewer"`), passing the user's arguments verbatim as scope (no args → uncommitted diff; `backend`/`frontend`/a path; `all`; `--fix`). For a large multi-area code scope you may also spawn several `code-reviewer` agents (one per area).
2. **Merge** into one report: Critical / Warnings / Suggestions (from code-reviewer) + OK / WARNING / ISSUE (from business-reviewer), with a combined Summary. Agents only edit files when args include `--fix`.

Scope modifiers:
- `--code-only` → run just `code-reviewer`. `--business-only` → run just `business-reviewer`.

This satisfies the project's "run /review before committing/pushing" rule and the "keep BUSINESS_LOGIC.md in sync" mandate in one pass — both lenses, isolated agent contexts.

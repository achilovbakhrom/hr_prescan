---
name: review
description: Review code for quality, security, performance, and architecture. Supports full codebase, specific features, or changed files.
user-invocable: true
---

# Code Review

Review code for quality, security, performance, architecture, and consistency with project conventions.

## Usage

- `/review` — review all uncommitted changes (git diff)
- `/review all` — review the entire codebase (high-level scan)
- `/review backend` — review all backend code
- `/review frontend` — review all frontend code
- `/review backend/apps/accounts` — review a specific module
- `/review frontend/src/features/candidates` — review a specific feature
- `/review --fix` — review and auto-fix issues found

## Steps

### 1. Determine Scope

Parse the arguments:
- No args → review uncommitted changes (`git diff` + `git diff --cached` + untracked files)
- `all` → scan entire codebase (read key files, check structure)
- `backend` / `frontend` → scan that layer
- Specific path → review that directory/file
- `--fix` flag → fix issues after review

### 2. Read Project Conventions

Before reviewing, read:
- `CLAUDE.md` for project rules
- `docs/CODE_STYLE.md` if it exists
- `docs/BUSINESS_LOGIC.md` for domain context

### 3. Linter Awareness

The backend uses **Ruff** (not Flake8) for linting and formatting. Ruff config lives in `backend/pyproject.toml` under `[tool.ruff]`. When reviewing:
- Suggest Ruff rule codes (e.g., `# noqa: S101`), not Flake8 codes
- Format suggestions should reference `ruff format`, not `black` or `autopep8`
- Import sorting is handled by Ruff's isort (`I` rules), not standalone isort

### 4. Backend Review (GRASP Principles)

Review backend Python/Django code against these criteria:

**Architecture (GRASP):**
- **Information Expert** — is logic placed in the class/module that has the data? Services should contain business logic, not views/serializers
- **Creator** — are objects created by the right module? (services create models, not views)
- **Controller** — do API views only handle HTTP concerns (parse input, call service, format output)?
- **Low Coupling** — are modules loosely coupled? Check for circular imports, cross-app direct model access
- **High Cohesion** — does each module have a single, clear responsibility?
- **Polymorphism** — are conditionals used where polymorphism would be cleaner?
- **Pure Fabrication** — are utility/service classes justified?
- **Indirection** — is the service layer used consistently (views → services → models)?
- **Protected Variations** — are interfaces stable? Are implementation details hidden?

**Project Patterns:**
- Service Layer: business logic in `services.py`, not in views or serializers
- Selectors: read queries in `selectors.py`, not inline in views
- Serializers: input validation + output formatting only, no business logic
- Models: data + constraints only, no business logic methods
- URLs: clean RESTful structure
- Migrations: no data loss, reversible where possible

**Code Quality:**
- DRY — duplicated logic?
- Dead code — unused imports, functions, variables?
- Naming — clear, consistent, Pythonic?
- Error handling — using `ApplicationError` consistently? Catching too broad?
- Type hints — present and correct?
- N+1 queries — missing `select_related`/`prefetch_related`?
- Security — raw SQL, unsanitized input, exposed secrets, missing permission checks?

**Django-Specific:**
- Proper use of `update_fields` on save
- Transaction safety (`@transaction.atomic` where needed)
- QuerySet optimization (avoid `.all()` when filtering)
- Permission classes on all views
- Proper status code usage in responses

### 5. Frontend Review (Feature-Sliced Design)

Review frontend Vue/TypeScript code against FSD principles:

**Architecture (FSD Layers):**
- **app/** — only app-wide config (router, store init, global styles). No business logic.
- **shared/** — only reusable utilities, UI kit, API client, constants. No feature-specific code.
- **features/** — each feature is self-contained with its own pages, components, services, stores, types, routes
- **No cross-feature imports** — features should not import from each other directly. If shared, move to `shared/`
- **Layer direction** — shared → features → app. Never the reverse.

**Feature Structure (per feature):**
- `pages/` — route-level components, minimal logic, compose from components
- `components/` — presentational + container components
- `services/` — API calls only, no business logic
- `stores/` — Pinia stores with state, getters, actions
- `types/` — TypeScript interfaces and type aliases
- `routes.ts` — route definitions
- `constants/` — feature-specific constants

**Code Quality:**
- **TypeScript strictness** — no `any`, proper interfaces, discriminated unions for status types
- **Component size** — components over 300 lines should be split
- **Props vs emit** — proper data flow (props down, events up)
- **Reactivity** — proper use of `ref`, `computed`, `watch`. No reactivity loss.
- **PrimeVue usage** — using PrimeVue components correctly, not reimplementing
- **Tailwind** — consistent utility classes, no conflicting styles
- **Dead code** — unused imports, unreachable code, commented-out blocks
- **Naming** — PascalCase components, camelCase functions/variables, kebab-case files
- **Error handling** — API errors caught and displayed, loading states

**Vue-Specific:**
- `<script setup>` used consistently
- Props properly typed with `defineProps<T>()`
- Emits properly typed with `defineEmits<T>()`
- No direct DOM manipulation (use refs)
- Computed properties for derived state (not methods)
- Watchers used sparingly and with clear purpose

### 6. Security Review (Both Layers)

- Authentication: all protected endpoints require auth
- Authorization: role-based access enforced (HR can't access admin endpoints)
- Input validation: all user input validated before processing
- XSS: no `v-html` with user content, no `innerHTML`
- CSRF: proper token handling
- Secrets: no hardcoded API keys, passwords, tokens in code
- File uploads: validated file types and sizes
- SQL injection: using ORM, no raw SQL with user input

### 7. Performance Review

**Backend:**
- N+1 queries (missing `select_related`/`prefetch_related`)
- Unbounded querysets (missing pagination or limits)
- Heavy operations in request cycle (should be Celery tasks)
- Missing database indexes on frequently filtered fields

**Frontend:**
- Unnecessary re-renders (computed vs method)
- Large component trees without lazy loading
- Missing route-level code splitting
- Unoptimized watchers (watching entire objects vs specific properties)
- API calls without debouncing on user input

### 8. Report

Output a structured report:

```
## Review: [scope]

### Critical Issues (must fix)
- [FILE:LINE] Description of the issue

### Warnings (should fix)
- [FILE:LINE] Description

### Suggestions (nice to have)
- [FILE:LINE] Description

### Architecture Notes
- Observations about structure, patterns, coupling

### Summary
- X critical issues, Y warnings, Z suggestions
- Overall assessment: [GOOD / NEEDS WORK / CRITICAL ISSUES]
```

### 9. Fix (if --fix flag)

If `--fix` was provided:
- Fix all critical issues
- Fix warnings where the fix is straightforward
- Skip suggestions (mention them in output)
- Re-run relevant tests after fixing to verify nothing broke

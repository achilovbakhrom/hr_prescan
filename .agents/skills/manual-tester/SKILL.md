---
name: manual-tester
description: Plan and execute manual QA for HR PreScreen user flows, releases, bug fixes, and exploratory testing. Use for manual testing, acceptance testing, regression passes, smoke checks, UX validation, vacancy creation via form or AI assistant, candidate pages, role/permission testing, tenant isolation checks, and defect reports.
user-invocable: true
---

# Manual Tester

Run practical manual QA for HR PreScreen. Focus on user-visible behavior, business-rule alignment, permissions, tenant isolation, async side effects, responsive UI, and clear defect evidence.

## Usage

- `/manual-tester` — create and execute a focused smoke pass for the current app state
- `/manual-tester release` — run a broader regression pass before release/deploy
- `/manual-tester feature <name>` — test a specific feature or changed area
- `/manual-tester bug <summary>` — reproduce a bug, isolate scope, and verify the fix
- `/manual-tester flow <flow>` — produce or execute a manual checklist for one flow
- `/manual-tester report` — summarize manual QA results from the current session

## Core Rules

- Read `AGENTS.md`, `docs/ROADMAP.md`, and relevant sections of `docs/BUSINESS_LOGIC.md` before testing behavior.
- If the request touches changed code, inspect `git diff`, changed routes, changed APIs, and related tests before choosing scenarios.
- Test at least one desktop viewport and one mobile viewport starting at 375px for UI flows.
- Test both visual themes, usually light and dark. If system theme exists, verify it resolves correctly after reload.
- Test localization on every manually visited page. Raw i18n keys such as `auth.login.title` or `dashboard.stats.total` are defects.
- For list/table pages, verify totals, pagination counts, empty states, and cross-page item counts.
- Use the Browser plugin for local UI checks when the app URL is known or obvious.
- Do not use real candidate PII. Use timestamped test data such as `qa+<timestamp>@example.com`.
- Record exact environment, account role, company, vacancy, candidate, browser viewport, and time for any defect.
- Treat console errors, failed network requests, broken loading states, and missing empty/error states as test findings.

## Preflight

1. Confirm scope:
   - Feature, bug, release, smoke, or exploratory pass.
   - Target environment: local, dev, staging, or production.
   - Required roles: Admin, HR account owner, invited HR, anonymous candidate, authenticated candidate.

2. Start or verify the app:
   - Local full stack: `make local-all`
   - Local stop: `make local-stop`
   - Local URLs: frontend `http://localhost:3000`, backend `http://localhost:8000`
   - Check health/API reachability before UI testing.

3. Prepare clean test data:
   - Use a unique company and vacancy name per run.
   - Prefer creating data through the UI unless API setup is faster and does not bypass the behavior under test.
   - Note any background worker dependency: Celery, RabbitMQ, LiveKit, MinIO, email, or AI provider.
   - Prepare enough records to test page totals where possible, especially vacancies, candidates, interviews, users, companies, and notifications.

4. Set global UI matrix:
   - Themes: light and dark at minimum.
   - Locales: English plus at least one non-English locale for smoke/targeted testing; all supported locales for release localization passes.
   - Supported web locales from business rules: `en`, `ru`, `uz`, `kk`, `tr`, `ar`, `es`, `fr`, `de`, `uk`.

## Test Suite Selection

### Smoke Pass

Use for quick confidence after a small change.

- Login/register works.
- HR dashboard loads without blocking errors.
- HR can create or open a vacancy; for vacancy-related changes, test both form creation and AI assistant creation.
- Public job board and public vacancy detail load.
- Candidate can submit an application.
- Candidate-facing dashboard/list/detail pages load when authenticated.
- HR candidate list/detail pages load for a vacancy.
- Analytics page loads and key totals are visible.
- List pages show totals that match visible/paginated data.
- Notifications panel opens.
- No raw i18n keys are visible on visited pages.
- Light and dark themes both render readable text and controls.
- Mobile navigation works at 375px.

### Targeted Feature Pass

Use for a changed feature. Test:

- Happy path.
- Required validation and bad input.
- Permission boundaries.
- Relevant status transitions.
- Empty, loading, success, and error states.
- Page refresh/deep link behavior.
- Mobile layout and keyboard interaction.
- Cross-feature side effects, such as dashboard counts or notifications.
- Theme behavior in light and dark.
- Translation coverage in English and at least one non-English locale.
- Totals and pagination behavior for every affected list/table page.

### Release Regression Pass

Use before deploys or broad merges. Cover every core flow below and add one negative scenario per flow. Also run the global UI quality gates against every top-level page.

## Core Manual Flows

### 1. Auth, Modes, And Tenancy

- Register an HR account and confirm company creation.
- Login, logout, refresh the page, and verify session persistence.
- Switch between HR mode and candidate mode where available.
- Invite an HR user, accept invitation, and verify selected company access.
- Verify one tenant cannot see another tenant's companies, vacancies, applications, interviews, or notifications.
- Verify role-specific navigation and protected pages reject unauthorized access.

### 2. Company Setup

- Edit company profile fields and logo/upload-related fields if available.
- Add a second company and change default membership.
- Verify company dropdown affects vacancy creation and scoped lists.
- Soft-delete or deactivate only where business rules allow it.

### 3. Vacancy Management

- Test vacancy creation through both supported entry points: manual form and HR AI assistant.
- Create a draft vacancy with company, title, description, requirements/responsibilities, skills, salary, location, visibility, screening language, CV requirement, and pipeline settings.
- Verify negotiable salary when min/max are empty, min/max validation, currency display, and public listing behavior.
- Generate AI vacancy content or screening setup when available; verify HR can review, edit, save, discard, and regenerate generated output.
- Configure prescanning questions and criteria. Prescanning is always enabled and always chat.
- Configure optional interview questions, criteria, duration, and prompt when enabled. Interview is optional and video/Meet only.
- Publish only when required setup is complete, with clear validation when setup is incomplete.
- Verify lifecycle: Draft -> Published -> Paused -> Published -> Archived. Published cannot return to Draft; Archived cannot reopen.
- Test public visibility, private share links, public search/filtering, SEO/public URL behavior, and archived/soft-deleted hiding.

#### 3A. Vacancy Creation Form Matrix

- Basic required fields: missing title, short title, missing description, long description, required skills empty/non-empty, location empty/remote/onsite/hybrid, company dropdown with one and multiple companies.
- Salary: both empty means negotiable; min only, max only, min greater than max, negative values, decimals, large values, currency/period labels.
- Visibility: public appears on job board after publish; private does not appear publicly but opens by share link; draft/paused/archived cannot accept public applications.
- Language: new vacancy defaults from current web locale; selected prescanning language persists and drives candidate-facing screening language.
- Screening setup: add/edit/delete/reorder prescanning questions; add/edit/delete criteria; generate with AI creates missing criteria before questions; custom criteria weights/names validate correctly if present.
- Optional interview: enable/disable, configure separate questions and criteria, duration validation, additional prompt, candidate interview link locked until prescanning advances in production behavior.
- Save behavior: save draft, leave and return, refresh mid-form, browser back, validation errors preserve input, duplicate submit does not create duplicate vacancies.
- Publish behavior: publish from form and from detail; incomplete setup blocks with actionable errors; successful publish updates list totals, dashboard counts, public/private visibility, and share links.
- Edit behavior: edit draft/published/paused where allowed, confirm restrictions after publish, verify changes propagate to public vacancy and candidate application form.

#### 3B. Vacancy Creation Via AI Assistant Matrix

- Start with minimal prompt: title only. Assistant should ask for missing required details instead of creating invalid data.
- Start with full job description pasted into chat. Assistant should preserve important details, infer structured fields, and avoid unsupported claims.
- Multi-company account: assistant must use default company when unambiguous or ask a clarification when needed.
- Draft creation: assistant-created vacancy appears in vacancy list with correct company, status, visibility, title, description, requirements/responsibilities, skills, salary/location, and language.
- Publication setup: when HR says "generate yourself" or "publish it", assistant creates missing prescanning questions and role-specific criteria before publishing.
- Screening generation: generated questions must align with criteria; HR can edit AI output before publish where the UI supports review.
- Disambiguation: when multiple accessible vacancies match the same title, assistant asks with status/company/candidate-count choices instead of failing silently.
- Safety and validation: vague, contradictory, too-short, unsupported, or out-of-scope prompts produce clear follow-up or error states; no raw JSON/internal tool text leaks to HR.
- Persistence: chat history, created draft link, follow-up edits, refresh, and returning to the assistant remain coherent.
- Side effects: dashboard totals, vacancy list totals, public job board, share link, notifications, and audit-visible status update after assistant actions.

### 4. Candidate Application

- Browse public job board as anonymous candidate.
- Apply to public and private vacancies with required fields.
- Upload a CV when supported; also test optional/no-CV path if allowed.
- Verify duplicate, invalid email/phone, oversized/unsupported file, and missing required field handling.
- Confirm application status and candidate-facing next step.
- If candidate registers later, verify previous applications link by email/phone.

### 5. Prescanning Chat

- Start prescanning immediately after applying and from a returned link.
- Verify chat language follows vacancy settings where applicable.
- Complete enough conversation to reach a result.
- Verify transcript, score, criteria notes, status movement, and HR visibility.
- Test interrupted session recovery via refresh/back/return link.
- Verify HR can manually move candidates and clear/recreate prescanning results where supported.

### 6. Interview Scheduling And Room

- Advance a candidate to interview-eligible state.
- Pick a time slot and verify confirmation, reminders, and calendar download where available.
- Open pre-interview checks for camera/mic and validation states.
- Join the LiveKit room as candidate and verify token/room access.
- Verify HR observer mode is silent and scoped to authorized HR users.
- Complete or simulate completion and check transcript, scores, recording link, and integrity flags.

### 7. Candidate Pages And HR Review

- Open candidate-facing dashboard, My Applications list, application detail, profile/CV surfaces, and candidate messages where available.
- Verify candidate pages show applications linked by authenticated candidate ID and matching email/phone after registration.
- Verify candidate application cards/details show vacancy title/company/status, CV match, prescanning/interview scores, next step, exact prescanning link, interview link availability, and Telegram shortcuts when available.
- Verify candidate page totals, filters, empty state, loading state, pagination or infinite loading, and refresh behavior.
- Verify candidate cannot see another candidate's applications or HR-only notes, criteria internals, private company data, or unauthorized interview observer links.
- Test candidate pages in light/dark themes, desktop and 375px mobile, English and at least one non-English locale.
- Review dashboard metrics, active vacancies, and recent activity.
- Open candidate list per vacancy; test filtering, sorting, score ranges, and status filters.
- Verify total candidate counts before and after filtering, sorting, pagination, status changes, and bulk actions.
- Open candidate detail; verify CV viewer, parsed CV data, scores, notes, transcript, recording, and integrity flags.
- Add/edit HR notes.
- Schedule human interview, send email, use direct chat, and perform bulk shortlist/reject where available.
- Verify all actions update statuses, notifications, and counts consistently.

### 8. Analytics And Reporting

- Open HR analytics and admin analytics pages when the role has access.
- Verify top-level totals: companies, users, vacancies, applications/candidates, prescreenings, interviews, revenue or usage where shown.
- Cross-check analytics totals against source pages or API/list counts when practical.
- Verify date range filters, company filters, status filters, chart tooltips, legends, empty states, and export/download actions if present.
- Confirm analytics refresh after creating or changing a relevant record.
- Verify unauthorized roles cannot open analytics routes or fetch analytics APIs.
- Test analytics in both light and dark themes at desktop and 375px mobile width.
- Test analytics in English and a non-English locale; release passes must check all supported locales.
- Report any visible raw translation key, placeholder label, untranslated button, broken pluralization, or wrong numeric/currency formatting.

### 9. Notifications, Billing, And Settings

- Verify notification bell count, dropdown/list, mark-read, and real-time updates if SSE is enabled.
- Verify notification totals across unread/read/all filters and paginated notification lists.
- Confirm billing-pause behavior: core HR workflows are not blocked while `BILLING_ENABLED=false`.
- If billing is enabled in the environment, test plan limits and upgrade prompts.
- Check account settings, profile forms, password/security flows, and language settings if in scope.

## Global UI Quality Gates

Run these checks for every manually visited page in smoke, targeted, or release testing:

- **Theme:** switch to light and dark, reload, and verify the selected theme persists. Text, icons, inputs, dropdowns, modals, charts, tables, toast messages, and disabled states must remain readable.
- **Localization:** switch locale and scan headings, navigation, buttons, field labels, placeholders, validation errors, empty states, toast messages, table headers, chart labels, pagination text, dialogs, and tooltips.
- **Raw key detection:** visible text must not contain dotted i18n-key patterns such as `feature.section.label`, `common.actions.save`, or `pages.analytics.title`.
- **Totals:** on every list/table/stat page, verify displayed totals match the number of records in the active scope. Check totals after search, filter, sort, page-size changes, next/previous page navigation, create/update/delete/status transitions, and browser refresh.
- **Pagination:** verify first page, last page, empty page after filters, page-size selector, next/previous disabled states, and count labels such as "showing X-Y of Z".
- **Responsive layout:** test desktop and 375px mobile. No clipped text, overlapping controls, hidden primary actions, or unusable tables/charts.

## Negative And Exploratory Checks

- Unauthorized direct URL access for HR-only and candidate-only pages.
- Cross-tenant object IDs in URLs and API calls.
- Browser refresh after each critical transition.
- Back button after create/update/delete/status actions.
- Slow network or failed API response where practical.
- Empty lists, first item, many items, long text, special characters, and narrow mobile viewport.
- Mismatched totals after filtering, pagination, status changes, or data refresh.
- Raw i18n keys, missing translations, mixed-language screens, and untranslated validation/toast text.
- Light/dark theme contrast issues, invisible chart series, unreadable disabled states, and theme persistence failures.
- Async delays: CV parsing, AI analysis, email, reminders, LiveKit, recording, notifications.

## Defect Report Format

For each issue, report:

```text
Severity: Critical | High | Medium | Low
Title:
Environment:
Role/account:
URL/route:
Viewport:
Test data:
Steps to reproduce:
Expected:
Actual:
Evidence:
Console/network errors:
Business rule affected:
Regression risk:
```

## Final QA Report

End with:

- Scope tested and environment.
- Passed flows.
- Failed flows with defect IDs or titles.
- Blocked or skipped tests and why.
- Residual risk.
- Recommended next validation: automated test, manual retest, logs, DB check, or deploy smoke.

# HR PreScan — Codex Project Guide

## What this project is

HR PreScan is a multi-tenant SaaS platform that automates candidate pre-screening using AI-powered interviews (text chat or video). The core goal is to help HR teams pre-filter large applicant pools before manual review.

## Read These Docs First

All detailed docs live in `docs/`:

- `docs/BUSINESS_LOGIC.md` — product requirements, user flows, statuses, scoring logic. Read this before making architectural or behavior-changing decisions.
- `docs/TECH_ARCHITECTURE.md` — services, communication, DB schema, API structure.
- `docs/CODE_STYLE.md` — SOLID/KISS/DRY principles, Service Layer pattern, feature-based Vue modules.
- `docs/DEVOPS.md` — CI/CD, zero-downtime deployment, backups, monitoring.
- `docs/ROADMAP.md` — current phase and task progress. Check this at the start of every session.

## Tech Stack

- Backend: Django, DRF, Celery, PostgreSQL, Redis, RabbitMQ
- Frontend: Vue 3, TypeScript, Pinia, PrimeVue, Tailwind CSS
- AI interview: LiveKit + Deepgram STT + Gemini 3.0 Flash + ElevenLabs TTS
- Storage: MinIO (S3-compatible)
- Deployment: Docker Compose, GitHub Actions CI/CD

## Project Structure

```text
├── backend/              # Django REST API
├── frontend/             # Vue.js SPA
├── livekit-agent/        # AI interview agent
├── docs/                 # Project documentation
├── deploy/               # Deployment & infrastructure
│   ├── nginx/            # Nginx configs (dev + prod)
│   ├── monitoring/       # Grafana, Prometheus configs
│   ├── livekit/          # LiveKit server config
│   ├── scripts/          # Backup, SSL, smoke-test scripts
│   ├── docker-compose.prod.yml
│   ├── docker-compose.monitoring.yml
│   └── docker-compose.management.yml
├── docker-compose.yml           # Base services
├── docker-compose.override.yml  # Dev overrides (auto-loaded)
└── Makefile                     # Dev commands
```

## Core Conventions

- Business logic decisions live in `docs/BUSINESS_LOGIC.md`. If behavior is unclear, check that file before assuming.
- Check `docs/ROADMAP.md` before starting work so changes align with the current phase.

### Backend

- Use a Service Layer: business logic belongs in `services.py`.
- Keep views thin: parse input, call service, return response.
- Put read-only queries in `selectors.py`.
- Favor low coupling and high cohesion between apps.
- Use `update_fields` on model `.save()` where applicable.
- Use `select_related` / `prefetch_related` to avoid N+1 queries.
- Use `@transaction.atomic` for multi-model operations.
- Every API view must have explicit permission classes.
- Keep files under 200 lines. Split oversized APIs/services by domain concern instead of extending them further.

### Frontend

- Follow feature-sliced design: `shared/` -> `features/` -> `app/`.
- Do not import upward across layers.
- Keep each feature self-contained with its own pages, components, services, stores, types, and routes.
- If logic is shared across features, move it to `shared/`.
- Services are for API calls only; business logic belongs in stores or feature modules.
- Use TypeScript strictly; avoid `any`.
- Use `<script setup>` with typed `defineProps` / `defineEmits`.
- PrimeVue is the component library, Tailwind handles utility styling.
- Every UI change must work on mobile screens starting at 375px.
- Keep Vue and TS files under 200 lines. Extract sub-components or composables instead of growing large files.

## Mandatory Rules

- Before any task, assess whether the change affects business logic: user flows, statuses, pipelines, scoring, vacancy lifecycle, candidate pipeline, API contracts, or other behavior documented in `docs/BUSINESS_LOGIC.md`.
- If business logic changes, update `docs/BUSINESS_LOGIC.md` in the same task.
- If unsure whether business logic changed, update the doc anyway.
- After finishing code changes, review the changed files before commit or push and fix critical issues first.

## Working Notes For Codex

- Prefer targeted validation after edits: relevant tests, linting, type checks, or framework health checks.
- Do not introduce large speculative refactors when a scoped fix will solve the problem.
- Preserve existing user changes in a dirty worktree unless explicitly asked to revert them.

## Important Product Notes

- Candidate account creation is optional.
- Vacancies can be public (job board) or private (link-only).
- AI interview questions are auto-generated, but HR can edit them before publishing.
- The platform does not dictate HR's post-screening workflow. It provides tools; HR decides the final process.
- Interview duration is configurable per vacancy.
- Scoring uses both fixed categories and custom HR-defined criteria.

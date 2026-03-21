# HR PreScan — Project Guide

## What is this project?

HR PreScan is a multi-tenant SaaS platform that automates candidate pre-screening using AI-powered interviews (text chat or video). The core goal: help HR pre-filter candidates so they don't manually screen 100+ applicants per vacancy.

## Documentation

All detailed docs live in `docs/`:

- `docs/BUSINESS_LOGIC.md` — product requirements, user flows, scoring logic. Read before making architectural decisions.
- `docs/TECH_ARCHITECTURE.md` — services, communication, DB schema, API structure.
- `docs/CODE_STYLE.md` — SOLID/KISS/DRY principles, Service Layer pattern, feature-based Vue modules.
- `docs/DEVOPS.md` — CI/CD, zero-downtime deployment, backups, monitoring.
- `docs/ROADMAP.md` — 16 phases (0-15) with checkboxes. Check at the start of every session for current progress.

## Tech Stack

- **Backend:** Django, DRF, Celery, PostgreSQL, Redis, RabbitMQ
- **Frontend:** Vue 3, TypeScript, Pinia, PrimeVue, Tailwind CSS
- **AI Interview:** LiveKit + Deepgram STT + GPT-4o + ElevenLabs TTS
- **Storage:** MinIO (S3-compatible)
- **Deployment:** Docker Compose, GitHub Actions CI/CD

## Project Structure

```
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

## Conventions

- Business logic decisions are in `docs/BUSINESS_LOGIC.md` — consult it for product requirements
- When in doubt about a feature, check `docs/BUSINESS_LOGIC.md` before assuming

### Backend — GRASP Principles + Service Layer

- **Service Layer pattern**: all business logic lives in `services.py`. Views (APIs) only handle HTTP: parse input → call service → return response. Serializers only validate input and format output. Models only define data and constraints.
- **Selectors**: read-only database queries live in `selectors.py`, not inline in views.
- **Information Expert**: logic belongs in the module that owns the data.
- **Low Coupling**: apps should not import models/services directly from other apps where avoidable. Use IDs and service calls.
- **High Cohesion**: each app has one clear domain (accounts, vacancies, applications, interviews).
- RESTful API structure with proper HTTP status codes.
- Always use `update_fields` on model `.save()`.
- Use `select_related` / `prefetch_related` to avoid N+1 queries.
- Use `@transaction.atomic` for multi-model operations.
- Permission classes on every API view.

### Frontend — Feature-Sliced Design (FSD)

- **Layer structure**: `shared/` → `features/` → `app/`. Never import upward.
- **Feature isolation**: each feature (`auth`, `candidates`, `vacancies`, etc.) is self-contained with its own `pages/`, `components/`, `services/`, `stores/`, `types/`, `routes.ts`.
- **No cross-feature imports**: if two features need the same thing, move it to `shared/`.
- **shared/**: reusable utilities, API client, UI components, constants, types. No business logic.
- **Pages**: route-level components that compose from smaller components. Minimal logic.
- **Services**: API calls only (axios/fetch). No business logic.
- **Stores**: Pinia stores with state, getters, actions. Business logic for the feature.
- TypeScript strict — no `any`, proper interfaces.
- `<script setup>` with typed `defineProps` / `defineEmits`.
- PrimeVue for UI components, Tailwind for utility styling.

## Mandatory Rules

- **Before starting any task** (bug fix, refactor, new feature, or anything else), assess whether the change affects business logic — user flows, statuses, pipelines, scoring, vacancy lifecycle, candidate pipeline, API contracts, or any behavior documented in `docs/BUSINESS_LOGIC.md`.
- **If it does affect business logic**, update `docs/BUSINESS_LOGIC.md` as part of the same task — not as a follow-up. The code and the docs must stay in sync at all times.
- **If unsure** whether a change affects business logic, err on the side of updating the doc.

## Important Notes

- Candidate account creation is optional
- Vacancies can be public (job board) or private (link-only)
- AI interview questions are auto-generated but HR can edit them before publishing
- The platform does NOT dictate HR's post-screening workflow — it provides tools (schedule, chat, email, reject) and HR decides
- Interview duration is configurable per vacancy
- Scoring uses both fixed categories (soft skills, language, communication, motivation, cultural fit) and custom HR-defined criteria

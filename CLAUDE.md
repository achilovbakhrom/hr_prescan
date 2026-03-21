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
- Keep backend API RESTful
- Frontend should be component-based (Vue.js single-file components)

## Important Notes

- Candidate account creation is optional
- Vacancies can be public (job board) or private (link-only)
- AI interview questions are auto-generated but HR can edit them before publishing
- The platform does NOT dictate HR's post-screening workflow — it provides tools (schedule, chat, email, reject) and HR decides
- Interview duration is configurable per vacancy
- Scoring uses both fixed categories (soft skills, language, communication, motivation, cultural fit) and custom HR-defined criteria

# HR PreScan — Project Guide

## What is this project?

HR PreScan is a multi-tenant SaaS platform that automates candidate pre-screening using AI-powered video interviews. The core goal: help HR pre-filter candidates so they don't manually screen 100+ applicants per vacancy.

Full business logic is documented in `BUSINESS_LOGIC.md` — always read it before making architectural decisions.
Technical architecture is documented in `TECH_ARCHITECTURE.md` — services, communication, DB schema, API structure, deployment.
Code style and patterns are documented in `CODE_STYLE.md` — SOLID/KISS/DRY principles, Service Layer pattern, feature-based Vue modules, tooling config.
DevOps and infrastructure are documented in `DEVOPS.md` — CI/CD, zero-downtime deployment, backups, monitoring, management UIs.
Development roadmap is in `ROADMAP.md` — 16 phases (0-15) with checkboxes. Check it at the start of every session to see current progress.
Agent team setup is in `AGENTS.md` — PM, Backend, Frontend, DevOps agents coordinating via GitHub Issues/PRs.

## Tech Stack

### Application
- **Backend:** Django (Python)
- **Frontend:** Vue.js
- **Database:** PostgreSQL
- **Cache/Sessions:** Redis
- **File Storage:** S3-compatible (AWS S3 or MinIO) — for CVs, interview recordings, media
- **Task Queue:** Celery + RabbitMQ — for CV parsing, AI scoring, emails, async jobs
- **Deployment:** Docker Compose with zero-downtime strategy

### AI Interview Pipeline (orchestrated by LiveKit Agents)
- **Video Room:** LiveKit (self-hosted) — WebRTC video rooms + VoicePipelineAgent for STT→LLM→TTS orchestration
- **STT:** Deepgram Nova-3 — real-time streaming, <300ms latency, native EN↔RU code-switching (`language=multi`)
- **TTS:** ElevenLabs Flash v2.5 — most natural voice, ~75ms latency, confirmed Russian support
- **LLM:** GPT-4.5.5 mini (OpenAI) — conversation logic, follow-up questions, candidate evaluation
- **Languages:** English and Russian (UI + AI interviews)

## Architecture Overview

### User Roles
- **Platform Admin** — manages the whole platform, users, billing, system settings
- **HR Manager** — belongs to a company, creates vacancies, reviews AI screening results
- **Candidate** — applies to vacancies, uploads CV, takes AI video interviews

### Core Flow
1. Company registers → chooses subscription → invites HR users
2. HR creates a vacancy (can share link on LinkedIn, job boards, etc.)
3. Candidate applies → uploads CV → picks interview time slot
4. AI analyzes CV pre-interview, generates tailored questions
5. AI conducts video interview (Google Meet-style room) at scheduled time
6. AI scores candidate on fixed categories + HR-defined custom criteria (1-10 scale)
7. HR reviews scores, filters candidates, decides next steps (full interview, chat, reject)

### Docker Compose Services (10 total)
1. **Django API** — backend REST API, business logic, auth, SSE notifications
2. **Vue.js (Nginx)** — frontend SPA
3. **PostgreSQL** — primary database
4. **Redis** — cache, sessions, SSE notification channel
5. **RabbitMQ** — message broker for Celery and inter-service communication
6. **Celery Worker** — async tasks (CV parsing, AI scoring, emails)
7. **Celery Beat** — scheduled tasks (interview reminders, digests)
8. **LiveKit Server** — WebRTC video rooms
9. **LiveKit Agent** — AI interview agent (Deepgram STT → GPT LLM → ElevenLabs TTS)
10. **MinIO** — S3-compatible file storage (CVs, recordings)

### Communication
- **Vue.js ↔ Django:** REST API (CRUD) + SSE (real-time notifications)
- **Vue.js → LiveKit:** WebRTC (candidate video/audio during interview)
- **Django ↔ Celery:** RabbitMQ (async task dispatch)
- **Django ↔ LiveKit:** RabbitMQ (room management, interview triggers)
- **LiveKit Agent → Django:** RabbitMQ (interview results, scores, transcript)
- **LiveKit Agent → External APIs:** Deepgram (WebSocket), OpenAI (HTTPS), ElevenLabs (HTTPS)
- **Django → Redis:** cache, sessions, SSE pub/sub
- **Celery → MinIO:** S3 API (file storage)

### Key Technical Components
- **Multi-tenancy** — company data isolation, per-company subscriptions
- **Video interview room** — real-time video with AI agent as interviewer
- **CV parser** — extract skills, experience, education from PDF/DOCX
- **AI evaluation engine** — scoring on fixed + custom criteria
- **Scheduling system** — calendar integration, room link generation
- **Anti-cheating** — face detection, gaze tracking, answer consistency checks
- **Notifications** — email (SMTP) + in-app (SSE via Redis pub/sub)

## Conventions

- Business logic decisions are in `BUSINESS_LOGIC.md` — consult it for product requirements
- When in doubt about a feature, check `BUSINESS_LOGIC.md` before assuming
- Keep backend API RESTful
- Frontend should be component-based (Vue.js single-file components)

## Important Notes

- Candidate account creation is optional
- Vacancies can be public (job board) or private (link-only)
- AI interview questions are auto-generated but HR can edit them before publishing
- The platform does NOT dictate HR's post-screening workflow — it provides tools (schedule, chat, email, reject) and HR decides
- Interview duration is configurable per vacancy
- Scoring uses both fixed categories (soft skills, language, communication, motivation, cultural fit) and custom HR-defined criteria

# HR PreScan — Development Roadmap

Each phase produces a working, deployable result. Tasks are ordered by dependency.
Mark tasks with `[x]` as they are completed.

---

## Phase 0: Agent Team Setup

**Goal:** Set up specialized Claude Code agents (PM, Backend, Frontend, DevOps) that work as a team via GitHub Issues/PRs.

- [x] 0.1 Create agent config directory (`agents/`)
- [x] 0.2 Create PM Agent prompt (orchestrator — reads roadmap, creates issues, reviews PRs, merges)
- [x] 0.3 Create Backend Engineer Agent prompt (Django, DRF, Celery, models, services, selectors)
- [x] 0.4 Create Frontend Engineer Agent prompt (Vue.js, TypeScript, Pinia, PrimeVue, Tailwind)
- [x] 0.5 Create DevOps Engineer Agent prompt (Docker, CI/CD, Nginx, monitoring)
- [x] 0.6 Create orchestration script (`scripts/run_agent.sh`) to launch agents with correct prompts
- [x] 0.7 Define git branching strategy (be/*, fe/*, devops/*, review process)
- [ ] 0.8 Test agent team on a small sample task (e.g., create a dummy Django app + Vue page)
- [x] 0.9 Document agent workflow in `AGENTS.md`

---

## Phase 1: Project Scaffolding & Infrastructure

**Goal:** Empty but runnable project with all services starting via Docker Compose.

- [x] 1.1 Initialize git repo, add `.gitignore` (Python, Node, Docker, env files)
- [x] 1.2 Create Django project (`config/`) with settings split (base, local, production, test)
- [x] 1.3 Create Vue.js project with Vite + TypeScript + Pinia + Vue Router + PrimeVue + Tailwind
- [x] 1.4 Create `Dockerfile` for backend (Python 3.12, Gunicorn)
- [x] 1.5 Create `Dockerfile` for frontend (Node build + Nginx)
- [x] 1.6 Create `docker-compose.yml` (base) with all 10 app services
- [x] 1.7 Create `docker-compose.override.yml` (dev: hot reload, exposed ports)
- [x] 1.8 Create `docker-compose.monitoring.yml` (Grafana, Prometheus, Jaeger, Loki)
- [x] 1.9 Create `docker-compose.management.yml` (Portainer, pgAdmin, RedisInsight)
- [x] 1.10 Setup health checks for all services
- [x] 1.11 Setup entrypoint script (wait for DB → migrate → collectstatic → start)
- [ ] 1.12 Verify all 18 services start and are healthy
- [x] 1.13 Setup Ruff + mypy (backend), ESLint + Prettier (frontend), pre-commit hooks
- [x] 1.14 Setup GitHub Actions CI (lint + format + type checks)

---

## Phase 2: Auth & User Management

**Goal:** Users can register, login, and have role-based access.

- [x] 2.1 Create `common` app — BaseModel (UUID, timestamps), custom exceptions, pagination
- [x] 2.2 Create `accounts` app — User model (email-based, role field: admin/hr/candidate)
- [x] 2.3 Create Company model (name, industry, size, country, logo, website, description)
- [x] 2.4 JWT authentication (access + refresh tokens) — login, logout, refresh endpoints
- [x] 2.5 User registration API (email + password)
- [x] 2.6 Email verification flow (send email, verify token)
- [ ] 2.7 Google OAuth 2.0 social login
- [x] 2.8 Role-based permissions (IsAdmin, IsHRManager, IsCandidate)
- [x] 2.9 Multi-tenancy middleware (scope HR queries to their company)
- [x] 2.10 Frontend: auth feature module — login, register, email verify pages
- [x] 2.11 Frontend: Axios client with JWT interceptor (auto-attach token, refresh on 401)
- [x] 2.12 Frontend: route guards (redirect unauthenticated, role-based access)
- [x] 2.13 Frontend: app layout (sidebar, navbar, role-based navigation)

---

## Phase 3: Company Onboarding

**Goal:** A company can register, set up profile, invite HR users.

- [x] 3.1 Company registration API (create company + admin user in one step)
- [x] 3.2 Company profile setup API (logo upload, description, website, default settings)
- [x] 3.3 HR invitation API (admin invites HR by email, generates signup link)
- [x] 3.4 HR signup via invitation link (auto-link to company)
- [x] 3.5 Company team management API (list HRs, activate/deactivate)
- [ ] 3.6 MinIO integration — file upload service (presigned URLs)
- [x] 3.7 Frontend: company registration wizard
- [x] 3.8 Frontend: company profile settings page
- [x] 3.9 Frontend: team management page (invite, list, deactivate HRs)

---

## Phase 4: Vacancy Management

**Goal:** HR can create, edit, publish, and share vacancies.

- [x] 4.1 Create `vacancies` app — Vacancy model (title, description, skills, salary, location, deadline, status, visibility)
- [x] 4.2 VacancyCriteria model (fixed + custom evaluation criteria per vacancy)
- [x] 4.3 InterviewQuestion model (AI-generated + HR-editable questions)
- [x] 4.4 Vacancy CRUD API (create, update, list, detail)
- [x] 4.5 Vacancy lifecycle API (publish, pause, close)
- [x] 4.6 Vacancy share link generation (unique URL for external sharing)
- [x] 4.7 Public job board API (list public vacancies, search, filter)
- [x] 4.8 AI question generation — service that generates interview questions from vacancy description (OpenAI integration)
- [x] 4.9 HR question editing API (review, edit, add, remove AI-suggested questions)
- [x] 4.10 Frontend: vacancy creation form
- [x] 4.11 Frontend: vacancy list page (with status badges, candidate counts)
- [x] 4.12 Frontend: vacancy detail/edit page
- [x] 4.13 Frontend: question review/edit interface
- [x] 4.14 Frontend: public job board page (searchable, filterable)
- [x] 4.15 Frontend: public vacancy detail page (with apply button)

---

## Phase 5: Candidate Application & CV Processing

**Goal:** Candidates can apply, upload CV, CV is parsed and analyzed by AI.

- [ ] 5.1 Create `applications` app — Application model (candidate info, CV file, status, parsed data, match score)
- [ ] 5.2 Application submission API (no auth required — name, email, phone, CV upload)
- [ ] 5.3 Optional candidate account creation (link applications to account)
- [ ] 5.4 CV upload to MinIO via presigned URL
- [ ] 5.5 Celery task: parse CV (extract text from PDF/DOCX)
- [ ] 5.6 Celery task: AI CV analysis (extract skills, experience, education — OpenAI)
- [ ] 5.7 Celery task: CV match scoring (compare CV vs vacancy requirements — OpenAI)
- [ ] 5.8 Candidate status management API (update status: applied → shortlisted → rejected)
- [ ] 5.9 Frontend: application form (public vacancy page)
- [ ] 5.10 Frontend: candidate dashboard (if logged in — my applications, statuses)
- [ ] 5.11 Frontend: HR candidate list per vacancy (table with scores, status, filtering, sorting)
- [ ] 5.12 Frontend: HR candidate detail page (CV viewer, parsed data, match score, notes)

---

## Phase 6: Interview Scheduling

**Goal:** Candidates pick time slots, calendar events are created, links are generated.

- [ ] 6.1 Create `interviews` app — Interview model (application FK, scheduled_at, room name, status, recording, transcript, scores)
- [ ] 6.2 InterviewScore model (criteria FK, score 1-10, AI notes)
- [ ] 6.3 InterviewIntegrityFlag model (flag type, severity, description, timestamp)
- [ ] 6.4 Scheduling API — candidate picks time slot
- [ ] 6.5 LiveKit integration — create room, generate participant tokens
- [ ] 6.6 Calendar invite generation (iCal format, attached to email)
- [ ] 6.7 Celery task: send scheduling confirmation email (with room link + calendar invite)
- [ ] 6.8 Celery task: send interview reminders (1 hour before, 15 min before)
- [ ] 6.9 Celery Beat: scheduled job for checking upcoming interviews and sending reminders
- [ ] 6.10 Frontend: calendar/time slot picker for candidates
- [ ] 6.11 Frontend: interview confirmation page (with link and calendar download)
- [ ] 6.12 Frontend: HR view of scheduled interviews

---

## Phase 7: AI Interview Agent (Core Feature)

**Goal:** AI agent conducts video interviews with candidates.

- [ ] 7.1 Create LiveKit Agent project (Python, separate Dockerfile)
- [ ] 7.2 Setup VoicePipelineAgent (Deepgram STT + GPT LLM + ElevenLabs TTS)
- [ ] 7.3 Agent: fetch interview context from Django API via RabbitMQ (vacancy, CV data, questions)
- [ ] 7.4 Agent: system prompt engineering (interviewer persona, question flow, language handling)
- [ ] 7.5 Agent: conduct structured interview (greet → ask questions → follow-ups → close)
- [ ] 7.6 Agent: handle EN/RU language (code-switching with Deepgram `language=multi`)
- [ ] 7.7 Agent: time management (track duration, wrap up when limit reached)
- [ ] 7.8 Agent: generate evaluation scores after interview (fixed + custom criteria, 1-10)
- [ ] 7.9 Agent: send results back to Django via RabbitMQ (scores, transcript, recording path)
- [ ] 7.10 Django: consume interview results from RabbitMQ, save to DB
- [ ] 7.11 LiveKit: configure recording egress to MinIO
- [ ] 7.12 Frontend: interview room page (LiveKit video room, candidate joins via link)
- [ ] 7.13 Frontend: pre-interview check page (camera/mic test, instructions)
- [ ] 7.14 Frontend: post-interview page (thank you, status update)
- [ ] 7.15 Test full interview loop end-to-end

---

## Phase 8: HR Review & Dashboard

**Goal:** HR can review AI scores, watch recordings, filter candidates.

- [ ] 8.1 Interview results API (scores with AI notes per category, overall score)
- [ ] 8.2 Interview transcript API (timestamped conversation)
- [ ] 8.3 Interview recording playback (presigned URL from MinIO)
- [ ] 8.4 Integrity flags API (anti-cheating flags per interview)
- [ ] 8.5 HR dashboard API (active vacancies, recent interviews, key metrics)
- [ ] 8.6 Candidate filtering/sorting API (by score range, category, status)
- [ ] 8.7 HR notes API (add/edit notes on candidates)
- [ ] 8.8 HR observer mode — generate observer token for live interview
- [ ] 8.9 Frontend: HR dashboard page (vacancy cards, stats, recent activity)
- [ ] 8.10 Frontend: candidate scores detail page (per-category scores, AI notes, integrity flags)
- [ ] 8.11 Frontend: interview recording player
- [ ] 8.12 Frontend: interview transcript viewer
- [ ] 8.13 Frontend: candidate filtering/sorting controls
- [ ] 8.14 Frontend: HR silent observer view (watch live interview)

---

## Phase 9: Notifications

**Goal:** Email and in-app notifications for all events.

- [ ] 9.1 Create `notifications` app — Notification model (user, type, title, message, data, is_read)
- [ ] 9.2 Notification creation service (called by other services when events happen)
- [ ] 9.3 Email notification templates (application received, interview scheduled, results ready, etc.)
- [ ] 9.4 Celery tasks for sending emails (SMTP integration)
- [ ] 9.5 SSE endpoint for real-time in-app notifications (Redis pub/sub)
- [ ] 9.6 Notification list/mark-read API
- [ ] 9.7 Frontend: notification bell with unread count
- [ ] 9.8 Frontend: notification dropdown/panel
- [ ] 9.9 Frontend: SSE composable (`useSSE`) for real-time updates
- [ ] 9.10 Wire up notifications to all events (new application, interview completed, status change, etc.)

---

## Phase 10: HR Post-Screening Actions

**Goal:** HR can take action on screened candidates.

- [ ] 10.1 Schedule full (human) interview — create event, send invite to candidate
- [ ] 10.2 Direct chat — messaging between HR and candidate within the platform
- [ ] 10.3 Send email to candidate from platform
- [ ] 10.4 Bulk actions (reject multiple, shortlist multiple)
- [ ] 10.5 Frontend: action buttons on candidate detail page
- [ ] 10.6 Frontend: chat interface (if direct chat is implemented)
- [ ] 10.7 Frontend: bulk action controls on candidate list

---

## Phase 11: Subscriptions & Billing

**Goal:** Companies choose plans with limits.

- [ ] 11.1 Create `subscriptions` app — SubscriptionPlan model, CompanySubscription
- [ ] 11.2 Plan limits enforcement (max vacancies, max interviews/month, max HRs)
- [ ] 11.3 Quota checking in services (before creating vacancy, scheduling interview, inviting HR)
- [ ] 11.4 Stripe integration (checkout, webhooks, subscription management)
- [ ] 11.5 Trial period logic
- [ ] 11.6 Frontend: pricing page
- [ ] 11.7 Frontend: subscription management page (current plan, upgrade, billing history)

---

## Phase 12: Admin Panel

**Goal:** Platform admin can manage companies, users, and system settings.

- [ ] 12.1 Admin company management API (list, detail, activate/block)
- [ ] 12.2 Admin user management API (list, detail, activate/block)
- [ ] 12.3 Admin platform analytics API (total companies, users, interviews, revenue)
- [ ] 12.4 Admin subscription plan management API
- [ ] 12.5 Frontend: admin dashboard
- [ ] 12.6 Frontend: admin company management page
- [ ] 12.7 Frontend: admin user management page
- [ ] 12.8 Frontend: admin analytics page

---

## Phase 13: Anti-Cheating & Integrity

**Goal:** AI monitors candidate behavior during interview.

- [ ] 13.1 Agent: face presence detection (flag if face disappears)
- [ ] 13.2 Agent: multiple faces detection
- [ ] 13.3 Agent: gaze deviation tracking
- [ ] 13.4 Agent: audio anomaly detection (second voice)
- [ ] 13.5 Agent: CV vs answer consistency checking
- [ ] 13.6 Integrity report generation (flags with severity, included in results)
- [ ] 13.7 Frontend: integrity flags display on candidate detail page

---

## Phase 14: Production Readiness

**Goal:** Production-grade deployment, monitoring, backups.

- [ ] 14.1 `docker-compose.prod.yml` with resource limits, restart policies
- [ ] 14.2 SSL/TLS setup (Let's Encrypt + Certbot + Nginx)
- [ ] 14.3 Network isolation (separate Docker networks per concern)
- [ ] 14.4 Automated DB backup script (daily + pre-migration)
- [ ] 14.5 Backup cron job setup
- [ ] 14.6 Grafana dashboards (application, infrastructure, business metrics)
- [ ] 14.7 Prometheus alert rules
- [ ] 14.8 OpenTelemetry instrumentation (Django, Celery, external API calls)
- [ ] 14.9 Structured JSON logging with trace correlation
- [ ] 14.10 CD pipeline (GitHub Actions → SSH deploy → rolling update)
- [ ] 14.11 Smoke tests post-deploy
- [ ] 14.12 Security review (CORS, CSRF, rate limiting, input sanitization)
- [ ] 14.13 Performance review (N+1 queries, caching strategy, connection pooling)

---

## Phase 15: Polish & Launch

**Goal:** Final touches before going live.

- [ ] 15.1 Landing page (hero, features, pricing, CTA)
- [ ] 15.2 SEO optimization (meta tags, sitemap, robots.txt for public job board)
- [ ] 15.3 Error pages (404, 500, 403)
- [ ] 15.4 Loading states and skeleton screens
- [ ] 15.5 Responsive design review
- [ ] 15.6 Accessibility review (ARIA labels, keyboard navigation)
- [ ] 15.7 i18n setup (EN/RU for all UI text)
- [ ] 15.8 GDPR compliance (data deletion request, privacy policy, cookie consent)
- [ ] 15.9 Terms of service page
- [ ] 15.10 Final end-to-end testing (full flow: register company → create vacancy → candidate applies → AI interview → HR reviews)

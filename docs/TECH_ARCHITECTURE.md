# HR PreScan — Technical Architecture

## 1. Tech Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Backend | Django (Python) | REST API, business logic, auth, SSE |
| Frontend | Vue.js | SPA (Single Page Application) |
| Database | PostgreSQL | Primary relational data store |
| Cache | Redis | Caching, sessions, SSE pub/sub |
| File Storage | MinIO (S3-compatible) | CVs, interview recordings, media |
| Task Queue | Celery + RabbitMQ | Async jobs, inter-service messaging |
| Video Room | LiveKit (self-hosted) | WebRTC rooms for interviews |
| AI Agent | LiveKit Agents (VoicePipelineAgent) | STT → LLM → TTS orchestration |
| STT | Deepgram Nova-3 | Real-time speech-to-text |
| TTS | ElevenLabs Flash v2.5 | Text-to-speech (natural voice) |
| LLM | Gemini 3.0 Flash (Google) | Conversation logic, evaluation |
| Deployment | Docker Compose | All services, zero-downtime |

---

## 2. Docker Compose Services

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Compose                        │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │  Nginx   │  │  Django  │  │  Celery  │  │ Celery  │ │
│  │ (Vue.js) │  │   API    │  │  Worker  │  │  Beat   │ │
│  │  :80/443 │  │  :8000   │  │          │  │         │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ LiveKit  │  │ LiveKit  │  │ RabbitMQ │              │
│  │  Server  │  │  Agent   │  │  :5672   │              │
│  │  :7880   │  │          │  │          │              │
│  └──────────┘  └──────────┘  └──────────┘              │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │PostgreSQL│  │  Redis   │  │  MinIO   │              │
│  │  :5432   │  │  :6379   │  │  :9000   │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└─────────────────────────────────────────────────────────┘
```

### 10 Services

| # | Service | Image | Port | Role |
|---|---------|-------|------|------|
| 1 | **Nginx (Vue.js)** | Custom (node build + nginx) | 80, 443 | Serves frontend SPA, reverse proxy to Django API |
| 2 | **Django API** | Custom (Python) | 8000 | REST API, auth, SSE notifications, admin |
| 3 | **PostgreSQL** | postgres:16 | 5432 | Primary database |
| 4 | **Redis** | redis:7 | 6379 | Cache, sessions, SSE pub/sub channel |
| 5 | **RabbitMQ** | rabbitmq:3-management | 5672, 15672 | Message broker (Celery tasks + inter-service) |
| 6 | **Celery Worker** | Same as Django | — | Async task execution |
| 7 | **Celery Beat** | Same as Django | — | Scheduled task dispatcher |
| 8 | **LiveKit Server** | livekit/livekit-server | 7880, 7881 | WebRTC SFU, room management |
| 9 | **LiveKit Agent** | Custom (Python) | — | AI interviewer (Deepgram + Gemini + ElevenLabs) |
| 10 | **MinIO** | minio/minio | 9000, 9001 | S3-compatible object storage |

---

## 3. Communication Architecture

```
                        ┌─────────────────┐
                        │    Candidate     │
                        │    Browser       │
                        └───────┬─────────┘
                                │
                    ┌───────────┼───────────┐
                    │ HTTPS     │ WebRTC    │ SSE
                    ▼           ▼           ▼
            ┌──────────┐  ┌──────────┐  ┌──────────┐
            │  Nginx   │  │ LiveKit  │  │  Django  │
            │ (Vue.js) │  │  Server  │  │   API    │
            └────┬─────┘  └────┬─────┘  └────┬─────┘
                 │             │              │
                 │ REST        │ Audio        │
                 ▼             ▼              │
            ┌──────────┐  ┌──────────┐       │
            │  Django  │  │ LiveKit  │       │
            │   API    │  │  Agent   │       │
            └────┬─────┘  └────┬─────┘       │
                 │             │              │
         ┌───────┼─────────────┼──────────────┤
         │       │             │              │
         ▼       ▼             ▼              ▼
    ┌─────────┐ ┌─────────┐ ┌──────────┐ ┌──────────┐
    │RabbitMQ │ │PostgreSQL│ │ External │ │  Redis   │
    │         │ │          │ │   APIs   │ │          │
    └─────────┘ └──────────┘ └──────────┘ └──────────┘
                              │  │  │
                     Deepgram─┘  │  └─ElevenLabs
                         Google Gemini
```

### Communication Protocols

| From | To | Protocol | Purpose |
|------|----|----------|---------|
| Browser | Nginx | HTTPS | Serve frontend, proxy API requests |
| Vue.js | Django API | REST (HTTP) | All CRUD operations, auth, data |
| Django API | Vue.js | SSE | Real-time notifications (new candidate, interview done) |
| Browser | LiveKit Server | WebRTC | Candidate video/audio during interview |
| Browser | LiveKit Server | WebRTC | HR silent observer mode |
| LiveKit Server | LiveKit Agent | Internal audio stream | Candidate audio to AI agent |
| LiveKit Agent | Deepgram | WebSocket | Real-time speech-to-text |
| LiveKit Agent | Google Gemini | HTTPS | Gemini 3.0 Flash for conversation |
| LiveKit Agent | ElevenLabs | HTTPS | Text-to-speech response |
| Django API | RabbitMQ | AMQP | Dispatch async tasks to Celery |
| Django API | RabbitMQ | AMQP | Send messages to LiveKit Agent (create room, start interview) |
| LiveKit Agent | RabbitMQ | AMQP | Send results back to Django (scores, transcript) |
| Celery Worker | RabbitMQ | AMQP | Consume tasks |
| Celery Worker | PostgreSQL | TCP | Read/write data |
| Celery Worker | MinIO | S3 (HTTP) | Store/retrieve files |
| Django API | PostgreSQL | TCP | Primary data access |
| Django API | Redis | Redis protocol | Cache, sessions, SSE pub/sub |
| Django API | MinIO | S3 (HTTP) | File upload URLs, metadata |

---

## 4. AI Interview Pipeline

```
Candidate speaks
       │
       ▼
┌──────────────┐    WebSocket     ┌──────────────┐
│  LiveKit     │ ──────────────►  │  Deepgram    │
│  Server      │                  │  Nova-3      │
│  (captures   │  ◄────────────── │  (STT)       │
│   audio)     │    transcript    └──────────────┘
└──────┬───────┘
       │ audio stream
       ▼
┌──────────────┐                  ┌──────────────┐
│  LiveKit     │    HTTPS         │  Google      │
│  Agent       │ ──────────────►  │  Gemini 2.5  │
│  (Voice      │                  │  Flash       │
│  Pipeline    │  ◄────────────── │  (LLM)       │
│  Agent)      │    response text └──────────────┘
│              │
│              │    HTTPS         ┌──────────────┐
│              │ ──────────────►  │  ElevenLabs  │
│              │                  │  Flash v2.5  │
│              │  ◄────────────── │  (TTS)       │
└──────┬───────┘    audio stream  └──────────────┘
       │
       ▼
Candidate hears AI response
```

### Pipeline Latency Budget

| Step | Service | Latency |
|------|---------|---------|
| Voice Activity Detection | LiveKit (built-in) | ~50ms |
| Speech-to-Text | Deepgram Nova-3 | ~150-300ms |
| LLM Response | Gemini 3.0 Flash | ~100-300ms |
| Text-to-Speech | ElevenLabs Flash v2.5 | ~75ms |
| **Total end-to-end** | | **~400-750ms** |

### AI Agent Configuration

```python
# LiveKit VoicePipelineAgent setup (conceptual)
agent = VoicePipelineAgent(
    stt=DeepgramSTT(
        model="nova-3",
        language="multi",           # EN↔RU code-switching
        interim_results=True,
        endpointing=300,            # ms silence before finalizing
    ),
    llm=GoogleLLM(
        model="gemini-3-flash-preview",
        system_prompt="...",        # Interview instructions, vacancy context, CV data
    ),
    tts=ElevenLabsTTS(
        model="eleven_flash_v2_5",
        voice="...",                # Selected interviewer voice
    ),
)
```

---

## 5. Data Flow Diagrams

### 5.1 Candidate Application Flow

```
Candidate                 Nginx/Vue.js              Django API           Celery Worker
    │                         │                         │                      │
    │  1. Browse vacancies    │                         │                      │
    │ ───────────────────────►│  GET /api/vacancies     │                      │
    │                         │ ───────────────────────►│                      │
    │                         │◄─────────────────────── │                      │
    │◄─────────────────────── │                         │                      │
    │                         │                         │                      │
    │  2. Apply + upload CV   │                         │                      │
    │ ───────────────────────►│  POST /api/apply        │                      │
    │                         │ ───────────────────────►│                      │
    │                         │                         │──── task: parse_cv ──►│
    │                         │                         │                      │── Upload CV to MinIO
    │                         │                         │                      │── Extract skills, exp
    │                         │                         │                      │── AI analyze vs vacancy
    │                         │                         │◄──── CV scores ──────│
    │                         │                         │                      │
    │  3. Pick time slot      │                         │                      │
    │ ───────────────────────►│  POST /api/schedule     │                      │
    │                         │ ───────────────────────►│                      │
    │                         │                         │── Create LiveKit room (RabbitMQ)
    │                         │                         │── Send calendar invite (Celery)
    │◄─── Interview link ──── │◄─────────────────────── │                      │
```

### 5.2 AI Interview Flow

```
Candidate              LiveKit Server        LiveKit Agent         Django API
    │                       │                      │                    │
    │  1. Join room (WebRTC)│                      │                    │
    │ ─────────────────────►│                      │                    │
    │                       │  2. Notify agent     │                    │
    │                       │ ────────────────────►│                    │
    │                       │                      │  3. Fetch context  │
    │                       │                      │ ──────────────────►│
    │                       │                      │◄── vacancy + CV ── │
    │                       │                      │                    │
    │  4. Candidate speaks  │                      │                    │
    │ ─────────────────────►│ ── audio stream ────►│                    │
    │                       │                      │── Deepgram (STT)   │
    │                       │                      │── Gemini (think)    │
    │                       │                      │── ElevenLabs (TTS) │
    │◄── AI voice response ─│◄── audio stream ────│                    │
    │                       │                      │                    │
    │  ... (repeat Q&A) ... │                      │                    │
    │                       │                      │                    │
    │  5. Interview ends    │                      │                    │
    │◄── goodbye ───────────│◄─────────────────────│                    │
    │                       │                      │  6. Send results   │
    │                       │                      │ ──────────────────►│
    │                       │                      │   (RabbitMQ)       │
    │                       │                      │   scores,          │
    │                       │                      │   transcript,      │
    │                       │                      │   recording        │
    │                       │                      │                    │
    │                       │                      │         HR ◄── SSE notification
```

---

## 6. Database Schema (High-Level)

### Core Tables

```
companies
├── id, name, industry, size, country, logo, website, description
├── subscription_plan, subscription_status, trial_ends_at
└── created_at, updated_at

users
├── id, email, password_hash, first_name, last_name, phone
├── role (admin | hr | candidate)
├── company_id (FK → companies, nullable for candidates)
├── is_active, email_verified
└── created_at, updated_at

vacancies
├── id, company_id (FK), created_by (FK → users)
├── title, description, required_skills, salary_min, salary_max
├── location, location_type (remote | onsite | hybrid)
├── visibility (public | private), share_token
├── status (draft | active | paused | closed)
├── deadline
├── interview_duration_minutes, interview_language (en | ru)
└── created_at, updated_at

vacancy_criteria
├── id, vacancy_id (FK)
├── name (e.g., "React experience")
├── description
├── weight (for scoring)
└── is_custom (false = fixed category, true = HR-defined)

interview_questions
├── id, vacancy_id (FK)
├── question_text
├── category (soft_skills | technical | language | custom)
├── order_index
├── is_ai_generated, is_edited_by_hr
└── created_at

applications
├── id, vacancy_id (FK), candidate_id (FK → users, nullable)
├── candidate_name, candidate_email, candidate_phone
├── cv_file_key (S3/MinIO path)
├── cv_parsed_data (JSON — extracted skills, experience, etc.)
├── cv_match_score
├── status (applied | interview_scheduled | interview_in_progress |
│          interview_completed | reviewing | shortlisted | rejected)
├── hr_notes
└── created_at, updated_at

interviews
├── id, application_id (FK)
├── livekit_room_name, livekit_room_token
├── scheduled_at, started_at, ended_at
├── duration_seconds
├── recording_file_key (S3/MinIO path)
├── transcript (JSON — timestamped conversation)
├── status (scheduled | in_progress | completed | no_show | cancelled)
└── created_at

interview_scores
├── id, interview_id (FK), criteria_id (FK → vacancy_criteria)
├── score (1-10)
├── ai_notes (text explanation for the score)
└── created_at

interview_integrity_flags
├── id, interview_id (FK)
├── flag_type (face_absent | multiple_faces | gaze_deviation |
│             audio_anomaly | cv_inconsistency | scripted_answer)
├── severity (info | warning | critical)
├── description
├── timestamp_seconds (when in the interview it occurred)
└── created_at

notifications
├── id, user_id (FK)
├── type (new_application | interview_completed | reminder | etc.)
├── title, message
├── data (JSON — links, IDs for navigation)
├── is_read
└── created_at

subscription_plans
├── id, name, price_monthly, price_yearly
├── max_vacancies, max_interviews_per_month, max_hr_users
├── max_storage_gb
└── is_active
```

---

## 7. API Structure (REST)

### Public Endpoints (no auth)
```
GET    /api/vacancies/                    — public job board listing
GET    /api/vacancies/{id}/               — vacancy detail
GET    /api/companies/{id}/               — company profile
POST   /api/auth/register/                — user registration
POST   /api/auth/login/                   — login (JWT)
POST   /api/auth/verify-email/            — email verification
POST   /api/apply/{vacancy_id}/           — candidate applies (no auth required)
```

### Candidate Endpoints (auth optional/required)
```
GET    /api/candidate/applications/       — my applications
GET    /api/candidate/applications/{id}/  — application detail + status
POST   /api/candidate/schedule/{app_id}/  — pick interview time slot
GET    /api/candidate/interview/{id}/     — get interview room link
```

### HR Endpoints (auth required, scoped to company)
```
GET    /api/hr/vacancies/                 — list my company's vacancies
POST   /api/hr/vacancies/                 — create vacancy
PUT    /api/hr/vacancies/{id}/            — update vacancy
PATCH  /api/hr/vacancies/{id}/status/     — change status (publish, pause, close)
GET    /api/hr/vacancies/{id}/questions/  — get AI-generated questions
PUT    /api/hr/vacancies/{id}/questions/  — edit questions
GET    /api/hr/vacancies/{id}/candidates/ — list candidates for vacancy
GET    /api/hr/candidates/{id}/           — candidate detail (scores, transcript, recording)
PATCH  /api/hr/candidates/{id}/status/    — update candidate status
POST   /api/hr/candidates/{id}/notes/     — add HR notes
GET    /api/hr/interviews/{id}/observe/   — get observer token for live interview
GET    /api/hr/dashboard/                 — dashboard stats
```

### Admin Endpoints (auth required, admin role)
```
GET    /api/admin/companies/              — list all companies
GET    /api/admin/companies/{id}/         — company detail
PATCH  /api/admin/companies/{id}/         — update company (activate/block)
GET    /api/admin/users/                  — list all users
PATCH  /api/admin/users/{id}/             — update user (activate/block)
GET    /api/admin/analytics/              — platform-wide stats
GET    /api/admin/subscriptions/          — manage subscription plans
```

### Notifications
```
GET    /api/notifications/                — list notifications
PATCH  /api/notifications/{id}/read/      — mark as read
GET    /api/notifications/stream/         — SSE stream for real-time
```

---

## 8. Authentication & Authorization

### Authentication
- **JWT (JSON Web Tokens)** — access token + refresh token
- Access token: short-lived (15-30 minutes)
- Refresh token: long-lived (7 days)
- Social login: Google OAuth 2.0
- Email verification required for HR and Admin roles

### Authorization (Role-Based Access Control)
```
Admin:
  - Full platform access
  - Manage companies, users, subscriptions
  - View platform analytics

HR Manager:
  - Scoped to their company only
  - CRUD vacancies (own company)
  - View candidates and scores (own company)
  - Observe live interviews (own company)

Candidate:
  - Browse public vacancies
  - Apply to vacancies (auth optional)
  - View own applications (auth required)
  - Join interview room (token-based, no auth needed)
```

### Multi-Tenancy Enforcement
- Every HR query is filtered by `company_id` at the Django queryset level
- Middleware validates that the authenticated user belongs to the correct company
- Candidates are not tied to a company — they apply across companies

---

## 9. File Storage (MinIO / S3)

### Bucket Structure
```
hr-prescan-files/
├── cvs/
│   └── {company_id}/{application_id}/resume.pdf
├── recordings/
│   └── {company_id}/{interview_id}/recording.webm
├── company-assets/
│   └── {company_id}/logo.png
└── temp/
    └── {upload_id}/...
```

### Upload Flow
- **CV upload:** Client → Django API (pre-signed URL) → Direct upload to MinIO
- **Interview recording:** LiveKit → Egress to MinIO (automatic via LiveKit)
- **Company logo:** Client → Django API → MinIO

---

## 10. Deployment & Zero-Downtime

### Docker Compose Strategy
- All 10 services defined in `docker-compose.yml`
- Environment-specific overrides: `docker-compose.override.yml` (dev), `docker-compose.prod.yml` (prod)

### Zero-Downtime Deployment
- **Rolling update** for Django API and Celery workers
- Nginx upstream with health checks — new container starts, health check passes, old container drains and stops
- Database migrations run before new code is deployed (backward-compatible migrations)
- LiveKit Server and Agent can be updated independently

### Environment Variables
```
# Database
POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

# Redis
REDIS_URL

# RabbitMQ
RABBITMQ_URL

# MinIO / S3
S3_ENDPOINT, S3_ACCESS_KEY, S3_SECRET_KEY, S3_BUCKET_NAME

# LiveKit
LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET

# External AI Services
DEEPGRAM_API_KEY
GOOGLE_API_KEY
ELEVENLABS_API_KEY

# Email
SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, FROM_EMAIL

# Auth
JWT_SECRET_KEY, GOOGLE_OAUTH_CLIENT_ID, GOOGLE_OAUTH_CLIENT_SECRET

# App
DJANGO_SECRET_KEY, DEBUG, ALLOWED_HOSTS, CORS_ORIGINS
```

---

## 11. External Services (API Keys Required)

| Service | Purpose | Pricing Model |
|---------|---------|---------------|
| **Deepgram** | Speech-to-text | $0.0092/min (multilingual streaming) |
| **Google Gemini** | LLM conversation | Per token (Gemini 3.0 Flash) |
| **ElevenLabs** | Text-to-speech | Per character (~$150/M chars) |
| **Google OAuth** | Social login | Free |
| **SMTP Provider** | Email delivery | Per email (SendGrid, Mailgun, etc.) |
| **Stripe** (future) | Payment processing | Per transaction |

### Estimated Cost Per Interview (30 min)
| Service | Cost |
|---------|------|
| Deepgram STT | ~$0.28 |
| Google Gemini | ~$0.05-0.15 |
| ElevenLabs TTS | ~$0.10-0.30 |
| **Total** | **~$0.43-0.73** |

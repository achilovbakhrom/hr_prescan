# HR PreScan

AI-powered candidate pre-screening platform. Companies post vacancies, candidates apply and are interviewed by an AI agent via video, and HR reviews scores and recordings.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 5, Django REST Framework, Celery, PostgreSQL |
| Frontend | Vue 3, TypeScript, Pinia, PrimeVue, Tailwind CSS |
| AI Interview | LiveKit, Deepgram STT, GPT-4o, ElevenLabs TTS |
| Message Broker | RabbitMQ |
| Cache | Redis |
| Storage | MinIO (S3-compatible) |
| Monitoring | Prometheus, Grafana, Jaeger, Loki |
| CI/CD | GitHub Actions |

## Architecture

```
┌─────────┐    ┌─────────┐    ┌──────────┐    ┌──────────┐
│ Frontend │───▶│  Nginx  │───▶│  Django  │───▶│ Postgres │
│ (Vue 3)  │    │         │    │  (API)   │    └──────────┘
└─────────┘    └─────────┘    └────┬─────┘
                                   │
                    ┌──────────────┼──────────────┐
                    ▼              ▼              ▼
              ┌──────────┐  ┌──────────┐  ┌──────────┐
              │ RabbitMQ │  │  Redis   │  │  MinIO   │
              └────┬─────┘  └──────────┘  └──────────┘
                   ▼
             ┌───────────┐    ┌──────────┐
             │  Celery   │    │ LiveKit  │
             │ Worker/   │    │ Agent    │
             │  Beat     │    │ (AI)     │
             └───────────┘    └──────────┘
```

---

## Local Development Setup

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose v2+
- [Node.js 22+](https://nodejs.org/) (for running frontend linters/formatters outside Docker)
- [Python 3.12+](https://www.python.org/) (for running backend linters outside Docker)
- Git

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/achilovbakhrom/hr_prescan.git
cd hr_prescan

# 2. Run setup (copies .env, builds images, starts services, runs migrations)
make setup

# 3. Create an admin user
make createsuperuser
```

That's it. The platform is now running at:

| Service | URL | Credentials |
|---------|-----|-------------|
| Frontend (Vite dev server) | http://localhost:5173 | — |
| Backend API | http://localhost:8000 | — |
| Browsable API | http://localhost:8000/api/health/ | — |
| RabbitMQ Management | http://localhost:15672 | guest / guest |
| MinIO Console | http://localhost:9001 | minioadmin / minioadmin |

### Manual Setup (without Make)

```bash
# Copy environment file
cp .env.example .env
# Edit .env — add your OpenAI/Deepgram/ElevenLabs API keys for AI features

# Build and start services
docker compose build
docker compose up -d

# Wait for services to be healthy, then run migrations
docker compose exec django python manage.py migrate --noinput
docker compose exec django python manage.py collectstatic --noinput

# Create admin user
docker compose exec django python manage.py createsuperuser
```

### Environment Variables

Edit `.env` after copying from `.env.example`. Key variables:

| Variable | Required | Description |
|----------|----------|-------------|
| `POSTGRES_PASSWORD` | Yes | Database password |
| `DJANGO_SECRET_KEY` | Yes | Django secret (generate a random string) |
| `OPENAI_API_KEY` | For AI | OpenAI API key (interview questions, CV analysis, evaluations) |
| `DEEPGRAM_API_KEY` | For AI | Deepgram API key (speech-to-text in interviews) |
| `ELEVENLABS_API_KEY` | For AI | ElevenLabs API key (text-to-speech for AI interviewer) |

The platform works without AI keys — vacancy management, candidate tracking, and HR workflows function normally. AI features (question generation, CV analysis, video interviews) require the respective API keys.

### Common Commands

```bash
make up                 # Start services
make down               # Stop services
make logs               # Tail all logs
make logs-django        # Tail Django logs only
make migrate            # Run database migrations
make makemigrations     # Generate new migrations
make shell              # Django interactive shell
make dbshell            # PostgreSQL interactive shell
make lint               # Run linters
make format             # Auto-format code
make typecheck          # Run type checks
make backup-db          # Backup database
make reset-db           # Reset database (destructive!)
```

### Optional Service Stacks

```bash
# Monitoring (Grafana, Prometheus, Jaeger, Loki)
make up-monitoring
# → Grafana:    http://localhost:3000 (admin/admin)
# → Prometheus: http://localhost:9090
# → Jaeger:     http://localhost:16686

# Management UIs (Portainer, pgAdmin, RedisInsight)
make up-management
# → pgAdmin:      http://localhost:5050 (admin@admin.com/admin)
# → RedisInsight:  http://localhost:5540
# → Portainer:     https://localhost:9443

# Everything at once
make up-all
```

### Running Without Docker (Backend)

For faster iteration, you can run the backend directly:

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set env vars (database must be running — use Docker for Postgres/Redis/RabbitMQ)
export DJANGO_SETTINGS_MODULE=config.settings.local
export POSTGRES_HOST=127.0.0.1
export POSTGRES_PORT=35432
export REDIS_URL=redis://127.0.0.1:36379/0
export RABBITMQ_URL=amqp://guest:guest@127.0.0.1:35672//
export LIVEKIT_URL=ws://127.0.0.1:37880

# Run migrations and server
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

The Make-based native local flow uses Docker context `desktop-linux` and an isolated
Compose project by default, with these host ports:

- Frontend: `5173`
- Backend: `8000`
- Postgres: `35432`
- Redis: `36379`
- RabbitMQ AMQP: `35672`
- RabbitMQ Management: `35673`
- LiveKit: `37880`
- MinIO API: `39000`
- MinIO Console: `39001`

If you want to change the context or ports, override the variables explicitly, for example:

```bash
make local-backend-all \
  LOCAL_DOCKER_CONTEXT=desktop-linux \
  LOCAL_DJANGO_PORT=48000 \
  LOCAL_FRONTEND_PORT=45173 \
  LOCAL_POSTGRES_PORT=45432
```

### Running Without Docker (Frontend)

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

### Project Structure

```
hr_prescan/
├── backend/                    # Django REST API
│   ├── apps/
│   │   ├── accounts/           # Users, companies, auth, permissions
│   │   ├── applications/       # Job applications, CV processing
│   │   ├── common/             # Base models, middleware, admin APIs
│   │   ├── interviews/         # Interview scheduling, scores, integrity
│   │   ├── notifications/      # Email + in-app notifications, messaging
│   │   ├── subscriptions/      # Plans, billing, quotas
│   │   └── vacancies/          # Job vacancies, criteria, questions
│   ├── config/                 # Django settings (base, local, production)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                   # Vue.js SPA
│   ├── src/
│   │   ├── app/                # Router, main.ts, App.vue
│   │   ├── features/           # Feature modules (auth, vacancies, etc.)
│   │   └── shared/             # Shared components, composables, constants
│   ├── Dockerfile
│   └── package.json
├── livekit-agent/              # AI interview agent
│   ├── agent.py                # Entry point
│   ├── interview_agent.py      # VoicePipelineAgent config
│   ├── evaluator.py            # Post-interview scoring
│   ├── integrity.py            # Anti-cheating monitoring
│   └── Dockerfile
├── docs/                       # Project documentation
│   ├── BUSINESS_LOGIC.md       # Product requirements, user flows
│   ├── TECH_ARCHITECTURE.md    # Services, DB schema, API structure
│   ├── CODE_STYLE.md           # Code conventions, patterns
│   ├── DEVOPS.md               # CI/CD, deployment, monitoring
│   └── ROADMAP.md              # Development phases
├── deploy/                     # Deployment & infrastructure
│   ├── nginx/                  # Nginx configs (dev + prod)
│   ├── monitoring/             # Grafana, Prometheus configs
│   ├── livekit/                # LiveKit server config
│   ├── scripts/                # Backup, SSL, smoke-test scripts
│   ├── docker-compose.prod.yml
│   ├── docker-compose.monitoring.yml
│   └── docker-compose.management.yml
├── docker-compose.yml          # Base services (10 containers)
├── docker-compose.override.yml # Dev overrides (hot reload, debug ports)
├── Makefile                    # Dev commands
└── .env.example                # Environment template
```

---

## Deployment Guide

### Prerequisites

- A Linux server (Ubuntu 22.04+ recommended) with:
  - Docker and Docker Compose v2+
  - At least 4 GB RAM, 2 vCPUs, 40 GB disk
  - Ports 80, 443, 7880, 7881/udp open
- A domain name pointing to your server's IP
- API keys for OpenAI, Deepgram, ElevenLabs (for AI interviews)

### Step 1: Server Setup

```bash
# SSH into your server
ssh user@your-server-ip

# Install Docker (if not installed)
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Log out and back in for group change to take effect

# Clone the repository
git clone https://github.com/achilovbakhrom/hr_prescan.git
cd hr_prescan
```

### Step 2: Configure Environment

```bash
cp .env.example .env
nano .env
```

Update these values for production:

```env
# Generate a strong secret key
DJANGO_SECRET_KEY=your-very-long-random-secret-key-here
DJANGO_SETTINGS_MODULE=config.settings.production

# Strong database password
POSTGRES_PASSWORD=your-strong-database-password

# MinIO credentials
MINIO_ACCESS_KEY=your-minio-access-key
MINIO_SECRET_KEY=your-minio-secret-key

# AI service keys
OPENAI_API_KEY=sk-...
DEEPGRAM_API_KEY=...
ELEVENLABS_API_KEY=...

# LiveKit (generate proper keys for production)
LIVEKIT_API_KEY=your-livekit-api-key
LIVEKIT_API_SECRET=your-livekit-api-secret

# Internal API key
INTERNAL_API_KEY=your-random-internal-api-key

# Your domain
CORS_ALLOWED_ORIGINS=https://yourdomain.com
ALLOWED_HOSTS=yourdomain.com

# Frontend
VITE_API_URL=https://yourdomain.com
```

### Step 3: SSL Certificates

```bash
# Edit the script with your domain and email
nano deploy/scripts/init-letsencrypt.sh
# Set DOMAIN=yourdomain.com and EMAIL=you@email.com

# Make scripts executable
chmod +x deploy/scripts/*.sh

# Get SSL certificates
./deploy/scripts/init-letsencrypt.sh
```

### Step 4: Build and Deploy

```bash
# Build production images
docker compose -f docker-compose.yml -f deploy/docker-compose.prod.yml build

# Start all services
docker compose -f docker-compose.yml -f deploy/docker-compose.prod.yml up -d

# Run migrations
docker compose -f docker-compose.yml -f deploy/docker-compose.prod.yml exec django python manage.py migrate --noinput

# Collect static files
docker compose -f docker-compose.yml -f deploy/docker-compose.prod.yml exec django python manage.py collectstatic --noinput

# Create admin user
docker compose -f docker-compose.yml -f deploy/docker-compose.prod.yml exec django python manage.py createsuperuser

# Verify deployment
./deploy/scripts/smoke-test.sh https://yourdomain.com
```

### Step 5: Setup Automated Backups

```bash
# Setup daily database backup cron job
./deploy/scripts/backup-cron-setup.sh
```

### Step 6: Enable Monitoring (Optional)

```bash
docker compose -f docker-compose.yml -f deploy/docker-compose.prod.yml -f deploy/docker-compose.monitoring.yml up -d

# Grafana will be available at http://your-server-ip:3000
# Default login: admin / admin (change immediately)
# Pre-configured dashboards: Application, Infrastructure, Business
```

### Updating the Application

```bash
cd hr_prescan
git pull origin main

# Rebuild and restart
docker compose -f docker-compose.yml -f deploy/docker-compose.prod.yml build
docker compose -f docker-compose.yml -f deploy/docker-compose.prod.yml up -d

# Run any new migrations
docker compose -f docker-compose.yml -f deploy/docker-compose.prod.yml exec django python manage.py migrate --noinput
```

### CI/CD (Automated Deployment)

The project includes a GitHub Actions CD pipeline (`.github/workflows/cd.yml`) that:
1. Builds Docker images on push to `main`
2. Pushes images to GitHub Container Registry
3. SSH deploys to your server with rolling updates
4. Runs migrations and smoke tests
5. Auto-rolls back on failure

To enable it, add these GitHub repository secrets:
- `DEPLOY_HOST` — your server IP
- `DEPLOY_USER` — SSH user
- `DEPLOY_KEY` — SSH private key
- `DEPLOY_PATH` — path on server (e.g., `/opt/hr_prescan`)

### Production Checklist

- [ ] Strong `DJANGO_SECRET_KEY` (50+ random characters)
- [ ] Strong `POSTGRES_PASSWORD`
- [ ] SSL certificate obtained and auto-renewing
- [ ] All AI API keys configured
- [ ] LiveKit API key/secret generated (not dev defaults)
- [ ] `INTERNAL_API_KEY` set to a random value
- [ ] `CORS_ALLOWED_ORIGINS` set to your domain only
- [ ] Firewall: only ports 80, 443, 7880, 7881/udp open
- [ ] Automated database backups running
- [ ] Monitoring stack deployed
- [ ] Admin user created with strong password
- [ ] Changed default Grafana admin password

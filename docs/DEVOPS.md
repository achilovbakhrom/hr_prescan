# HR PreScan — DevOps & Infrastructure

## 1. Docker Compose Services (Full List)

### Application Services (10)

| # | Service | Image | Ports | Role |
|---|---------|-------|-------|------|
| 1 | Nginx (Vue.js) | Custom | 80, 443 | Frontend SPA + reverse proxy |
| 2 | Django API | Custom | 8000 | Backend REST API |
| 3 | PostgreSQL | postgres:16 | 5432 | Primary database |
| 4 | Redis | redis:7 | 6379 | Cache, sessions, SSE |
| 5 | RabbitMQ | rabbitmq:3-management | 5672, 15672 | Message broker |
| 6 | Celery Worker | Same as Django | — | Async task execution |
| 7 | Celery Beat | Same as Django | — | Scheduled tasks |
| 8 | LiveKit Server | livekit/livekit-server | 7880, 7881 | WebRTC video rooms |
| 9 | LiveKit Agent | Custom | — | AI interviewer |
| 10 | MinIO | minio/minio | 9000, 9001 | S3-compatible storage |

### Infrastructure & Monitoring Services (8)

| # | Service | Image | Ports | Role |
|---|---------|-------|-------|------|
| 11 | Portainer | portainer/portainer-ce | 9443 | Container management UI |
| 12 | pgAdmin | dpage/pgadmin4 | 5050 | PostgreSQL admin UI |
| 13 | RedisInsight | redis/redisinsight | 5540 | Redis management UI |
| 14 | RabbitMQ Management | (built into rabbitmq image) | 15672 | RabbitMQ admin UI |
| 15 | Grafana | grafana/grafana | 3000 | Metrics dashboards, alerting |
| 16 | Prometheus | prom/prometheus | 9090 | Metrics collection |
| 17 | Jaeger | jaegertracing/all-in-one | 16686, 4317 | Distributed tracing (OpenTelemetry) |
| 18 | Loki | grafana/loki | 3100 | Log aggregation |

**Total: 18 services**

---

## 2. Observability Stack (Grafana + Prometheus + Jaeger + Loki)

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Grafana (UI)                              │
│                        :3000                                     │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│   │   Metrics     │  │   Traces     │  │    Logs      │         │
│   │  (Prometheus) │  │  (Jaeger)    │  │   (Loki)     │         │
│   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
└──────────┼──────────────────┼──────────────────┼────────────────┘
           │                  │                  │
    ┌──────▼───────┐   ┌──────▼───────┐   ┌──────▼───────┐
    │  Prometheus   │   │   Jaeger     │   │    Loki      │
    │  :9090        │   │   :16686     │   │    :3100     │
    │  (scrape)     │   │   :4317      │   │              │
    └──────┬───────┘   └──────┬───────┘   └──────┬───────┘
           │                  │                  │
           │        OTLP      │       Promtail   │
           │       (gRPC)     │      (log ship)  │
    ┌──────┴──────────────────┴──────────────────┴───────┐
    │              Application Services                    │
    │  Django, Celery, LiveKit Agent                       │
    │  (OpenTelemetry SDK instrumented)                    │
    └─────────────────────────────────────────────────────┘
```

### 2.1 Metrics (Prometheus + Grafana)

**What to monitor:**

| Category | Metrics |
|----------|---------|
| **Django API** | Request rate, latency (p50/p95/p99), error rate (4xx/5xx), active connections |
| **Celery** | Task success/failure rate, task duration, queue depth, worker utilization |
| **PostgreSQL** | Active connections, query duration, cache hit ratio, table sizes, replication lag |
| **Redis** | Memory usage, hit/miss ratio, connected clients, evictions |
| **RabbitMQ** | Queue depth, message rate, consumer count, unacked messages |
| **LiveKit** | Active rooms, participant count, track quality, connection failures |
| **MinIO** | Storage used, request rate, errors |
| **System** | CPU, memory, disk, network per container |

**Django instrumentation:**
```python
# Use django-prometheus for automatic metrics
INSTALLED_APPS += ['django_prometheus']
MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    # ... other middleware ...
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]
```

### 2.2 Tracing (Jaeger + OpenTelemetry)

**Purpose:** Trace a request across services — e.g., API call → Celery task → external API → DB query.

**Instrumentation:**
```python
# Django + Celery + external calls
# Use opentelemetry-python SDK

pip install opentelemetry-api \
            opentelemetry-sdk \
            opentelemetry-exporter-otlp \
            opentelemetry-instrumentation-django \
            opentelemetry-instrumentation-celery \
            opentelemetry-instrumentation-requests \
            opentelemetry-instrumentation-psycopg2 \
            opentelemetry-instrumentation-redis
```

**Key traces to capture:**
- Full interview lifecycle: application → CV parsing → scheduling → interview → scoring
- External API latency: Deepgram, Google Gemini, ElevenLabs response times
- Database query performance
- Celery task chains

### 2.3 Logs (Loki + Promtail)

**Purpose:** Centralized log aggregation. All container logs → Loki → queryable in Grafana.

**Setup:**
- Promtail ships Docker container stdout/stderr to Loki
- Grafana provisions Prometheus, Loki, and Jaeger datasources from `deploy/monitoring/grafana/provisioning/datasources.yml`
- Monitoring ports bind to `127.0.0.1` by default. Grafana may be exposed through the production nginx reverse proxy with `GRAFANA_DOMAIN` (for example `grafana.prescreen-app.com`) and `GRAFANA_CERT_DOMAIN` after a matching TLS certificate exists; Prometheus, Loki, and Jaeger stay private and should still be accessed by tunnel/VPN.
- Structured JSON logging in Django (use `python-json-logger`)
- Log levels: DEBUG (dev), INFO (prod default), WARNING, ERROR, CRITICAL
- Correlation: include `trace_id` in logs for linking to Jaeger traces

**Django logging config:**
```python
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
        },
    },
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s %(trace_id)s',
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console'],
    },
}
```

### 2.4 Grafana Dashboards (Pre-built)

| Dashboard | Purpose |
|-----------|---------|
| **Application Overview** | Request rate, error rate, latency, active users |
| **Interview Pipeline** | Active interviews, AI response latency, STT/TTS/LLM breakdown |
| **Celery Tasks** | Task throughput, failure rate, queue backlog |
| **Infrastructure** | CPU/memory/disk per container |
| **Database** | PostgreSQL performance, slow queries, connections |
| **Business Metrics** | Interviews/day, candidates/vacancy, conversion rates |

### 2.5 Alerting (Grafana Alerts)

| Alert | Condition | Severity |
|-------|-----------|----------|
| API error rate > 5% | 5xx responses exceed threshold | Critical |
| API latency p95 > 2s | Slow responses | Warning |
| Celery queue depth > 100 | Tasks backing up | Warning |
| DB connections > 80% | Connection pool exhaustion | Critical |
| Disk usage > 85% | Storage running low | Warning |
| Interview agent crash | LiveKit Agent not responding | Critical |
| External API failure | Deepgram/Google Gemini/ElevenLabs errors | Critical |
| SSL certificate expiry < 14 days | Certificate about to expire | Warning |

---

## 3. CI/CD Pipeline

### 3.1 Pipeline Overview

```
Push to branch          Push/Merge to main         Deployment
─────────────          ──────────────────         ──────────
     │                        │                        │
     ▼                        ▼                        ▼
┌─────────┐            ┌─────────┐            ┌──────────────┐
│  Lint   │            │  Lint   │            │ Pull images  │
│  Format │            │  Format │            │ Backup DB    │
│  Types  │            │  Types  │            │ Run migrations│
└─────────┘            │  Build  │            │ Health check │
                       │  Push   │            │ Rolling update│
                       └─────────┘            │ Verify       │
                                              └──────────────┘
```

**Note:** Unit tests are skipped for the MVP phase. Linters, formatters, and type checkers enforce code quality. Tests will be added post-MVP.

### 3.2 CI Pipeline (GitHub Actions)

```yaml
# .github/workflows/ci.yml

name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  backend-quality:
    name: Backend — Lint, Format, Types
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install ruff mypy django-stubs djangorestframework-stubs
      - name: Ruff lint
        run: ruff check backend/
      - name: Ruff format check
        run: ruff format --check backend/
      - name: Mypy type check
        run: mypy backend/

  frontend-quality:
    name: Frontend — Lint, Format, Types
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      - run: cd frontend && npm ci
      - name: ESLint
        run: cd frontend && npm run lint
      - name: Prettier format check
        run: cd frontend && npx prettier --check "src/**/*.{ts,vue,json,css,scss}"
      - name: TypeScript type check
        run: cd frontend && npx vue-tsc --noEmit

  # Uncomment when tests are added post-MVP:
  # backend-test:
  #   name: Backend — Tests
  #   needs: [backend-quality]
  #   ...
  # frontend-test:
  #   name: Frontend — Tests
  #   needs: [frontend-quality]
  #   ...

  build:
    needs: [backend-quality, frontend-quality]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          context: ./backend
          push: true
          tags: ghcr.io/${{ github.repository }}/backend:${{ github.sha }}
      - uses: docker/build-push-action@v6
        with:
          context: ./frontend
          push: true
          tags: ghcr.io/${{ github.repository }}/frontend:${{ github.sha }}
      - uses: docker/build-push-action@v6
        with:
          context: ./livekit-agent
          push: true
          tags: ghcr.io/${{ github.repository }}/livekit-agent:${{ github.sha }}
```

### 3.3 CD Pipeline (Deployment)

```yaml
# .github/workflows/deploy.yml

name: Deploy

on:
  workflow_run:
    workflows: [CI]
    types: [completed]
    branches: [main]

jobs:
  deploy:
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to server via SSH
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/hr-prescan

            # Pull latest images
            docker compose -f docker-compose.prod.yml pull

            # Run migrations BEFORE deploying new code
            docker compose -f docker-compose.prod.yml run --rm \
              -e DJANGO_SETTINGS_MODULE=config.settings.production \
              django python manage.py migrate --noinput

            # Zero-downtime rolling update
            docker compose -f docker-compose.prod.yml up -d \
              --no-deps --scale django=2 django

            # Wait for new container to be healthy
            sleep 10

            # Scale back to 1 (removes old container)
            docker compose -f docker-compose.prod.yml up -d \
              --no-deps --scale django=1 django

            # Update other services
            docker compose -f docker-compose.prod.yml up -d \
              celery-worker celery-beat livekit-agent

            # Cleanup old images
            docker image prune -f
```

---

## 4. Zero-Downtime Deployment Strategy

### 4.1 Django API (Rolling Update)

```
Step 1: Pull new image
Step 2: Run migrations (backward-compatible!)
Step 3: Start new container alongside old one (scale=2)
Step 4: Nginx health check detects new container is ready
Step 5: Nginx routes traffic to both containers
Step 6: Stop old container (scale=1)
Step 7: Zero downtime achieved
```

### 4.2 Migration Rules for Zero-Downtime

**CRITICAL:** Migrations must be backward-compatible. The old code runs alongside new code during deployment.

| Safe | Unsafe | How to Fix |
|------|--------|------------|
| Add nullable column | Add non-nullable column | Add as nullable, backfill, then make non-null in next deploy |
| Add table | Drop table | Stop using table first, drop in next deploy |
| Add index | Rename column | Add new column, migrate data, drop old column in next deploy |
| Add default value | Remove column still used | Remove from code first, drop column in next deploy |

**Rule: Every migration must work with both the old and new code running simultaneously.**

### 4.3 Nginx Health Check Config

```nginx
upstream django {
    server django:8000;
}

server {
    location /api/ {
        proxy_pass http://django;
        proxy_connect_timeout 5s;
        proxy_read_timeout 30s;
    }

    location /api/health/ {
        proxy_pass http://django;
        proxy_connect_timeout 2s;
        proxy_read_timeout 2s;
    }
}
```

### 4.4 Django Health Check Endpoint

```python
# config/urls.py
urlpatterns += [
    path('api/health/', health_check_view),
]

# Checks: DB connection, Redis connection, RabbitMQ connection, MinIO connection
# Returns 200 if all healthy, 503 if any dependency is down
```

---

## 5. Database Backup

### 5.1 Backup Strategy

| Type | Frequency | Retention | Method |
|------|-----------|-----------|--------|
| **Full backup** | Daily at 02:00 UTC | 30 days | `pg_dump` → compressed → S3/MinIO |
| **Incremental WAL** | Continuous | 7 days | WAL archiving to S3/MinIO |
| **Pre-migration** | Before every deploy | 3 backups | `pg_dump` triggered by CI/CD |

### 5.2 Automated Backup Script

```bash
#!/bin/bash
# scripts/backup_db.sh

set -euo pipefail

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="hr_prescan_${TIMESTAMP}.sql.gz"
BACKUP_BUCKET="hr-prescan-backups"

# Create compressed backup
docker compose exec -T postgres \
  pg_dump -U $POSTGRES_USER -d $POSTGRES_DB \
  | gzip > "/tmp/${BACKUP_FILE}"

# Upload to MinIO/S3
docker compose exec -T minio \
  mc cp "/tmp/${BACKUP_FILE}" "local/${BACKUP_BUCKET}/daily/${BACKUP_FILE}"

# Cleanup local temp file
rm -f "/tmp/${BACKUP_FILE}"

# Remove backups older than 30 days
docker compose exec -T minio \
  mc rm --recursive --force --older-than 30d "local/${BACKUP_BUCKET}/daily/"

echo "Backup completed: ${BACKUP_FILE}"
```

### 5.3 Backup Cron (via Celery Beat or host crontab)

```bash
# Host crontab
0 2 * * * /opt/hr-prescan/scripts/backup_db.sh >> /var/log/backup.log 2>&1
```

### 5.4 Pre-Migration Backup (in CD Pipeline)

```bash
# Run before migrations in deploy script
docker compose -f docker-compose.prod.yml exec -T postgres \
  pg_dump -U $POSTGRES_USER -d $POSTGRES_DB \
  | gzip > "backups/pre_migration_$(date +%Y%m%d_%H%M%S).sql.gz"
```

### 5.5 Restore Procedure

```bash
# Stop application
docker compose stop django celery-worker celery-beat

# Restore from backup
gunzip -c backup_file.sql.gz | docker compose exec -T postgres \
  psql -U $POSTGRES_USER -d $POSTGRES_DB

# Restart application
docker compose up -d django celery-worker celery-beat
```

---

## 6. Admin & Management UIs

### 6.1 Portainer (Container Management)

- **URL:** `https://server:9443`
- **Purpose:** Visual Docker management — view containers, logs, restart, exec into containers
- **Access:** Admin only, protected with Portainer auth

```yaml
# docker-compose.prod.yml (Portainer service)
portainer:
  image: portainer/portainer-ce:latest
  restart: always
  ports:
    - "9443:9443"
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock
    - portainer_data:/data
```

### 6.2 pgAdmin (PostgreSQL Management)

- **URL:** `http://server:5050`
- **Purpose:** Database browsing, query execution, schema inspection
- **Access:** Admin only

```yaml
pgadmin:
  image: dpage/pgadmin4:latest
  restart: always
  ports:
    - "5050:80"
  environment:
    PGADMIN_DEFAULT_EMAIL: admin@hrprescan.com
    PGADMIN_DEFAULT_PASSWORD: ${PGADMIN_PASSWORD}
  volumes:
    - pgadmin_data:/var/lib/pgadmin
```

### 6.3 RedisInsight (Redis Management)

- **URL:** `http://server:5540`
- **Purpose:** Browse Redis keys, monitor memory, debug cache

```yaml
redisinsight:
  image: redis/redisinsight:latest
  restart: always
  ports:
    - "5540:5540"
  volumes:
    - redisinsight_data:/data
```

### 6.4 RabbitMQ Management

- **URL:** `http://server:15672`
- **Purpose:** Queue monitoring, message rates, consumer status
- **Built into:** `rabbitmq:3-management` image (no extra service needed)

### 6.5 MinIO Console

- **URL:** `http://server:9001`
- **Purpose:** Browse buckets/files, manage access policies
- **Built into:** MinIO image (no extra service needed)

---

## 7. Security

### 7.1 Network Isolation

```yaml
# docker-compose.prod.yml — define networks

networks:
  frontend:        # Nginx, Django
  backend:         # Django, PostgreSQL, Redis, RabbitMQ, Celery, MinIO
  livekit:         # LiveKit Server, LiveKit Agent
  monitoring:      # Grafana, Prometheus, Jaeger, Loki
  management:      # Portainer, pgAdmin, RedisInsight

# Service network assignments:
# Nginx:          frontend
# Django:         frontend, backend
# PostgreSQL:     backend
# Redis:          backend
# RabbitMQ:       backend
# Celery:         backend
# MinIO:          backend
# LiveKit Server: frontend, livekit
# LiveKit Agent:  livekit, backend
# Grafana:        monitoring
# Prometheus:     monitoring, backend (to scrape metrics)
# Jaeger:         monitoring, backend (to receive traces)
# Loki:           monitoring
# Portainer:      management
# pgAdmin:        management, backend
# RedisInsight:   management, backend
```

### 7.2 Exposed Ports (Production)

Only these ports should be publicly accessible:

| Port | Service | Purpose |
|------|---------|---------|
| 80 | Nginx | HTTP → redirect to HTTPS |
| 443 | Nginx | HTTPS (frontend + API) |
| 7880 | LiveKit | WebRTC signaling |
| 7881 | LiveKit | WebRTC media (UDP) |

All management UIs (Portainer, pgAdmin, Grafana, etc.) should be accessible only via:
- VPN, or
- SSH tunnel, or
- IP whitelist via firewall

### 7.3 SSL/TLS

- Use **Let's Encrypt** with **Certbot** for automatic SSL certificates
- Nginx terminates SSL
- Internal service communication is plain HTTP/TCP (within Docker network)

```yaml
certbot:
  image: certbot/certbot
  volumes:
    - certbot_conf:/etc/letsencrypt
    - certbot_www:/var/www/certbot
  entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h; done'"
```

### 7.4 Secrets Management

- **Never** store secrets in docker-compose files or git
- Use `.env` files (not committed) or Docker secrets
- Rotate API keys (Deepgram, Google Gemini, ElevenLabs) periodically
- Use separate credentials for dev/staging/prod

```bash
# .env.prod (not in git, managed on server)
POSTGRES_PASSWORD=<generated>
DJANGO_SECRET_KEY=<generated>
DEEPGRAM_API_KEY=<from-dashboard>
GOOGLE_API_KEY=<from-dashboard>
ELEVENLABS_API_KEY=<from-dashboard>
LIVEKIT_API_SECRET=<generated>
JWT_SECRET_KEY=<generated>
```

---

## 8. Docker Compose Files

### 8.1 File Organization

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Base service definitions (shared) |
| `docker-compose.override.yml` | Development overrides (auto-loaded, hot reload, exposed ports) |
| `docker-compose.prod.yml` | Production overrides (images from registry, resource limits, restart policies) |
| `docker-compose.monitoring.yml` | Monitoring stack (Grafana, Prometheus, Jaeger, Loki) |
| `docker-compose.management.yml` | Management UIs (Portainer, pgAdmin, RedisInsight) |

### 8.2 Running

```bash
# Development (uses docker-compose.yml + docker-compose.override.yml automatically)
docker compose up -d

# Production
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Production + monitoring
docker compose -f docker-compose.yml -f docker-compose.prod.yml \
               -f docker-compose.monitoring.yml up -d

# Production + monitoring + management UIs
docker compose -f docker-compose.yml -f docker-compose.prod.yml \
               -f docker-compose.monitoring.yml \
               -f docker-compose.management.yml up -d
```

---

## 9. Startup Order & Dependencies

### 9.1 Service Dependency Chain

```
PostgreSQL ──►  Django API ──►  Celery Worker
Redis      ──►              ──►  Celery Beat
RabbitMQ   ──►              ──►  LiveKit Agent
MinIO      ──►
LiveKit Server ──►  LiveKit Agent
```

### 9.2 Startup Sequence

```yaml
# docker-compose.yml — depends_on with health checks

services:
  postgres:
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 5s
      timeout: 3s
      retries: 5

  redis:
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  rabbitmq:
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "check_running"]
      interval: 10s
      timeout: 5s
      retries: 5

  minio:
    healthcheck:
      test: ["CMD", "mc", "ready", "local"]
      interval: 5s
      timeout: 3s
      retries: 5

  django:
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      rabbitmq:
        condition: service_healthy
      minio:
        condition: service_healthy
    # Entrypoint: run migrations, then start server
    entrypoint: |
      sh -c "
        python manage.py migrate --noinput &&
        python manage.py collectstatic --noinput &&
        gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
      "

  celery-worker:
    depends_on:
      django:
        condition: service_healthy

  celery-beat:
    depends_on:
      django:
        condition: service_healthy

  livekit-agent:
    depends_on:
      livekit:
        condition: service_healthy
      rabbitmq:
        condition: service_healthy
```

### 9.3 Migration Before Startup

**Key rule:** Migrations run as part of Django's entrypoint, BEFORE Gunicorn starts accepting traffic.

```dockerfile
# backend/Dockerfile

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
```

```bash
#!/bin/bash
# backend/entrypoint.sh

set -e

echo "Waiting for database..."
python manage.py wait_for_db

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers ${GUNICORN_WORKERS:-4} \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
```

---

## 10. Resource Limits (Production)

```yaml
# docker-compose.prod.yml — resource constraints

services:
  django:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 256M

  celery-worker:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 1G

  postgres:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G

  redis:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  livekit:
    deploy:
      resources:
        limits:
          cpus: '4.0'
          memory: 2G

  livekit-agent:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 1G
```

---

## 11. Environments

| Environment | Purpose | Infrastructure |
|-------------|---------|---------------|
| **Local (dev)** | Development | Docker Compose on developer machine, hot reload, debug mode |
| **Staging** | Pre-production testing | Single VPS, same stack as prod but smaller resources |
| **Production** | Live platform | VPS/cloud server, full monitoring, backups, SSL |

### Environment Parity

- All environments use Docker Compose with the same base `docker-compose.yml`
- Only overrides differ (ports, debug flags, resource limits, image sources)
- Developers run the full stack locally — no "works on my machine" issues

---

## 12. Useful Operational Commands

```bash
# Start monitoring locally
make up-monitoring

# Start monitoring on dev/prod compose stack
docker compose \
  -f docker-compose.yml \
  -f deploy/docker-compose.prod.yml \
  -f deploy/docker-compose.staging.yml \
  -f deploy/docker-compose.monitoring.yml \
  up -d grafana prometheus loki promtail jaeger

# Access remote Grafana securely from your machine
ssh -L 3000:127.0.0.1:3000 <user>@<server>
# Then open http://127.0.0.1:3000

# Access remote Jaeger securely from your machine
ssh -L 16686:127.0.0.1:16686 <user>@<server>
# Then open http://127.0.0.1:16686

# View logs for a specific service
docker compose logs -f django

# Execute Django management command
docker compose exec django python manage.py createsuperuser

# Run Django shell
docker compose exec django python manage.py shell_plus

# Run specific migration
docker compose exec django python manage.py migrate interviews 0003

# Backup database manually
docker compose exec postgres pg_dump -U $POSTGRES_USER $POSTGRES_DB > backup.sql

# Monitor container resource usage
docker stats

# Enter a container for debugging
docker compose exec django bash

# Restart a single service
docker compose restart celery-worker

# View RabbitMQ queues
docker compose exec rabbitmq rabbitmqctl list_queues

# Clear Redis cache
docker compose exec redis redis-cli FLUSHDB

# Check Celery task status
docker compose exec django celery -A config inspect active
```

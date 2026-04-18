.PHONY: help setup up down restart logs build \
       migrate makemigrations createsuperuser shell \
       lint format typecheck test \
       up-monitoring up-management up-all \
       clean reset-db backup-db ensure-env \
       local-setup local-infra local-backend local-backend-all local-frontend local-stop local-stop-all \
       local-test local-test-backend local-test-frontend local-test-e2e \
       local-telegram local-telegram-webhook

# Ensure a project-root .env exists so docker compose variable
# interpolation (LIVEKIT_API_KEY etc.) finds the values. On servers this
# symlink is created during provisioning; for local dev we auto-create it.
# No-op if .env already exists.
ensure-env:
	@if [ ! -e .env ]; then \
		if [ -e backend/.env ]; then \
			ln -s backend/.env .env; \
			echo "Created .env -> backend/.env symlink for docker compose."; \
		else \
			echo "ERROR: backend/.env not found. Run 'make local-setup' or copy backend/.env.example."; \
			exit 1; \
		fi; \
	fi

# ─── General ──────────────────────────────────────────────────────────────────

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ─── Setup ────────────────────────────────────────────────────────────────────

setup: ## First-time setup: copy env, build images, start services, run migrations
	@test -f backend/.env || cp backend/.env.example backend/.env
	@test -f frontend/.env || cp frontend/.env.example frontend/.env
	@$(MAKE) ensure-env
	@echo "✅ .env files ready (edit backend/.env and frontend/.env)"
	docker compose build
	docker compose up -d
	@echo "⏳ Waiting for services to be healthy..."
	@sleep 10
	docker compose exec django python manage.py migrate --noinput
	docker compose exec django python manage.py collectstatic --noinput
	@echo ""
	@echo "🚀 HR PreScan is running!"
	@echo "   Frontend:  http://localhost:5173"
	@echo "   Backend:   http://localhost:8000"
	@echo "   API docs:  http://localhost:8000/api/health/"
	@echo "   RabbitMQ:  http://localhost:15672 (guest/guest)"
	@echo "   MinIO:     http://localhost:9001 (minioadmin/minioadmin)"
	@echo ""
	@echo "Run 'make createsuperuser' to create an admin account."

# ─── Docker ───────────────────────────────────────────────────────────────────

up: ensure-env ## Start all dev services
	docker compose up -d

down: ## Stop all services
	docker compose down

restart: ## Restart all services
	docker compose restart

build: ## Rebuild Docker images
	docker compose build

logs: ## Tail logs for all services
	docker compose logs -f

logs-django: ## Tail Django logs
	docker compose logs -f django

logs-celery: ## Tail Celery worker logs
	docker compose logs -f celery-worker

logs-agent: ## Tail LiveKit agent logs
	docker compose logs -f livekit-agent

# ─── Django Management ────────────────────────────────────────────────────────

migrate: ## Run Django migrations
	docker compose exec django python manage.py migrate

makemigrations: ## Create new migrations
	docker compose exec django python manage.py makemigrations

createsuperuser: ## Create Django superuser (admin)
	docker compose exec django python manage.py createsuperuser

shell: ## Open Django shell
	docker compose exec django python manage.py shell

dbshell: ## Open database shell
	docker compose exec postgres psql -U $${POSTGRES_USER:-hr_prescan} -d $${POSTGRES_DB:-hr_prescan}

# ─── Code Quality ─────────────────────────────────────────────────────────────

lint: ## Run linters (backend + frontend)
	cd backend && ruff check .
	cd frontend && npm run lint:check

format: ## Auto-format code (backend + frontend)
	cd backend && ruff format . && ruff check --fix .
	cd frontend && npm run format

typecheck: ## Run type checks (backend + frontend)
	cd backend && mypy .
	cd frontend && npm run typecheck

# ─── Optional Service Stacks ─────────────────────────────────────────────────

PROD_COMPOSE = -f docker-compose.yml -f deploy/docker-compose.prod.yml
MON_COMPOSE  = -f docker-compose.yml -f docker-compose.override.yml -f deploy/docker-compose.monitoring.yml
MGMT_COMPOSE = -f docker-compose.yml -f docker-compose.override.yml -f deploy/docker-compose.management.yml

up-monitoring: ## Start monitoring stack (Grafana, Prometheus, Jaeger, Loki)
	docker compose $(MON_COMPOSE) up -d

up-management: ## Start management UIs (Portainer, pgAdmin, RedisInsight)
	docker compose $(MGMT_COMPOSE) up -d

up-all: ## Start everything (dev + monitoring + management)
	docker compose -f docker-compose.yml -f docker-compose.override.yml -f deploy/docker-compose.monitoring.yml -f deploy/docker-compose.management.yml up -d

up-prod: ## Start production stack
	docker compose $(PROD_COMPOSE) up -d

# ─── Database ─────────────────────────────────────────────────────────────────

backup-db: ## Backup database
	./deploy/scripts/backup-db.sh

reset-db: ## Reset database (destructive!)
	@echo "⚠️  This will delete all data. Press Ctrl+C to cancel."
	@sleep 3
	docker compose down -v
	docker compose up -d postgres redis rabbitmq minio
	@sleep 5
	docker compose up -d
	@sleep 10
	docker compose exec django python manage.py migrate --noinput

# ─── Local Dev (native Django + Celery + Vite, infra in Docker) ─────────────

VENV = $(CURDIR)/backend/.venv/bin

local-setup: ## First-time local dev setup: venv, deps, infra, migrate
	@test -f backend/.env || cp backend/.env.example backend/.env
	@test -f frontend/.env || cp frontend/.env.example frontend/.env
	docker compose up -d postgres redis rabbitmq minio livekit
	@test -d backend/.venv || python3 -m venv backend/.venv
	$(VENV)/pip install -r backend/requirements.txt
	cd frontend && npm install
	@echo "Waiting for Postgres to be ready..."
	@until docker compose exec -T postgres pg_isready -U hr_prescan 2>/dev/null; do sleep 1; done
	$(MAKE) local-migrate
	@echo ""
	@echo "Local dev ready! Run:"
	@echo "  make local-all       # Start everything (backend + celery + frontend)"
	@echo "  make local-backend-all  # Django + Celery worker + Celery beat (no frontend)"
	@echo "  make local-backend   # Django only on :8000"
	@echo "  make local-frontend  # Vite only on :5173"

local-infra: ensure-env ## Start only infra in Docker (stop app containers to free ports)
	-@docker compose stop django celery-worker celery-beat frontend nginx 2>/dev/null || true
	docker compose up -d postgres redis rabbitmq minio livekit

local-backend: ## Run Django dev server natively
	cd backend && $(VENV)/python manage.py runserver 0.0.0.0:8000

local-celery: ## Run Celery worker natively
	cd backend && $(VENV)/celery -A config worker -l info --concurrency=2

local-celery-beat: ## Run Celery beat natively
	cd backend && $(VENV)/celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler

local-frontend: ## Run Vite dev server natively
	cd frontend && npm run dev

local-backend-all: local-infra ## Start infra + Django + Celery worker + Celery beat
	@echo "Starting infra containers..."
	@sleep 3
	@echo "Running migrations..."
	@cd backend && $(VENV)/python manage.py migrate --noinput
	@echo "Starting Django server..."
	@cd backend && $(VENV)/python manage.py runserver 0.0.0.0:8000 &
	@echo "Starting Celery worker..."
	@cd backend && $(VENV)/celery -A config worker -l info --concurrency=2 &
	@echo "Starting Celery beat..."
	@cd backend && $(VENV)/celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler &
	@echo ""
	@echo "Backend services started in background:"
	@echo "  Django:   http://localhost:8000"
	@echo "  Celery:   worker + beat"
	@echo "  RabbitMQ: http://localhost:15672"
	@echo "  MinIO:    http://localhost:9001"
	@echo ""
	@echo "Run 'make local-stop' to stop everything."

local-all: local-infra ## Start infra + backend + celery + frontend (all in background)
	@echo "Starting infra containers..."
	@sleep 3
	@echo "Starting Django server..."
	@cd backend && $(VENV)/python manage.py runserver 0.0.0.0:8000 &
	@echo "Starting Celery worker..."
	@cd backend && $(VENV)/celery -A config worker -l info --concurrency=2 &
	@echo "Starting Vite dev server..."
	@cd frontend && npm run dev &
	@echo ""
	@echo "All services started in background:"
	@echo "  Django:   http://localhost:8000"
	@echo "  Vite:     http://localhost:5173"
	@echo "  RabbitMQ: http://localhost:15672"
	@echo "  MinIO:    http://localhost:9001"
	@echo ""
	@echo "Run 'make local-stop' to stop everything."

local-pip: ## Install Python dependencies (local)
	$(VENV)/pip install -r backend/requirements.txt

local-migrate: ## Run migrations (local)
	cd backend && $(VENV)/python manage.py migrate

local-makemigrations: ## Create migrations (local)
	cd backend && $(VENV)/python manage.py makemigrations

local-createsuperuser: ## Create superuser (local)
	cd backend && $(VENV)/python manage.py createsuperuser

local-shell: ## Django shell (local)
	cd backend && $(VENV)/python manage.py shell

local-telegram: local-telegram-hr ## Run HR Telegram bot in polling mode (alias)

local-telegram-hr: ## Run HR Telegram bot in polling mode (local dev)
	cd backend && $(VENV)/python manage.py run_telegram_bot --role hr

local-telegram-candidate: ## Run Candidate Telegram bot in polling mode (local dev)
	cd backend && $(VENV)/python manage.py run_telegram_bot --role candidate

local-telegram-webhook: ## Start ngrok tunnel + register Telegram webhook (local dev)
	./deploy/scripts/telegram-ngrok.sh 8000

local-stop: ## Stop everything (infra + background processes)
	@echo "Stopping background processes..."
	-@pkill -f "manage.py runserver" 2>/dev/null || true
	-@pkill -f "celery -A config worker" 2>/dev/null || true
	-@pkill -f "celery -A config beat" 2>/dev/null || true
	-@pkill -f "vite" 2>/dev/null || true
	docker compose down
	@echo "All stopped."

local-stop-all: ## Force-kill all local backend/frontend processes + stop Docker
	@echo "Force-killing all processes..."
	-@pkill -9 -f "manage.py runserver" 2>/dev/null && echo "  Django stopped" || true
	-@pkill -9 -f "celery -A config" 2>/dev/null && echo "  Celery worker stopped" || true
	-@pkill -9 -f "celery.*config" 2>/dev/null && echo "  Celery beat stopped" || true
	-@pkill -9 -f "vite" 2>/dev/null && echo "  Vite stopped" || true
	-@pkill -9 -f "node.*frontend" 2>/dev/null && echo "  Node frontend stopped" || true
	-@lsof -ti :8000 | xargs kill -9 2>/dev/null && echo "  Port 8000 freed" || true
	-@lsof -ti :5173 | xargs kill -9 2>/dev/null && echo "  Port 5173 freed" || true
	docker compose down
	@echo "All force-stopped."

# ─── Testing (local) ─────────────────────────────────────────────────────────

local-test: local-test-backend local-test-frontend ## Run all tests (backend + frontend)

local-test-backend: ## Run backend tests (pytest)
	cd backend && $(VENV)/python -m pytest tests/ -v --tb=short

local-test-frontend: ## Run frontend unit tests (vitest)
	cd frontend && npx vitest run --reporter=verbose

local-test-e2e: ## Run all E2E tests (playwright) — app must be running
	cd e2e && .venv/bin/python -m pytest -v

local-test-e2e-api: ## Run E2E API tests only — backend must be running
	cd e2e && .venv/bin/python -m pytest api/ -v

local-test-e2e-ui: ## Run E2E UI tests only — app must be running
	cd e2e && .venv/bin/python -m pytest ui/ -v

# ─── Dev Server DB Tunnel ────────────────────────────────────────────────────
# Creds live in .env.dev-server (gitignored). See .env.dev-server.example for keys.

DEV_ENV_FILE = .env.dev-server

define DEV_SSH_CMD
set -a; . $(DEV_ENV_FILE); set +a; \
SSHPASS="$$DEV_SSH_PASS" sshpass -e ssh -o StrictHostKeyChecking=accept-new
endef

dev-db-tunnel: ## Open SSH tunnel to dev Postgres (localhost:$$DEV_PG_LOCAL_PORT)
	@test -f $(DEV_ENV_FILE) || { echo "Missing $(DEV_ENV_FILE) (copy from .env.dev-server.example)"; exit 1; }
	@command -v sshpass >/dev/null || { echo "sshpass not installed: brew install sshpass"; exit 1; }
	@set -a; . $(DEV_ENV_FILE); set +a; \
	IP=$$(SSHPASS="$$DEV_SSH_PASS" sshpass -e ssh -o StrictHostKeyChecking=accept-new $$DEV_SSH_USER@$$DEV_SSH_HOST \
	  "docker inspect $$DEV_PG_CONTAINER --format '{{(index .NetworkSettings.Networks \"'$$DEV_PG_NETWORK'\").IPAddress}}'"); \
	if [ -z "$$IP" ]; then echo "Could not resolve postgres container IP"; exit 1; fi; \
	SSHPASS="$$DEV_SSH_PASS" sshpass -e ssh -fN -o StrictHostKeyChecking=accept-new \
	  -L $$DEV_PG_LOCAL_PORT:$$IP:5432 $$DEV_SSH_USER@$$DEV_SSH_HOST; \
	echo "Tunnel open on localhost:$$DEV_PG_LOCAL_PORT"; \
	echo "  host=localhost port=$$DEV_PG_LOCAL_PORT user=$$DEV_PG_USER db=$$DEV_PG_DB"

dev-db-tunnel-stop: ## Close SSH tunnel to dev Postgres
	@set -a; . $(DEV_ENV_FILE); set +a; \
	pkill -f "ssh -fN .* -L $$DEV_PG_LOCAL_PORT:" 2>/dev/null && echo "Tunnel closed." || echo "No tunnel running."

# ─── Cleanup ──────────────────────────────────────────────────────────────────

clean: ## Remove containers, volumes, and built images
	docker compose down -v --rmi local

.PHONY: help setup up down restart logs build \
       migrate makemigrations createsuperuser shell \
       lint format typecheck test \
       up-monitoring up-management up-all \
       clean reset-db backup-db

# ─── General ──────────────────────────────────────────────────────────────────

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ─── Setup ────────────────────────────────────────────────────────────────────

setup: ## First-time setup: copy env, build images, start services, run migrations
	@test -f .env || cp .env.example .env
	@echo "✅ .env file ready (edit it with your API keys)"
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

up: ## Start all dev services
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

up-monitoring: ## Start monitoring stack (Grafana, Prometheus, Jaeger, Loki)
	docker compose -f docker-compose.yml -f docker-compose.override.yml -f docker-compose.monitoring.yml up -d

up-management: ## Start management UIs (Portainer, pgAdmin, RedisInsight)
	docker compose -f docker-compose.yml -f docker-compose.override.yml -f docker-compose.management.yml up -d

up-all: ## Start everything (dev + monitoring + management)
	docker compose -f docker-compose.yml -f docker-compose.override.yml -f docker-compose.monitoring.yml -f docker-compose.management.yml up -d

# ─── Database ─────────────────────────────────────────────────────────────────

backup-db: ## Backup database
	./scripts/backup-db.sh

reset-db: ## Reset database (destructive!)
	@echo "⚠️  This will delete all data. Press Ctrl+C to cancel."
	@sleep 3
	docker compose down -v
	docker compose up -d postgres redis rabbitmq minio
	@sleep 5
	docker compose up -d
	@sleep 10
	docker compose exec django python manage.py migrate --noinput

# ─── Cleanup ──────────────────────────────────────────────────────────────────

clean: ## Remove containers, volumes, and built images
	docker compose down -v --rmi local

"""
Celery application configuration for HR PreScan.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from backend/ directory (same as manage.py)
env_file = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_file)

from celery import Celery
from dotenv import load_dotenv

# Load backend/.env when running natively (celery bypasses manage.py, which
# normally handles this). In Docker / prod, env vars are already in the
# environment and load_dotenv is a no-op.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("hr_prescan")

# Read config from Django settings, using the CELERY_ namespace.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks in all installed apps.
app.autodiscover_tasks()

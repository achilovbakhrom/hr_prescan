"""
Celery application configuration for HR PreScan.
"""

import os
from pathlib import Path

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

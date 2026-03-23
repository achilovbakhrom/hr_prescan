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

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("hr_prescan")

# Read config from Django settings, using the CELERY_ namespace.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks in all installed apps.
app.autodiscover_tasks()

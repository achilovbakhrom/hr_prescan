"""
Base Django settings for HR PreScan.

Shared settings used across all environments.
Environment-specific values are read from environment variables.
"""

import os
from datetime import timedelta
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-change-me-in-production",
)

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    # Third-party
    "rest_framework",
    "corsheaders",
    "django_prometheus",
    "storages",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "django_celery_beat",
    "drf_spectacular",
    # Local
    "apps.common",
    "apps.accounts",
    "apps.vacancies",
    "apps.applications",
    "apps.interviews",
    "apps.notifications",
    "apps.subscriptions",
    "apps.integrations",
]

MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.common.middleware.CompanyMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database — PostgreSQL
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "hr_prescan"),
        "USER": os.environ.get("POSTGRES_USER", "postgres"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "postgres"),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        "ATOMIC_REQUESTS": True,
    }
}

# Cache — Redis
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# Celery — RabbitMQ broker, Redis result backend
CELERY_BROKER_URL = os.environ.get(
    "RABBITMQ_URL", "amqp://guest:guest@localhost:5672//"
)
CELERY_RESULT_BACKEND = os.environ.get("REDIS_URL", "redis://localhost:6379/1")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"

from celery.schedules import crontab  # noqa: E402

CELERY_BEAT_SCHEDULE = {
    "check-expired-trials": {
        "task": "apps.subscriptions.tasks.check_expired_trials",
        "schedule": crontab(hour=0, minute=15),
    },
}

# MinIO / S3 storage
AWS_ACCESS_KEY_ID = os.environ.get("MINIO_ACCESS_KEY", "")
AWS_SECRET_ACCESS_KEY = os.environ.get("MINIO_SECRET_KEY", "")
AWS_STORAGE_BUCKET_NAME = os.environ.get("MINIO_BUCKET_NAME", "hr-prescan")
AWS_S3_ENDPOINT_URL = os.environ.get("MINIO_ENDPOINT", "http://localhost:9000")
AWS_S3_REGION_NAME = os.environ.get("AWS_S3_REGION_NAME", "us-east-1")
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None

# Django REST Framework
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "apps.common.pagination.StandardPagination",
    "PAGE_SIZE": 20,
    "EXCEPTION_HANDLER": "rest_framework.views.exception_handler",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_RATES": {
        "auth": "10/minute",
        "ai_scoring": "20/hour",
        "file_upload": "30/hour",
    },
}

# drf-spectacular — OpenAPI / Swagger
SPECTACULAR_SETTINGS = {
    "TITLE": "HR PreScan API",
    "DESCRIPTION": "AI-powered candidate pre-screening platform API",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Custom user model
AUTH_USER_MODEL = "accounts.User"

# CORS
CORS_ALLOWED_ORIGINS = os.environ.get(
    "CORS_ALLOWED_ORIGINS", "http://localhost:3000"
).split(",")

# Internationalization
LANGUAGE_CODE = "en"
USE_I18N = True
USE_L10N = True
TIME_ZONE = "UTC"
USE_TZ = True

LANGUAGES = [
    ("en", "English"),
    ("ru", "Russian"),
    ("uz", "Uzbek"),
]

LOCALE_PATHS = [
    BASE_DIR / "locale",
]

# Static files
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Logging — structured JSON for production; plain text for local
# Falls back gracefully if python-json-logger is not installed.
# ---------------------------------------------------------------------------
_USE_JSON_LOGS = os.environ.get("USE_JSON_LOGS", "false").lower() == "true"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[%(asctime)s] %(levelname)-8s %(name)s: %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s %(pathname)s %(lineno)d",
            "rename_fields": {"asctime": "timestamp", "levelname": "level"},
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json" if _USE_JSON_LOGS else "verbose",
        },
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": os.environ.get("DJANGO_LOG_LEVEL", "INFO"),
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console"],
            "level": os.environ.get("DJANGO_LOG_LEVEL", "DEBUG"),
            "propagate": False,
        },
        # Silence noisy libraries
        "urllib3": {"handlers": ["null"], "propagate": False},
        "botocore": {"handlers": ["null"], "propagate": False},
        "s3transfer": {"handlers": ["null"], "propagate": False},
    },
}

# Simple JWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# Google OAuth
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")

# Google Gemini
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3-flash-preview")

# Telegram bots
# Two separate bots: one for HRs (manage vacancies, candidates, etc.) and one
# for candidates (browse jobs, apply, take prescan interview). Each needs its
# own token/username/webhook secret. The legacy single-bot env vars
# (TELEGRAM_BOT_TOKEN/USERNAME/WEBHOOK_SECRET/WEBHOOK_URL) remain readable as a
# fallback for the HR bot so existing deployments keep working.
TELEGRAM_HR_BOT_TOKEN = os.environ.get(
    "TELEGRAM_HR_BOT_TOKEN", os.environ.get("TELEGRAM_BOT_TOKEN", ""),
)
TELEGRAM_HR_BOT_USERNAME = os.environ.get(
    "TELEGRAM_HR_BOT_USERNAME", os.environ.get("TELEGRAM_BOT_USERNAME", ""),
)
TELEGRAM_HR_WEBHOOK_SECRET = os.environ.get(
    "TELEGRAM_HR_WEBHOOK_SECRET", os.environ.get("TELEGRAM_WEBHOOK_SECRET", ""),
)
TELEGRAM_HR_WEBHOOK_URL = os.environ.get(
    "TELEGRAM_HR_WEBHOOK_URL", os.environ.get("TELEGRAM_WEBHOOK_URL", ""),
)

TELEGRAM_CANDIDATE_BOT_TOKEN = os.environ.get("TELEGRAM_CANDIDATE_BOT_TOKEN", "")
TELEGRAM_CANDIDATE_BOT_USERNAME = os.environ.get("TELEGRAM_CANDIDATE_BOT_USERNAME", "")
TELEGRAM_CANDIDATE_WEBHOOK_SECRET = os.environ.get("TELEGRAM_CANDIDATE_WEBHOOK_SECRET", "")
TELEGRAM_CANDIDATE_WEBHOOK_URL = os.environ.get("TELEGRAM_CANDIDATE_WEBHOOK_URL", "")

# Token used by the Telegram Login Widget on the candidate web auth pages.
# Prefers the candidate bot, falls back to HR bot for backwards-compat.
TELEGRAM_LOGIN_WIDGET_TOKEN = (
    TELEGRAM_CANDIDATE_BOT_TOKEN or TELEGRAM_HR_BOT_TOKEN
)

# Frontend URL (for Telegram bot "Open website" button, etc.)
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")

# Email
EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True").lower() in ("true", "1")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "PreScreen AI <noreply@prescreenai.com>")

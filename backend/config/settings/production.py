"""
Production settings for HR PreScan.

Extends base settings with:
- Security hardening (SSL, HSTS, CSP)
- DRF throttling
- Connection pooling
- OpenTelemetry / Jaeger tracing
- Structured JSON logging
"""

import os

from config.settings.base import *

# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------
DEBUG = False

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")

# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_TRUSTED_ORIGINS = os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")
X_FRAME_OPTIONS = "DENY"

# ---------------------------------------------------------------------------
# Database — persistent connections for production
# ---------------------------------------------------------------------------
DATABASES["default"]["CONN_MAX_AGE"] = 60  # seconds  # noqa: F405
DATABASES["default"]["OPTIONS"] = {  # noqa: F405
    "connect_timeout": 10,
    "application_name": "hr_prescan",
}

# ---------------------------------------------------------------------------
# Cache — tune for production
# ---------------------------------------------------------------------------
CACHES["default"]["OPTIONS"].update(  # noqa: F405
    {
        "SOCKET_CONNECT_TIMEOUT": 5,
        "SOCKET_TIMEOUT": 5,
        "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
        "CONNECTION_POOL_KWARGS": {"max_connections": 50},
    }
)

# ---------------------------------------------------------------------------
# Django REST Framework — throttling
# ---------------------------------------------------------------------------
REST_FRAMEWORK.update(  # noqa: F405
    {
        "DEFAULT_THROTTLE_CLASSES": [
            "rest_framework.throttling.AnonRateThrottle",
            "rest_framework.throttling.UserRateThrottle",
        ],
        "DEFAULT_THROTTLE_RATES": {
            "anon": "60/minute",
            "user": "300/minute",
        },
    }
)

# ---------------------------------------------------------------------------
# Static / Media — media uses S3/MinIO; nginx proxies static admin assets to Django.
# ---------------------------------------------------------------------------
SERVE_STATIC_VIA_DJANGO = os.environ.get("SERVE_STATIC_VIA_DJANGO", "true").lower() == "true"

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# ---------------------------------------------------------------------------
# OpenTelemetry — Jaeger OTLP export
# ---------------------------------------------------------------------------
OTEL_ENABLED = os.environ.get("OTEL_ENABLED", "true").lower() == "true"
OTEL_SERVICE_NAME = os.environ.get("OTEL_SERVICE_NAME", "hr-prescan-backend")
OTEL_EXPORTER_OTLP_ENDPOINT = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://jaeger:4317")

if OTEL_ENABLED:
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.instrumentation.celery import CeleryInstrumentor
        from opentelemetry.instrumentation.django import DjangoInstrumentor
        from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
        from opentelemetry.instrumentation.redis import RedisInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        _resource = Resource.create({"service.name": OTEL_SERVICE_NAME})
        _provider = TracerProvider(resource=_resource)
        _exporter = OTLPSpanExporter(endpoint=OTEL_EXPORTER_OTLP_ENDPOINT)
        _provider.add_span_processor(BatchSpanProcessor(_exporter))
        trace.set_tracer_provider(_provider)

        DjangoInstrumentor().instrument()
        Psycopg2Instrumentor().instrument()
        RedisInstrumentor().instrument()
        CeleryInstrumentor().instrument()

    except ImportError:
        import logging as _logging

        _logging.getLogger(__name__).warning("OpenTelemetry packages not installed — tracing disabled.")

# ---------------------------------------------------------------------------
# Structured JSON logging (production)
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
            "rename_fields": {"asctime": "timestamp", "levelname": "level"},
        },
        "verbose": {
            "format": "[%(asctime)s] %(levelname)s %(name)s %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        },
    },
    "handlers": {
        "console_json": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console_json"],
            "level": os.environ.get("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "django": {
            "handlers": ["console_json"],
            "level": "INFO",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["console_json"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console_json"],
            "level": "ERROR",
            "propagate": False,
        },
        # Silence noisy third-party loggers
        "urllib3": {
            "handlers": ["null"],
            "propagate": False,
        },
        "botocore": {
            "handlers": ["null"],
            "propagate": False,
        },
    },
}

"""
Local development settings for HR PreScan.
"""

from config.settings.base import *

DEBUG = True

ALLOWED_HOSTS = ["*"]

# CORS — allow everything in development
CORS_ALLOW_ALL_ORIGINS = True

# Add browsable API renderer in development
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [  # type: ignore[name-defined]  # noqa: F405
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
]

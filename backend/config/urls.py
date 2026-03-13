"""
Root URL configuration for HR PreScan.
"""

from django.contrib import admin
from django.http import JsonResponse
from django.urls import path


def health_check(request):
    """Simple health check endpoint."""
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check, name="health-check"),
]

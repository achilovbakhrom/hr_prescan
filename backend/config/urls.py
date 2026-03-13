"""
Root URL configuration for HR PreScan.
"""

from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

from apps.accounts.urls import hr_urlpatterns
from apps.vacancies.urls import hr_urlpatterns as vacancy_hr_urlpatterns
from apps.vacancies.urls import public_urlpatterns as vacancy_public_urlpatterns


def health_check(request):
    """Simple health check endpoint."""
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check, name="health-check"),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/hr/company/", include((hr_urlpatterns, "hr"))),
    path("api/hr/vacancies/", include((vacancy_hr_urlpatterns, "hr-vacancies"))),
    path("api/public/vacancies/", include((vacancy_public_urlpatterns, "public-vacancies"))),
]

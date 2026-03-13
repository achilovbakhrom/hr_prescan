"""
Root URL configuration for HR PreScan.
"""

from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

from apps.accounts.urls import hr_urlpatterns
from apps.applications.urls import (
    candidate_urlpatterns as application_candidate_urlpatterns,
    hr_candidate_urlpatterns as application_hr_candidate_urlpatterns,
    hr_vacancy_urlpatterns as application_hr_vacancy_urlpatterns,
    public_urlpatterns as application_public_urlpatterns,
)
from apps.interviews.urls import (
    candidate_urlpatterns as interview_candidate_urlpatterns,
    hr_candidate_urlpatterns as interview_hr_candidate_urlpatterns,
    hr_interview_urlpatterns,
)
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
    path("api/hr/vacancies/", include((application_hr_vacancy_urlpatterns, "hr-applications"))),
    path("api/hr/candidates/", include((application_hr_candidate_urlpatterns, "hr-candidates"))),
    path("api/hr/candidates/", include((interview_hr_candidate_urlpatterns, "hr-interview-schedule"))),
    path("api/hr/interviews/", include((hr_interview_urlpatterns, "hr-interviews"))),
    path("api/public/vacancies/", include((vacancy_public_urlpatterns, "public-vacancies"))),
    path("api/public/vacancies/", include((application_public_urlpatterns, "public-applications"))),
    path("api/candidate/", include((application_candidate_urlpatterns, "candidate"))),
    path("api/candidate/", include((interview_candidate_urlpatterns, "candidate-interviews"))),
]

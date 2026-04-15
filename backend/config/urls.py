"""
Root URL configuration for HR PreScan.
"""

from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from apps.accounts.apis import PublicCvViewApi
from apps.accounts.urls import candidate_profile_urlpatterns, hr_urlpatterns
from apps.applications.urls import (
    candidate_urlpatterns as application_candidate_urlpatterns,
)
from apps.applications.urls import (
    hr_candidate_urlpatterns as application_hr_candidate_urlpatterns,
)
from apps.applications.urls import (
    hr_vacancy_urlpatterns as application_hr_vacancy_urlpatterns,
)
from apps.applications.urls import (
    public_urlpatterns as application_public_urlpatterns,
)
from apps.common.apis import HRDashboardApi
from apps.common.apis_ai import AIAssistantApi
from apps.common.apis_candidate_ai import CandidateAIAssistantApi
from apps.common.apis_candidate_dashboard import CandidateDashboardApi
from apps.common.apis_country import CountryListApi
from apps.common.apis_education_level import EducationLevelListApi
from apps.common.apis_hr_analytics import HRAnalyticsApi
from apps.common.apis_industry import IndustryListApi
from apps.common.apis_language import LanguageListApi
from apps.common.apis_search import HRGlobalSearchApi
from apps.common.apis_skill import SkillListApi
from apps.common.apis_translate import BatchTranslateApi, TranslateAIContentApi
from apps.common.urls_admin import admin_urlpatterns
from apps.integrations.urls import (
    hr_telegram_urlpatterns,
    telegram_urlpatterns,
)
from apps.interviews.urls import (
    candidate_urlpatterns as interview_candidate_urlpatterns,
)
from apps.interviews.urls import (
    hr_candidate_urlpatterns as interview_hr_candidate_urlpatterns,
)
from apps.interviews.urls import (
    hr_interview_urlpatterns,
)
from apps.interviews.urls import (
    public_urlpatterns as interview_public_urlpatterns,
)
from apps.notifications.urls import (
    candidate_urlpatterns as notification_candidate_urlpatterns,
)
from apps.notifications.urls import (
    hr_bulk_urlpatterns as notification_hr_bulk_urlpatterns,
)
from apps.notifications.urls import (
    hr_candidate_urlpatterns as notification_hr_candidate_urlpatterns,
)
from apps.notifications.urls import (
    notification_urlpatterns,
)
from apps.subscriptions.urls import (
    hr_urlpatterns as subscription_hr_urlpatterns,
)
from apps.subscriptions.urls import (
    public_urlpatterns as subscription_public_urlpatterns,
)
from apps.vacancies.urls import employer_urlpatterns as employer_hr_urlpatterns
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
    path("api/hr/employers/", include((employer_hr_urlpatterns, "hr-employers"))),
    path("api/hr/vacancies/", include((vacancy_hr_urlpatterns, "hr-vacancies"))),
    path("api/hr/vacancies/", include((application_hr_vacancy_urlpatterns, "hr-applications"))),
    path("api/hr/candidates/", include((application_hr_candidate_urlpatterns, "hr-candidates"))),
    path("api/hr/candidates/", include((interview_hr_candidate_urlpatterns, "hr-interview-schedule"))),
    path("api/hr/candidates/", include((notification_hr_candidate_urlpatterns, "hr-messaging"))),
    path("api/hr/candidates/", include((notification_hr_bulk_urlpatterns, "hr-bulk-actions"))),
    path("api/hr/interviews/", include((hr_interview_urlpatterns, "hr-interviews"))),
    path("api/hr/dashboard/", HRDashboardApi.as_view(), name="hr-dashboard"),
    path("api/hr/search/", HRGlobalSearchApi.as_view(), name="hr-search"),
    path("api/hr/ai-assistant/", AIAssistantApi.as_view(), name="hr-ai-assistant"),
    path("api/hr/analytics/", HRAnalyticsApi.as_view(), name="hr-analytics"),
    path("api/hr/translate/", TranslateAIContentApi.as_view(), name="hr-translate"),
    path("api/hr/translate/batch/", BatchTranslateApi.as_view(), name="hr-translate-batch"),
    path("api/notifications/", include((notification_urlpatterns, "notifications"))),
    path("api/public/countries/", CountryListApi.as_view(), name="public-countries"),
    path("api/public/industries/", IndustryListApi.as_view(), name="public-industries"),
    path("api/public/skills/", SkillListApi.as_view(), name="public-skills"),
    path("api/public/languages/", LanguageListApi.as_view(), name="public-languages"),
    path("api/public/education-levels/", EducationLevelListApi.as_view(), name="public-education-levels"),
    path("api/cv/<str:token>/", PublicCvViewApi.as_view(), name="public-cv-view"),
    path("api/public/vacancies/", include((vacancy_public_urlpatterns, "public-vacancies"))),
    path("api/public/vacancies/", include((application_public_urlpatterns, "public-applications"))),
    path("api/public/", include((interview_public_urlpatterns, "public-interviews"))),
    path("api/candidate/ai-assistant/", CandidateAIAssistantApi.as_view(), name="candidate-ai-assistant"),
    path("api/candidate/dashboard/", CandidateDashboardApi.as_view(), name="candidate-dashboard"),
    path("api/candidate/profile/", include((candidate_profile_urlpatterns, "candidate-profile"))),
    path("api/candidate/", include((application_candidate_urlpatterns, "candidate"))),
    path("api/candidate/", include((interview_candidate_urlpatterns, "candidate-interviews"))),
    path("api/candidate/", include((notification_candidate_urlpatterns, "candidate-messages"))),
    # Subscriptions
    path("api/subscriptions/", include((subscription_public_urlpatterns, "subscriptions"))),
    path("api/hr/subscription/", include((subscription_hr_urlpatterns, "hr-subscription"))),
    # Telegram integration
    path("api/telegram/", include((telegram_urlpatterns, "telegram"))),
    path("api/hr/telegram/", include((hr_telegram_urlpatterns, "hr-telegram"))),
    # Admin panel
    path("api/admin-panel/", include((admin_urlpatterns, "admin-panel"))),
    # API documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

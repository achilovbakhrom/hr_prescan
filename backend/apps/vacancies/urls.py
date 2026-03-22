from django.urls import path

from apps.vacancies.apis import (
    EmployerCompanyDetailApi,
    EmployerCompanyListCreateApi,
    GenerateQuestionsApi,
    ParseCompanyFileApi,
    ParseCompanyUrlApi,
    ParseEmployerFileApi,
    ParseEmployerUrlApi,
    PublicVacancyDetailApi,
    PublicVacancyListApi,
    VacancyCriteriaDetailApi,
    VacancyCriteriaListCreateApi,
    VacancyDetailApi,
    VacancyListCreateApi,
    VacancyQuestionDetailApi,
    VacancyQuestionListCreateApi,
    VacancyRegenerateKeywordsApi,
    VacancyStatusApi,
)

# HR URLs — mounted at /api/hr/vacancies/
hr_urlpatterns = [
    path("", VacancyListCreateApi.as_view(), name="vacancy-list-create"),
    path("parse-company-file/", ParseCompanyFileApi.as_view(), name="parse-company-file"),
    path("parse-company-url/", ParseCompanyUrlApi.as_view(), name="parse-company-url"),
    path("<uuid:vacancy_id>/", VacancyDetailApi.as_view(), name="vacancy-detail"),
    path("<uuid:vacancy_id>/status/", VacancyStatusApi.as_view(), name="vacancy-status"),
    path("<uuid:vacancy_id>/criteria/", VacancyCriteriaListCreateApi.as_view(), name="vacancy-criteria-list-create"),
    path(
        "<uuid:vacancy_id>/criteria/<uuid:criteria_id>/",
        VacancyCriteriaDetailApi.as_view(),
        name="vacancy-criteria-detail",
    ),
    path(
        "<uuid:vacancy_id>/questions/",
        VacancyQuestionListCreateApi.as_view(),
        name="vacancy-question-list-create",
    ),
    path(
        "<uuid:vacancy_id>/questions/<uuid:question_id>/",
        VacancyQuestionDetailApi.as_view(),
        name="vacancy-question-detail",
    ),
    path(
        "<uuid:vacancy_id>/questions/generate/",
        GenerateQuestionsApi.as_view(),
        name="vacancy-generate-questions",
    ),
    path(
        "<uuid:vacancy_id>/regenerate-keywords/",
        VacancyRegenerateKeywordsApi.as_view(),
        name="vacancy-regenerate-keywords",
    ),
]

# Employer URLs — mounted at /api/hr/employers/
employer_urlpatterns = [
    path("", EmployerCompanyListCreateApi.as_view(), name="employer-list-create"),
    path("<uuid:employer_id>/", EmployerCompanyDetailApi.as_view(), name="employer-detail"),
    path("parse-file/", ParseEmployerFileApi.as_view(), name="employer-parse-file"),
    path("parse-url/", ParseEmployerUrlApi.as_view(), name="employer-parse-url"),
]

# Public URLs — mounted at /api/public/vacancies/
public_urlpatterns = [
    path("", PublicVacancyListApi.as_view(), name="public-vacancy-list"),
    path("<uuid:vacancy_id>/", PublicVacancyDetailApi.as_view(), name="public-vacancy-detail"),
    path("share/<uuid:share_token>/", PublicVacancyDetailApi.as_view(), name="public-vacancy-share"),
]

from django.urls import path

from apps.vacancies.apis import (
    GenerateInstructionsApi,
    GenerateQuestionsApi,
    GenerateVacancyContentApi,
    ParseCompanyFileApi,
    ParseCompanyUrlApi,
    PublicVacancyDetailApi,
    PublicVacancyListApi,
    PublicVacancySitemapApi,
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
    path("generate-content/", GenerateVacancyContentApi.as_view(), name="vacancy-generate-content"),
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
        "<uuid:vacancy_id>/instructions/generate/",
        GenerateInstructionsApi.as_view(),
        name="vacancy-generate-instructions",
    ),
    path(
        "<uuid:vacancy_id>/regenerate-keywords/",
        VacancyRegenerateKeywordsApi.as_view(),
        name="vacancy-regenerate-keywords",
    ),
]

# Public URLs — mounted at /api/public/vacancies/
public_urlpatterns = [
    path("", PublicVacancyListApi.as_view(), name="public-vacancy-list"),
    path("sitemap.xml", PublicVacancySitemapApi.as_view(), name="public-vacancy-sitemap"),
    path("<uuid:vacancy_id>/", PublicVacancyDetailApi.as_view(), name="public-vacancy-detail"),
    path("share/<uuid:share_token>/", PublicVacancyDetailApi.as_view(), name="public-vacancy-share"),
]

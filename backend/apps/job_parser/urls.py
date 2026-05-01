from django.urls import path

from apps.job_parser.apis import (
    ParsedVacancyImportApi,
    ParsedVacancyListApi,
    ParsedVacancySourceListCreateApi,
    ParsedVacancySourceStopApi,
    ParsedVacancySourceSyncApi,
    ParsedVacancySourceSyncNowApi,
    TelegramMessageParseApi,
)

hr_urlpatterns = [
    path("sources/", ParsedVacancySourceListCreateApi.as_view(), name="source-list"),
    path("sources/<uuid:source_id>/sync/", ParsedVacancySourceSyncApi.as_view(), name="source-sync"),
    path("sources/<uuid:source_id>/sync-now/", ParsedVacancySourceSyncNowApi.as_view(), name="source-sync-now"),
    path("sources/<uuid:source_id>/stop/", ParsedVacancySourceStopApi.as_view(), name="source-stop"),
    path(
        "sources/<uuid:source_id>/telegram-message/",
        TelegramMessageParseApi.as_view(),
        name="telegram-message-parse",
    ),
    path("vacancies/", ParsedVacancyListApi.as_view(), name="parsed-vacancy-list"),
    path("vacancies/<uuid:vacancy_id>/import/", ParsedVacancyImportApi.as_view(), name="parsed-vacancy-import"),
]

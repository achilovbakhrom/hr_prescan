from django.urls import path

from apps.applications.apis import (
    CandidateApplicationDetailApi,
    CandidateApplicationListApi,
    HRApplicationDetailApi,
    HRApplicationListApi,
    HRApplicationNotesApi,
    HRApplicationStatusApi,
    HRBatchMoveApi,
    HRBulkStatusApi,
    HRCvDownloadApi,
    HRSoftDeleteApi,
    SubmitApplicationApi,
)

# Public URLs — mounted at /api/public/vacancies/
public_urlpatterns = [
    path(
        "<uuid:vacancy_id>/apply/",
        SubmitApplicationApi.as_view(),
        name="submit-application",
    ),
]

# Candidate URLs — mounted at /api/candidate/
candidate_urlpatterns = [
    path(
        "applications/",
        CandidateApplicationListApi.as_view(),
        name="candidate-application-list",
    ),
    path(
        "applications/<uuid:application_id>/",
        CandidateApplicationDetailApi.as_view(),
        name="candidate-application-detail",
    ),
]

# HR URLs — split between vacancy-scoped and direct candidate endpoints
# Vacancy-scoped: mounted at /api/hr/vacancies/
hr_vacancy_urlpatterns = [
    path(
        "<uuid:vacancy_id>/candidates/",
        HRApplicationListApi.as_view(),
        name="hr-application-list",
    ),
    path(
        "<uuid:vacancy_id>/candidates/batch-move/",
        HRBatchMoveApi.as_view(),
        name="hr-batch-move",
    ),
]

# Direct candidate endpoints: mounted at /api/hr/candidates/
hr_candidate_urlpatterns = [
    path(
        "bulk-status/",
        HRBulkStatusApi.as_view(),
        name="hr-bulk-status",
    ),
    path(
        "soft-delete/",
        HRSoftDeleteApi.as_view(),
        name="hr-soft-delete",
    ),
    path(
        "<uuid:application_id>/",
        HRApplicationDetailApi.as_view(),
        name="hr-application-detail",
    ),
    path(
        "<uuid:application_id>/status/",
        HRApplicationStatusApi.as_view(),
        name="hr-application-status",
    ),
    path(
        "<uuid:application_id>/notes/",
        HRApplicationNotesApi.as_view(),
        name="hr-application-notes",
    ),
    path(
        "<uuid:application_id>/cv-download/",
        HRCvDownloadApi.as_view(),
        name="hr-cv-download",
    ),
]

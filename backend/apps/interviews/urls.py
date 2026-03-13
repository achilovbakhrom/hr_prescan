from django.urls import path

from apps.interviews.apis import (
    CancelInterviewApi,
    CandidateInterviewApi,
    CandidateScheduleApi,
    HRInterviewDetailApi,
    HRInterviewListApi,
    InterviewRecordingApi,
    InterviewTranscriptApi,
    ObserverTokenApi,
    ScheduleInterviewApi,
)

# HR candidate-scoped URLs — mounted at /api/hr/candidates/
hr_candidate_urlpatterns = [
    path(
        "<uuid:application_id>/schedule-interview/",
        ScheduleInterviewApi.as_view(),
        name="schedule-interview",
    ),
]

# HR interview URLs — mounted at /api/hr/interviews/
hr_interview_urlpatterns = [
    path(
        "",
        HRInterviewListApi.as_view(),
        name="hr-interview-list",
    ),
    path(
        "<uuid:interview_id>/",
        HRInterviewDetailApi.as_view(),
        name="hr-interview-detail",
    ),
    path(
        "<uuid:interview_id>/cancel/",
        CancelInterviewApi.as_view(),
        name="cancel-interview",
    ),
    path(
        "<uuid:interview_id>/observer-token/",
        ObserverTokenApi.as_view(),
        name="observer-token",
    ),
    path(
        "<uuid:interview_id>/transcript/",
        InterviewTranscriptApi.as_view(),
        name="interview-transcript",
    ),
    path(
        "<uuid:interview_id>/recording/",
        InterviewRecordingApi.as_view(),
        name="interview-recording",
    ),
]

# Candidate URLs — mounted at /api/candidate/
candidate_urlpatterns = [
    path(
        "schedule/<uuid:application_id>/",
        CandidateScheduleApi.as_view(),
        name="candidate-schedule",
    ),
    path(
        "interview/<uuid:interview_id>/",
        CandidateInterviewApi.as_view(),
        name="candidate-interview",
    ),
]

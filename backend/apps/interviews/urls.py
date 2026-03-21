from django.urls import path

from apps.interviews.apis import (
    CancelInterviewApi,
    CandidateInterviewApi,
    ChatHistoryApi,
    ChatMessageApi,
    HRApplicationInterviewApi,
    HRInterviewDetailApi,
    HRInterviewListApi,
    IntegrityFlagsApi,
    InterviewRecordingApi,
    InterviewRoomJoinApi,
    InterviewTranscriptApi,
    ObserverTokenApi,
    PublicInterviewApi,
    ResetInterviewApi,
    ScheduleHumanInterviewApi,
    StartInterviewApi,
)

# HR candidate-scoped URLs — mounted at /api/hr/candidates/
hr_candidate_urlpatterns = [
    path(
        "<uuid:application_id>/schedule-human-interview/",
        ScheduleHumanInterviewApi.as_view(),
        name="schedule-human-interview",
    ),
    path(
        "<uuid:application_id>/interview/",
        HRApplicationInterviewApi.as_view(),
        name="hr-application-interview",
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
        "<uuid:interview_id>/reset/",
        ResetInterviewApi.as_view(),
        name="reset-interview",
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
    path(
        "<uuid:interview_id>/integrity-flags/",
        IntegrityFlagsApi.as_view(),
        name="interview-integrity-flags",
    ),
]

# Public URLs — mounted at /api/public/
public_urlpatterns = [
    path(
        "interview/<uuid:interview_id>/join/",
        InterviewRoomJoinApi.as_view(),
        name="interview-room-join",
    ),
    path(
        "interview/<uuid:token>/",
        PublicInterviewApi.as_view(),
        name="public-interview",
    ),
    path(
        "interview/<uuid:token>/start/",
        StartInterviewApi.as_view(),
        name="start-interview",
    ),
    path(
        "interview/<uuid:token>/chat/",
        ChatMessageApi.as_view(),
        name="chat-message",
    ),
    path(
        "interview/<uuid:token>/chat/history/",
        ChatHistoryApi.as_view(),
        name="chat-history",
    ),
]

# Candidate URLs — mounted at /api/candidate/
candidate_urlpatterns = [
    path(
        "interview/<uuid:interview_id>/",
        CandidateInterviewApi.as_view(),
        name="candidate-interview",
    ),
]

"""Internal URL patterns for LiveKit agent communication.

Mounted at ``/api/internal/interviews/``.
"""

from django.urls import path

from apps.interviews.apis.internal import (
    InternalInterviewContextApi,
    InternalInterviewResultsApi,
)

urlpatterns = [
    path(
        "<uuid:interview_id>/context/",
        InternalInterviewContextApi.as_view(),
        name="internal-interview-context",
    ),
    path(
        "<uuid:interview_id>/results/",
        InternalInterviewResultsApi.as_view(),
        name="internal-interview-results",
    ),
]

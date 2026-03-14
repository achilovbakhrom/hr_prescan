from django.urls import path

from apps.notifications.apis import (
    BulkStatusUpdateApi,
    CandidateMessageListApi,
    HRMessageListApi,
    NotificationListApi,
    NotificationReadAllApi,
    NotificationReadApi,
    NotificationUnreadCountApi,
    SendCandidateEmailApi,
)

# Notification URLs — mounted at /api/notifications/
notification_urlpatterns = [
    path(
        "",
        NotificationListApi.as_view(),
        name="notification-list",
    ),
    path(
        "<uuid:notification_id>/read/",
        NotificationReadApi.as_view(),
        name="notification-read",
    ),
    path(
        "read-all/",
        NotificationReadAllApi.as_view(),
        name="notification-read-all",
    ),
    path(
        "unread-count/",
        NotificationUnreadCountApi.as_view(),
        name="notification-unread-count",
    ),
]

# HR candidate messaging — mounted at /api/hr/candidates/
hr_candidate_urlpatterns = [
    path(
        "<uuid:application_id>/messages/",
        HRMessageListApi.as_view(),
        name="hr-message-list",
    ),
    path(
        "<uuid:application_id>/email/",
        SendCandidateEmailApi.as_view(),
        name="send-candidate-email",
    ),
]

# Bulk actions — mounted at /api/hr/candidates/
hr_bulk_urlpatterns = [
    path(
        "bulk-status/",
        BulkStatusUpdateApi.as_view(),
        name="bulk-status-update",
    ),
]

# Candidate messaging — mounted at /api/candidate/
candidate_urlpatterns = [
    path(
        "messages/",
        CandidateMessageListApi.as_view(),
        name="candidate-message-list",
    ),
]

import logging

from apps.applications.models import Application
from apps.interviews.models import Interview

logger = logging.getLogger(__name__)


def enqueue_cv_processing(*, application: Application, cv_file_path: str, snapshot_applied: bool = False) -> None:
    if not cv_file_path and not snapshot_applied:
        return
    from django.db import transaction

    from apps.applications.tasks import calculate_cv_match, process_cv

    if cv_file_path:
        transaction.on_commit(lambda: process_cv.delay(str(application.id)))
    else:
        transaction.on_commit(lambda: calculate_cv_match.delay(str(application.id)))


def sync_candidate_base(*, application: Application) -> None:
    from django.db import transaction

    from apps.applications.services.candidate_base import sync_hr_candidate_for_application

    transaction.on_commit(lambda: sync_hr_candidate_for_application(application=application))


def notify_candidate_prescanning_ready(*, application: Application, prescan_session: Interview) -> None:
    from apps.notifications.services import (
        notify_candidate_prescanning_ready as _notify,
    )

    _notify(application=application, prescan_session=prescan_session)


def notify_hr_application_received(*, application: Application) -> None:
    """Notify the company's HR/owner of a new application (in-app + email).

    Runs after commit and is fully guarded: a notification failure must never
    break the apply transaction.
    """
    from django.db import transaction

    def _send() -> None:
        try:
            from apps.notifications.services import notify_application_received

            notify_application_received(application=application)
        except Exception as exc:
            logger.warning("Failed to send HR application-received notification: %s", exc)

    transaction.on_commit(_send)


def submission_result(*, application: Application, prescan_session: Interview) -> dict:
    interview_session = (
        application.sessions.filter(session_type=Interview.SessionType.INTERVIEW)
        .exclude(status=Interview.Status.CANCELLED)
        .order_by("-created_at")
        .first()
    )
    return {
        "application": application,
        "prescan_session": prescan_session,
        "prescan_token": str(prescan_session.interview_token),
        "interview_session": interview_session,
        "interview_token": str(interview_session.interview_token) if interview_session else None,
    }

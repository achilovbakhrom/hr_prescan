from uuid import UUID

from django.db import IntegrityError

from apps.accounts.models import User
from apps.applications.models import Application
from apps.common.exceptions import ApplicationError
from apps.common.messages import (
    MSG_ALREADY_APPLIED,
    MSG_CV_REQUIRED,
    MSG_STATUS_TRANSITION_INVALID,
    MSG_VACANCY_NOT_ACCEPTING,
    MSG_VACANCY_NOT_FOUND,
)
from apps.interviews.models import Interview
from apps.vacancies.models import Vacancy

# Valid status transitions: current_status -> set of allowed next statuses
STATUS_TRANSITIONS: dict[str, set[str]] = {
    Application.Status.APPLIED: {
        Application.Status.PRESCANNED,
        Application.Status.SHORTLISTED,
        Application.Status.HIRED,
        Application.Status.REJECTED,
        Application.Status.ARCHIVED,
        Application.Status.EXPIRED,
    },
    Application.Status.PRESCANNED: {
        Application.Status.INTERVIEWED,
        Application.Status.SHORTLISTED,
        Application.Status.HIRED,
        Application.Status.REJECTED,
        Application.Status.ARCHIVED,
        Application.Status.APPLIED,
        Application.Status.EXPIRED,
    },
    Application.Status.INTERVIEWED: {
        Application.Status.SHORTLISTED,
        Application.Status.HIRED,
        Application.Status.REJECTED,
        Application.Status.ARCHIVED,
        Application.Status.PRESCANNED,
    },
    Application.Status.SHORTLISTED: {
        Application.Status.HIRED,
        Application.Status.REJECTED,
        Application.Status.ARCHIVED,
        Application.Status.APPLIED,
    },
    Application.Status.HIRED: {
        Application.Status.ARCHIVED,
    },
    Application.Status.REJECTED: {
        Application.Status.APPLIED,
        Application.Status.ARCHIVED,
    },
    Application.Status.EXPIRED: {
        Application.Status.APPLIED,
        Application.Status.ARCHIVED,
    },
    Application.Status.ARCHIVED: {
        Application.Status.APPLIED,
    },
}


def submit_application(
    *,
    vacancy_id: UUID,
    candidate_name: str,
    candidate_email: str,
    candidate_phone: str = "",
    cv_file_path: str = "",
    cv_original_filename: str = "",
    candidate: User | None = None,
    channel: str = "web",
) -> dict:
    """Submit a new application to a vacancy.

    Creates the Application and a PENDING prescanning session immediately.
    Returns a dict with the application and prescanning session info.
    """
    try:
        vacancy = Vacancy.objects.get(id=vacancy_id)
    except Vacancy.DoesNotExist:
        raise ApplicationError(str(MSG_VACANCY_NOT_FOUND)) from None

    if vacancy.status != Vacancy.Status.PUBLISHED:
        raise ApplicationError(str(MSG_VACANCY_NOT_ACCEPTING))

    if vacancy.cv_required and not cv_file_path:
        raise ApplicationError(str(MSG_CV_REQUIRED))

    try:
        application = Application.objects.create(
            vacancy=vacancy,
            candidate=candidate,
            candidate_name=candidate_name,
            candidate_email=candidate_email,
            candidate_phone=candidate_phone,
            cv_file=cv_file_path,
            cv_original_filename=cv_original_filename,
        )
    except IntegrityError:
        raise ApplicationError(str(MSG_ALREADY_APPLIED)) from None

    if cv_file_path:
        from django.db import transaction

        from apps.applications.tasks import process_cv

        transaction.on_commit(lambda: process_cv.delay(str(application.id)))

    # Create prescanning session immediately (always chat mode)
    prescan_session = Interview.objects.create(
        application=application,
        session_type=Interview.SessionType.PRESCANNING,
        screening_mode=Interview.ScreeningMode.CHAT,
        status=Interview.Status.PENDING,
        language=vacancy.prescanning_language,
        channel=channel,
    )

    return {
        "application": application,
        "prescan_session": prescan_session,
        "prescan_token": str(prescan_session.interview_token),
    }


def create_interview_session(*, application: Application) -> Interview | None:
    """Create an interview session for a prescanned application.

    Only creates if the vacancy has interview_enabled=True.
    Returns the new Interview session or None if interview not enabled.
    """
    vacancy = application.vacancy
    if not vacancy.interview_enabled:
        return None

    interview_kwargs: dict = {
        "application": application,
        "session_type": Interview.SessionType.INTERVIEW,
        "screening_mode": vacancy.interview_mode,
        "status": Interview.Status.PENDING,
        "language": vacancy.prescanning_language,
    }
    if vacancy.interview_mode == Interview.ScreeningMode.MEET:
        interview_kwargs["duration_minutes"] = vacancy.interview_duration
        interview_kwargs["livekit_room_name"] = f"interview-{application.id}"

    return Interview.objects.create(**interview_kwargs)


def update_application_status(
    *,
    application: Application,
    status: str,
    updated_by: User,
) -> Application:
    """Update the status of an application with transition validation.

    When resetting to Applied, cancels all existing sessions and creates
    a fresh prescanning session (full pipeline restart).
    """
    current = application.status
    allowed = STATUS_TRANSITIONS.get(current, set())

    if status not in allowed:
        raise ApplicationError(str(MSG_STATUS_TRANSITION_INVALID).format(current=current, target=status))

    # Reset to Applied = full pipeline restart
    if status == Application.Status.APPLIED and current != Application.Status.APPLIED:
        _reset_pipeline(application=application)

    application.status = status
    application.save(update_fields=["status", "updated_at"])
    return application


def _reset_pipeline(*, application: Application) -> None:
    """Cancel all existing sessions and create a fresh prescanning session."""
    # Cancel all non-completed, non-cancelled sessions
    active_sessions = application.sessions.exclude(
        status__in=[Interview.Status.COMPLETED, Interview.Status.CANCELLED, Interview.Status.EXPIRED]
    )
    active_sessions.update(status=Interview.Status.CANCELLED)

    # Create fresh prescanning session
    Interview.objects.create(
        application=application,
        session_type=Interview.SessionType.PRESCANNING,
        screening_mode=Interview.ScreeningMode.CHAT,
        status=Interview.Status.PENDING,
    )

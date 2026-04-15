import logging
import uuid
from datetime import datetime

from django.utils import timezone

from apps.applications.models import Application
from apps.common.exceptions import ApplicationError
from apps.common.messages import (
    MSG_CANNOT_CANCEL_SESSION,
    MSG_CANNOT_START_SESSION,
)
from apps.interviews.models import Interview
from apps.vacancies.models import Vacancy

logger = logging.getLogger(__name__)


def cancel_interview(*, interview: Interview) -> Interview:
    """Cancel a pending or in-progress session and revert application status."""
    if interview.status not in (Interview.Status.PENDING, Interview.Status.IN_PROGRESS):
        raise ApplicationError(str(MSG_CANNOT_CANCEL_SESSION).format(status=interview.status))

    interview.status = Interview.Status.CANCELLED
    interview.save(update_fields=["status", "updated_at"])

    # Revert application status based on session type
    application = interview.application
    if interview.session_type == Interview.SessionType.PRESCANNING:
        application.status = Application.Status.APPLIED
    else:
        application.status = Application.Status.PRESCANNED
    application.save(update_fields=["status", "updated_at"])

    return interview


def start_interview(*, interview: Interview) -> Interview:
    """Mark an interview as in progress.

    Accepts PENDING status. Sets started_at to now.
    For meet mode, generates a LiveKit candidate token.
    """
    from apps.interviews.services.interview_livekit import generate_candidate_token

    if interview.status != Interview.Status.PENDING:
        raise ApplicationError(str(MSG_CANNOT_START_SESSION).format(status=interview.status))

    interview.status = Interview.Status.IN_PROGRESS
    interview.started_at = timezone.now()

    update_fields = ["status", "started_at", "updated_at"]

    if interview.screening_mode == Interview.ScreeningMode.MEET:
        if not interview.livekit_room_name:
            interview.livekit_room_name = f"interview-{interview.id}"
            update_fields.append("livekit_room_name")
        interview.candidate_token = generate_candidate_token(interview=interview)
        update_fields.append("candidate_token")
    elif interview.screening_mode == Interview.ScreeningMode.CHAT:
        from apps.interviews.chat_service import generate_greeting

        try:
            greeting = generate_greeting(interview)
        except Exception as e:
            logger.warning("Failed to generate AI greeting: %s. Using fallback.", e)
            vacancy = interview.application.vacancy
            greeting = (
                f"Hello! Welcome to the interview for the {vacancy.title} position. "
                f"I'll be asking you a series of questions to learn more about your "
                f"experience and skills. Please take your time with each answer.\n\n"
                f"Let's start — could you briefly introduce yourself and tell me "
                f"why you're interested in this role?"
            )
        interview.chat_history = [
            {
                "role": "ai",
                "text": greeting,
                "timestamp": timezone.now().isoformat(),
            }
        ]
        update_fields.append("chat_history")

    interview.save(update_fields=update_fields)

    return interview


def reset_interview(*, interview: Interview) -> Interview:
    """Reset an abandoned session by creating a new one.

    Marks the old session as CANCELLED, creates a fresh session preserving
    session_type. Returns the newly created session.
    """
    if interview.status not in (Interview.Status.IN_PROGRESS, Interview.Status.CANCELLED):
        raise ApplicationError(f"Cannot reset session with status '{interview.status}'.")

    application = interview.application

    # Mark old session as cancelled
    if interview.status != Interview.Status.CANCELLED:
        interview.status = Interview.Status.CANCELLED
        interview.save(update_fields=["status", "updated_at"])

    # Create a fresh session with the same session_type
    session_kwargs: dict = {
        "application": application,
        "session_type": interview.session_type,
        "screening_mode": interview.screening_mode,
        "interview_token": uuid.uuid4(),
        "status": Interview.Status.PENDING,
    }
    if interview.screening_mode == Interview.ScreeningMode.MEET:
        session_kwargs["duration_minutes"] = application.vacancy.interview_duration
        session_kwargs["livekit_room_name"] = f"interview-{application.id}"

    new_session = Interview.objects.create(**session_kwargs)

    # Revert application status based on session type
    if interview.session_type == Interview.SessionType.PRESCANNING:
        application.status = Application.Status.APPLIED
    else:
        application.status = Application.Status.PRESCANNED
    application.save(update_fields=["status", "updated_at"])

    return new_session


def expire_interviews_for_vacancy(*, vacancy: Vacancy) -> int:
    """Expire all PENDING interviews for a vacancy.

    Sets matching interviews to EXPIRED and their applications to EXPIRED.
    Returns the number of interviews expired.
    """
    pending_interviews = Interview.objects.filter(
        application__vacancy=vacancy,
        status=Interview.Status.PENDING,
    ).select_related("application")

    count = 0
    for interview in pending_interviews:
        interview.status = Interview.Status.EXPIRED
        interview.save(update_fields=["status", "updated_at"])

        interview.application.status = Application.Status.EXPIRED
        interview.application.save(update_fields=["status", "updated_at"])
        count += 1

    return count


def schedule_human_interview(
    *,
    application: Application,
    scheduled_at: datetime,
    interviewer_name: str,
    meeting_link: str = "",
) -> dict:
    """Schedule a human (non-AI) interview and notify the candidate."""
    data = {
        "application_id": str(application.id),
        "candidate_name": application.candidate_name,
        "candidate_email": application.candidate_email,
        "vacancy_title": application.vacancy.title,
        "scheduled_at": scheduled_at.isoformat(),
        "interviewer_name": interviewer_name,
        "meeting_link": meeting_link,
    }

    if application.candidate:
        from apps.notifications.models import Notification
        from apps.notifications.services import create_notification

        create_notification(
            user=application.candidate,
            type=Notification.Type.INTERVIEW_SCHEDULED,
            title="Human Interview Scheduled",
            message=(
                f"A follow-up interview for {application.vacancy.title} has been "
                f"scheduled with {interviewer_name} on "
                f"{scheduled_at.strftime('%b %d, %Y %H:%M UTC')}."
            ),
            data=data,
        )

    logger.info(
        "Human interview scheduled for application %s with %s at %s",
        application.id,
        interviewer_name,
        scheduled_at,
    )

    return data

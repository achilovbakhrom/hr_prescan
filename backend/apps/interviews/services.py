import logging
import os
import uuid
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from django.utils import timezone
from livekit.api import AccessToken, VideoGrants

from apps.applications.models import Application
from apps.common.exceptions import ApplicationError
from apps.common.messages import (
    MSG_CANNOT_CANCEL_SESSION,
    MSG_CANNOT_START_SESSION,
    MSG_INTERVIEW_NOT_FOUND,
)
from apps.interviews.models import Interview, InterviewIntegrityFlag, InterviewScore
from apps.vacancies.models import Vacancy

logger = logging.getLogger(__name__)

LIVEKIT_API_KEY = os.environ.get("LIVEKIT_API_KEY", "")
LIVEKIT_API_SECRET = os.environ.get("LIVEKIT_API_SECRET", "")


def cancel_interview(*, interview: Interview) -> Interview:
    """Cancel a pending or in-progress session and revert application status."""
    if interview.status not in (Interview.Status.PENDING, Interview.Status.IN_PROGRESS):
        raise ApplicationError(
            str(MSG_CANNOT_CANCEL_SESSION).format(status=interview.status)
        )

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
    if interview.status != Interview.Status.PENDING:
        raise ApplicationError(
            str(MSG_CANNOT_START_SESSION).format(status=interview.status)
        )

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
        # Generate AI greeting for chat mode via OpenAI
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
        interview.chat_history = [{
            "role": "ai",
            "text": greeting,
            "timestamp": timezone.now().isoformat(),
        }]
        update_fields.append("chat_history")

    interview.save(update_fields=update_fields)

    # In-progress state is tracked on the session object only;
    # application status remains at its current pipeline stage.

    return interview


def reset_interview(*, interview: Interview) -> Interview:
    """Reset an abandoned session by creating a new one.

    Validates session is IN_PROGRESS or CANCELLED. Marks the old session
    as CANCELLED (if not already), creates a new session for the same
    application with a fresh token, preserving the session_type.

    Returns the newly created session.
    """
    if interview.status not in (Interview.Status.IN_PROGRESS, Interview.Status.CANCELLED):
        raise ApplicationError(
            f"Cannot reset session with status '{interview.status}'."
        )

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


def complete_session(
    *,
    interview: Interview,
    overall_score: Decimal,
    ai_summary: str,
    transcript: list,
    recording_path: str = "",
    ai_decision: str = "advance",
) -> Interview:
    """Complete a screening session (prescanning or interview) with results.

    Args:
        ai_decision: "advance" to move candidate forward, "reject" to reject.
    """
    if interview.status != Interview.Status.IN_PROGRESS:
        raise ApplicationError(
            f"Cannot complete session with status '{interview.status}'."
        )

    from django.utils import timezone

    interview.status = Interview.Status.COMPLETED
    interview.completed_at = timezone.now()
    interview.overall_score = overall_score
    interview.ai_summary = ai_summary
    interview.transcript = transcript
    interview.recording_path = recording_path
    interview.save(
        update_fields=[
            "status",
            "completed_at",
            "overall_score",
            "ai_summary",
            "transcript",
            "recording_path",
            "updated_at",
        ]
    )

    application = interview.application

    if interview.session_type == Interview.SessionType.PRESCANNING:
        if ai_decision == "reject":
            application.status = Application.Status.REJECTED
        else:
            application.status = Application.Status.PRESCANNED
            # Auto-create interview session if vacancy has it enabled
            from apps.applications.services import create_interview_session

            create_interview_session(application=application)
    elif interview.session_type == Interview.SessionType.INTERVIEW:
        if ai_decision == "reject":
            application.status = Application.Status.REJECTED
        else:
            application.status = Application.Status.INTERVIEWED

    application.save(update_fields=["status", "updated_at"])

    return interview


def save_interview_scores(
    *,
    interview: Interview,
    scores: list[dict],
) -> list[InterviewScore]:
    """Create InterviewScore objects for each criteria.

    Args:
        interview: The interview to save scores for.
        scores: List of dicts with keys: criteria_id, score, ai_notes.
    """
    score_objects = []
    for score_data in scores:
        score_obj = InterviewScore.objects.create(
            interview=interview,
            criteria_id=score_data["criteria_id"],
            score=score_data["score"],
            ai_notes=score_data.get("ai_notes", ""),
        )
        score_objects.append(score_obj)
    return score_objects


def add_integrity_flag(
    *,
    interview: Interview,
    flag_type: str,
    severity: str,
    description: str,
    timestamp_seconds: int | None = None,
) -> InterviewIntegrityFlag:
    """Create an integrity flag for an interview."""
    return InterviewIntegrityFlag.objects.create(
        interview=interview,
        flag_type=flag_type,
        severity=severity,
        description=description,
        timestamp_seconds=timestamp_seconds,
    )


def create_integrity_flags(
    *,
    interview_id: UUID,
    flags_data: list[dict],
) -> list[InterviewIntegrityFlag]:
    """Bulk-create IntegrityFlag records for an interview.

    Args:
        interview_id: UUID of the interview to attach flags to.
        flags_data: List of dicts with keys: flag_type, severity, description,
                    and optionally timestamp_seconds.

    Returns:
        List of created InterviewIntegrityFlag instances.
    """
    try:
        interview = Interview.objects.get(id=interview_id)
    except Interview.DoesNotExist:
        raise ApplicationError(str(MSG_INTERVIEW_NOT_FOUND))

    flag_objects = [
        InterviewIntegrityFlag(
            interview=interview,
            flag_type=flag["flag_type"],
            severity=flag["severity"],
            description=flag["description"],
            timestamp_seconds=flag.get("timestamp_seconds"),
        )
        for flag in flags_data
    ]

    created = InterviewIntegrityFlag.objects.bulk_create(flag_objects)
    logger.info(
        "Created %d integrity flags for interview %s.", len(created), interview_id
    )
    return created


def _create_livekit_token(
    *,
    room_name: str,
    participant_identity: str,
    participant_name: str,
    can_publish: bool = True,
    can_subscribe: bool = True,
) -> str:
    """Create a LiveKit access token with the given grants."""
    if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
        raise ApplicationError(
            "LiveKit credentials not configured. "
            "Set LIVEKIT_API_KEY and LIVEKIT_API_SECRET."
        )

    token = (
        AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        .with_identity(participant_identity)
        .with_name(participant_name)
        .with_grants(
            VideoGrants(
                room=room_name,
                room_join=True,
                can_publish=can_publish,
                can_subscribe=can_subscribe,
            )
        )
    )
    return token.to_jwt()


def generate_candidate_token(*, interview: Interview) -> str:
    """Generate a LiveKit participant token for the candidate."""
    return _create_livekit_token(
        room_name=interview.livekit_room_name,
        participant_identity=f"candidate-{interview.application.id}",
        participant_name=interview.application.candidate_name,
        can_publish=True,
        can_subscribe=True,
    )


def generate_observer_token(*, interview: Interview) -> str:
    """Generate a LiveKit observer token for HR to watch live (no publishing)."""
    return _create_livekit_token(
        room_name=interview.livekit_room_name,
        participant_identity=f"observer-{interview.id}",
        participant_name="HR Observer",
        can_publish=False,
        can_subscribe=True,
    )


def schedule_human_interview(
    *,
    application: Application,
    scheduled_at: datetime,
    interviewer_name: str,
    meeting_link: str = "",
) -> dict:
    """Schedule a human (non-AI) interview for a candidate.

    This does NOT create an Interview model instance (that is for AI interviews).
    Instead it returns scheduling data and sends a notification to the candidate.
    """
    data = {
        "application_id": str(application.id),
        "candidate_name": application.candidate_name,
        "candidate_email": application.candidate_email,
        "vacancy_title": application.vacancy.title,
        "scheduled_at": scheduled_at.isoformat(),
        "interviewer_name": interviewer_name,
        "meeting_link": meeting_link,
    }

    # Notify candidate
    if application.candidate:
        from apps.notifications.services import create_notification
        from apps.notifications.models import Notification

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

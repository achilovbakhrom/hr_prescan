import logging
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from apps.applications.models import Application
from apps.common.exceptions import ApplicationError
from apps.interviews.models import Interview, InterviewIntegrityFlag, InterviewScore

logger = logging.getLogger(__name__)


def schedule_interview(
    *,
    application: Application,
    scheduled_at: datetime,
) -> Interview:
    """Create an interview for an application and update status."""
    if application.status not in (
        Application.Status.APPLIED,
        Application.Status.REVIEWING,
    ):
        raise ApplicationError(
            f"Cannot schedule interview for application with status '{application.status}'."
        )

    if hasattr(application, "interview"):
        raise ApplicationError("This application already has an interview scheduled.")

    interview = Interview.objects.create(
        application=application,
        scheduled_at=scheduled_at,
        duration_minutes=application.vacancy.interview_duration,
    )

    # Generate LiveKit room name (stub)
    interview.livekit_room_name = f"interview-{interview.id}"
    interview.candidate_token = generate_candidate_token(interview=interview)
    interview.save(update_fields=["livekit_room_name", "candidate_token", "updated_at"])

    # Update application status
    application.status = Application.Status.INTERVIEW_SCHEDULED
    application.save(update_fields=["status", "updated_at"])

    # Trigger confirmation email
    from apps.interviews.tasks import send_scheduling_confirmation_email

    send_scheduling_confirmation_email.delay(str(interview.id))

    return interview


def cancel_interview(*, interview: Interview) -> Interview:
    """Cancel a scheduled interview and revert application status."""
    if interview.status not in (Interview.Status.SCHEDULED,):
        raise ApplicationError(
            f"Cannot cancel interview with status '{interview.status}'."
        )

    interview.status = Interview.Status.CANCELLED
    interview.save(update_fields=["status", "updated_at"])

    # Revert application status
    application = interview.application
    application.status = Application.Status.APPLIED
    application.save(update_fields=["status", "updated_at"])

    return interview


def start_interview(*, interview: Interview) -> Interview:
    """Mark an interview as in progress."""
    if interview.status != Interview.Status.SCHEDULED:
        raise ApplicationError(
            f"Cannot start interview with status '{interview.status}'."
        )

    interview.status = Interview.Status.IN_PROGRESS
    interview.save(update_fields=["status", "updated_at"])

    application = interview.application
    application.status = Application.Status.INTERVIEW_IN_PROGRESS
    application.save(update_fields=["status", "updated_at"])

    return interview


def complete_interview(
    *,
    interview: Interview,
    overall_score: Decimal,
    ai_summary: str,
    transcript: list,
    recording_path: str = "",
) -> Interview:
    """Mark an interview as completed with results."""
    if interview.status != Interview.Status.IN_PROGRESS:
        raise ApplicationError(
            f"Cannot complete interview with status '{interview.status}'."
        )

    interview.status = Interview.Status.COMPLETED
    interview.overall_score = overall_score
    interview.ai_summary = ai_summary
    interview.transcript = transcript
    interview.recording_path = recording_path
    interview.save(
        update_fields=[
            "status",
            "overall_score",
            "ai_summary",
            "transcript",
            "recording_path",
            "updated_at",
        ]
    )

    application = interview.application
    application.status = Application.Status.INTERVIEW_COMPLETED
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
        raise ApplicationError(f"Interview {interview_id} not found.")

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


def generate_candidate_token(*, interview: Interview) -> str:
    """Generate a LiveKit participant token for the candidate.

    STUB: Returns a placeholder token. Real implementation will use LiveKit SDK.
    """
    return f"candidate-token-{interview.id}"


def generate_observer_token(*, interview: Interview) -> str:
    """Generate a LiveKit observer token for HR to watch live.

    STUB: Returns a placeholder token. Real implementation will use LiveKit SDK.
    """
    return f"observer-token-{interview.id}"


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

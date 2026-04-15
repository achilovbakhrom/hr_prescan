import logging
from decimal import Decimal
from uuid import UUID

from apps.applications.models import Application
from apps.common.exceptions import ApplicationError
from apps.common.messages import MSG_INTERVIEW_NOT_FOUND
from apps.interviews.models import Interview, InterviewIntegrityFlag, InterviewScore

logger = logging.getLogger(__name__)


def complete_session(
    *,
    interview: Interview,
    overall_score: Decimal,
    ai_summary: str,
    ai_summary_translations: dict | None = None,
    transcript: list,
    recording_path: str = "",
    ai_decision: str = "advance",
) -> Interview:
    """Complete a screening session (prescanning or interview) with results.

    Args:
        ai_decision: "advance" to move candidate forward, "reject" to reject.
    """
    if interview.status != Interview.Status.IN_PROGRESS:
        raise ApplicationError(f"Cannot complete session with status '{interview.status}'.")

    from django.utils import timezone

    interview.status = Interview.Status.COMPLETED
    interview.completed_at = timezone.now()
    interview.overall_score = overall_score
    interview.ai_summary = ai_summary
    interview.transcript = transcript
    interview.recording_path = recording_path

    update_fields = [
        "status",
        "completed_at",
        "overall_score",
        "ai_summary",
        "transcript",
        "recording_path",
        "updated_at",
    ]

    if ai_summary_translations is not None:
        interview.ai_summary_translations = ai_summary_translations
        update_fields.append("ai_summary_translations")

    interview.save(update_fields=update_fields)

    application = interview.application

    if interview.session_type == Interview.SessionType.PRESCANNING:
        if ai_decision == "reject":
            application.status = Application.Status.REJECTED
        elif application.vacancy.interview_enabled:
            # Intermediate step: candidate must still pass the interview
            application.status = Application.Status.PRESCANNED
            from apps.applications.services import create_interview_session

            create_interview_session(application=application)
        else:
            # Prescanning is the final AI step → shortlist on advance
            application.status = Application.Status.SHORTLISTED
    elif interview.session_type == Interview.SessionType.INTERVIEW:
        if ai_decision == "reject":
            application.status = Application.Status.REJECTED
        else:
            # Interview is the final AI step → shortlist on advance
            application.status = Application.Status.SHORTLISTED

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
        raise ApplicationError(str(MSG_INTERVIEW_NOT_FOUND)) from None

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
    logger.info("Created %d integrity flags for interview %s.", len(created), interview_id)
    return created

import logging
from decimal import Decimal

from apps.applications.models import Application
from apps.common.exceptions import ApplicationError
from apps.interviews.models import Interview, InterviewScore

logger = logging.getLogger(__name__)


def complete_session(
    *,
    interview: Interview,
    overall_score: Decimal,
    ai_summary: str,
    ai_summary_translations: dict | None = None,
    decision_support: dict | None = None,
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
    interview.decision_support = decision_support or {}
    interview.transcript = transcript
    interview.recording_path = recording_path

    update_fields = [
        "status",
        "completed_at",
        "overall_score",
        "ai_summary",
        "decision_support",
        "transcript",
        "recording_path",
        "updated_at",
    ]

    if ai_summary_translations is not None:
        interview.ai_summary_translations = ai_summary_translations
        update_fields.append("ai_summary_translations")

    interview.save(update_fields=update_fields)

    application = interview.application
    candidate_interview = None

    if interview.session_type == Interview.SessionType.PRESCANNING:
        if ai_decision == "reject":
            application.status = Application.Status.REJECTED
        elif application.vacancy.interview_enabled:
            # Intermediate step: candidate must still pass the interview
            application.status = Application.Status.PRESCANNED
            from apps.applications.services import create_interview_session

            candidate_interview = create_interview_session(application=application)
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
    if candidate_interview is not None:
        from apps.notifications.services import notify_candidate_interview_ready

        notify_candidate_interview_ready(application=application, interview=candidate_interview)

    from apps.applications.services.candidate_base import sync_hr_candidate_for_application

    sync_hr_candidate_for_application(application=application)

    # Notify HR team via Telegram (non-blocking, fire-and-forget)
    try:
        from django.db import transaction

        from apps.notifications.tasks import notify_hr_company_telegram

        transaction.on_commit(
            lambda: notify_hr_company_telegram.delay(
                company_id=str(application.vacancy.company_id),
                application_id=str(application.id),
                candidate_name=application.candidate_name,
                vacancy_title=application.vacancy.title,
                session_type=interview.session_type,
                overall_score=float(overall_score),
            )
        )
    except Exception as exc:
        logger.warning("Failed to schedule HR Telegram notification: %s", exc)

    # Notify HR team in-app + email (alongside the Telegram push, guarded so a
    # notification failure never affects session completion).
    _notify_hr_session_completed(interview=interview)

    return interview


def _notify_hr_session_completed(*, interview: Interview) -> None:
    """Create the in-app + email HR notification for a completed session.

    Covers both prescanning and interview steps; fully guarded. Deferred to
    on_commit so the Notification row (and its enqueued email) is never created
    if the surrounding score-saving transaction rolls back.
    """
    from django.db import transaction

    def _send() -> None:
        try:
            from apps.notifications.services import notify_session_completed

            notify_session_completed(interview=interview)
        except Exception as exc:
            logger.warning("Failed to send HR session-completed notification: %s", exc)

    transaction.on_commit(_send)


def save_interview_scores(
    *,
    interview: Interview,
    scores: list[dict],
) -> list[InterviewScore]:
    """Create InterviewScore objects for each criteria.

    Args:
        interview: The interview to save scores for.
        scores: List of dicts with keys: criteria_id, score, ai_notes, evidence.
    """
    InterviewScore.objects.filter(interview=interview).delete()
    score_objects = []
    for score_data in scores:
        score_obj = InterviewScore.objects.create(
            interview=interview,
            criteria_id=score_data["criteria_id"],
            score=score_data["score"],
            ai_notes=score_data.get("ai_notes", ""),
            evidence=score_data.get("evidence", []),
        )
        score_objects.append(score_obj)
    return score_objects

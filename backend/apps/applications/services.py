import random
from uuid import UUID

from django.db import IntegrityError

from apps.accounts.models import User
from apps.applications.models import Application
from apps.common.exceptions import ApplicationError
from apps.vacancies.models import Vacancy


# Valid status transitions: current_status -> set of allowed next statuses
_STATUS_TRANSITIONS: dict[str, set[str]] = {
    Application.Status.APPLIED: {
        Application.Status.INTERVIEW_SCHEDULED,
        Application.Status.REVIEWING,
        Application.Status.REJECTED,
    },
    Application.Status.INTERVIEW_SCHEDULED: {
        Application.Status.INTERVIEW_IN_PROGRESS,
        Application.Status.REJECTED,
    },
    Application.Status.INTERVIEW_IN_PROGRESS: {
        Application.Status.INTERVIEW_COMPLETED,
        Application.Status.REJECTED,
    },
    Application.Status.INTERVIEW_COMPLETED: {
        Application.Status.REVIEWING,
        Application.Status.SHORTLISTED,
        Application.Status.REJECTED,
    },
    Application.Status.REVIEWING: {
        Application.Status.SHORTLISTED,
        Application.Status.REJECTED,
    },
    Application.Status.SHORTLISTED: {
        Application.Status.REJECTED,
    },
    Application.Status.REJECTED: set(),
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
) -> Application:
    """Submit a new application to a vacancy."""
    try:
        vacancy = Vacancy.objects.get(id=vacancy_id)
    except Vacancy.DoesNotExist:
        raise ApplicationError("Vacancy not found.")

    if vacancy.status != Vacancy.Status.PUBLISHED:
        raise ApplicationError("This vacancy is not accepting applications.")

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
        raise ApplicationError("You have already applied to this vacancy.")

    if cv_file_path:
        from apps.applications.tasks import process_cv

        process_cv.delay(str(application.id))

    return application


def update_application_status(
    *,
    application: Application,
    status: str,
    updated_by: User,
) -> Application:
    """Update the status of an application with transition validation."""
    current = application.status
    allowed = _STATUS_TRANSITIONS.get(current, set())

    if status not in allowed:
        raise ApplicationError(
            f"Cannot transition from '{current}' to '{status}'."
        )

    application.status = status
    application.save(update_fields=["status", "updated_at"])
    return application


def add_hr_note(*, application: Application, note: str) -> Application:
    """Append a note to the application's HR notes."""
    if application.hr_notes:
        application.hr_notes += f"\n\n---\n\n{note}"
    else:
        application.hr_notes = note

    application.save(update_fields=["hr_notes", "updated_at"])
    return application


def process_cv_text(*, application_id: UUID) -> None:
    """Extract text from CV file.

    STUB: In real implementation, download from MinIO and parse PDF/DOCX.
    For now, sets cv_parsed_text to a placeholder.
    """
    try:
        application = Application.objects.get(id=application_id)
    except Application.DoesNotExist:
        return

    application.cv_parsed_text = (
        f"[Placeholder CV text for {application.candidate_name}] "
        "Experienced professional with relevant skills and qualifications."
    )
    application.save(update_fields=["cv_parsed_text", "updated_at"])


def analyze_cv_with_ai(*, application_id: UUID) -> None:
    """AI analysis of CV to extract structured data.

    STUB: In real implementation, send cv_parsed_text to OpenAI.
    For now, sets cv_parsed_data to a placeholder dict.
    """
    try:
        application = Application.objects.get(id=application_id)
    except Application.DoesNotExist:
        return

    application.cv_parsed_data = {
        "skills": ["Python", "Django", "REST APIs", "PostgreSQL"],
        "experience_years": 5,
        "education": [
            {
                "degree": "Bachelor of Science",
                "field": "Computer Science",
                "institution": "University",
            }
        ],
        "languages": ["English"],
        "summary": f"Experienced professional: {application.candidate_name}",
    }
    application.save(update_fields=["cv_parsed_data", "updated_at"])


def calculate_match_score(*, application_id: UUID) -> None:
    """Compare CV against vacancy requirements and compute match score.

    STUB: In real implementation, send to OpenAI with vacancy criteria.
    For now, sets match_score to a random value between 50 and 95.
    """
    try:
        application = Application.objects.select_related("vacancy").get(
            id=application_id
        )
    except Application.DoesNotExist:
        return

    score = random.uniform(50, 95)
    application.match_score = round(score, 2)
    application.match_details = {
        "overall": round(score, 2),
        "criteria_scores": {
            "technical_skills": round(random.uniform(40, 100), 2),
            "experience_relevance": round(random.uniform(40, 100), 2),
            "education_fit": round(random.uniform(40, 100), 2),
        },
        "notes": "Placeholder match analysis.",
    }
    application.save(
        update_fields=["match_score", "match_details", "updated_at"]
    )


def bulk_update_status(
    *,
    application_ids: list[UUID],
    status: str,
    updated_by: User,
) -> int:
    """Update multiple applications to a new status. Returns count of updated records.

    Only transitions that are valid per _STATUS_TRANSITIONS are applied;
    applications that cannot transition are silently skipped.
    """
    applications = Application.objects.filter(
        id__in=application_ids,
        vacancy__company=updated_by.company,
    ).select_related("vacancy")

    updated = 0
    for application in applications:
        allowed = _STATUS_TRANSITIONS.get(application.status, set())
        if status not in allowed:
            continue

        application.status = status
        application.save(update_fields=["status", "updated_at"])

        # Trigger notification
        from apps.notifications.services import notify_status_changed

        notify_status_changed(application=application)
        updated += 1

    return updated

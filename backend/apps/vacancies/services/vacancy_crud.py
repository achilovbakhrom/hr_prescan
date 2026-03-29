import logging

from django.db import transaction

from apps.accounts.models import Company, User
from apps.common.exceptions import ApplicationError
from apps.common.messages import (
    MSG_CANNOT_CHANGE_MODE,
    MSG_NO_INTERVIEW_QUESTIONS,
    MSG_NO_PRESCANNING_QUESTIONS,
    MSG_ONLY_DRAFT_PAUSED_PUBLISH,
    MSG_ONLY_PUBLISHED_PAUSE,
    MSG_ONLY_PUBLISHED_PAUSED_ARCHIVE,
)
from apps.vacancies.models import ScreeningStep, Vacancy

from .criteria_questions import create_default_criteria

logger = logging.getLogger(__name__)


@transaction.atomic
def create_vacancy(
    *,
    company: Company,
    created_by: User,
    title: str,
    description: str,
    **kwargs: object,
) -> Vacancy:
    """Create a vacancy with default evaluation criteria."""
    vacancy = Vacancy.objects.create(
        company=company,
        created_by=created_by,
        title=title,
        description=description,
        **kwargs,
    )
    create_default_criteria(vacancy=vacancy)

    from apps.vacancies.tasks import generate_keywords_task

    transaction.on_commit(lambda: generate_keywords_task.delay(str(vacancy.id)))

    return vacancy


def update_vacancy(*, vacancy: Vacancy, data: dict) -> Vacancy:
    """Update allowed vacancy fields.

    interview_mode can only be changed if the vacancy has no applications.
    """
    allowed_fields = {
        "title",
        "description",
        "requirements",
        "responsibilities",
        "skills",
        "salary_min",
        "salary_max",
        "salary_currency",
        "location",
        "is_remote",
        "employment_type",
        "experience_level",
        "deadline",
        "visibility",
        "interview_duration",
        "interview_mode",
        "interview_enabled",
        "cv_required",
        "company_info",
        "prescanning_prompt",
        "interview_prompt",
        "prescanning_language",
    }

    # Guard: interview_mode cannot be changed once applications exist
    if "interview_mode" in data and data["interview_mode"] != vacancy.interview_mode and vacancy.applications.exists():
        raise ApplicationError(str(MSG_CANNOT_CHANGE_MODE))

    update_fields: list[str] = []

    for field, value in data.items():
        if field in allowed_fields:
            setattr(vacancy, field, value)
            update_fields.append(field)

    if not update_fields:
        return vacancy

    update_fields.append("updated_at")
    vacancy.save(update_fields=update_fields)

    # Regenerate keywords when search-relevant fields change
    search_relevant_fields = {"title", "description", "requirements", "skills"}
    if search_relevant_fields & set(update_fields):
        from apps.vacancies.tasks import generate_keywords_task

        transaction.on_commit(lambda: generate_keywords_task.delay(str(vacancy.id)))

    return vacancy


def publish_vacancy(*, vacancy: Vacancy) -> Vacancy:
    """Publish a vacancy. Allowed from draft or paused.

    Lifecycle: draft -> published <-> paused -> archived. Cannot go back to draft.
    """
    if vacancy.status not in (Vacancy.Status.DRAFT, Vacancy.Status.PAUSED):
        raise ApplicationError(str(MSG_ONLY_DRAFT_PAUSED_PUBLISH))

    if not vacancy.questions.filter(is_active=True, step=ScreeningStep.PRESCANNING).exists():
        raise ApplicationError(str(MSG_NO_PRESCANNING_QUESTIONS))

    if (
        vacancy.interview_enabled
        and not vacancy.questions.filter(is_active=True, step=ScreeningStep.INTERVIEW).exists()
    ):
        raise ApplicationError(str(MSG_NO_INTERVIEW_QUESTIONS))

    vacancy.status = Vacancy.Status.PUBLISHED
    vacancy.save(update_fields=["status", "updated_at"])
    return vacancy


def pause_vacancy(*, vacancy: Vacancy) -> Vacancy:
    """Pause a published vacancy. Can be resumed (published again)."""
    if vacancy.status != Vacancy.Status.PUBLISHED:
        raise ApplicationError(str(MSG_ONLY_PUBLISHED_PAUSE))

    vacancy.status = Vacancy.Status.PAUSED
    vacancy.save(update_fields=["status", "updated_at"])
    return vacancy


def archive_vacancy(*, vacancy: Vacancy) -> Vacancy:
    """Archive a vacancy and expire all pending sessions.

    Allowed from published or paused. Terminal state -- cannot go back.
    """
    if vacancy.status not in (Vacancy.Status.PUBLISHED, Vacancy.Status.PAUSED):
        raise ApplicationError(str(MSG_ONLY_PUBLISHED_PAUSED_ARCHIVE))

    vacancy.status = Vacancy.Status.ARCHIVED
    vacancy.save(update_fields=["status", "updated_at"])

    # Expire all pending sessions for this vacancy
    from apps.interviews.services import expire_interviews_for_vacancy

    expire_interviews_for_vacancy(vacancy=vacancy)

    return vacancy


def soft_delete_vacancy(*, vacancy: Vacancy) -> Vacancy:
    """Soft-delete a vacancy. Only draft or archived vacancies can be deleted."""
    if vacancy.status not in (Vacancy.Status.DRAFT, Vacancy.Status.ARCHIVED):
        raise ApplicationError("Only draft or archived vacancies can be deleted.")
    vacancy.is_deleted = True
    vacancy.save(update_fields=["is_deleted", "updated_at"])
    return vacancy

from uuid import UUID

from django.db import IntegrityError

from apps.accounts.models import User
from apps.applications.models import Application
from apps.applications.services.application_reopen import (
    can_reopen_application,
    get_existing_application,
    reopen_application,
)
from apps.applications.services.cv_selection import get_candidate_platform_cv
from apps.common.exceptions import ApplicationError
from apps.common.messages import (
    MSG_ALREADY_APPLIED,
    MSG_CV_REQUIRED,
    MSG_VACANCY_NOT_ACCEPTING,
    MSG_VACANCY_NOT_FOUND,
)
from apps.interviews.models import Interview
from apps.vacancies.models import Vacancy


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

    if not cv_file_path:
        cv_file_path, cv_original_filename = get_candidate_platform_cv(candidate=candidate)

    if vacancy.cv_required and not cv_file_path:
        raise ApplicationError(str(MSG_CV_REQUIRED))

    existing = get_existing_application(vacancy=vacancy, candidate_email=candidate_email)
    if existing:
        if not can_reopen_application(existing):
            raise ApplicationError(str(MSG_ALREADY_APPLIED))
        application, prescan_session = reopen_application(
            application=existing,
            candidate=candidate,
            candidate_name=candidate_name,
            candidate_email=candidate_email,
            candidate_phone=candidate_phone,
            cv_file_path=cv_file_path,
            cv_original_filename=cv_original_filename,
            channel=channel,
        )
        _enqueue_cv_processing(application=application, cv_file_path=cv_file_path)
        return _submission_result(application=application, prescan_session=prescan_session)

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

    _enqueue_cv_processing(application=application, cv_file_path=cv_file_path)

    # Create prescanning session immediately (always chat mode)
    prescan_session = Interview.objects.create(
        application=application,
        session_type=Interview.SessionType.PRESCANNING,
        screening_mode=Interview.ScreeningMode.CHAT,
        status=Interview.Status.PENDING,
        language=vacancy.prescanning_language,
        channel=channel,
    )

    return _submission_result(application=application, prescan_session=prescan_session)


def _enqueue_cv_processing(*, application: Application, cv_file_path: str) -> None:
    if not cv_file_path:
        return
    from django.db import transaction

    from apps.applications.tasks import process_cv

    transaction.on_commit(lambda: process_cv.delay(str(application.id)))


def _submission_result(*, application: Application, prescan_session: Interview) -> dict:
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

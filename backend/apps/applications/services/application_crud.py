from uuid import UUID

from django.db import IntegrityError

from apps.accounts.models import User
from apps.applications.models import Application
from apps.applications.services.application_reopen import (
    can_reopen_application,
    get_existing_application,
    reopen_application,
)
from apps.applications.services.application_submit_helpers import (
    enqueue_cv_processing,
    notify_candidate_prescanning_ready,
    notify_hr_application_received,
    submission_result,
    sync_candidate_base,
)
from apps.applications.services.cv_selection import get_candidate_platform_cv, is_candidate_platform_cv_file
from apps.applications.services.profile_cv_snapshot import (
    apply_candidate_profile_cv_snapshot,
    build_candidate_profile_cv_snapshot,
)
from apps.common.exceptions import ApplicationError
from apps.common.language import resolve_interview_language
from apps.common.messages import (
    MSG_ALREADY_APPLIED,
    MSG_CV_OR_LINKEDIN_NOT_BOTH,
    MSG_CV_REQUIRED,
    MSG_PRESCREEN_CONSENT_REQUIRED,
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
    profile_photo: str = "",
    linkedin_url: str = "",
    cover_note: str = "",
    prescreen_consent: bool = False,
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

    # Web apply requires explicit consent to AI pre-screening.
    # The Telegram flow only collects name/contact/CV, so it is exempt.
    if channel == "web" and not prescreen_consent:
        raise ApplicationError(str(MSG_PRESCREEN_CONSENT_REQUIRED))

    # CV-or-LinkedIn are mutually exclusive on the web path: a candidate
    # provides one or the other, not both.
    if channel == "web" and cv_file_path and linkedin_url:
        raise ApplicationError(str(MSG_CV_OR_LINKEDIN_NOT_BOTH))

    if not cv_file_path:
        cv_file_path, cv_original_filename = get_candidate_platform_cv(candidate=candidate)

    should_snapshot_profile = not cv_file_path or is_candidate_platform_cv_file(
        candidate=candidate,
        cv_file_path=cv_file_path,
    )
    profile_snapshot = build_candidate_profile_cv_snapshot(candidate=candidate) if should_snapshot_profile else None

    if vacancy.cv_required and not cv_file_path and profile_snapshot is None:
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
            profile_photo=profile_photo,
            linkedin_url=linkedin_url,
            cover_note=cover_note,
            prescreen_consent=prescreen_consent,
            channel=channel,
        )
        snapshot_applied = apply_candidate_profile_cv_snapshot(application=application, snapshot=profile_snapshot)
        enqueue_cv_processing(application=application, cv_file_path=cv_file_path, snapshot_applied=snapshot_applied)
        sync_candidate_base(application=application)
        notify_candidate_prescanning_ready(application=application, prescan_session=prescan_session)
        notify_hr_application_received(application=application)
        return submission_result(application=application, prescan_session=prescan_session)

    try:
        application = Application.objects.create(
            vacancy=vacancy,
            candidate=candidate,
            candidate_name=candidate_name,
            candidate_email=candidate_email,
            candidate_phone=candidate_phone,
            cv_file=cv_file_path,
            cv_original_filename=cv_original_filename,
            profile_photo=profile_photo,
            linkedin_url=linkedin_url,
            cover_note=cover_note,
            prescreen_consent=prescreen_consent,
        )
    except IntegrityError:
        raise ApplicationError(str(MSG_ALREADY_APPLIED)) from None

    snapshot_applied = apply_candidate_profile_cv_snapshot(application=application, snapshot=profile_snapshot)
    enqueue_cv_processing(application=application, cv_file_path=cv_file_path, snapshot_applied=snapshot_applied)

    # Create prescanning session immediately (always chat mode)
    prescan_session = Interview.objects.create(
        application=application,
        session_type=Interview.SessionType.PRESCANNING,
        screening_mode=Interview.ScreeningMode.CHAT,
        status=Interview.Status.PENDING,
        language=vacancy.prescanning_language,
        channel=channel,
    )

    if vacancy.interview_enabled:
        create_interview_session(application=application)

    sync_candidate_base(application=application)
    notify_candidate_prescanning_ready(application=application, prescan_session=prescan_session)
    notify_hr_application_received(application=application)
    return submission_result(application=application, prescan_session=prescan_session)


def create_interview_session(*, application: Application) -> Interview | None:
    """Create an interview session for a prescanned application.

    Only creates if the vacancy has interview_enabled=True.
    Returns the new Interview session or None if interview not enabled.
    """
    vacancy = application.vacancy
    if not vacancy.interview_enabled:
        return None

    existing = (
        application.sessions.filter(
            session_type=Interview.SessionType.INTERVIEW,
        )
        .exclude(status=Interview.Status.CANCELLED)
        .order_by("-created_at")
        .first()
    )
    if existing is not None:
        return existing

    interview_kwargs: dict = {
        "application": application,
        "session_type": Interview.SessionType.INTERVIEW,
        "screening_mode": Interview.ScreeningMode.MEET,
        "status": Interview.Status.PENDING,
        "language": resolve_interview_language(vacancy.prescanning_language),
    }

    interview = Interview.objects.create(**interview_kwargs)
    interview.livekit_room_name = f"interview-{interview.id}"
    interview.save(update_fields=["livekit_room_name", "updated_at"])
    return interview

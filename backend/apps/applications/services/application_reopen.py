from django.utils import timezone

from apps.accounts.models import User
from apps.applications.models import Application
from apps.interviews.models import Interview
from apps.vacancies.models import Vacancy


def can_reopen_application(application: Application) -> bool:
    return application.is_deleted or application.status == Application.Status.ARCHIVED


def get_existing_application(*, vacancy: Vacancy, candidate_email: str) -> Application | None:
    return Application.objects.filter(vacancy=vacancy, candidate_email=candidate_email).first()


def reopen_application(
    *,
    application: Application,
    candidate_name: str,
    candidate_email: str,
    candidate_phone: str,
    cv_file_path: str,
    cv_original_filename: str,
    candidate: User | None,
    channel: str,
) -> tuple[Application, Interview]:
    application.sessions.exclude(
        status__in=[Interview.Status.COMPLETED, Interview.Status.CANCELLED, Interview.Status.EXPIRED],
    ).update(status=Interview.Status.CANCELLED)

    now = timezone.now()
    application.candidate = candidate or application.candidate
    application.candidate_name = candidate_name
    application.candidate_email = candidate_email
    application.candidate_phone = candidate_phone
    application.cv_file = cv_file_path
    application.cv_original_filename = cv_original_filename
    application.cv_parsed_text = ""
    application.cv_parsed_data = {}
    application.match_score = None
    application.match_details = {}
    application.match_notes_translations = {}
    application.cv_summary_translations = {}
    application.status = Application.Status.APPLIED
    application.is_deleted = False
    application.hr_notes = ""
    application.created_at = now
    application.save(
        update_fields=[
            "candidate",
            "candidate_name",
            "candidate_email",
            "candidate_phone",
            "cv_file",
            "cv_original_filename",
            "cv_parsed_text",
            "cv_parsed_data",
            "match_score",
            "match_details",
            "match_notes_translations",
            "cv_summary_translations",
            "status",
            "is_deleted",
            "hr_notes",
            "created_at",
            "updated_at",
        ],
    )

    prescan_session = Interview.objects.create(
        application=application,
        session_type=Interview.SessionType.PRESCANNING,
        screening_mode=Interview.ScreeningMode.CHAT,
        status=Interview.Status.PENDING,
        language=application.vacancy.prescanning_language,
        channel=channel,
    )
    return application, prescan_session

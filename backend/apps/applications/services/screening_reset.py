from django.db import transaction

from apps.applications.models import Application
from apps.applications.services.application_crud import create_interview_session
from apps.interviews.models import Interview


@transaction.atomic
def reset_application_screening(*, application: Application, session_type: str) -> Application:
    """Clear a candidate screening step and create a fresh pending link."""
    if session_type == Interview.SessionType.PRESCANNING:
        application.sessions.filter(
            session_type__in=[
                Interview.SessionType.PRESCANNING,
                Interview.SessionType.INTERVIEW,
            ],
        ).delete()
        application.status = Application.Status.APPLIED
        application.save(update_fields=["status", "updated_at"])
        Interview.objects.create(
            application=application,
            session_type=Interview.SessionType.PRESCANNING,
            screening_mode=Interview.ScreeningMode.CHAT,
            status=Interview.Status.PENDING,
            language=application.vacancy.prescanning_language,
            channel=Interview.Channel.WEB,
        )
        create_interview_session(application=application)
        return application

    application.sessions.filter(session_type=Interview.SessionType.INTERVIEW).delete()
    if application.status != Application.Status.APPLIED:
        application.status = Application.Status.PRESCANNED
        application.save(update_fields=["status", "updated_at"])
    create_interview_session(application=application)
    return application

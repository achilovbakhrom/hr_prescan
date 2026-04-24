from apps.accounts.models import User
from apps.applications.models import Application
from apps.common.exceptions import ApplicationError
from apps.common.messages import MSG_STATUS_TRANSITION_INVALID
from apps.interviews.models import Interview

STATUS_TRANSITIONS: dict[str, set[str]] = {
    Application.Status.APPLIED: {
        Application.Status.PRESCANNED,
        Application.Status.SHORTLISTED,
        Application.Status.HIRED,
        Application.Status.REJECTED,
        Application.Status.ARCHIVED,
        Application.Status.EXPIRED,
    },
    Application.Status.PRESCANNED: {
        Application.Status.INTERVIEWED,
        Application.Status.SHORTLISTED,
        Application.Status.HIRED,
        Application.Status.REJECTED,
        Application.Status.ARCHIVED,
        Application.Status.APPLIED,
        Application.Status.EXPIRED,
    },
    Application.Status.INTERVIEWED: {
        Application.Status.SHORTLISTED,
        Application.Status.HIRED,
        Application.Status.REJECTED,
        Application.Status.ARCHIVED,
        Application.Status.PRESCANNED,
    },
    Application.Status.SHORTLISTED: {
        Application.Status.HIRED,
        Application.Status.REJECTED,
        Application.Status.ARCHIVED,
        Application.Status.APPLIED,
    },
    Application.Status.HIRED: {Application.Status.ARCHIVED},
    Application.Status.REJECTED: {Application.Status.APPLIED, Application.Status.ARCHIVED},
    Application.Status.EXPIRED: {Application.Status.APPLIED, Application.Status.ARCHIVED},
    Application.Status.ARCHIVED: {Application.Status.APPLIED},
}


def update_application_status(*, application: Application, status: str, updated_by: User) -> Application:
    current = application.status
    allowed = STATUS_TRANSITIONS.get(current, set())

    if status not in allowed:
        raise ApplicationError(str(MSG_STATUS_TRANSITION_INVALID).format(current=current, target=status))

    if status == Application.Status.APPLIED and current != Application.Status.APPLIED:
        _reset_pipeline(application=application)

    application.status = status
    application.save(update_fields=["status", "updated_at"])
    return application


def _reset_pipeline(*, application: Application) -> None:
    application.sessions.exclude(
        status__in=[Interview.Status.COMPLETED, Interview.Status.CANCELLED, Interview.Status.EXPIRED],
    ).update(status=Interview.Status.CANCELLED)

    Interview.objects.create(
        application=application,
        session_type=Interview.SessionType.PRESCANNING,
        screening_mode=Interview.ScreeningMode.CHAT,
        status=Interview.Status.PENDING,
    )

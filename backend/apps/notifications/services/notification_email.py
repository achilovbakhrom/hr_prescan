from django.db.models import QuerySet

from apps.accounts.models import Company, User
from apps.applications.models import Application
from apps.interviews.models import Interview
from apps.notifications.models import Notification
from apps.notifications.services.notification_crud import create_notification

# ---------------------------------------------------------------------------
# Recipient resolution
# ---------------------------------------------------------------------------


def _hr_recipients(*, company: Company) -> QuerySet[User]:
    """Active HR/admin users who hold a membership in ``company``.

    Membership is the source of truth, not the user's live active-company pointer
    (``User.company``): a multi-company HR/admin currently switched into a different
    company (or candidate mode) must still receive the company's notifications.
    """
    return (
        User.objects.filter(
            memberships__company=company,
            memberships__role__in=[User.Role.HR, User.Role.ADMIN],
            is_active=True,
        )
        .distinct()
    )


# ---------------------------------------------------------------------------
# Domain-specific notification creators
# ---------------------------------------------------------------------------


def notify_application_received(*, application: Application) -> None:
    """Create notification for all HR users in the company when a new application arrives."""
    company = application.vacancy.company
    hr_users = _hr_recipients(company=company)

    for user in hr_users:
        create_notification(
            user=user,
            type=Notification.Type.APPLICATION_RECEIVED,
            title="New Application Received",
            message=(f"{application.candidate_name} applied for {application.vacancy.title}."),
            data={
                "application_id": str(application.id),
                "vacancy_id": str(application.vacancy_id),
            },
        )


def notify_interview_ready(*, interview: Interview) -> None:
    """Notify candidate and HR users when an interview is ready."""
    application = interview.application
    company = application.vacancy.company

    # Notify candidate (if they have an account)
    if application.candidate:
        create_notification(
            user=application.candidate,
            type=Notification.Type.INTERVIEW_SCHEDULED,
            title="Interview Ready",
            message=(
                f"Your interview for {application.vacancy.title} is ready. "
                f"Start whenever you're ready using the interview link."
            ),
            data={
                "interview_id": str(interview.id),
                "application_id": str(application.id),
                "interview_token": str(interview.interview_token),
            },
        )

    # Notify HR users
    hr_users = _hr_recipients(company=company)
    for user in hr_users:
        create_notification(
            user=user,
            type=Notification.Type.INTERVIEW_SCHEDULED,
            title="New Application",
            message=(
                f"New application from {application.candidate_name} ({application.vacancy.title}). Interview link sent."
            ),
            data={
                "interview_id": str(interview.id),
                "application_id": str(application.id),
            },
        )


def notify_session_completed(*, interview: Interview) -> None:
    """Notify HR users (in-app + email) when an AI screening session completes.

    Handles both prescanning and interview sessions, including the score
    summary. The matching Telegram push is fired separately by the caller.
    """
    application = interview.application
    company = application.vacancy.company

    is_prescanning = interview.session_type == Interview.SessionType.PRESCANNING
    step_label = "prescanning" if is_prescanning else "interview"
    title = "Prescanning Completed" if is_prescanning else "Interview Completed"
    score = interview.overall_score

    hr_users = _hr_recipients(company=company)

    for user in hr_users:
        create_notification(
            user=user,
            type=Notification.Type.INTERVIEW_COMPLETED,
            title=title,
            message=(
                f"{application.candidate_name} completed {step_label} for "
                f"{application.vacancy.title}. Score: {score}."
            ),
            data={
                "interview_id": str(interview.id),
                "application_id": str(application.id),
                "session_type": interview.session_type,
                "overall_score": str(score) if score is not None else None,
            },
        )


# Backwards-compatible alias: the interview step specifically.
notify_interview_completed = notify_session_completed


def notify_status_changed(*, application: Application) -> None:
    """Notify candidate when their application status changes.

    Account candidates get an in-app notification plus the queued email
    (via create_notification). Anonymous applicants (no linked account,
    only candidate_email) receive the same status-change email directly.
    """
    title = "Application Status Updated"
    message = (
        f"Your application for {application.vacancy.title} "
        f"has been updated to: {application.get_status_display()}."
    )

    if application.candidate:
        create_notification(
            user=application.candidate,
            type=Notification.Type.STATUS_CHANGED,
            title=title,
            message=message,
            data={
                "application_id": str(application.id),
                "vacancy_id": str(application.vacancy_id),
                "new_status": application.status,
            },
        )
        return

    if not application.candidate_email:
        return

    from apps.notifications.tasks import send_status_change_email

    send_status_change_email.delay(
        to=application.candidate_email,
        subject=title,
        title=title,
        message=message,
        application_id=str(application.id),
    )

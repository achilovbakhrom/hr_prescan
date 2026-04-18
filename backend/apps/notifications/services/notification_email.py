from apps.accounts.models import User
from apps.applications.models import Application
from apps.interviews.models import Interview
from apps.notifications.models import Notification
from apps.notifications.services.notification_crud import create_notification

# ---------------------------------------------------------------------------
# Domain-specific notification creators
# ---------------------------------------------------------------------------


def notify_application_received(*, application: Application) -> None:
    """Create notification for all HR users in the company when a new application arrives."""
    company = application.vacancy.company
    hr_users = User.objects.filter(
        company=company,
        role__in=[User.Role.HR, User.Role.ADMIN],
        is_active=True,
    )

    for user in hr_users:
        create_notification(
            user=user,
            notification_type=Notification.Type.APPLICATION_RECEIVED,
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
            notification_type=Notification.Type.INTERVIEW_SCHEDULED,
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
    hr_users = User.objects.filter(
        company=company,
        role__in=[User.Role.HR, User.Role.ADMIN],
        is_active=True,
    )
    for user in hr_users:
        create_notification(
            user=user,
            notification_type=Notification.Type.INTERVIEW_SCHEDULED,
            title="New Application",
            message=(
                f"New application from {application.candidate_name} ({application.vacancy.title}). Interview link sent."
            ),
            data={
                "interview_id": str(interview.id),
                "application_id": str(application.id),
            },
        )


def notify_interview_completed(*, interview: Interview) -> None:
    """Notify HR users when an interview is completed."""
    application = interview.application
    company = application.vacancy.company

    hr_users = User.objects.filter(
        company=company,
        role__in=[User.Role.HR, User.Role.ADMIN],
        is_active=True,
    )

    for user in hr_users:
        create_notification(
            user=user,
            notification_type=Notification.Type.INTERVIEW_COMPLETED,
            title="Interview Completed",
            message=(
                f"{application.candidate_name} completed the interview for "
                f"{application.vacancy.title}. Score: {interview.overall_score}."
            ),
            data={
                "interview_id": str(interview.id),
                "application_id": str(application.id),
                "overall_score": str(interview.overall_score) if interview.overall_score else None,
            },
        )


def notify_status_changed(*, application: Application) -> None:
    """Notify candidate when their application status changes."""
    if not application.candidate:
        return

    create_notification(
        user=application.candidate,
        notification_type=Notification.Type.STATUS_CHANGED,
        title="Application Status Updated",
        message=(
            f"Your application for {application.vacancy.title} has been updated to: {application.get_status_display()}."
        ),
        data={
            "application_id": str(application.id),
            "vacancy_id": str(application.vacancy_id),
            "new_status": application.status,
        },
    )

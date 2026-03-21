import logging
from uuid import UUID

from django.db.models import QuerySet

from apps.accounts.models import User
from apps.applications.models import Application
from apps.interviews.models import Interview
from apps.notifications.models import Message, Notification

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Core notification helpers
# ---------------------------------------------------------------------------


def create_notification(
    *,
    user: User,
    type: str,
    title: str,
    message: str,
    data: dict | None = None,
) -> Notification:
    """Create a notification for a user and queue an email task."""
    notification = Notification.objects.create(
        user=user,
        type=type,
        title=title,
        message=message,
        data=data or {},
    )

    from apps.notifications.tasks import send_email_notification

    send_email_notification.delay(str(notification.id))

    return notification


def mark_as_read(*, notification: Notification) -> Notification:
    """Mark a single notification as read."""
    if not notification.is_read:
        notification.is_read = True
        notification.save(update_fields=["is_read", "updated_at"])
    return notification


def mark_all_as_read(*, user: User) -> int:
    """Mark all unread notifications for a user as read. Returns count."""
    return Notification.objects.filter(user=user, is_read=False).update(is_read=True)


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
            type=Notification.Type.APPLICATION_RECEIVED,
            title="New Application Received",
            message=(
                f"{application.candidate_name} applied for "
                f"{application.vacancy.title}."
            ),
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
    hr_users = User.objects.filter(
        company=company,
        role__in=[User.Role.HR, User.Role.ADMIN],
        is_active=True,
    )
    for user in hr_users:
        create_notification(
            user=user,
            type=Notification.Type.INTERVIEW_SCHEDULED,
            title="New Application",
            message=(
                f"New application from {application.candidate_name} "
                f"({application.vacancy.title}). Interview link sent."
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
            type=Notification.Type.INTERVIEW_COMPLETED,
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
        type=Notification.Type.STATUS_CHANGED,
        title="Application Status Updated",
        message=(
            f"Your application for {application.vacancy.title} "
            f"has been updated to: {application.get_status_display()}."
        ),
        data={
            "application_id": str(application.id),
            "vacancy_id": str(application.vacancy_id),
            "new_status": application.status,
        },
    )


# ---------------------------------------------------------------------------
# Messaging
# ---------------------------------------------------------------------------


def send_message(
    *,
    sender: User,
    recipient: User,
    content: str,
    application: Application | None = None,
) -> Message:
    """Send a direct message from one user to another."""
    return Message.objects.create(
        sender=sender,
        recipient=recipient,
        application=application,
        content=content,
    )


def get_message_thread(
    *,
    user: User,
    other_user: User,
    application: Application | None = None,
) -> QuerySet[Message]:
    """Return the message thread between two users, optionally scoped to an application."""
    from django.db.models import Q

    qs = Message.objects.filter(
        Q(sender=user, recipient=other_user) | Q(sender=other_user, recipient=user)
    )

    if application is not None:
        qs = qs.filter(application=application)

    return qs.select_related("sender", "recipient")


def mark_messages_as_read(*, user: User, other_user: User) -> int:
    """Mark all messages from other_user to user as read."""
    return Message.objects.filter(
        sender=other_user,
        recipient=user,
        is_read=False,
    ).update(is_read=True)

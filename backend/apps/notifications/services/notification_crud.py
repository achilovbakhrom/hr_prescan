import logging

from django.db.models import QuerySet

from apps.accounts.models import User
from apps.applications.models import Application
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

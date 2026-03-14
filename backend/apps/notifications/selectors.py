from django.db.models import QuerySet

from apps.accounts.models import User
from apps.notifications.models import Notification


def get_user_notifications(
    *,
    user: User,
    unread_only: bool = False,
) -> QuerySet[Notification]:
    """Return notifications for a user, optionally only unread ones."""
    qs = Notification.objects.filter(user=user)
    if unread_only:
        qs = qs.filter(is_read=False)
    return qs


def get_unread_count(*, user: User) -> int:
    """Return the number of unread notifications for a user."""
    return Notification.objects.filter(user=user, is_read=False).count()

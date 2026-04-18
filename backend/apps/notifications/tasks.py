import logging

from celery import shared_task
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task
def send_email_notification(notification_id: str) -> None:
    """Send an email for an in-app notification."""
    from apps.common.email import send_templated_email
    from apps.notifications.models import Notification

    try:
        notification = Notification.objects.select_related("user").get(id=notification_id)
    except Notification.DoesNotExist:
        logger.error("send_email_notification: notification %s not found", notification_id)
        return

    action_url = ""
    data = notification.data or {}
    if data.get("application_id"):
        action_url = f"{settings.FRONTEND_URL}/candidates/{data['application_id']}"
    elif data.get("interview_id"):
        action_url = f"{settings.FRONTEND_URL}/interviews/{data['interview_id']}"

    send_templated_email(
        to=notification.user.email,
        subject=notification.title,
        template="notification",
        context={
            "notification_title": notification.title,
            "notification_message": notification.message,
            "action_url": action_url,
        },
    )


@shared_task
def send_candidate_email(application_id: str, subject: str, body: str) -> None:
    """Send a custom email from HR to a candidate."""
    from apps.applications.models import Application
    from apps.common.email import send_templated_email

    try:
        application = Application.objects.select_related("vacancy__company").get(id=application_id)
    except Application.DoesNotExist:
        logger.error("send_candidate_email: application %s not found", application_id)
        return

    send_templated_email(
        to=application.candidate_email,
        subject=subject,
        template="candidate_email",
        context={
            "candidate_name": application.candidate_name,
            "email_subject": subject,
            "email_body": body,
            "vacancy_title": application.vacancy.title,
            "company_name": application.vacancy.company.name,
        },
    )

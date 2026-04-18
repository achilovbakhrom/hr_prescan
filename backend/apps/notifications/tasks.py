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
def notify_hr_company_telegram(
    company_id: str,
    application_id: str,
    candidate_name: str,
    vacancy_title: str,
    session_type: str,
    overall_score: float,
) -> None:
    """Push a Telegram message to all HR users in a company when a session completes."""
    from apps.accounts.models import User
    from apps.integrations.telegram_bot.bots import ROLE_HR, get_client

    hr_users = list(
        User.objects.filter(
            company_id=company_id,
            role=User.Role.HR,
            telegram_id__isnull=False,
        ).exclude(telegram_id=0)
    )
    if not hr_users:
        return

    client = get_client(role=ROLE_HR)
    label = "Prescanning result" if session_type == "prescanning" else "Interview result"
    candidate_url = f"{settings.FRONTEND_URL}/candidates/{application_id}"
    msg = (
        f"🔔 *{label}*\n\n"
        f"*{candidate_name}* completed {session_type} for *{vacancy_title}*\n"
        f"Score: *{overall_score:.1f}/10*\n\n"
        f"[View candidate →]({candidate_url})"
    )
    for user in hr_users:
        try:
            client.send_message(
                chat_id=user.telegram_id,
                text=msg,
                parse_mode="Markdown",
                disable_web_page_preview=True,
            )
        except Exception as exc:
            logger.warning("Telegram push failed for HR user %s: %s", user.id, exc)


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

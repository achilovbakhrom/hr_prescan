import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def send_email_notification(notification_id: str) -> None:
    """Send an email for a notification.

    STUB: Logs the event. Real implementation will send via email service.
    """
    logger.info("Notification %s: email notification sent (stub).", notification_id)


@shared_task
def send_candidate_email(application_id: str, subject: str, body: str) -> None:
    """Send a custom email to a candidate.

    STUB: Logs the event. Real implementation will send via email service.
    """
    logger.info(
        "Application %s: sending email to candidate — subject: %s (stub).",
        application_id,
        subject,
    )

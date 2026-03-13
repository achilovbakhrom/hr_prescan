import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def send_scheduling_confirmation_email(interview_id: str) -> None:
    """Send confirmation email when an interview is scheduled.

    STUB: Logs the event. Real implementation will send via email service.
    """
    logger.info("Interview %s: scheduling confirmation email sent.", interview_id)


@shared_task
def send_interview_reminder(interview_id: str) -> None:
    """Send a reminder email before an upcoming interview.

    STUB: Logs the event. Real implementation will send via email service.
    """
    logger.info("Interview %s: reminder email sent.", interview_id)


@shared_task
def check_upcoming_interviews() -> None:
    """Celery Beat task: find interviews in the next hour and send reminders.

    For each upcoming scheduled interview, triggers send_interview_reminder.
    """
    from apps.interviews.selectors import get_upcoming_interviews

    upcoming = get_upcoming_interviews(hours_ahead=1)
    count = 0
    for interview in upcoming:
        send_interview_reminder.delay(str(interview.id))
        count += 1

    if count:
        logger.info("Triggered reminders for %d upcoming interviews.", count)

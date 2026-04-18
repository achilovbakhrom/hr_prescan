import logging

from celery import shared_task
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task
def evaluate_telegram_interview(interview_id: str) -> None:
    """Evaluate a Telegram-based prescreening interview with Gemini and complete it."""
    from apps.interviews.chat_service.evaluation import evaluate_chat_interview
    from apps.interviews.models import Interview

    try:
        interview = Interview.objects.select_related(
            "application__vacancy__company",
            "application__vacancy__employer",
        ).get(id=interview_id)
    except Interview.DoesNotExist:
        logger.error("evaluate_telegram_interview: session %s not found", interview_id)
        return

    evaluate_chat_interview(interview)
    logger.info("evaluate_telegram_interview: completed for session %s", interview_id)


@shared_task
def send_scheduling_confirmation_email(interview_id: str) -> None:
    """Send confirmation email when an interview is scheduled."""
    from apps.common.email import send_templated_email
    from apps.interviews.models import Interview

    try:
        interview = Interview.objects.select_related(
            "application__vacancy__company",
        ).get(id=interview_id)
    except Interview.DoesNotExist:
        logger.error("send_scheduling_confirmation_email: interview %s not found", interview_id)
        return

    application = interview.application
    vacancy = application.vacancy
    interview_url = f"{settings.FRONTEND_URL}/interview/{interview.interview_token}"

    send_templated_email(
        to=application.candidate_email,
        subject=f"Interview Scheduled - {vacancy.title}",
        template="interview_scheduled",
        context={
            "candidate_name": application.candidate_name,
            "vacancy_title": vacancy.title,
            "company_name": vacancy.company.name,
            "scheduled_at": interview.scheduled_at.strftime("%B %d, %Y at %H:%M UTC")
            if interview.scheduled_at
            else "TBD",
            "duration": vacancy.interview_duration or 30,
            "interview_url": interview_url,
        },
    )


@shared_task
def send_interview_reminder(interview_id: str) -> None:
    """Send a reminder email before an upcoming interview."""
    from apps.common.email import send_templated_email
    from apps.interviews.models import Interview

    try:
        interview = Interview.objects.select_related(
            "application__vacancy__company",
        ).get(id=interview_id)
    except Interview.DoesNotExist:
        logger.error("send_interview_reminder: interview %s not found", interview_id)
        return

    application = interview.application
    vacancy = application.vacancy
    interview_url = f"{settings.FRONTEND_URL}/interview/{interview.interview_token}"

    send_templated_email(
        to=application.candidate_email,
        subject=f"Interview Reminder - {vacancy.title}",
        template="interview_reminder",
        context={
            "candidate_name": application.candidate_name,
            "vacancy_title": vacancy.title,
            "scheduled_at": interview.scheduled_at.strftime("%B %d, %Y at %H:%M UTC")
            if interview.scheduled_at
            else "Soon",
            "interview_url": interview_url,
        },
    )


@shared_task
def check_upcoming_interviews() -> None:
    """Celery Beat task: find interviews in the next hour and send reminders."""
    from apps.interviews.selectors import get_upcoming_interviews

    upcoming = get_upcoming_interviews(hours_ahead=1)
    count = 0
    for interview in upcoming:
        send_interview_reminder.delay(str(interview.id))
        count += 1

    if count:
        logger.info("Triggered reminders for %d upcoming interviews.", count)

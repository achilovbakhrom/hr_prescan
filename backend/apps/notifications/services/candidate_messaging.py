import logging

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.applications.models import Application
from apps.common.exceptions import ApplicationError
from apps.notifications.models import Message, Notification

logger = logging.getLogger(__name__)

NO_PLATFORM_INBOX_MESSAGE = "Candidate has no platform inbox; use direct contact."


def send_candidate_message(
    *,
    sender: User,
    application: Application,
    content: str,
) -> Message:
    """Store an HR message, then deliver it via Telegram or web notification."""
    if application.candidate is None:
        raise ApplicationError(NO_PLATFORM_INBOX_MESSAGE, extra={"code": "candidate_no_platform_inbox"})

    candidate = application.candidate
    with transaction.atomic():
        message = Message.objects.create(
            sender=sender,
            recipient=candidate,
            application=application,
            content=content,
            delivery_channel=_delivery_channel(candidate=candidate),
        )
        notification = _create_direct_message_notification(message=message, application=application)

    if message.delivery_channel == Message.DeliveryChannel.TELEGRAM:
        _deliver_telegram(message=message, notification=notification)
    else:
        message.delivery_status = Message.DeliveryStatus.DELIVERED
        message.delivered_at = timezone.now()
        message.save(update_fields=["delivery_status", "delivered_at", "updated_at"])
        _sync_notification_delivery(notification=notification, message=message)

    return message


def _delivery_channel(*, candidate: User) -> str:
    return Message.DeliveryChannel.TELEGRAM if candidate.telegram_id else Message.DeliveryChannel.WEB


def _create_direct_message_notification(*, message: Message, application: Application) -> Notification:
    title = f"New message from {message.sender.full_name or message.sender.email}"
    return Notification.objects.create(
        user=message.recipient,
        type=Notification.Type.DIRECT_MESSAGE,
        title=title,
        message=message.content,
        data={
            "message_id": str(message.id),
            "application_id": str(application.id),
            "vacancy_title": application.vacancy.title,
            "delivery_channel": message.delivery_channel,
            "delivery_status": message.delivery_status,
        },
    )


def _deliver_telegram(*, message: Message, notification: Notification) -> None:
    from apps.integrations.telegram_bot.bots import ROLE_CANDIDATE, get_client

    candidate = message.recipient
    text = _telegram_message_text(message=message)
    try:
        response = get_client(role=ROLE_CANDIDATE).send_message(
            chat_id=candidate.telegram_id,
            text=text,
            parse_mode=None,
            disable_web_page_preview=True,
        )
    except Exception as exc:
        logger.warning("Candidate Telegram message failed for %s: %s", candidate.id, exc)
        _mark_failed(message=message, reason=str(exc))
        _sync_notification_delivery(notification=notification, message=message)
        return

    if response.get("ok"):
        result = response.get("result") or {}
        message.delivery_status = Message.DeliveryStatus.DELIVERED
        message.delivered_at = timezone.now()
        message.telegram_message_id = str(result.get("message_id") or "")
        message.delivery_failure_reason = ""
        message.save(
            update_fields=[
                "delivery_status",
                "delivered_at",
                "telegram_message_id",
                "delivery_failure_reason",
                "updated_at",
            ]
        )
    else:
        reason = response.get("description") or response.get("error") or "Telegram delivery failed."
        _mark_failed(message=message, reason=str(reason))
    _sync_notification_delivery(notification=notification, message=message)


def _mark_failed(*, message: Message, reason: str) -> None:
    message.delivery_status = Message.DeliveryStatus.FAILED
    message.delivery_failure_reason = reason[:2000]
    message.save(update_fields=["delivery_status", "delivery_failure_reason", "updated_at"])


def _sync_notification_delivery(*, notification: Notification, message: Message) -> None:
    data = dict(notification.data or {})
    data["delivery_status"] = message.delivery_status
    data["telegram_message_id"] = message.telegram_message_id
    data["delivery_failure_reason"] = message.delivery_failure_reason
    notification.data = data
    notification.save(update_fields=["data", "updated_at"])


def _telegram_message_text(*, message: Message) -> str:
    application = message.application
    vacancy_title = application.vacancy.title if application and application.vacancy else "your application"
    sender_name = message.sender.full_name or message.sender.email
    return f"New message from {sender_name} about {vacancy_title}:\n\n{message.content}"

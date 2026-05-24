import logging

from django.conf import settings
from django.utils import timezone

from apps.accounts.models import User
from apps.applications.models import Application
from apps.integrations.telegram_bot.bots import ROLE_CANDIDATE, get_client
from apps.interviews.models import Interview
from apps.notifications.models import Message, Notification

logger = logging.getLogger(__name__)

SYSTEM_MESSAGE_TEXT = {
    "prescanning_ready": {
        "en": "Your prescreening for {vacancy_title} is ready.\n\nStart here:\n{link}",
        "ru": "Ваш прескрининг на вакансию {vacancy_title} готов.\n\nНачните здесь:\n{link}",  # noqa: RUF001
        "uz": "{vacancy_title} vakansiyasi uchun preskrining tayyor.\n\nBu yerdan boshlang:\n{link}",
    },
    "interview_ready": {
        "en": "You advanced to the interview for {vacancy_title}.\n\nStart here:\n{link}",
        "ru": "Вы прошли на интервью по вакансии {vacancy_title}.\n\nНачните здесь:\n{link}",  # noqa: RUF001
        "uz": "{vacancy_title} vakansiyasi bo'yicha intervyuga o'tdingiz.\n\nBu yerdan boshlang:\n{link}",
    },
}

SYSTEM_MESSAGE_TITLES = {
    "prescanning_ready": {
        "en": "Prescreening ready",
        "ru": "Прескрининг готов",
        "uz": "Preskrining tayyor",
    },
    "interview_ready": {
        "en": "Interview ready",
        "ru": "Интервью готово",
        "uz": "Intervyu tayyor",
    },
}


def notify_candidate_prescanning_ready(
    *,
    application: Application,
    prescan_session: Interview,
) -> Notification | None:
    """Send the exact prescanning deep link through the candidate Telegram bot."""
    link = build_prescanning_deep_link(prescan_token=str(prescan_session.interview_token))
    if not link:
        return None
    return _send_candidate_system_message(
        application=application,
        interview=prescan_session,
        kind="prescanning_ready",
        link=link,
    )


def notify_candidate_interview_ready(
    *,
    application: Application,
    interview: Interview,
) -> Notification | None:
    """Send the web-only interview link through the candidate Telegram bot."""
    return _send_candidate_system_message(
        application=application,
        interview=interview,
        kind="interview_ready",
        link=build_interview_url(interview_token=str(interview.interview_token)),
    )


def build_prescanning_deep_link(*, prescan_token: str) -> str:
    username = _candidate_bot_username()
    if not username:
        logger.info("Candidate Telegram bot username is not configured; prescreen link was not sent.")
        return ""
    return f"https://t.me/{username}?start=ps_{prescan_token}"


def build_interview_url(*, interview_token: str) -> str:
    return f"{settings.FRONTEND_URL.rstrip('/')}/interview/{interview_token}"


def _send_candidate_system_message(
    *,
    application: Application,
    interview: Interview,
    kind: str,
    link: str,
) -> Notification | None:
    candidate = application.candidate
    if candidate is None:
        return None

    lang = _message_language(candidate=candidate)
    text = _localized_message(kind=kind, lang=lang, vacancy_title=application.vacancy.title, link=link)
    delivery_channel = Message.DeliveryChannel.WEB
    if _has_candidate_bot_join(candidate=candidate):
        delivery_channel = Message.DeliveryChannel.TELEGRAM
    notification = Notification.objects.create(
        user=candidate,
        type=Notification.Type.SYSTEM,
        title=_localized_title(kind=kind, lang=lang),
        message=text,
        data={
            "kind": kind,
            "application_id": str(application.id),
            "vacancy_id": str(application.vacancy_id),
            "interview_id": str(interview.id),
            "interview_token": str(interview.interview_token),
            "link": link,
            "delivery_channel": delivery_channel,
            "delivery_status": Message.DeliveryStatus.PENDING,
        },
    )

    if delivery_channel == Message.DeliveryChannel.WEB:
        _mark_delivery_delivered(notification=notification, telegram_message_id="")
        return notification

    try:
        result = get_client(role=ROLE_CANDIDATE).send_message(
            chat_id=candidate.telegram_id,
            text=text,
            parse_mode=None,
            disable_web_page_preview=True,
        )
    except Exception as exc:
        logger.warning("Failed to send candidate Telegram system message: %s", exc)
        _mark_delivery_failed(notification=notification, reason=str(exc))
        return notification

    if result.get("ok"):
        _mark_delivery_delivered(
            notification=notification,
            telegram_message_id=str(result.get("result", {}).get("message_id", "")),
        )
    else:
        _mark_delivery_failed(
            notification=notification,
            reason=str(result.get("description") or result.get("error") or "Telegram delivery failed"),
        )
    return notification


def _has_candidate_bot_join(*, candidate: User) -> bool:
    return bool(candidate.telegram_id)


def _candidate_bot_username() -> str:
    return (getattr(settings, "TELEGRAM_CANDIDATE_BOT_USERNAME", "") or "").strip().lstrip("@")


def _message_language(*, candidate: User) -> str:
    language = getattr(candidate, "language", "en") or "en"
    return language if language in SYSTEM_MESSAGE_TEXT["prescanning_ready"] else "en"


def _localized_message(*, kind: str, lang: str, vacancy_title: str, link: str) -> str:
    template = SYSTEM_MESSAGE_TEXT[kind].get(lang) or SYSTEM_MESSAGE_TEXT[kind]["en"]
    return template.format(vacancy_title=vacancy_title, link=link)


def _localized_title(*, kind: str, lang: str) -> str:
    return SYSTEM_MESSAGE_TITLES[kind].get(lang) or SYSTEM_MESSAGE_TITLES[kind]["en"]


def _mark_delivery_delivered(*, notification: Notification, telegram_message_id: str) -> None:
    notification.data = {
        **notification.data,
        "delivery_status": Message.DeliveryStatus.DELIVERED,
        "delivered_at": timezone.now().isoformat(),
        "telegram_message_id": telegram_message_id,
    }
    notification.save(update_fields=["data", "updated_at"])


def _mark_delivery_failed(*, notification: Notification, reason: str) -> None:
    notification.data = {
        **notification.data,
        "delivery_status": Message.DeliveryStatus.FAILED,
        "delivery_failure_reason": reason,
    }
    notification.save(update_fields=["data", "updated_at"])

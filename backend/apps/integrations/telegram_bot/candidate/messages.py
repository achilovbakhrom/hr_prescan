"""Candidate bot screen for recent HR messages."""

from __future__ import annotations

from apps.integrations.telegram_bot.i18n import t
from apps.integrations.telegram_bot.keyboards import button, inline_keyboard
from apps.notifications.models import Message

CB_MESSAGES = "cand:messages"


def show_recent_messages(*, client, chat_id: int, user, lang: str) -> None:
    messages = list(
        Message.objects.filter(recipient=user)
        .select_related("sender", "application", "application__vacancy")
        .order_by("-created_at")[:5]
    )
    if not messages:
        text = t("candidate.messages_empty", lang=lang)
    else:
        items = [_format_message(message=message) for message in messages]
        text = t("candidate.messages_title", lang=lang) + "\n\n" + "\n\n".join(items)
    client.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=None,
        reply_markup=inline_keyboard([[button(text=t("candidate.button_back", lang=lang), callback_data="cand:menu")]]),
    )


def _format_message(*, message: Message) -> str:
    sender_name = message.sender.full_name or message.sender.email
    vacancy_title = ""
    if message.application and message.application.vacancy:
        vacancy_title = f" ({message.application.vacancy.title})"
    created = message.created_at.strftime("%Y-%m-%d %H:%M")
    return f"{created} - {sender_name}{vacancy_title}:\n{message.content}"

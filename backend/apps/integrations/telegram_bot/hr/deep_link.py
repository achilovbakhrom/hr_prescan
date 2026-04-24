"""Confirmed HR/admin Telegram deep-link account linking."""

from __future__ import annotations

from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.integrations.models import TelegramLinkCode
from apps.integrations.telegram_bot.client import TelegramClient
from apps.integrations.telegram_bot.hr.i18n import text as hr_text
from apps.integrations.telegram_bot.hr.onboarding import is_hr_placeholder, merge_hr_placeholder
from apps.integrations.telegram_bot.keyboards import button, inline_keyboard

CB_LINK_PREFIX = "hr:link:"


def request_deep_link_confirmation(
    *,
    client: TelegramClient,
    chat_id: int,
    token: str,
    telegram_id: int | None = None,
) -> None:
    link = _get_deep_link(token=token)
    lang = _link_language(link=link, telegram_id=telegram_id)
    if link is None or link.user.role not in {User.Role.ADMIN, User.Role.HR}:
        client.send_message(
            chat_id=chat_id,
            text=hr_text("link_invalid", lang=lang),
        )
        return

    client.send_message(
        chat_id=chat_id,
        text=hr_text("link_confirm", lang=lang, email=link.user.email),
        reply_markup=inline_keyboard(
            [
                [button(text=hr_text("btn_connect", lang=lang), callback_data=f"{CB_LINK_PREFIX}ok:{token}")],
                [button(text=hr_text("btn_cancel", lang=lang), callback_data=f"{CB_LINK_PREFIX}no:{token}")],
            ]
        ),
    )


def handle_link_callback(
    *,
    client: TelegramClient,
    chat_id: int,
    telegram_id: int,
    telegram_username: str,
    data: str,
) -> bool:
    if not is_link_callback(data=data):
        return False

    parts = data.split(":", 3)
    lang = _telegram_language(telegram_id=telegram_id)
    if len(parts) != 4:
        client.send_message(chat_id=chat_id, text=hr_text("link_invalid", lang=lang))
        return True

    action, token = parts[2], parts[3]
    if action == "no":
        client.send_message(chat_id=chat_id, text=hr_text("link_cancelled", lang=lang))
        return True
    if action != "ok":
        client.send_message(chat_id=chat_id, text=hr_text("link_invalid", lang=lang))
        return True

    _try_deep_link(
        client=client,
        chat_id=chat_id,
        telegram_id=telegram_id,
        telegram_username=telegram_username,
        token=token,
    )
    return True


def is_link_callback(*, data: str) -> bool:
    return data.startswith(CB_LINK_PREFIX)


def _try_deep_link(
    *,
    client: TelegramClient,
    chat_id: int,
    telegram_id: int,
    telegram_username: str,
    token: str,
) -> None:
    try:
        with transaction.atomic():
            link = (
                TelegramLinkCode.objects.filter(
                    code=token,
                    is_used=False,
                    expires_at__gt=timezone.now(),
                )
                .select_related("user")
                .select_for_update()
                .first()
            )

            if link is None or link.user.role not in {User.Role.ADMIN, User.Role.HR}:
                lang = _telegram_language(telegram_id=telegram_id)
                client.send_message(
                    chat_id=chat_id,
                    text=hr_text("link_invalid", lang=lang),
                )
                return

            if not isinstance(telegram_id, int) or telegram_id <= 0:
                client.send_message(chat_id=chat_id, text=hr_text("telegram_invalid", user=link.user))
                return

            user = link.user
            existing = (
                User.objects.select_for_update()
                .filter(telegram_id=telegram_id, role__in=[User.Role.ADMIN, User.Role.HR])
                .exclude(id=user.id)
                .first()
            )
            if existing is not None:
                if not is_hr_placeholder(user=existing, telegram_id=telegram_id):
                    client.send_message(
                        chat_id=chat_id,
                        text=hr_text("link_conflict", user=existing),
                    )
                    return
                merge_hr_placeholder(source=existing, target=user)

            user.telegram_id = telegram_id
            user.telegram_username = telegram_username
            user.save(update_fields=["telegram_id", "telegram_username", "updated_at"])

            link.is_used = True
            link.save(update_fields=["is_used", "updated_at"])
    except IntegrityError:
        lang = _telegram_language(telegram_id=telegram_id)
        client.send_message(
            chat_id=chat_id,
            text=hr_text("link_conflict", lang=lang),
        )
        return

    company_name = user.company.name if user.company else ""
    client.send_message(
        chat_id=chat_id,
        text=hr_text("connected", user=user, email=user.email, company=f" ({company_name})" if company_name else ""),
    )


def _get_deep_link(*, token: str) -> TelegramLinkCode | None:
    return (
        TelegramLinkCode.objects.filter(
            code=token,
            is_used=False,
            expires_at__gt=timezone.now(),
        )
        .select_related("user")
        .first()
    )


def _link_language(*, link: TelegramLinkCode | None, telegram_id: int | None) -> str:
    if telegram_id:
        lang = _telegram_language(telegram_id=telegram_id)
        if lang:
            return lang
    return link.user.language if link is not None else User.Language.EN


def _telegram_language(*, telegram_id: int) -> str:
    user = User.objects.filter(telegram_id=telegram_id, role__in=[User.Role.ADMIN, User.Role.HR]).first()
    return user.language if user is not None else User.Language.EN

"""Candidate Telegram account linking and safe placeholder merges."""

from __future__ import annotations

from dataclasses import dataclass

from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.integrations.models import TelegramLinkCode
from apps.integrations.telegram_bot.candidate.merge import merge_candidate_accounts
from apps.integrations.telegram_bot.i18n import t
from apps.integrations.telegram_bot.keyboards import button, inline_keyboard

LINK_PAYLOAD_PREFIX = "link_"
CB_LINK_PREFIX = "cand:link:"


@dataclass(frozen=True)
class LinkResult:
    ok: bool
    merged: bool = False
    conflict: bool = False


def is_account_link_payload(*, payload: str) -> bool:
    return payload.startswith(LINK_PAYLOAD_PREFIX) and len(payload) > len(LINK_PAYLOAD_PREFIX)


def is_account_link_callback(*, data: str) -> bool:
    return data.startswith(CB_LINK_PREFIX)


def request_account_link(*, client, chat_id: int, telegram_id: int, payload: str, lang: str) -> bool:
    """Ask the Telegram user to confirm before linking a web candidate profile."""
    if not is_account_link_payload(payload=payload):
        return False

    token = payload.removeprefix(LINK_PAYLOAD_PREFIX)
    link = _get_valid_link(token=token)
    if link is None or link.user.role != User.Role.CANDIDATE:
        client.send_message(chat_id=chat_id, text=t("candidate.link_invalid", lang=lang))
        return True

    lang = _link_language(link=link, telegram_id=telegram_id, fallback=lang)
    client.send_message(
        chat_id=chat_id,
        text=t("candidate.link_confirm", lang=lang, email=link.user.email),
        reply_markup=inline_keyboard(
            [
                [button(text=t("candidate.btn_link_confirm", lang=lang), callback_data=f"{CB_LINK_PREFIX}ok:{token}")],
                [button(text=t("candidate.btn_link_cancel", lang=lang), callback_data=f"{CB_LINK_PREFIX}no:{token}")],
            ]
        ),
    )
    return True


def handle_account_link_callback(
    *,
    client,
    chat_id: int,
    telegram_id: int,
    telegram_username: str,
    data: str,
    lang: str,
) -> bool:
    """Handle confirm/cancel callbacks without creating a Telegram-only user first."""
    if not is_account_link_callback(data=data):
        return False

    parts = data.split(":", 3)
    if len(parts) != 4:
        client.send_message(chat_id=chat_id, text=t("candidate.link_invalid", lang=lang))
        return True

    action, token = parts[2], parts[3]
    link = _get_valid_link(token=token)
    if link is not None:
        lang = _link_language(link=link, telegram_id=telegram_id, fallback=lang)

    if action == "no":
        client.send_message(chat_id=chat_id, text=t("candidate.link_cancelled", lang=lang))
        return True
    if action != "ok":
        client.send_message(chat_id=chat_id, text=t("candidate.link_invalid", lang=lang))
        return True

    result = confirm_account_link(token=token, telegram_id=telegram_id, telegram_username=telegram_username)
    if result.ok:
        key = "candidate.link_merged" if result.merged else "candidate.link_success"
        client.send_message(chat_id=chat_id, text=t(key, lang=lang))
    elif result.conflict:
        client.send_message(chat_id=chat_id, text=t("candidate.link_conflict", lang=lang))
    else:
        client.send_message(chat_id=chat_id, text=t("candidate.link_invalid", lang=lang))
    return True


def confirm_account_link(*, token: str, telegram_id: int, telegram_username: str) -> LinkResult:
    try:
        with transaction.atomic():
            link = _get_valid_link_for_update(token=token)
            if link is None or link.user.role != User.Role.CANDIDATE:
                return LinkResult(ok=False)

            target = link.user
            existing = (
                User.objects.select_for_update()
                .filter(telegram_id=telegram_id)
                .exclude(id=target.id)
                .first()
            )
            if existing is not None:
                if not _is_mergeable_telegram_candidate(user=existing, telegram_id=telegram_id):
                    return LinkResult(ok=False, conflict=True)
                merge_candidate_accounts(source=existing, target=target)

            if target.telegram_id and target.telegram_id != telegram_id:
                return LinkResult(ok=False, conflict=True)

            target.telegram_id = telegram_id
            target.telegram_username = telegram_username
            fields = ["telegram_id", "telegram_username", "updated_at"]
            if existing and not target.phone and existing.phone:
                target.phone = existing.phone
                fields.append("phone")
            target.save(update_fields=fields)

            link.is_used = True
            link.save(update_fields=["is_used", "updated_at"])
            return LinkResult(ok=True, merged=existing is not None)
    except IntegrityError:
        return LinkResult(ok=False, conflict=True)


def _get_valid_link(*, token: str) -> TelegramLinkCode | None:
    return TelegramLinkCode.objects.select_related("user").filter(
        code=token,
        is_used=False,
        expires_at__gt=timezone.now(),
    ).first()


def _get_valid_link_for_update(*, token: str) -> TelegramLinkCode | None:
    return (
        TelegramLinkCode.objects.select_for_update()
        .select_related("user")
        .filter(code=token, is_used=False, expires_at__gt=timezone.now())
        .first()
    )


def _is_mergeable_telegram_candidate(*, user: User, telegram_id: int) -> bool:
    return (
        user.role == User.Role.CANDIDATE
        and user.email == f"tg_{telegram_id}@telegram.local"
        and user.telegram_id == telegram_id
    )


def _link_language(*, link: TelegramLinkCode, telegram_id: int, fallback: str) -> str:
    existing = User.objects.filter(telegram_id=telegram_id).only("language").first()
    if existing is not None and existing.language:
        return existing.language
    return link.user.language or fallback

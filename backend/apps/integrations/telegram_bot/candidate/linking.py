"""Candidate Telegram account linking and safe placeholder merges."""

from __future__ import annotations

from dataclasses import dataclass

from django.db import IntegrityError, transaction
from django.db.models import Q
from django.utils import timezone

from apps.accounts.models import CandidateProfile, User
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
    already_linked: bool = False


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
    if link is None or not _has_candidate_space(user=link.user):
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
        if result.already_linked:
            key = "candidate.link_already_connected_resume"
        else:
            key = "candidate.link_merged" if result.merged else "candidate.link_success"
        client.send_message(chat_id=chat_id, text=t(key, lang=lang))
        if result.already_linked:
            from apps.integrations.telegram_bot.candidate.menus import send_main_menu

            send_main_menu(client=client, chat_id=chat_id, lang=lang)
    elif result.conflict:
        client.send_message(chat_id=chat_id, text=t("candidate.link_conflict", lang=lang))
    else:
        client.send_message(chat_id=chat_id, text=t("candidate.link_invalid", lang=lang))
    return True


def confirm_account_link(*, token: str, telegram_id: int, telegram_username: str) -> LinkResult:
    try:
        with transaction.atomic():
            link = _get_valid_link_for_update(token=token)
            if link is None or not _has_candidate_space(user=link.user):
                return LinkResult(ok=False)

            target = link.user
            existing = _candidate_user_for_telegram_for_update(telegram_id=telegram_id, exclude_user_id=target.id)
            if existing is not None:
                if not _is_mergeable_telegram_candidate(user=existing, telegram_id=telegram_id):
                    if _has_candidate_space(user=existing):
                        return LinkResult(ok=True, already_linked=True)
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
    return (
        TelegramLinkCode.objects.select_related("user")
        .filter(
            code=token,
            is_used=False,
            expires_at__gt=timezone.now(),
        )
        .first()
    )


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


def _has_candidate_space(*, user: User) -> bool:
    return user.role == User.Role.CANDIDATE or CandidateProfile.objects.filter(user=user).exists()


def _candidate_user_for_telegram_for_update(*, telegram_id: int, exclude_user_id) -> User | None:
    existing = (
        User.objects.select_for_update()
        .filter(telegram_id=telegram_id, role=User.Role.CANDIDATE)
        .exclude(id=exclude_user_id)
        .first()
    )
    if existing is not None:
        return existing
    profile = (
        CandidateProfile.objects.select_for_update()
        .select_related("user")
        .filter(user__telegram_id=telegram_id)
        .exclude(user_id=exclude_user_id)
        .first()
    )
    return profile.user if profile is not None else None


def _link_language(*, link: TelegramLinkCode, telegram_id: int, fallback: str) -> str:
    existing = (
        User.objects.filter(telegram_id=telegram_id)
        .filter(Q(role=User.Role.CANDIDATE) | Q(candidate_profile__isnull=False))
        .only("language")
        .first()
    )
    if existing is not None and existing.language:
        return existing.language
    return link.user.language or fallback

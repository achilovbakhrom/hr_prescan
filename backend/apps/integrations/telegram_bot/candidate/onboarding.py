"""Required candidate bot onboarding: phone first, language second."""

from __future__ import annotations

import re

from apps.integrations.telegram_bot.bots import ROLE_CANDIDATE
from apps.integrations.telegram_bot.candidate.menus import send_main_menu
from apps.integrations.telegram_bot.candidate.states import (
    SK_PENDING_START_PAYLOAD,
    STATE_ONBOARD_PHONE,
)
from apps.integrations.telegram_bot.i18n import t
from apps.integrations.telegram_bot.sessions import get_session, update_session

_PHONE_RE = re.compile(r"^\+?[\d\s\-()]{7,20}$")


def is_required(*, user) -> bool:
    return not bool(user.phone) or not bool(user.onboarding_completed)


def handle_text(*, client, chat_id: int, user, text: str, session: dict, lang: str) -> bool:
    if not is_required(user=user):
        return False

    if text.startswith("/start "):
        update_session(
            role=ROLE_CANDIDATE,
            telegram_id=user.telegram_id,
            **{SK_PENDING_START_PAYLOAD: text[7:].strip()},
        )

    if not user.phone and (session.get("state") == STATE_ONBOARD_PHONE or _PHONE_RE.match(text.strip())):
        _handle_phone(client=client, chat_id=chat_id, user=user, text=text, lang=lang)
        return True

    if not user.phone:
        prompt_phone(client=client, chat_id=chat_id, user=user, lang=lang)
        return True

    from apps.integrations.telegram_bot.candidate.language_settings import send_language_picker

    send_language_picker(client=client, chat_id=chat_id, lang=lang)
    return True


def after_language_selected(*, client, chat_id: int, user, lang: str) -> bool:
    if not is_required(user=user):
        return False
    if not user.phone:
        prompt_phone(client=client, chat_id=chat_id, user=user, lang=lang)
        return True
    user.onboarding_completed = True
    user.save(update_fields=["onboarding_completed", "updated_at"])
    session = get_session(role=ROLE_CANDIDATE, telegram_id=user.telegram_id)
    pending_payload = session.get(SK_PENDING_START_PAYLOAD, "")
    update_session(role=ROLE_CANDIDATE, telegram_id=user.telegram_id, state="", **{SK_PENDING_START_PAYLOAD: None})
    client.send_message(chat_id=chat_id, text=t("candidate.onboard_complete", lang=lang))
    if pending_payload:
        from apps.integrations.telegram_bot.candidate.start import handle_start_command

        if handle_start_command(client=client, chat_id=chat_id, user=user, payload=pending_payload, lang=lang):
            return True
    send_main_menu(client=client, chat_id=chat_id, lang=lang)
    return True


def prompt_phone(*, client, chat_id: int, user, lang: str) -> None:
    update_session(role=ROLE_CANDIDATE, telegram_id=user.telegram_id, state=STATE_ONBOARD_PHONE)
    client.send_message(
        chat_id=chat_id,
        text=t("candidate.onboard_ask_phone", lang=lang),
        reply_markup=_phone_keyboard(lang=lang),
    )


def _handle_phone(*, client, chat_id: int, user, text: str, lang: str) -> None:
    phone = text.strip()
    if not _PHONE_RE.match(phone):
        client.send_message(chat_id=chat_id, text=t("candidate.reg_invalid_phone", lang=lang))
        return

    user.phone = phone
    user.onboarding_completed = False
    user.save(update_fields=["phone", "onboarding_completed", "updated_at"])
    update_session(role=ROLE_CANDIDATE, telegram_id=user.telegram_id, state="")
    client.send_message(
        chat_id=chat_id,
        text=t("candidate.onboard_phone_saved", lang=lang),
        reply_markup={"remove_keyboard": True},
    )

    from apps.integrations.telegram_bot.candidate.language_settings import send_language_picker

    send_language_picker(client=client, chat_id=chat_id, lang=lang)


def _phone_keyboard(*, lang: str) -> dict:
    return {
        "keyboard": [[{"text": t("candidate.btn_share_phone", lang=lang), "request_contact": True}]],
        "resize_keyboard": True,
        "one_time_keyboard": True,
        "input_field_placeholder": "+998901234567",
    }

"""Candidate bot — multi-step registration flow.

New users (no phone set) are walked through:
  1. Enter full name (FIO)
  2. Enter phone number
  → account updated, password generated and sent, main menu shown.
"""

from __future__ import annotations

import logging
import re

from apps.integrations.telegram_bot.candidate.auth import complete_registration
from apps.integrations.telegram_bot.candidate.states import (
    SK_REG_NAME,
    STATE_REG_NAME,
    STATE_REG_PHONE,
)
from apps.integrations.telegram_bot.i18n import t
from apps.integrations.telegram_bot.sessions import update_session

logger = logging.getLogger(__name__)

_PHONE_RE = re.compile(r"^\+?[\d\s\-()]{7,20}$")


def handle_registration_text(
    *,
    client,
    chat_id: int,
    user,
    text: str,
    session: dict,
    lang: str,
) -> None:
    """Route incoming text during the registration flow."""
    state = session.get("state")

    if state == STATE_REG_PHONE:
        _handle_phone(client=client, chat_id=chat_id, user=user, text=text, session=session, lang=lang)
    else:
        # STATE_REG_NAME or fresh session — always (re)start from name step
        if state != STATE_REG_NAME:
            update_session(role="candidate", telegram_id=user.telegram_id, state=STATE_REG_NAME)
        _handle_name(client=client, chat_id=chat_id, user=user, text=text, lang=lang)


def prompt_registration(*, client, chat_id: int, user, lang: str) -> None:
    """Send the name prompt and set state=reg_name. Called on /start for new users."""
    update_session(role="candidate", telegram_id=user.telegram_id, state=STATE_REG_NAME)
    client.send_message(chat_id=chat_id, text=t("candidate.reg_ask_name", lang=lang))


def _handle_name(*, client, chat_id: int, user, text: str, lang: str) -> None:
    words = text.strip().split()
    if len(words) < 2:
        client.send_message(chat_id=chat_id, text=t("candidate.reg_invalid_name", lang=lang))
        return

    full_name = " ".join(words)
    update_session(
        role="candidate",
        telegram_id=user.telegram_id,
        state=STATE_REG_PHONE,
        **{SK_REG_NAME: full_name},
    )
    client.send_message(
        chat_id=chat_id,
        text=t("candidate.reg_ask_phone", lang=lang, name=words[0]),
    )


def _handle_phone(
    *,
    client,
    chat_id: int,
    user,
    text: str,
    session: dict,
    lang: str,
) -> None:
    phone = text.strip()
    if not _PHONE_RE.match(phone):
        client.send_message(chat_id=chat_id, text=t("candidate.reg_invalid_phone", lang=lang))
        return

    full_name = session.get(SK_REG_NAME, "").strip()
    if not full_name:
        # Safety: shouldn't happen, restart from name
        update_session(role="candidate", telegram_id=user.telegram_id, state=STATE_REG_NAME)
        client.send_message(chat_id=chat_id, text=t("candidate.reg_ask_name", lang=lang))
        return

    password = complete_registration(user=user, full_name=full_name, phone=phone)

    # Clear registration session keys
    update_session(
        role="candidate",
        telegram_id=user.telegram_id,
        state="",
        **{SK_REG_NAME: None},
    )

    client.send_message(
        chat_id=chat_id,
        text=t("candidate.reg_complete", lang=lang, email=user.email, password=password),
        parse_mode="Markdown",
    )

    # Show main menu
    from apps.integrations.telegram_bot.candidate.menus import main_menu_keyboard

    client.send_message(
        chat_id=chat_id,
        text=t("candidate.main_menu", lang=lang),
        reply_markup=main_menu_keyboard(lang=lang),
    )

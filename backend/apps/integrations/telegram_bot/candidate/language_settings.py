"""Candidate bot language settings."""

from __future__ import annotations

from apps.accounts.models import User
from apps.integrations.telegram_bot.candidate.menus import CB_LANG, CB_LANG_PREFIX, language_keyboard, send_main_menu
from apps.integrations.telegram_bot.i18n import t


def is_language_callback(*, data: str) -> bool:
    return data == CB_LANG or data.startswith(CB_LANG_PREFIX)


def send_language_picker(*, client, chat_id: int, lang: str) -> None:
    client.send_message(
        chat_id=chat_id,
        text=t("candidate.language_prompt", lang=lang),
        reply_markup=language_keyboard(lang=lang),
    )


def handle_language_callback(*, client, chat_id: int, user: User, data: str, lang: str) -> None:
    if data == CB_LANG:
        send_language_picker(client=client, chat_id=chat_id, lang=lang)
        return

    language = data.removeprefix(CB_LANG_PREFIX)
    if language not in {User.Language.EN, User.Language.RU, User.Language.UZ}:
        send_language_picker(client=client, chat_id=chat_id, lang=lang)
        return

    user.language = language
    user.save(update_fields=["language", "updated_at"])
    client.send_message(chat_id=chat_id, text=t("candidate.language_saved", lang=language))
    from apps.integrations.telegram_bot.candidate.onboarding import after_language_selected

    if after_language_selected(client=client, chat_id=chat_id, user=user, lang=language):
        return
    send_main_menu(client=client, chat_id=chat_id, lang=language)

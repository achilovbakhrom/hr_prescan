"""Inline keyboards used by the candidate bot.

Callback grammar (always under 64 bytes — Telegram cap):
    cand:vac:apply:<uuid>   -> confirm apply on a vacancy (existing flow)
    cand:menu               -> back to main menu
    cand:ps:start           -> start prescreening flow
    cand:ps:name_confirm    -> confirm stored name
    cand:ps:name_change     -> change name
    cand:ps:phone_confirm   -> confirm stored phone
    cand:ps:phone_change    -> change phone
    cand:ps:cv_skip         -> skip optional CV
"""

from __future__ import annotations

from uuid import UUID

from apps.integrations.telegram_bot import keyboards as kb
from apps.integrations.telegram_bot.i18n import t

# Existing
CB_VAC_APPLY = "cand:vac:apply"
CB_MENU = "cand:menu"

# Prescreening
CB_PS_START = "cand:ps:start"
CB_PS_NAME_CONFIRM = "cand:ps:name_confirm"
CB_PS_NAME_CHANGE = "cand:ps:name_change"
CB_PS_PHONE_CONFIRM = "cand:ps:phone_confirm"
CB_PS_PHONE_CHANGE = "cand:ps:phone_change"
CB_PS_CV_SKIP = "cand:ps:cv_skip"


def main_menu_keyboard(*, lang: str) -> dict:
    return kb.inline_keyboard(
        [
            [
                kb.button(
                    text=t("candidate.btn_prescreening", lang=lang),
                    callback_data=CB_PS_START,
                )
            ],
        ]
    )


def vacancy_actions_keyboard(*, vacancy_id: UUID, lang: str) -> dict:
    """Apply / Back buttons shown under a vacancy card."""
    return kb.inline_keyboard(
        [
            [
                kb.button(
                    text=t("candidate.button_apply", lang=lang),
                    callback_data=f"{CB_VAC_APPLY}:{vacancy_id}",
                )
            ],
            [
                kb.button(
                    text=t("candidate.button_back", lang=lang),
                    callback_data=CB_MENU,
                )
            ],
        ]
    )


def confirm_name_keyboard(*, lang: str) -> dict:
    return kb.inline_keyboard(
        [
            [
                kb.button(text=t("candidate.btn_confirm", lang=lang), callback_data=CB_PS_NAME_CONFIRM),
                kb.button(text=t("candidate.btn_change", lang=lang), callback_data=CB_PS_NAME_CHANGE),
            ],
        ]
    )


def confirm_phone_keyboard(*, lang: str) -> dict:
    return kb.inline_keyboard(
        [
            [
                kb.button(text=t("candidate.btn_confirm", lang=lang), callback_data=CB_PS_PHONE_CONFIRM),
                kb.button(text=t("candidate.btn_change", lang=lang), callback_data=CB_PS_PHONE_CHANGE),
            ],
        ]
    )


def cv_keyboard(*, lang: str) -> dict:
    """Skip button for optional CV upload."""
    return kb.inline_keyboard(
        [
            [kb.button(text=t("candidate.btn_skip_cv", lang=lang), callback_data=CB_PS_CV_SKIP)],
        ]
    )


def parse_callback(*, data: str) -> tuple[str, str | None]:
    """Split a callback_data string into ``(action, arg)``.

    Examples:
        ``cand:vac:apply:abc-123`` -> ``("cand:vac:apply", "abc-123")``
        ``cand:menu``              -> ``("cand:menu", None)``
        ``cand:ps:start``          -> ``("cand:ps:start", None)``
    """
    if not data:
        return "", None
    parts = data.split(":", 3)
    if len(parts) >= 4:
        return ":".join(parts[:3]), parts[3]
    return data, None

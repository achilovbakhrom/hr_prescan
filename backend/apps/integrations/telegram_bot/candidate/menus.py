"""Inline keyboards used by the candidate bot.

Centralised here so callback_data conventions stay consistent across modules.

Callback grammar (always under 64 bytes — Telegram cap):
    cand:vac:apply:<uuid>    -> confirm apply on a vacancy
    cand:menu                -> back to main menu

PR2 will add more shapes (cand:vac:show, cand:apps:list, etc.) once the
candidate AI agent + job browser ship.
"""

from __future__ import annotations

from uuid import UUID

from apps.integrations.telegram_bot import keyboards as kb
from apps.integrations.telegram_bot.i18n import t

CB_VAC_APPLY = "cand:vac:apply"
CB_MENU = "cand:menu"


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


def parse_callback(*, data: str) -> tuple[str, str | None]:
    """Split a callback_data string into ``(action, arg)``.

    Examples:
        ``cand:vac:apply:abc-123`` -> ``("cand:vac:apply", "abc-123")``
        ``cand:menu``              -> ``("cand:menu", None)``
    """
    if not data:
        return "", None
    parts = data.split(":", 3)
    if len(parts) >= 4:
        return ":".join(parts[:3]), parts[3]
    return data, None

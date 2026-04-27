"""Inline keyboards used by the candidate bot."""

from __future__ import annotations

from uuid import UUID

from apps.accounts.models import User
from apps.integrations.telegram_bot import keyboards as kb
from apps.integrations.telegram_bot.i18n import t

CB_VAC_APPLY = "cand:vac:apply"
CB_MENU = "cand:menu"
CB_LANG = "cand:lang"
CB_LANG_PREFIX = "cand:lang:"
CB_JOB_SEARCH = "cand:jobs:search"
CB_CV = "cand:cv"
CB_CV_ASSISTANT = "cand:cv:assistant"
CB_CV_LIST = "cand:cv:list"
CB_CV_GENERATE = "cand:cv:generate"
CB_CV_UPLOAD = "cand:cv:upload"

# Prescreening
CB_PS_START = "cand:ps:start"
CB_PS_NAME_CONFIRM = "cand:ps:name_confirm"
CB_PS_NAME_CHANGE = "cand:ps:name_change"
CB_PS_PHONE_CONFIRM = "cand:ps:phone_confirm"
CB_PS_PHONE_CHANGE = "cand:ps:phone_change"
CB_PS_CV_SKIP = "cand:ps:cv_skip"
CB_PS_CV_UPLOAD = "cand:ps:cv_upload"
CB_PS_CV_SELECT = "cand:ps:cv"
CB_PS_CV_SELECT_PREFIX = "cand:ps:cv:"


def main_menu_keyboard(*, lang: str) -> dict:
    return kb.inline_keyboard(
        [
            [
                kb.button(text=t("candidate.btn_search_jobs", lang=lang), callback_data=CB_JOB_SEARCH),
            ],
            [
                kb.button(
                    text=t("candidate.btn_prescreening", lang=lang),
                    callback_data=CB_PS_START,
                )
            ],
            [
                kb.button(text=t("candidate.btn_create_cv_ai", lang=lang), callback_data=CB_CV_ASSISTANT),
                kb.button(text=t("candidate.btn_my_cvs", lang=lang), callback_data=CB_CV_LIST),
            ],
            [kb.button(text=t("candidate.btn_cv_center", lang=lang), callback_data=CB_CV)],
            [
                kb.button(
                    text=t("candidate.btn_language", lang=lang),
                    callback_data=CB_LANG,
                )
            ],
        ]
    )


def language_keyboard(*, lang: str) -> dict:
    return kb.inline_keyboard(
        [
            [
                kb.button(text="English", callback_data=f"{CB_LANG_PREFIX}{User.Language.EN}"),
                kb.button(text="Русский", callback_data=f"{CB_LANG_PREFIX}{User.Language.RU}"),
                kb.button(text="O'zbek", callback_data=f"{CB_LANG_PREFIX}{User.Language.UZ}"),
            ],
            [kb.button(text=t("candidate.button_back", lang=lang), callback_data=CB_MENU)],
        ]
    )


def send_main_menu(*, client, chat_id: int, lang: str) -> None:
    client.send_message(
        chat_id=chat_id,
        text=t("candidate.main_menu", lang=lang),
        reply_markup=main_menu_keyboard(lang=lang),
    )


def cv_center_keyboard(*, lang: str) -> dict:
    return kb.inline_keyboard(
        [
            [kb.button(text=t("candidate.btn_my_cvs", lang=lang), callback_data=CB_CV_LIST)],
            [kb.button(text=t("candidate.btn_generate_cv", lang=lang), callback_data=CB_CV_GENERATE)],
            [kb.button(text=t("candidate.btn_upload_new_cv", lang=lang), callback_data=CB_CV_UPLOAD)],
            [kb.button(text=t("candidate.button_back", lang=lang), callback_data=CB_MENU)],
        ]
    )


def cv_list_keyboard(*, rows: list[list[dict]], lang: str) -> dict:
    return kb.inline_keyboard(
        [
            *rows,
            [kb.button(text=t("candidate.btn_generate_cv", lang=lang), callback_data=CB_CV_GENERATE)],
            [kb.button(text=t("candidate.btn_upload_new_cv", lang=lang), callback_data=CB_CV_UPLOAD)],
            [kb.button(text=t("candidate.button_back", lang=lang), callback_data=CB_CV)],
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
            [kb.button(text=t("candidate.btn_upload_new_cv", lang=lang), callback_data=CB_PS_CV_UPLOAD)],
            [kb.button(text=t("candidate.btn_skip_cv", lang=lang), callback_data=CB_PS_CV_SKIP)],
        ]
    )


def cv_selection_keyboard(*, cv_options: list[dict], lang: str, cv_required: bool) -> dict:
    rows = [
        [
            kb.button(
                text=_cv_button_label(cv=cv, lang=lang),
                callback_data=f"{CB_PS_CV_SELECT_PREFIX}{cv['id']}",
            )
        ]
        for cv in cv_options
    ]
    rows.append([kb.button(text=t("candidate.btn_upload_new_cv", lang=lang), callback_data=CB_PS_CV_UPLOAD)])
    if not cv_required:
        rows.append([kb.button(text=t("candidate.btn_skip_cv", lang=lang), callback_data=CB_PS_CV_SKIP)])
    return kb.inline_keyboard(rows)


def _cv_button_label(*, cv: dict, lang: str) -> str:
    suffix = f" {t('candidate.cv_active_suffix', lang=lang)}" if cv["is_active"] else ""
    return f"📄 {cv['name'][:36]}{suffix}"


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

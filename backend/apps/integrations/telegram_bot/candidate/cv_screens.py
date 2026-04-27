"""Button-driven candidate CV screens for Telegram."""

from __future__ import annotations

import io
import logging

from apps.accounts.cv_services import generate_cv_pdf, get_or_create_candidate_profile
from apps.accounts.models import CandidateCV
from apps.applications.services import generate_cv_download_url, upload_cv_to_s3
from apps.integrations.telegram_bot.bots import ROLE_CANDIDATE
from apps.integrations.telegram_bot.candidate.menus import (
    CB_CV,
    CB_CV_GENERATE,
    CB_CV_LIST,
    CB_CV_UPLOAD,
    cv_center_keyboard,
    cv_list_keyboard,
)
from apps.integrations.telegram_bot.candidate.states import STATE_CV_UPLOAD
from apps.integrations.telegram_bot.i18n import t
from apps.integrations.telegram_bot.keyboards import button
from apps.integrations.telegram_bot.sessions import update_session

ALLOWED_EXTENSIONS = (".pdf", ".docx", ".doc", ".txt")
logger = logging.getLogger(__name__)


class _InMemoryUpload:
    def __init__(self, *, name: str, content: bytes, content_type: str):
        self.name = name
        self.content_type = content_type
        self._buffer = io.BytesIO(content)

    def read(self, *args, **kwargs):
        return self._buffer.read(*args, **kwargs)

    def seek(self, *args, **kwargs):
        return self._buffer.seek(*args, **kwargs)


def is_cv_callback(*, data: str) -> bool:
    return data in {CB_CV, CB_CV_LIST, CB_CV_GENERATE, CB_CV_UPLOAD}


def handle_cv_callback(*, client, chat_id: int, user, data: str, lang: str) -> None:
    if data == CB_CV:
        send_cv_center(client=client, chat_id=chat_id, lang=lang)
    elif data == CB_CV_LIST:
        send_cv_list(client=client, chat_id=chat_id, user=user, lang=lang)
    elif data == CB_CV_GENERATE:
        generate_platform_cv(client=client, chat_id=chat_id, user=user, lang=lang)
    elif data == CB_CV_UPLOAD:
        prompt_cv_upload(client=client, chat_id=chat_id, user=user, lang=lang)


def send_cv_center(*, client, chat_id: int, lang: str) -> None:
    client.send_message(
        chat_id=chat_id,
        text=t("candidate.cv_center", lang=lang),
        reply_markup=cv_center_keyboard(lang=lang),
    )


def send_cv_list(*, client, chat_id: int, user, lang: str) -> None:
    cvs = list(CandidateCV.objects.filter(profile__user=user).order_by("-is_active", "-created_at")[:8])
    if not cvs:
        client.send_message(
            chat_id=chat_id,
            text=t("candidate.cv_empty", lang=lang),
            reply_markup=cv_center_keyboard(lang=lang),
        )
        return

    lines = [t("candidate.cv_list_title", lang=lang)]
    rows = []
    for cv in cvs:
        active = f" {t('candidate.cv_active_suffix', lang=lang)}" if cv.is_active else ""
        lines.append(f"• {cv.name}{active}")
        if cv.file:
            try:
                rows.append([button(text=f"📄 {cv.name[:34]}", url=generate_cv_download_url(cv_file_path=cv.file))])
            except Exception as exc:
                logger.debug("Could not generate CV download URL for %s: %s", cv.id, exc)
                continue
    client.send_message(
        chat_id=chat_id,
        text="\n".join(lines),
        reply_markup=cv_list_keyboard(rows=rows, lang=lang),
    )


def generate_platform_cv(*, client, chat_id: int, user, lang: str) -> None:
    client.send_message(chat_id=chat_id, text=t("candidate.cv_generating", lang=lang))
    try:
        profile = get_or_create_candidate_profile(user=user)
        cv, download_url = generate_cv_pdf(profile=profile, template_name="classic", cv_name="Telegram CV")
    except Exception:
        client.send_message(chat_id=chat_id, text=t("candidate.cv_generate_failed", lang=lang))
        return

    rows = [[button(text=t("candidate.btn_download_cv", lang=lang), url=download_url)]]
    client.send_message(
        chat_id=chat_id,
        text=t("candidate.cv_generated", lang=lang, name=cv.name),
        reply_markup=cv_list_keyboard(rows=rows, lang=lang),
    )


def prompt_cv_upload(*, client, chat_id: int, user, lang: str) -> None:
    update_session(role=ROLE_CANDIDATE, telegram_id=user.telegram_id, state=STATE_CV_UPLOAD)
    client.send_message(chat_id=chat_id, text=t("candidate.cv_upload_prompt", lang=lang))


def handle_cv_upload(*, client, chat_id: int, user, document: dict, lang: str) -> None:
    file_name = document.get("file_name", "cv")
    if not _is_allowed(file_name=file_name):
        client.send_message(chat_id=chat_id, text=t("candidate.cv_invalid_format", lang=lang))
        return

    file_meta = client.get_file(file_id=document.get("file_id"))
    file_path = file_meta.get("file_path") if file_meta else ""
    content = client.download_file(file_path=file_path) if file_path else None
    if not content:
        client.send_message(chat_id=chat_id, text=t("common.error_generic", lang=lang))
        return

    upload = _InMemoryUpload(
        name=file_name,
        content=content,
        content_type=document.get("mime_type", "application/octet-stream"),
    )
    try:
        key = upload_cv_to_s3(file_obj=upload, vacancy_id=f"profile/{user.id}")
        profile = get_or_create_candidate_profile(user=user)
        CandidateCV.objects.filter(profile=profile, is_active=True).update(is_active=False)
        CandidateCV.objects.create(profile=profile, name=file_name[:255], file=key, is_active=True)
    except Exception:
        client.send_message(chat_id=chat_id, text=t("common.error_generic", lang=lang))
        return

    update_session(role=ROLE_CANDIDATE, telegram_id=user.telegram_id, state="")
    client.send_message(chat_id=chat_id, text=t("candidate.cv_uploaded_to_profile", lang=lang, name=file_name))
    send_cv_list(client=client, chat_id=chat_id, user=user, lang=lang)


def _is_allowed(*, file_name: str) -> bool:
    return file_name.lower().endswith(ALLOWED_EXTENSIONS)

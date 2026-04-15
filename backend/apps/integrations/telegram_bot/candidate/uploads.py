"""Candidate bot — handle Telegram document messages (CV uploads).

When a candidate sends a PDF/DOCX, we download it from Telegram, push it to
S3/MinIO via the existing ``upload_cv_to_s3`` helper, then store the resulting
object key on the bot session so the next Apply tap can use it.

If the user already has a pending apply (set by ``apply.confirm_apply`` when
they tried to apply without a CV), we resume the apply automatically here.
"""

from __future__ import annotations

import io
import logging
from uuid import UUID

from apps.applications.services import upload_cv_to_s3
from apps.integrations.telegram_bot.bots import ROLE_CANDIDATE
from apps.integrations.telegram_bot.client import TelegramClient
from apps.integrations.telegram_bot.i18n import t
from apps.integrations.telegram_bot.sessions import get_session, update_session

logger = logging.getLogger(__name__)

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
}
ALLOWED_EXTENSIONS = (".pdf", ".docx", ".doc", ".txt")
MAX_CV_BYTES = 10 * 1024 * 1024  # 10 MB


class _InMemoryUpload:
    """Minimal Django UploadedFile-like wrapper for boto3 ``upload_fileobj``."""

    def __init__(self, *, name: str, content: bytes, content_type: str):
        self.name = name
        self._buffer = io.BytesIO(content)
        self.content_type = content_type
        self.size = len(content)

    def read(self, *args, **kwargs):
        return self._buffer.read(*args, **kwargs)

    def seek(self, *args, **kwargs):
        return self._buffer.seek(*args, **kwargs)


def handle_document(
    *,
    client: TelegramClient,
    chat_id: int,
    user,
    document: dict,
    lang: str,
) -> None:
    """Process an incoming Telegram document. Stores CV on the user's session."""
    file_name = document.get("file_name", "cv")
    mime_type = document.get("mime_type", "application/octet-stream")
    file_size = document.get("file_size", 0) or 0
    file_id = document.get("file_id")

    if not _is_allowed(mime_type=mime_type, file_name=file_name):
        client.send_message(chat_id=chat_id, text=t("candidate.cv_invalid_format", lang=lang))
        return
    if file_size and file_size > MAX_CV_BYTES:
        client.send_message(chat_id=chat_id, text=t("candidate.cv_invalid_format", lang=lang))
        return

    file_meta = client.get_file(file_id=file_id)
    if not file_meta:
        client.send_message(chat_id=chat_id, text=t("common.error_generic", lang=lang))
        return
    file_path = file_meta.get("file_path")
    content = client.download_file(file_path=file_path) if file_path else None
    if not content:
        client.send_message(chat_id=chat_id, text=t("common.error_generic", lang=lang))
        return

    upload = _InMemoryUpload(name=file_name, content=content, content_type=mime_type)
    pending = get_session(role=ROLE_CANDIDATE, telegram_id=user.telegram_id).get(
        "pending_apply_vacancy_id",
    )
    bucket_scope = pending or "telegram"

    try:
        cv_key = upload_cv_to_s3(file_obj=upload, vacancy_id=bucket_scope)
    except Exception as exc:
        logger.error("CV upload failed for tg_id=%s: %s", user.telegram_id, exc)
        client.send_message(chat_id=chat_id, text=t("common.error_generic", lang=lang))
        return

    update_session(
        role=ROLE_CANDIDATE,
        telegram_id=user.telegram_id,
        cv_file_path=cv_key,
        cv_original_filename=file_name,
    )
    client.send_message(chat_id=chat_id, text=t("candidate.cv_uploaded", lang=lang))

    # If there's a pending apply, resume it now.
    if pending:
        try:
            vacancy_id = UUID(pending)
        except ValueError, TypeError:
            return
        from apps.integrations.telegram_bot.candidate.apply import confirm_apply

        confirm_apply(
            client=client,
            chat_id=chat_id,
            user=user,
            vacancy_id=vacancy_id,
            cv_file_path=cv_key,
            cv_original_filename=file_name,
            lang=lang,
        )


def _is_allowed(*, mime_type: str, file_name: str) -> bool:
    if mime_type in ALLOWED_MIME_TYPES:
        return True
    name_lower = file_name.lower()
    return any(name_lower.endswith(ext) for ext in ALLOWED_EXTENSIONS)

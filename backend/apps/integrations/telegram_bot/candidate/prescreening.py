"""Candidate bot — prescreening flow public API.

Entry points called from handlers.py:
  handle_prescreening_callback()  - inline-button actions
  handle_prescreening_text()      - free-text input during flow
  handle_cv_upload()              - document upload in ps_cv state
"""

from __future__ import annotations

import logging

from apps.integrations.telegram_bot.bots import ROLE_CANDIDATE
from apps.integrations.telegram_bot.candidate.menus import (
    CB_PS_CV_SKIP,
    CB_PS_NAME_CHANGE,
    CB_PS_NAME_CONFIRM,
    CB_PS_PHONE_CHANGE,
    CB_PS_PHONE_CONFIRM,
    CB_PS_START,
)
from apps.integrations.telegram_bot.candidate.prescreening_steps import (
    go_to_confirm_phone,
    go_to_cv_step,
    handle_new_name,
    handle_new_phone,
    handle_vacancy_code,
    start_interview_submission,
)
from apps.integrations.telegram_bot.candidate.states import (
    SK_CV_FILENAME,
    SK_CV_PATH,
    SK_VACANCY_ID,
    STATE_PS_CHANGE_NAME,
    STATE_PS_CHANGE_PHONE,
    STATE_PS_CODE,
    STATE_PS_INTERVIEW,
)
from apps.integrations.telegram_bot.i18n import t
from apps.integrations.telegram_bot.sessions import update_session

logger = logging.getLogger(__name__)


def handle_prescreening_callback(*, client, chat_id: int, user, data: str, session: dict, lang: str) -> None:
    if data == CB_PS_START:
        update_session(role=ROLE_CANDIDATE, telegram_id=user.telegram_id, state=STATE_PS_CODE)
        client.send_message(chat_id=chat_id, text=t("candidate.ps_ask_code", lang=lang))

    elif data == CB_PS_NAME_CONFIRM:
        go_to_confirm_phone(client=client, chat_id=chat_id, user=user, session=session, lang=lang)

    elif data == CB_PS_NAME_CHANGE:
        update_session(role=ROLE_CANDIDATE, telegram_id=user.telegram_id, state=STATE_PS_CHANGE_NAME)
        client.send_message(chat_id=chat_id, text=t("candidate.ps_ask_new_name", lang=lang))

    elif data == CB_PS_PHONE_CONFIRM:
        go_to_cv_step(client=client, chat_id=chat_id, user=user, session=session, lang=lang)

    elif data == CB_PS_PHONE_CHANGE:
        update_session(role=ROLE_CANDIDATE, telegram_id=user.telegram_id, state=STATE_PS_CHANGE_PHONE)
        client.send_message(chat_id=chat_id, text=t("candidate.ps_ask_new_phone", lang=lang))

    elif data == CB_PS_CV_SKIP:
        updated_session = {**session, SK_CV_PATH: "", SK_CV_FILENAME: ""}
        update_session(role=ROLE_CANDIDATE, telegram_id=user.telegram_id, **{SK_CV_PATH: "", SK_CV_FILENAME: ""})
        start_interview_submission(client=client, chat_id=chat_id, user=user, session=updated_session, lang=lang)


def handle_prescreening_text(*, client, chat_id: int, user, text: str, session: dict, lang: str) -> None:
    state = session.get("state", "")

    if state == STATE_PS_CODE:
        handle_vacancy_code(client=client, chat_id=chat_id, user=user, text=text, lang=lang)
    elif state == STATE_PS_CHANGE_NAME:
        handle_new_name(client=client, chat_id=chat_id, user=user, text=text, session=session, lang=lang)
    elif state == STATE_PS_CHANGE_PHONE:
        handle_new_phone(client=client, chat_id=chat_id, user=user, text=text, session=session, lang=lang)
    elif state == STATE_PS_INTERVIEW:
        from apps.integrations.telegram_bot.candidate.interview_flow import handle_interview_answer

        handle_interview_answer(client=client, chat_id=chat_id, user=user, text=text, session=session, lang=lang)


def handle_cv_upload(*, client, chat_id: int, user, document: dict, session: dict, lang: str) -> None:
    """Upload CV document then proceed to interview submission."""
    from apps.applications.services.s3_utils import upload_cv_to_s3
    from apps.integrations.telegram_bot.bots import get_client
    from apps.integrations.telegram_bot.candidate.uploads import (
        MAX_CV_BYTES,
        _InMemoryUpload,
        _is_allowed,
    )

    file_name = document.get("file_name", "cv")
    mime_type = document.get("mime_type", "application/octet-stream")
    file_size = document.get("file_size", 0) or 0
    file_id = document.get("file_id")

    if not _is_allowed(mime_type=mime_type, file_name=file_name) or (file_size and file_size > MAX_CV_BYTES):
        client.send_message(chat_id=chat_id, text=t("candidate.cv_invalid_format", lang=lang))
        return

    bot_client = get_client(role=ROLE_CANDIDATE)
    file_meta = bot_client.get_file(file_id=file_id)
    file_path = (file_meta or {}).get("file_path")
    content = bot_client.download_file(file_path=file_path) if file_path else None
    if not content:
        client.send_message(chat_id=chat_id, text=t("common.error_generic", lang=lang))
        return

    vacancy_id = session.get(SK_VACANCY_ID, "telegram")
    upload = _InMemoryUpload(name=file_name, content=content, content_type=mime_type)
    try:
        cv_key = upload_cv_to_s3(file_obj=upload, vacancy_id=vacancy_id)
    except Exception as exc:
        logger.error("CV upload failed for tg_id=%s: %s", user.telegram_id, exc)
        client.send_message(chat_id=chat_id, text=t("common.error_generic", lang=lang))
        return

    update_session(role=ROLE_CANDIDATE, telegram_id=user.telegram_id, **{SK_CV_PATH: cv_key, SK_CV_FILENAME: file_name})
    client.send_message(chat_id=chat_id, text=t("candidate.cv_uploaded", lang=lang))
    start_interview_submission(
        client=client,
        chat_id=chat_id,
        user=user,
        session={**session, SK_CV_PATH: cv_key, SK_CV_FILENAME: file_name},
        lang=lang,
    )

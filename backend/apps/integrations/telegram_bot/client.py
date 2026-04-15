"""Thin wrapper around the Telegram Bot HTTP API.

Each ``TelegramClient`` instance is bound to a single bot token, so the
codebase can host multiple bots (HR + candidate) side-by-side.
"""
from __future__ import annotations

import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 15


class TelegramClient:
    """Bot-token-scoped client for the Telegram Bot API."""

    def __init__(self, *, token: str):
        if not token:
            raise ValueError("TelegramClient requires a non-empty bot token")
        self.token = token
        self.api_url = f"https://api.telegram.org/bot{token}"
        self.file_url = f"https://api.telegram.org/file/bot{token}"

    # ----- write methods -----

    def send_message(
        self,
        *,
        chat_id: int | str,
        text: str,
        parse_mode: str = "Markdown",
        reply_markup: dict[str, Any] | None = None,
        disable_web_page_preview: bool = False,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview,
        }
        if reply_markup is not None:
            payload["reply_markup"] = reply_markup
        return self._post("sendMessage", payload)

    def edit_message_text(
        self,
        *,
        chat_id: int | str,
        message_id: int,
        text: str,
        parse_mode: str = "Markdown",
        reply_markup: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": parse_mode,
        }
        if reply_markup is not None:
            payload["reply_markup"] = reply_markup
        return self._post("editMessageText", payload)

    def answer_callback_query(
        self,
        *,
        callback_query_id: str,
        text: str = "",
        show_alert: bool = False,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"callback_query_id": callback_query_id}
        if text:
            payload["text"] = text
            payload["show_alert"] = show_alert
        return self._post("answerCallbackQuery", payload)

    def send_chat_action(self, *, chat_id: int | str, action: str = "typing") -> dict[str, Any]:
        return self._post("sendChatAction", {"chat_id": chat_id, "action": action})

    # ----- read / file methods -----

    def get_file(self, *, file_id: str) -> dict[str, Any] | None:
        """Resolve a Telegram file_id to its file_path metadata."""
        try:
            resp = requests.get(
                f"{self.api_url}/getFile",
                params={"file_id": file_id},
                timeout=DEFAULT_TIMEOUT,
            )
            data = resp.json()
            if data.get("ok"):
                return data.get("result")
            logger.warning("getFile failed: %s", data)
            return None
        except requests.RequestException as exc:
            logger.error("getFile request error: %s", exc)
            return None

    def download_file(self, *, file_path: str) -> bytes | None:
        """Download a file from Telegram CDN given its file_path."""
        try:
            resp = requests.get(
                f"{self.file_url}/{file_path}",
                timeout=DEFAULT_TIMEOUT,
            )
            if resp.status_code == 200:
                return resp.content
            logger.warning("download_file failed: status=%s", resp.status_code)
            return None
        except requests.RequestException as exc:
            logger.error("download_file request error: %s", exc)
            return None

    def delete_webhook(self) -> dict[str, Any]:
        return self._post("deleteWebhook", {})

    def set_webhook(self, *, url: str, secret_token: str = "") -> dict[str, Any]:
        payload: dict[str, Any] = {"url": url}
        if secret_token:
            payload["secret_token"] = secret_token
        return self._post("setWebhook", payload)

    def get_updates(self, *, offset: int, timeout: int = 30) -> dict[str, Any]:
        """Long-poll for new updates (used by the polling management command)."""
        try:
            resp = requests.get(
                f"{self.api_url}/getUpdates",
                params={"offset": offset, "timeout": timeout},
                timeout=timeout + 5,
            )
            return resp.json()
        except requests.RequestException as exc:
            logger.error("getUpdates request error: %s", exc)
            return {"ok": False, "error": str(exc)}

    # ----- internals -----

    def _post(self, method: str, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            resp = requests.post(
                f"{self.api_url}/{method}",
                json=payload,
                timeout=DEFAULT_TIMEOUT,
            )
            data = resp.json()
            if not data.get("ok"):
                logger.warning("Telegram %s failed: %s", method, data.get("description"))
            return data
        except requests.RequestException as exc:
            logger.error("Telegram %s request error: %s", method, exc)
            return {"ok": False, "error": str(exc)}

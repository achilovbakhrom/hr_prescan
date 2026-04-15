"""Voice-message transcription via Gemini.

Used by both bots: candidates can answer interview questions by voice, and HR
can issue voice commands. Returns plain text or ``None`` on failure.
"""
from __future__ import annotations

import logging

from django.conf import settings
from google import genai
from google.genai import types

from apps.integrations.telegram_bot.client import TelegramClient

logger = logging.getLogger(__name__)

_TRANSCRIBE_PROMPT = (
    "Transcribe this audio accurately. The speaker may use Russian, English, "
    "Uzbek, or a mix. Return only the transcription text, nothing else."
)


def transcribe_voice(*, client: TelegramClient, file_id: str) -> str | None:
    """Download a Telegram voice message and transcribe it with Gemini."""
    if not file_id:
        return None

    file_meta = client.get_file(file_id=file_id)
    if not file_meta:
        return None
    file_path = file_meta.get("file_path")
    if not file_path:
        return None

    audio_bytes = client.download_file(file_path=file_path)
    if not audio_bytes:
        return None

    try:
        gemini = genai.Client(api_key=settings.GOOGLE_API_KEY)
        response = gemini.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=[
                types.Part.from_bytes(data=audio_bytes, mime_type="audio/ogg"),
                _TRANSCRIBE_PROMPT,
            ],
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_level="MINIMAL"),
            ),
        )
        return (response.text or "").strip()
    except Exception as exc:  # noqa: BLE001 — Gemini SDK raises various types
        logger.error("Telegram voice transcription error: %s", exc)
        return None

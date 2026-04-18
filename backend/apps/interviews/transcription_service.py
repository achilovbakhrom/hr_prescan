"""
Voice message transcription service — handles S3 upload and Gemini transcription.

Responsibilities:
- Upload voice message audio files to S3/MinIO
- Transcribe audio using Google Gemini multimodal API
"""

import logging
import uuid

import boto3
from botocore.config import Config as BotoConfig
from django.conf import settings
from google import genai
from google.genai import types

from apps.common.exceptions import ApplicationError
from apps.common.messages import MSG_AUDIO_TRANSCRIPTION_FAILED

logger = logging.getLogger(__name__)


def _get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
        config=BotoConfig(signature_version="s3v4"),
    )


def upload_voice_message_to_s3(*, file_obj, interview_id: str, filename: str = "audio.webm") -> str:
    """Upload voice message to S3. Returns object key."""
    ext = filename.rsplit(".", 1)[-1] if "." in filename else "webm"
    prefix = (getattr(settings, "S3_KEY_PREFIX", "") or "").strip("/")
    base = f"voice-messages/{interview_id}/{uuid.uuid4()}.{ext}"
    key = f"{prefix}/{base}" if prefix else base

    s3 = _get_s3_client()
    s3.upload_fileobj(
        file_obj,
        settings.AWS_STORAGE_BUCKET_NAME,
        key,
        ExtraArgs={"ContentType": "audio/webm"},
    )
    return key


def transcribe_audio(*, file_bytes: bytes, filename: str = "audio.webm") -> str:
    """Transcribe audio using Google Gemini multimodal API. Returns transcript text."""
    client = genai.Client(api_key=settings.GOOGLE_API_KEY)

    mime_type = "audio/webm"
    if filename.endswith(".ogg"):
        mime_type = "audio/ogg"
    elif filename.endswith(".mp3"):
        mime_type = "audio/mp3"

    try:
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=[
                types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
                "Transcribe this audio accurately. The speaker may use Russian, English, "
                "or a mix. Return only the transcription text, nothing else.",
            ],
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_level="MINIMAL"),
            ),
        )
    except Exception as e:
        logger.error("Gemini transcription failed: %s", e)
        raise ApplicationError(str(MSG_AUDIO_TRANSCRIPTION_FAILED)) from e

    return response.text.strip()

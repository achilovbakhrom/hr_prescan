"""
Voice message transcription service — handles S3 upload and Whisper transcription.

Responsibilities:
- Upload voice message audio files to S3/MinIO
- Transcribe audio using OpenAI Whisper API
"""

import logging
import uuid

import boto3
from botocore.config import Config as BotoConfig
from django.conf import settings
from openai import OpenAI

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
    key = f"voice-messages/{interview_id}/{uuid.uuid4()}.{ext}"

    s3 = _get_s3_client()
    s3.upload_fileobj(
        file_obj,
        settings.AWS_STORAGE_BUCKET_NAME,
        key,
        ExtraArgs={"ContentType": "audio/webm"},
    )
    return key


def transcribe_audio(*, file_bytes: bytes, filename: str = "audio.webm") -> str:
    """Transcribe audio using OpenAI Whisper API. Returns transcript text."""
    client = OpenAI(api_key=settings.OPENAI_API_KEY, timeout=30.0)

    try:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=(filename, file_bytes, "audio/webm"),
        )
    except Exception as e:
        logger.error("Whisper transcription failed: %s", e)
        raise ApplicationError(str(MSG_AUDIO_TRANSCRIPTION_FAILED))

    return transcript.text

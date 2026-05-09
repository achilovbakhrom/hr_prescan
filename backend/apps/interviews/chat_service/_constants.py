"""Shared constants for the chat_service package."""

from django.conf import settings
from google import genai

from apps.common.language import LANGUAGE_NAMES

SESSION_COMPLETE_ADVANCE = "[SESSION_ADVANCE]"
SESSION_COMPLETE_REJECT = "[SESSION_REJECT]"


def _language_name(code: str) -> str:
    return LANGUAGE_NAMES.get(code, "English")


def get_client() -> genai.Client:
    return genai.Client(api_key=settings.GOOGLE_API_KEY)

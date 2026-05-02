"""Gemini helpers shared by translation services."""

import logging
from collections.abc import Sequence

from django.conf import settings
from google import genai
from google.genai import errors, types

logger = logging.getLogger(__name__)

DEPRECATED_TRANSLATION_MODELS = {"gemini-2.0-flash-lite"}


def _translation_model_names() -> list[str]:
    fallback_model = getattr(settings, "GEMINI_MODEL", "")
    configured_model = getattr(settings, "GEMINI_TRANSLATION_MODEL", "")
    if fallback_model and configured_model in DEPRECATED_TRANSLATION_MODELS:
        configured_model = ""
    names = [configured_model, fallback_model]
    return list(dict.fromkeys(name for name in names if name))


def _is_missing_model_error(exc: errors.ClientError) -> bool:
    return getattr(exc, "code", None) == 404 or getattr(exc, "status", None) == "NOT_FOUND"


def generate_translation_content(
    *,
    client: genai.Client,
    contents: Sequence[types.Content],
    config: types.GenerateContentConfig,
):
    """Generate translation content, falling back if the configured model is gone."""
    model_names = _translation_model_names()
    if not model_names:
        model_names = ["gemini-3-flash-preview"]

    last_index = len(model_names) - 1
    for index, model_name in enumerate(model_names):
        try:
            return client.models.generate_content(
                model=model_name,
                contents=contents,
                config=config,
            )
        except errors.ClientError as exc:
            if index < last_index and _is_missing_model_error(exc):
                logger.warning(
                    "Gemini translation model %s is unavailable; retrying with %s.",
                    model_name,
                    model_names[index + 1],
                )
                continue
            raise

    raise RuntimeError("No Gemini translation model returned a response.")

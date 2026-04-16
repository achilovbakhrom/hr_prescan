"""AI content translation service for individual fields using Gemini."""

import logging
from uuid import UUID

from django.conf import settings
from google import genai
from google.genai import types

from apps.common.exceptions import ApplicationError

logger = logging.getLogger(__name__)

LANGUAGE_NAMES = {
    "en": "English",
    "ru": "Russian",
    "uz": "Uzbek",
}

# (model_key, field_key) -> (app_label.ModelName, source_field, translations_field)
# For JSON subfields (match_details.notes, cv_parsed_data.summary),
# source_field is the JSONField name and we extract the subkey.
TRANSLATABLE_FIELDS = {
    ("interview", "ai_summary"): {
        "model": "interviews.Interview",
        "source_field": "ai_summary",
        "translations_field": "ai_summary_translations",
    },
    ("interview_score", "ai_notes"): {
        "model": "interviews.InterviewScore",
        "source_field": "ai_notes",
        "translations_field": "ai_notes_translations",
    },
    ("application", "match_notes"): {
        "model": "applications.Application",
        "source_field": "match_details",
        "source_subkey": "notes",
        "translations_field": "match_notes_translations",
    },
    ("application", "cv_summary"): {
        "model": "applications.Application",
        "source_field": "cv_parsed_data",
        "source_subkey": "summary",
        "translations_field": "cv_summary_translations",
    },
    ("employer", "description"): {
        "model": "vacancies.EmployerCompany",
        "source_field": "description",
        "translations_field": "description_translations",
    },
}


def _get_model_class(model_path: str):
    """Resolve 'app_label.ModelName' to the Django model class."""
    from django.apps import apps

    app_label, model_name = model_path.split(".")
    return apps.get_model(app_label, model_name)


def _get_source_text(obj, field_config: dict) -> str:
    """Extract the source text from the object, handling JSON subkeys."""
    value = getattr(obj, field_config["source_field"])
    subkey = field_config.get("source_subkey")
    if subkey and isinstance(value, dict):
        return value.get(subkey, "")
    return value or ""


def translate_ai_content(
    *,
    model_name: str,
    object_id: UUID,
    field_name: str,
    target_language: str,
    user,
) -> str:
    """Translate an AI-generated text field to the target language.

    Returns the translated text. Stores it in the translations JSONField
    so subsequent requests are served from cache.
    """
    key = (model_name, field_name)
    field_config = TRANSLATABLE_FIELDS.get(key)
    if not field_config:
        raise ApplicationError(f"Unknown translation target: {model_name}.{field_name}")

    lang_name = LANGUAGE_NAMES.get(target_language)
    if not lang_name:
        raise ApplicationError(f"Unsupported language: {target_language}")

    # Load the object
    model_class = _get_model_class(field_config["model"])
    try:
        obj = model_class.objects.get(id=object_id)
    except model_class.DoesNotExist:
        raise ApplicationError("Object not found.") from None

    # Check if translation already cached
    translations = getattr(obj, field_config["translations_field"]) or {}
    if target_language in translations:
        return translations[target_language]

    # Get source text
    source_text = _get_source_text(obj, field_config)
    if not source_text.strip():
        raise ApplicationError("No content to translate.")

    # Call Gemini to translate
    try:
        client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        response = client.models.generate_content(
            model=settings.GEMINI_TRANSLATION_MODEL,
            contents=[
                types.Content(
                    role="user",
                    parts=[types.Part(text=f"Translate the following text to {lang_name}:\n\n{source_text}")],
                ),
            ],
            config=types.GenerateContentConfig(
                system_instruction=(
                    f"You are a professional translator. Translate the given text to {lang_name}. "
                    "Preserve the professional tone, formatting, and all technical details. "
                    "Return ONLY the translated text, nothing else."
                ),
                temperature=0.2,
            ),
        )
        translated = response.text.strip()
    except Exception as e:
        logger.error("Translation error: %s", e)
        raise ApplicationError("Translation failed. Please try again.") from e

    # Store in translations JSONField
    translations[target_language] = translated
    setattr(obj, field_config["translations_field"], translations)
    obj.save(update_fields=[field_config["translations_field"], "updated_at"])

    return translated

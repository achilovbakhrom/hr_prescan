"""AI content translation service using Gemini."""

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
        raise ApplicationError("Object not found.")

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
            model=settings.GEMINI_MODEL,
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
        raise ApplicationError("Translation failed. Please try again.")

    # Store in translations JSONField
    translations[target_language] = translated
    setattr(obj, field_config["translations_field"], translations)
    obj.save(update_fields=[field_config["translations_field"], "updated_at"])

    return translated


def batch_translate_vacancy_items(
    *,
    item_type: str,
    vacancy_id: UUID,
    step: str,
    target_language: str,
    user,
) -> list[dict]:
    """Translate all criteria or questions for a vacancy step in one Gemini call.

    Args:
        item_type: "criteria" or "questions"
        vacancy_id: UUID of the vacancy
        step: "prescanning" or "interview"
        target_language: target language code
        user: requesting user

    Returns list of {id, translations} dicts with updated translations.
    """
    import json
    from apps.vacancies.models import InterviewQuestion, Vacancy, VacancyCriteria

    lang_name = LANGUAGE_NAMES.get(target_language)
    if not lang_name:
        raise ApplicationError(f"Unsupported language: {target_language}")

    try:
        vacancy = Vacancy.objects.get(id=vacancy_id, company=user.company)
    except Vacancy.DoesNotExist:
        raise ApplicationError("Vacancy not found.")

    if item_type == "criteria":
        items = list(VacancyCriteria.objects.filter(vacancy=vacancy, step=step).order_by("order"))
        texts = {str(item.id): f"{item.name}: {item.description}" if item.description else item.name for item in items}
    elif item_type == "questions":
        items = list(InterviewQuestion.objects.filter(vacancy=vacancy, step=step, is_active=True).order_by("order"))
        texts = {str(item.id): item.text for item in items}
    else:
        raise ApplicationError(f"Invalid item_type: {item_type}")

    if not items:
        return []

    # Check which items already have cached translations
    to_translate = {}
    results = []
    for item in items:
        existing = item.translations or {}
        if target_language in existing:
            results.append({"id": str(item.id), "translations": existing})
        else:
            to_translate[str(item.id)] = texts[str(item.id)]

    if not to_translate:
        return results

    # Build batch prompt
    items_json = json.dumps(
        [{"id": k, "text": v} for k, v in to_translate.items()],
        ensure_ascii=False,
    )

    try:
        client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=[
                types.Content(
                    role="user",
                    parts=[types.Part(text=f"Translate each item's text to {lang_name}:\n\n{items_json}")],
                ),
            ],
            config=types.GenerateContentConfig(
                system_instruction=(
                    f"You are a professional translator. Translate each item's 'text' field to {lang_name}. "
                    "Preserve professional tone and technical terms. "
                    "Return ONLY a valid JSON array with the same structure: "
                    '[{"id": "...", "text": "translated text"}, ...]'
                ),
                temperature=0.2,
                response_mime_type="application/json",
            ),
        )
        translated_items = json.loads(response.text)
    except Exception as e:
        logger.error("Batch translation error: %s", e)
        raise ApplicationError("Translation failed. Please try again.")

    # Build lookup of translated texts
    translated_map = {t["id"]: t["text"] for t in translated_items if "id" in t and "text" in t}

    # Update each item's translations field
    for item in items:
        item_id = str(item.id)
        if item_id in translated_map:
            translations = dict(item.translations or {})
            translations[target_language] = translated_map[item_id]
            item.translations = translations
            item.save(update_fields=["translations", "updated_at"])
            results.append({"id": item_id, "translations": translations})

    return results

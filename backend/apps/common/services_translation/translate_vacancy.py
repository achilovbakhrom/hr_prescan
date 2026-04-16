"""Batch translation service for vacancy criteria and questions."""

import json
import logging
from uuid import UUID

from django.conf import settings
from google import genai
from google.genai import types

from apps.common.exceptions import ApplicationError
from apps.common.services_translation.translate_text import LANGUAGE_NAMES

logger = logging.getLogger(__name__)


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
    from apps.vacancies.models import InterviewQuestion, Vacancy, VacancyCriteria

    lang_name = LANGUAGE_NAMES.get(target_language)
    if not lang_name:
        raise ApplicationError(f"Unsupported language: {target_language}")

    try:
        vacancy = Vacancy.objects.get(id=vacancy_id, company=user.company)
    except Vacancy.DoesNotExist:
        raise ApplicationError("Vacancy not found.") from None

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
            model=settings.GEMINI_TRANSLATION_MODEL,
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
        raise ApplicationError("Translation failed. Please try again.") from e

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

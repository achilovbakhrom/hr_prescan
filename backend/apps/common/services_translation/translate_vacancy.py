"""Batch translation service for vacancy criteria and questions."""

import json
import logging
import re
from uuid import UUID

from django.conf import settings
from google import genai
from google.genai import types

from apps.common.exceptions import ApplicationError
from apps.common.services_translation.translate_text import LANGUAGE_NAMES

logger = logging.getLogger(__name__)

_JSON_FENCE_RE = re.compile(r"^```(?:json)?\s*(?P<body>.*?)\s*```$", re.DOTALL | re.IGNORECASE)


def _translation_response_schema() -> types.Schema:
    return types.Schema(
        type=types.Type.ARRAY,
        items=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "id": types.Schema(type=types.Type.STRING),
                "text": types.Schema(type=types.Type.STRING),
            },
            required=["id", "text"],
        ),
    )


def _json_from_response_text(text: str) -> object:
    text = text.strip()
    fence_match = _JSON_FENCE_RE.match(text)
    if fence_match:
        text = fence_match.group("body").strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start_positions = [pos for pos in (text.find("["), text.find("{")) if pos >= 0]
        if not start_positions:
            raise
        start = min(start_positions)
        end = max(text.rfind("]"), text.rfind("}"))
        if end <= start:
            raise
        return json.loads(text[start : end + 1])


def _parse_translated_items(response) -> list[dict[str, str]]:
    parsed = getattr(response, "parsed", None)
    payload = parsed if parsed is not None else _json_from_response_text(getattr(response, "text", "") or "")

    if isinstance(payload, dict):
        if isinstance(payload.get("id"), str) and isinstance(payload.get("text"), str):
            payload = [payload]
        else:
            for key in ("items", "translations", "results"):
                if isinstance(payload.get(key), list):
                    payload = payload[key]
                    break
            else:
                payload = [{"id": key, "text": value} for key, value in payload.items()]

    if not isinstance(payload, list):
        raise ValueError("Translation response must be a JSON array.")

    translated_items: list[dict[str, str]] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        item_id = item.get("id")
        text = item.get("text")
        if isinstance(item_id, str) and isinstance(text, str):
            translated_items.append({"id": item_id, "text": text})
    if not translated_items:
        raise ValueError("Translation response did not include any translated items.")
    return translated_items


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
    from apps.vacancies.models import InterviewQuestion, VacancyCriteria
    from apps.vacancies.selectors import get_user_vacancy_by_id

    lang_name = LANGUAGE_NAMES.get(target_language)
    if not lang_name:
        raise ApplicationError(f"Unsupported language: {target_language}")

    vacancy = get_user_vacancy_by_id(vacancy_id=vacancy_id, user=user)
    if vacancy is None:
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
                    "Return a JSON array with the same structure: "
                    '[{"id": "...", "text": "translated text"}, ...]. '
                    "Do not wrap it in an object or Markdown."
                ),
                temperature=0.2,
                response_mime_type="application/json",
                response_schema=_translation_response_schema(),
            ),
        )
        translated_items = _parse_translated_items(response)
    except Exception as e:
        logger.exception(
            "Batch translation error for vacancy=%s item_type=%s step=%s target_language=%s response=%r",
            vacancy_id,
            item_type,
            step,
            target_language,
            getattr(locals().get("response", None), "text", None),
        )
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

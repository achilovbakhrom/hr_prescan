import json
import logging
from decimal import Decimal
from typing import Any

from django.conf import settings
from google import genai
from google.genai import types

from apps.common.exceptions import ApplicationError
from apps.common.language import LANGUAGE_NAMES
from apps.common.messages import MSG_AI_VACANCY_CONTENT_FAILED
from apps.vacancies.services.ai_json import (
    has_complete_vacancy_content,
    load_json_object,
    normalize_vacancy_content,
    require_complete_vacancy_content,
)
from apps.vacancies.services.vacancy_content_context import (
    clean_generation_context,
    merge_with_current_content,
    response_payload,
)
from apps.vacancies.services.vacancy_content_prompts import (
    generation_instruction,
    grading_instruction,
    revision_instruction,
)

logger = logging.getLogger(__name__)
MIN_ACCEPTABLE_SCORE = 8


def generate_vacancy_content(
    *,
    title: str,
    language: str = "en",
    description: str | None = None,
    requirements: str | None = None,
    responsibilities: str | None = None,
    employment_type: str | None = None,
    experience_level: str | None = None,
    skills: list[str] | None = None,
    salary_min: Decimal | int | None = None,
    salary_max: Decimal | int | None = None,
    salary_currency: str | None = None,
    location: str | None = None,
    is_remote: bool | None = None,
    additional_instruction: str | None = None,
    generation_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Generate or regenerate candidate-facing vacancy copy with short-lived context."""
    context = {
        "title": title.strip(),
        "language": LANGUAGE_NAMES.get(language, "English"),
        "current_content": {
            "description": (description or "").strip(),
            "requirements": (requirements or "").strip(),
            "responsibilities": (responsibilities or "").strip(),
        },
        "employment_type": employment_type or "not specified",
        "experience_level": experience_level or "not specified",
        "skills": skills or [],
        "salary_min": str(salary_min) if salary_min is not None else None,
        "salary_max": str(salary_max) if salary_max is not None else None,
        "salary_currency": salary_currency or "USD",
        "location": location or "",
        "is_remote": is_remote,
        "additional_instruction": (additional_instruction or "").strip(),
        "generation_context": clean_generation_context(generation_context or {}),
    }

    try:
        client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        draft = _generate_content(client=client, context=context)
        draft = merge_with_current_content(draft, context["current_content"])
        grade = _grade_content(client=client, context=context, content=draft)
        if _score(grade) >= MIN_ACCEPTABLE_SCORE and has_complete_vacancy_content(draft):
            return response_payload(content=draft, context=context)
        revised = _revise_content(client=client, context=context, content=draft, grade=grade)
        revised = merge_with_current_content(revised, context["current_content"])
        return response_payload(content=require_complete_vacancy_content(revised), context=context)
    except Exception as exc:
        logger.exception("Failed to generate vacancy content for title %s", title)
        raise ApplicationError(str(MSG_AI_VACANCY_CONTENT_FAILED)) from exc


def _generate_content(*, client: genai.Client, context: dict[str, Any]) -> dict[str, str]:
    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=[_content_payload(context)],
        config=types.GenerateContentConfig(
            system_instruction=generation_instruction(),
            temperature=0.6,
            response_mime_type="application/json",
        ),
    )
    return normalize_vacancy_content(load_json_object(response.text))


def _grade_content(
    *,
    client: genai.Client,
    context: dict[str, Any],
    content: dict[str, str],
) -> dict[str, Any]:
    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=[
            types.Content(
                role="user",
                parts=[types.Part(text=json.dumps({"context": context, "content": content}, ensure_ascii=False))],
            )
        ],
        config=types.GenerateContentConfig(
            system_instruction=grading_instruction(),
            temperature=0.1,
            response_mime_type="application/json",
        ),
    )
    return load_json_object(response.text)


def _revise_content(
    *,
    client: genai.Client,
    context: dict[str, Any],
    content: dict[str, str],
    grade: dict[str, Any],
) -> dict[str, str]:
    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part(
                        text=json.dumps(
                            {"context": context, "draft": content, "review": grade},
                            ensure_ascii=False,
                        )
                    )
                ],
            )
        ],
        config=types.GenerateContentConfig(
            system_instruction=revision_instruction(),
            temperature=0.4,
            response_mime_type="application/json",
        ),
    )
    return normalize_vacancy_content(load_json_object(response.text))


def _content_payload(context: dict[str, Any]) -> types.Content:
    previous_turns = json.dumps(context["generation_context"].get("turns", []), ensure_ascii=False)
    return types.Content(
        role="user",
        parts=[
            types.Part(
                text=(
                    f"Title: {context['title']}\n"
                    f"Language: {context['language']}\n"
                    f"Employment type: {context['employment_type']}\n"
                    f"Experience level: {context['experience_level']}\n"
                    f"Skills: {', '.join(context['skills']) or 'not specified'}\n"
                    f"Salary min: {context['salary_min'] or 'not specified'}\n"
                    f"Salary max: {context['salary_max'] or 'not specified'}\n"
                    f"Salary currency: {context['salary_currency']}\n"
                    f"Location: {context['location'] or 'not specified'}\n"
                    f"Remote: {context['is_remote']}"
                    f"\nCurrent description: {context['current_content']['description'] or 'empty'}"
                    f"\nCurrent requirements: {context['current_content']['requirements'] or 'empty'}"
                    f"\nCurrent responsibilities: {context['current_content']['responsibilities'] or 'empty'}"
                    f"\nAdditional HR instruction: {context['additional_instruction'] or 'none'}"
                    f"\nPrevious AI turns: {previous_turns}"
                )
            )
        ],
    )


def _score(grade: dict[str, Any]) -> int:
    try:
        return int(grade.get("score", 0))
    except (TypeError, ValueError):
        return 0

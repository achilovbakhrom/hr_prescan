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

logger = logging.getLogger(__name__)
MIN_ACCEPTABLE_SCORE = 8


def generate_vacancy_content(
    *,
    title: str,
    language: str = "en",
    employment_type: str | None = None,
    experience_level: str | None = None,
    skills: list[str] | None = None,
    salary_min: Decimal | int | None = None,
    salary_max: Decimal | int | None = None,
    salary_currency: str | None = None,
    location: str | None = None,
    is_remote: bool | None = None,
) -> dict[str, str]:
    """Generate candidate-facing vacancy copy and self-review it with AI."""
    context = {
        "title": title.strip(),
        "language": LANGUAGE_NAMES.get(language, "English"),
        "employment_type": employment_type or "not specified",
        "experience_level": experience_level or "not specified",
        "skills": skills or [],
        "salary_min": str(salary_min) if salary_min is not None else None,
        "salary_max": str(salary_max) if salary_max is not None else None,
        "salary_currency": salary_currency or "USD",
        "location": location or "",
        "is_remote": is_remote,
    }

    try:
        client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        draft = _generate_content(client=client, context=context)
        grade = _grade_content(client=client, context=context, content=draft)
        if _score(grade) >= MIN_ACCEPTABLE_SCORE and has_complete_vacancy_content(draft):
            return draft
        revised = _revise_content(client=client, context=context, content=draft, grade=grade)
        return require_complete_vacancy_content(revised)
    except Exception as exc:
        logger.exception("Failed to generate vacancy content for title %s", title)
        raise ApplicationError(str(MSG_AI_VACANCY_CONTENT_FAILED)) from exc


def _generate_content(*, client: genai.Client, context: dict[str, Any]) -> dict[str, str]:
    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=[_content_payload(context)],
        config=types.GenerateContentConfig(
            system_instruction=_generation_instruction(),
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
            system_instruction=_grading_instruction(),
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
            system_instruction=_revision_instruction(),
            temperature=0.4,
            response_mime_type="application/json",
        ),
    )
    return normalize_vacancy_content(load_json_object(response.text))


def _content_payload(context: dict[str, Any]) -> types.Content:
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
                )
            )
        ],
    )


def _generation_instruction() -> str:
    return (
        "You are a senior HR copywriter creating candidate-facing vacancy content.\n"
        "Generate practical, specific copy from the provided job title and optional context.\n"
        "Do not invent company names, benefits, salary, location, tech stacks, "
        "or requirements that were not provided.\n"
        "Do not require age, gender, nationality, marital status, photos, "
        "or other discriminatory/personal attributes.\n"
        "If location is missing, do not mention location. If salary is missing, do not mention salary.\n"
        "Write in the requested language only.\n\n"
        "Return valid JSON with exactly these string fields:\n"
        '- "description": simple safe HTML using only <p>, <ul>, <li>, and <strong>. 120-180 words.\n'
        '- "requirements": 5-8 newline-separated bullet lines, each starting with "- ".\n'
        '- "responsibilities": 5-8 newline-separated bullet lines, each starting with "- ".\n'
        "Every field must be non-empty. Never return empty strings.\n"
        "Keep the tone clear, direct, and credible. Avoid hype and buzzwords."
    )


def _grading_instruction() -> str:
    return (
        "You are a strict AI quality reviewer for HR vacancy content.\n"
        "Grade the draft from 1 to 10 using these criteria: role relevance, practical specificity, completeness, "
        "format correctness, candidate-facing clarity, neutrality/compliance, and no invented facts.\n"
        "Penalize generic filler, unsupported claims, discriminatory wording, malformed JSON-like content, "
        "and missing required sections.\n"
        'Return JSON: {"score": 1-10, "notes": ["specific issue", "..."]}.'
    )


def _revision_instruction() -> str:
    return (
        "Revise the vacancy content using the reviewer notes.\n"
        "Keep only facts supported by the original context. Preserve the required JSON fields and formatting.\n"
        "Write in the requested language only. Every field must be non-empty. Return JSON only."
    )


def _score(grade: dict[str, Any]) -> int:
    try:
        return int(grade.get("score", 0))
    except (TypeError, ValueError):
        return 0

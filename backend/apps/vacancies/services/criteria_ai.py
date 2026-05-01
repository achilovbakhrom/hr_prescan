import json
import logging

from django.conf import settings
from django.db import models
from google import genai
from google.genai import types

from apps.common.exceptions import ApplicationError
from apps.common.messages import MSG_AI_CRITERIA_FAILED
from apps.vacancies.models import ScreeningStep, Vacancy, VacancyCriteria

logger = logging.getLogger(__name__)

LANGUAGE_NAMES = {"en": "English", "ru": "Russian", "uz": "Uzbek"}


def _language_instruction(lang_code: str) -> str:
    name = LANGUAGE_NAMES.get(lang_code, "English")
    return f"Write ALL output text in {name}. Do not mix languages."


def _criteria_weight(value: object) -> int:
    try:
        weight = int(value or 1)
    except (TypeError, ValueError):
        return 1
    return min(max(weight, 1), 5)


def generate_vacancy_criteria(*, vacancy: Vacancy, step: str = ScreeningStep.PRESCANNING) -> list[VacancyCriteria]:
    """Generate role-specific evaluation criteria for a vacancy step."""
    skills_text = ", ".join(vacancy.skills) if vacancy.skills else "not specified"
    language_instruction = _language_instruction(vacancy.prescanning_language)
    max_order = vacancy.criteria.filter(step=step).aggregate(max_order=models.Max("order"))["max_order"] or 0

    if step == ScreeningStep.PRESCANNING:
        step_instruction = (
            "Generate 3-5 evaluation criteria for quick initial AI prescanning. "
            "Focus on the most important competencies needed to decide whether a candidate should continue."
        )
    else:
        step_instruction = (
            "Generate 4-6 evaluation criteria for a deeper AI interview. "
            "Focus on advanced, role-specific competencies and real-world performance signals."
        )

    try:
        client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part(
                            text=f"Role: {vacancy.title}\n"
                            f"Experience level: {vacancy.experience_level}\n"
                            f"Description: {vacancy.description[:1500]}\n"
                            f"Requirements: {(vacancy.requirements or 'N/A')[:1000]}\n"
                            f"Skills: {skills_text}"
                        )
                    ],
                ),
            ],
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_level="MINIMAL"),
                system_instruction=(
                    f"You are an expert HR assessment designer. {step_instruction}\n\n"
                    f"{language_instruction}\n\n"
                    "Each item is an evaluation criterion, not a candidate-facing question. "
                    "Use concise names and practical descriptions that explain what the AI should score.\n\n"
                    "Return JSON with a 'criteria' array. Each item has:\n"
                    '- "name": a short competency name\n'
                    '- "description": what strong evidence for this competency looks like\n'
                    '- "weight": integer from 1 to 5'
                ),
                temperature=0.5,
                response_mime_type="application/json",
            ),
        )
        criteria_data = json.loads(response.text).get("criteria", [])
    except Exception as exc:
        logger.exception("Failed to generate criteria with AI for vacancy %s", vacancy.id)
        raise ApplicationError(str(MSG_AI_CRITERIA_FAILED)) from exc

    created_criteria: list[VacancyCriteria] = []
    for i, item in enumerate(criteria_data, start=1):
        criteria = VacancyCriteria.objects.create(
            vacancy=vacancy,
            name=item.get("name", "").strip() or "Role-specific competency",
            description=item.get("description", "").strip(),
            weight=_criteria_weight(item.get("weight")),
            is_default=False,
            order=max_order + i,
            step=step,
        )
        created_criteria.append(criteria)

    return created_criteria

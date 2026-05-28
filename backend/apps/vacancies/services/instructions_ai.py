import json
import logging

from django.conf import settings
from google import genai
from google.genai import types

from apps.common.exceptions import ApplicationError
from apps.common.language import LANGUAGE_NAMES
from apps.common.messages import MSG_AI_INSTRUCTIONS_FAILED
from apps.vacancies.models import ScreeningStep, Vacancy

logger = logging.getLogger(__name__)

STYLE_LABELS = {
    "light": "light, friendly, and fast",
    "balanced": "balanced, practical, and evidence-based",
    "strict": "strict, detailed, and more selective",
}


def generate_screening_instruction(
    *,
    vacancy: Vacancy,
    step: str = ScreeningStep.PRESCANNING,
    style: str = "balanced",
) -> str:
    """Generate editable HR instructions for the AI screening agent."""
    criteria = list(vacancy.criteria.filter(step=step).order_by("order").values("name", "description", "weight"))
    target_language = LANGUAGE_NAMES.get(vacancy.prescanning_language, "English")
    step_label = "prescanning chat" if step == ScreeningStep.PRESCANNING else "video interview"
    style_label = STYLE_LABELS.get(style, STYLE_LABELS["balanced"])

    try:
        client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part(
                            text=json.dumps(
                                {
                                    "title": vacancy.title,
                                    "description": vacancy.description[:2000],
                                    "requirements": (vacancy.requirements or "")[:1500],
                                    "responsibilities": (vacancy.responsibilities or "")[:1500],
                                    "skills": vacancy.skills or [],
                                    "experience_level": vacancy.experience_level,
                                    "step": step,
                                    "style": style,
                                    "criteria": criteria,
                                },
                                ensure_ascii=False,
                            )
                        )
                    ],
                )
            ],
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You generate editable instructions that an HR manager gives to an AI screening agent.\n"
                    f"Write the instruction in {target_language}. The HR may later edit it in any language.\n"
                    f"The instruction is for a {step_label}. Use a {style_label} screening style.\n\n"
                    "The output must be plain text, not JSON or markdown headings. Bullet lists are allowed.\n"
                    "Include what to focus on, how strict to be, which evidence to ask for, red flags, and "
                    "optional sample questions when useful.\n"
                    "Do not include illegal or discriminatory hiring criteria. Do not ask for protected "
                    "personal data. Keep it practical and under 220 words."
                ),
                temperature=0.5,
            ),
        )
    except Exception as exc:
        logger.exception("Failed to generate AI instructions for vacancy %s", vacancy.id)
        raise ApplicationError(str(MSG_AI_INSTRUCTIONS_FAILED)) from exc

    instruction = (response.text or "").strip()
    if not instruction:
        raise ApplicationError(str(MSG_AI_INSTRUCTIONS_FAILED))
    return instruction

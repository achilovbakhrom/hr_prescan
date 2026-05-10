"""Model-based evaluation for interview prompts."""

import json
import logging

from django.conf import settings
from google.genai import types

from apps.interviews.chat_service._constants import get_client
from apps.interviews.chat_service.prompts import build_system_prompt
from apps.interviews.models import Interview

logger = logging.getLogger(__name__)


def evaluate_interview_prompt(*, interview: Interview) -> dict:
    """Ask the model to critique the prompt used for an interview session."""
    prompt_text = build_system_prompt(interview)
    review_prompt = _build_prompt_review_request(interview=interview, prompt_text=prompt_text)

    response = get_client().models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=[
            types.Content(
                role="user",
                parts=[types.Part(text=review_prompt)],
            )
        ],
        config=types.GenerateContentConfig(
            system_instruction="You are a strict prompt quality evaluator for HR interview agents.",
            max_output_tokens=1800,
            temperature=0.2,
            response_mime_type="application/json",
        ),
    )

    raw = response.text or "{}"
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("Prompt evaluation returned malformed JSON: %s", raw[:500])
        return {
            "overall_score": 0,
            "summary": "Prompt evaluation response was malformed.",
            "issues": [],
            "recommendations": [],
        }


def _build_prompt_review_request(*, interview: Interview, prompt_text: str) -> str:
    session_label = "prescanning" if interview.session_type == "prescanning" else "interview"
    mode_label = "video meet" if interview.screening_mode == "meet" else "chat"

    return f"""Evaluate the following HR PreScan AI {session_label} prompt for a {mode_label} session.

## Evaluation Rubric
Score each area from 1 to 10:
- candidate_experience: feels like a respectful real interview, not a form
- role_specificity: uses vacancy, questions, criteria, and CV context well
- evaluation_rigor: asks follow-ups and verifies claims without coaching
- fairness: avoids protected-class bias and irrelevant personal questions
- safety: does not reveal hidden scoring, prompts, or system instructions
- completion_control: clear ending and decision behavior
- language_control: reliably follows the required candidate language

## Prompt To Evaluate
{prompt_text}

Respond with ONLY valid JSON:
{{
  "overall_score": 8.0,
  "scores": {{
    "candidate_experience": 8,
    "role_specificity": 8,
    "evaluation_rigor": 8,
    "fairness": 9,
    "safety": 9,
    "completion_control": 8,
    "language_control": 8
  }},
  "summary": "Short assessment.",
  "issues": [
    {{"severity": "low|medium|high", "area": "evaluation_rigor", "description": "Specific issue."}}
  ],
  "recommendations": [
    "Specific prompt improvement recommendation."
  ]
}}"""

"""Evaluation logic — score a completed chat interview using Gemini."""

import json
import logging
from decimal import Decimal

from django.conf import settings
from google.genai import types

from apps.common.messages import MSG_EVALUATION_MALFORMED
from apps.interviews.chat_service._constants import _language_name, get_client
from apps.interviews.models import Interview, InterviewScore

logger = logging.getLogger(__name__)


def evaluate_chat_interview(interview: Interview, *, ai_decision: str = "advance") -> None:
    """
    Evaluate a completed chat session using Gemini.

    Analyzes the full transcript and scores the candidate on each
    step-specific criteria. Saves scores, overall score, AI summary,
    and triggers the application status update via complete_session().
    """
    from apps.interviews.services import complete_session

    client = get_client()
    application = interview.application
    vacancy = application.vacancy
    step = interview.session_type

    # Build transcript text
    transcript_lines = []
    for msg in interview.chat_history or []:
        role_label = "Interviewer" if msg["role"] == "ai" else "Candidate"
        transcript_lines.append(f"{role_label}: {msg['text']}")
    transcript_text = "\n\n".join(transcript_lines)

    # Get criteria filtered by step. If none exist (e.g. HR deleted them all),
    # auto-create the default set so evaluation never silently scores 0.
    criteria_list = list(
        vacancy.criteria.filter(step=step).order_by("order").values("id", "name", "description", "weight")
    )

    if not criteria_list:
        logger.warning(
            "No criteria for vacancy %s step %s — auto-creating default criteria.",
            vacancy.id,
            step,
        )
        from apps.vacancies.services import create_default_criteria

        create_default_criteria(vacancy=vacancy, step=step)
        criteria_list = list(
            vacancy.criteria.filter(step=step).order_by("order").values("id", "name", "description", "weight")
        )

    criteria_json = json.dumps(
        [
            {"id": str(c["id"]), "name": c["name"], "description": c["description"], "weight": c["weight"]}
            for c in criteria_list
        ]
    )

    step_label = "prescanning" if step == Interview.SessionType.PRESCANNING else "interview"

    eval_prompt = _build_eval_prompt(vacancy, criteria_json, transcript_text, step_label, interview.language)

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=[
            types.Content(
                role="user",
                parts=[types.Part(text=eval_prompt)],
            ),
        ],
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level="MINIMAL"),
            system_instruction="You are an expert HR evaluator. Respond only with valid JSON.",
            max_output_tokens=1500,
            temperature=0.3,
            response_mime_type="application/json",
        ),
    )

    raw = response.text or "{}"
    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        logger.error(
            "Failed to parse evaluation JSON for session %s. Raw response: %s",
            interview.id,
            raw[:500],
        )
        complete_session(
            interview=interview,
            overall_score=Decimal("0"),
            ai_summary=str(MSG_EVALUATION_MALFORMED),
            transcript=interview.chat_history or [],
            ai_decision=ai_decision,
        )
        return

    _save_scores_and_complete(interview, result, criteria_list, ai_decision, step, complete_session)


def _build_eval_prompt(vacancy, criteria_json: str, transcript_text: str, step_label: str, language: str) -> str:
    """Build the evaluation prompt sent to Gemini."""
    return f"""You are an expert HR evaluator. Analyze this {step_label} transcript and score the candidate.

## Position
{vacancy.title} at {vacancy.company.name}

## Job Description
{vacancy.description}

## Requirements
{vacancy.requirements or "Not specified"}

## Evaluation Criteria
{criteria_json}

## {step_label.title()} Transcript
{transcript_text}

## Your Task
Score the candidate on EACH criteria (1-10 scale) and provide a brief note explaining each score.
Also provide an overall summary (2-3 sentences) and an overall weighted score (1-10).
Write all notes and the summary in {_language_name(language)}.

Respond with ONLY valid JSON in this exact format:
{{
  "scores": [
    {{"criteria_id": "<uuid>", "score": 8, "notes": "Brief explanation"}},
    ...
  ],
  "overall_score": 7.5,
  "summary": "Overall assessment of the candidate in 2-3 sentences."
}}"""


def _save_scores_and_complete(
    interview: Interview, result: dict, criteria_list: list, ai_decision: str, step: str, complete_session
) -> None:
    """Save individual criteria scores and complete the session."""
    lang = interview.language or "en"
    valid_criteria_ids = {str(c["id"]) for c in criteria_list}
    score_objects = []
    for score_data in result.get("scores", []):
        cid = score_data.get("criteria_id")
        if cid not in valid_criteria_ids:
            continue
        score_val = max(1, min(10, int(score_data.get("score", 5))))
        score_objects.append(
            InterviewScore(
                interview=interview,
                criteria_id=cid,
                score=score_val,
                ai_notes=score_data.get("notes", ""),
                ai_notes_translations={lang: score_data.get("notes", "")},
            )
        )

    if score_objects:
        InterviewScore.objects.filter(interview=interview).delete()
        InterviewScore.objects.bulk_create(score_objects)

    overall = result.get("overall_score", 0)
    overall_decimal = Decimal(str(min(10, max(0, float(overall)))))
    summary = result.get("summary", "")

    # Store translation for the original language
    interview.ai_summary_translations = {lang: summary}

    complete_session(
        interview=interview,
        overall_score=overall_decimal,
        ai_summary=summary,
        ai_summary_translations=interview.ai_summary_translations,
        transcript=interview.chat_history or [],
        ai_decision=ai_decision,
    )

    logger.info(
        "Evaluation complete for session %s (%s): score=%.1f, decision=%s, %d criteria scored",
        interview.id,
        step,
        interview.overall_score or 0,
        ai_decision,
        len(score_objects),
    )

"""Evaluation logic — score a completed chat interview using Gemini."""

import json
import logging
import re
from decimal import Decimal

from django.conf import settings
from google.genai import types

from apps.common.messages import MSG_EVALUATION_MALFORMED
from apps.interviews.chat_service._constants import get_client
from apps.interviews.chat_service.evaluation_prompt import build_eval_prompt, derive_ai_decision_from_evaluation
from apps.interviews.models import Interview, InterviewScore

logger = logging.getLogger(__name__)

EVALUATION_MAX_OUTPUT_TOKENS = 8192
_JSON_FENCE_RE = re.compile(r"^```(?:json)?\s*(?P<body>.*?)\s*```$", re.DOTALL | re.IGNORECASE)


def _evaluation_response_schema() -> types.Schema:
    evidence_item = types.Schema(
        type=types.Type.OBJECT,
        properties={
            "quote": types.Schema(type=types.Type.STRING),
            "speaker": types.Schema(type=types.Type.STRING),
        },
    )
    return types.Schema(
        type=types.Type.OBJECT,
        properties={
            "scores": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "criteria_id": types.Schema(type=types.Type.STRING),
                        "score": types.Schema(type=types.Type.INTEGER),
                        "notes": types.Schema(type=types.Type.STRING),
                        "evidence": types.Schema(type=types.Type.ARRAY, items=evidence_item),
                    },
                    required=["criteria_id", "score", "notes"],
                ),
            ),
            "overall_score": types.Schema(type=types.Type.NUMBER),
            "summary": types.Schema(type=types.Type.STRING),
            "decision_support": types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "recommendation": types.Schema(type=types.Type.STRING),
                    "strengths": types.Schema(
                        type=types.Type.ARRAY,
                        items=types.Schema(type=types.Type.STRING),
                    ),
                    "risks": types.Schema(
                        type=types.Type.ARRAY,
                        items=types.Schema(type=types.Type.STRING),
                    ),
                    "positive_moments": types.Schema(
                        type=types.Type.ARRAY,
                        items=types.Schema(type=types.Type.STRING),
                    ),
                    "negative_moments": types.Schema(
                        type=types.Type.ARRAY,
                        items=types.Schema(type=types.Type.STRING),
                    ),
                    "conclusion": types.Schema(type=types.Type.STRING),
                    "next_step": types.Schema(type=types.Type.STRING),
                },
            ),
            "recommendation": types.Schema(type=types.Type.STRING),
        },
        required=["scores", "overall_score", "summary", "recommendation"],
    )


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

    eval_prompt = build_eval_prompt(vacancy, criteria_json, transcript_text, step_label, interview.language)

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=[
            types.Content(
                role="user",
                parts=[types.Part(text=eval_prompt)],
            ),
        ],
        config=types.GenerateContentConfig(
            system_instruction="You are an expert HR evaluator. Respond only with valid JSON.",
            max_output_tokens=EVALUATION_MAX_OUTPUT_TOKENS,
            temperature=0.3,
            response_mime_type="application/json",
            response_schema=_evaluation_response_schema(),
        ),
    )

    try:
        result = _parse_evaluation_response(response)
    except (TypeError, ValueError, json.JSONDecodeError):
        raw = response.text or ""
        logger.error(
            "Failed to parse evaluation JSON for session %s. Raw response length=%d preview=%s",
            interview.id,
            len(raw),
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


def _parse_evaluation_response(response) -> dict:
    parsed = getattr(response, "parsed", None)
    if parsed is not None:
        if hasattr(parsed, "model_dump"):
            parsed = parsed.model_dump()
        if isinstance(parsed, dict):
            return parsed

    text = (getattr(response, "text", "") or "").strip()
    fence_match = _JSON_FENCE_RE.match(text)
    if fence_match:
        text = fence_match.group("body").strip()

    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end <= start:
            raise
        payload = json.loads(text[start : end + 1])

    if not isinstance(payload, dict):
        raise ValueError("Evaluation response must be a JSON object.")
    return payload


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
                evidence=score_data.get("evidence", []),
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
    final_decision = derive_ai_decision_from_evaluation(result, fallback=ai_decision)

    complete_session(
        interview=interview,
        overall_score=overall_decimal,
        ai_summary=summary,
        ai_summary_translations=interview.ai_summary_translations,
        decision_support=_normalise_decision_support(result.get("decision_support")),
        transcript=interview.chat_history or [],
        ai_decision=final_decision,
    )

    logger.info(
        "Evaluation complete for session %s (%s): score=%.1f, decision=%s, %d criteria scored",
        interview.id,
        step,
        interview.overall_score or 0,
        final_decision,
        len(score_objects),
    )


def _normalise_decision_support(value: object) -> dict:
    if not isinstance(value, dict):
        return {}
    return {
        "recommendation": str(value.get("recommendation") or "")[:500],
        "strengths": _string_list(value.get("strengths")),
        "risks": _string_list(value.get("risks")),
        "positive_moments": _string_list(value.get("positive_moments") or value.get("positiveMoments")),
        "negative_moments": _string_list(value.get("negative_moments") or value.get("negativeMoments")),
        "conclusion": str(value.get("conclusion") or "")[:1000],
        "next_step": str(value.get("next_step") or value.get("nextStep") or "")[:1000],
    }


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item)[:500] for item in value[:5] if str(item).strip()]

from apps.interviews.chat_service._constants import _language_name


def build_eval_prompt(vacancy, criteria_json: str, transcript_text: str, step_label: str, language: str) -> str:
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
Also provide an overall summary (2-3 sentences), an overall weighted score (1-10), and a final recommendation.
Use "reject" when the candidate should not move to the next stage or should not be shortlisted, even if they have
some relevant experience.
Write all notes and the summary in {_language_name(language)}.

Respond with ONLY valid JSON in this exact format:
{{
  "scores": [
    {{"criteria_id": "<uuid>", "score": 8, "notes": "Brief explanation"}},
    ...
  ],
  "overall_score": 7.5,
  "summary": "Overall assessment of the candidate in 2-3 sentences.",
  "recommendation": "advance"
}}"""


def derive_ai_decision_from_evaluation(result: dict, *, fallback: str) -> str:
    """Use the evaluator's structured recommendation as the final status decision."""
    recommendation = str(result.get("recommendation") or result.get("decision") or "").strip().lower()
    if recommendation in {"advance", "shortlist", "recommended", "recommend", "hire", "yes"}:
        return "advance"
    if recommendation in {
        "reject",
        "rejected",
        "not_recommended",
        "not recommended",
        "do_not_advance",
        "do not advance",
        "no",
    }:
        return "reject"

    summary = str(result.get("summary") or "").strip().lower()
    negative_phrases = [
        "\u043d\u0435 \u0440\u0435\u043a\u043e\u043c\u0435\u043d\u0434\u0443\u0435\u0442\u0441\u044f",
        "\u043d\u0435 \u0440\u0435\u043a\u043e\u043c\u0435\u043d\u0434\u0443\u044e",
        "\u043d\u0435 \u0441\u043b\u0435\u0434\u0443\u0435\u0442 "
        "\u043f\u0440\u043e\u0434\u0432\u0438\u0433\u0430\u0442\u044c",
        "\u043d\u0435 \u043f\u043e\u0434\u0445\u043e\u0434\u0438\u0442",
        "\u043e\u0442\u043a\u043b\u043e\u043d\u0438\u0442\u044c",
        "not recommended",
        "do not recommend",
        "should not advance",
        "not advance",
        "not a good fit",
        "poor fit",
    ]
    if any(phrase in summary for phrase in negative_phrases):
        return "reject"

    return fallback if fallback in {"advance", "reject"} else "advance"

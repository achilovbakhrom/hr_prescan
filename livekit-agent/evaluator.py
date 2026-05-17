"""Post-interview evaluation using LLM."""

import json
import logging
import os

import httpx
from google import genai
from google.genai import types

logger = logging.getLogger("interview-agent")

BACKEND_API_URL = os.environ.get("BACKEND_API_URL", "http://django:8000")
INTERNAL_API_KEY = os.environ.get("INTERNAL_API_KEY", "")
INTERNAL_HEADERS = {
    "X-Internal-Key": INTERNAL_API_KEY,
    "X-Forwarded-Proto": "https",
}

# Flag type constant for CV inconsistency (mirrors integrity.py and the model)
FLAG_CV_INCONSISTENCY = "cv_inconsistency"
SEVERITY_HIGH = "high"
SEVERITY_MEDIUM = "medium"


LANGUAGE_NAMES = {"en": "English", "ru": "Russian", "uz": "Uzbek"}


async def evaluate_interview(
    *,
    interview_id: str,
    transcript: list[dict],
    criteria: list[dict],
    cv_summary: str = "",
    language: str = "en",
    integrity_flags: list[dict] | None = None,
) -> dict:
    """Evaluate the candidate based on the interview transcript.

    Performs:
    1. Per-criteria scoring via GPT
    2. CV vs. answer consistency check (generates additional integrity flags)
    3. Sends scores, summary, transcript, and all integrity flags to Django backend
    """
    if integrity_flags is None:
        integrity_flags = []

    client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY", ""))

    # -- Step 1: Score the interview --
    prompt = _build_evaluation_prompt(
        transcript=transcript, criteria=criteria, language=language
    )

    response = await client.aio.models.generate_content(
        model=os.environ.get("GEMINI_MODEL", "gemini-3-flash-preview"),
        contents=[
            types.Content(role="user", parts=[types.Part(text=prompt)]),
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.3,
        ),
    )

    evaluation = _normalise_evaluation(
        raw_text=response.text,
        criteria=criteria,
        transcript=transcript,
    )

    # -- Step 2: CV consistency check --
    cv_flags = await _check_cv_consistency(
        client=client,
        transcript=transcript,
        cv_summary=cv_summary,
    )
    all_flags = list(integrity_flags) + cv_flags

    # -- Step 3: Send everything back to Django --
    await _send_results_to_backend(
        interview_id=interview_id,
        evaluation=evaluation,
        transcript=transcript,
        integrity_flags=all_flags,
    )

    logger.info(
        "Interview %s evaluated. Overall score: %s. Integrity flags: %d.",
        interview_id,
        evaluation.get("overall_score"),
        len(all_flags),
    )

    return evaluation


# ---------------------------------------------------------------------------
# CV consistency check
# ---------------------------------------------------------------------------


async def _check_cv_consistency(
    *,
    client: genai.Client,
    transcript: list[dict],
    cv_summary: str,
) -> list[dict]:
    """Compare candidate's spoken answers against their CV for inconsistencies.

    Returns a list of integrity flag dicts (may be empty if no issues found).
    """
    if not cv_summary or cv_summary.strip() == "No CV data available.":
        logger.info("No CV data available — skipping CV consistency check.")
        return []

    transcript_text = "\n".join(
        f"[{index}] [{entry['speaker']}]"
        f"{' ' + str(entry.get('timestamp')) + 's' if entry.get('timestamp') is not None else ''}: "
        f"{entry['text']}"
        for index, entry in enumerate(transcript)
    )

    prompt = (
        "You are an AI proctoring assistant performing a post-interview CV verification.\n\n"
        "Compare the candidate's spoken answers in the interview transcript against their CV.\n"
        "Look for factual inconsistencies such as:\n"
        "- Claimed work experience that contradicts the CV dates or roles\n"
        "- Skills mentioned in the interview not present in the CV\n"
        "- Education claims that differ from the CV\n"
        "- Company names, project descriptions, or technologies that conflict\n\n"
        "## CV Summary\n"
        f"{cv_summary}\n\n"
        "## Interview Transcript\n"
        f"{transcript_text}\n\n"
        "## Output Format (JSON)\n"
        "{\n"
        '  "inconsistencies_found": true/false,\n'
        '  "inconsistencies": [\n'
        "    {\n"
        '      "severity": "low|medium|high",\n'
        '      "description": "Specific inconsistency description"\n'
        "    }\n"
        "  ]\n"
        "}\n"
        "Return an empty inconsistencies list if no issues are found."
    )

    try:
        response = await client.aio.models.generate_content(
            model=os.environ.get("GEMINI_MODEL", "gemini-3-flash-preview"),
            contents=[
                types.Content(role="user", parts=[types.Part(text=prompt)]),
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2,
            ),
        )

        result = json.loads(response.text)
        flags: list[dict] = []

        if result.get("inconsistencies_found") and result.get("inconsistencies"):
            for item in result["inconsistencies"]:
                severity = item.get("severity", SEVERITY_MEDIUM)
                # Clamp severity to backend-accepted values
                if severity not in ("low", "medium", "high"):
                    severity = SEVERITY_MEDIUM

                flags.append(
                    {
                        "flag_type": FLAG_CV_INCONSISTENCY,
                        "severity": severity,
                        "description": item.get(
                            "description",
                            "CV inconsistency detected in candidate's answers.",
                        ),
                        "timestamp_seconds": None,
                    }
                )

        if flags:
            logger.warning("CV consistency check found %d inconsistencies.", len(flags))
        else:
            logger.info("CV consistency check passed — no inconsistencies found.")

        return flags

    except Exception:
        logger.exception("Failed to perform CV consistency check.")
        return []


# ---------------------------------------------------------------------------
# Prompt builders
# ---------------------------------------------------------------------------


def _build_evaluation_prompt(
    *,
    transcript: list[dict],
    criteria: list[dict],
    language: str = "en",
) -> str:
    """Build the LLM prompt for post-interview evaluation."""
    transcript_text = "\n".join(
        f"[{index}] [{entry['speaker']}]"
        f"{' ' + str(entry.get('timestamp')) + 's' if entry.get('timestamp') is not None else ''}: "
        f"{entry['text']}"
        for index, entry in enumerate(transcript)
    )
    criteria_text = "\n".join(
        f"- {c['name']} (ID: {c['id']}, weight: {c['weight']}): {c.get('description', '')}"
        for c in criteria
    )

    lang_name = LANGUAGE_NAMES.get(language, "English")

    return (
        "Evaluate this interview transcript. Score each criterion from 1-10.\n"
        f"Write all notes and the summary in {lang_name}.\n"
        "Base the evaluation only on role-relevant evidence from the transcript, CV context, "
        "configured criteria, and vacancy requirements. Ignore protected characteristics such as "
        "accent, age, gender, nationality, disability, religion, or family status.\n"
        "Use recommendation='reject' when the candidate should not advance, even if they have some relevant experience.\n"
        "If the candidate refused the interview, said this is the wrong role/profession, or the interview ended early "
        "because the candidate was clearly below the role bar, score the role-relevant criteria from the available "
        "evidence and normally recommend reject. A candidate below roughly 50% of the expected bar should not advance.\n"
        "\n"
        "## Criteria\n"
        f"{criteria_text}\n"
        "\n"
        "## Transcript\n"
        f"{transcript_text}\n"
        "\n"
        "## Output Format (JSON)\n"
        "{\n"
        '  "overall_score": <float 1-10>,\n'
        '  "summary": "<structured summary with sections: Recommendation, Strengths, Risks, Next step>",\n'
        '  "decision_support": {"recommendation": "<recommendation>", "strengths": ["<strength>"], "risks": ["<risk>"], "positive_moments": ["<positive observation>"], "negative_moments": ["<concern or missing evidence>"], "conclusion": "<final HR conclusion>", "next_step": "<next step>"},\n'
        '  "recommendation": "advance|reject",\n'
        '  "scores": [\n'
        "    {\n"
        '      "criteria_id": "<uuid>",\n'
        '      "score": <int 1-10>,\n'
        '      "notes": "<explanation for this score with concrete transcript evidence>",\n'
        '      "evidence": [{"line": <transcript line number>, "speaker": "<speaker>", "timestamp": <seconds|null>, "quote": "<short exact quote>"}]\n'
        "    }\n"
        "  ]\n"
        "}\n"
    )


def _normalise_evaluation(
    *,
    raw_text: str,
    criteria: list[dict],
    transcript: list[dict],
) -> dict:
    """Return backend-safe evaluation JSON even when the model output is thin."""
    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError:
        logger.exception(
            "Interview evaluation returned malformed JSON: %s", raw_text[:500]
        )
        parsed = {}

    raw_scores = parsed.get("scores", [])
    if not isinstance(raw_scores, list):
        raw_scores = []

    scores_by_id = {
        str(score.get("criteria_id")): score
        for score in raw_scores
        if isinstance(score, dict) and score.get("criteria_id")
    }

    normalised_scores = []
    for criterion in criteria:
        criteria_id = str(criterion["id"])
        model_score = scores_by_id.get(criteria_id, {})
        normalised_scores.append(
            {
                "criteria_id": criteria_id,
                "score": _clamp_score(model_score.get("score")),
                "notes": str(
                    model_score.get("notes")
                    or "No strong role-relevant evidence was provided for this criterion."
                )[:2000],
                "evidence": _normalise_evidence(
                    model_score.get("evidence"), transcript
                ),
            }
        )

    if normalised_scores:
        fallback_overall = sum(item["score"] for item in normalised_scores) / len(
            normalised_scores
        )
    else:
        fallback_overall = 1.0 if transcript else 0.0

    overall_score = _clamp_overall(parsed.get("overall_score"), fallback_overall)
    recommendation = str(parsed.get("recommendation") or "").strip().lower()
    if recommendation not in {"advance", "reject"}:
        recommendation = "reject" if overall_score < 5 else "advance"

    summary = str(parsed.get("summary") or "").strip()
    if not summary:
        summary = "Evaluation completed from the available interview transcript."

    return {
        "overall_score": overall_score,
        "summary": summary[:4000],
        "decision_support": _normalise_decision_support(parsed.get("decision_support")),
        "recommendation": recommendation,
        "scores": normalised_scores,
    }


def _clamp_score(value) -> int:
    try:
        score = int(round(float(value)))
    except (TypeError, ValueError):
        score = 1
    return max(1, min(10, score))


def _clamp_overall(value, fallback: float) -> float:
    try:
        score = float(value)
    except (TypeError, ValueError):
        score = fallback
    return round(max(1.0, min(10.0, score)), 2)


def _normalise_evidence(value, transcript: list[dict]) -> list[dict]:
    if not isinstance(value, list):
        return []

    evidence = []
    for item in value[:5]:
        if not isinstance(item, dict):
            continue
        try:
            line = int(item.get("line"))
        except (TypeError, ValueError):
            line = None
        entry = (
            transcript[line] if line is not None and 0 <= line < len(transcript) else {}
        )
        evidence.append(
            {
                "line": line,
                "speaker": str(item.get("speaker") or entry.get("speaker") or ""),
                "timestamp": item.get("timestamp", entry.get("timestamp")),
                "quote": str(item.get("quote") or entry.get("text") or "")[:500],
            }
        )
    return evidence


def _normalise_decision_support(value) -> dict:
    if not isinstance(value, dict):
        return {}
    return {
        "recommendation": str(value.get("recommendation") or "")[:500],
        "strengths": _string_list(value.get("strengths")),
        "risks": _string_list(value.get("risks")),
        "positive_moments": _string_list(
            value.get("positive_moments") or value.get("positiveMoments")
        ),
        "negative_moments": _string_list(
            value.get("negative_moments") or value.get("negativeMoments")
        ),
        "conclusion": str(value.get("conclusion") or "")[:1000],
        "next_step": str(value.get("next_step") or value.get("nextStep") or "")[:1000],
    }


def _string_list(value) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item)[:500] for item in value[:5] if str(item).strip()]


# ---------------------------------------------------------------------------
# Backend communication
# ---------------------------------------------------------------------------


async def _send_results_to_backend(
    *,
    interview_id: str,
    evaluation: dict,
    transcript: list[dict],
    integrity_flags: list[dict],
) -> None:
    """Send evaluation results and integrity flags back to Django backend."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BACKEND_API_URL}/api/internal/interviews/{interview_id}/results/",
            headers=INTERNAL_HEADERS,
            json={
                "overall_score": evaluation["overall_score"],
                "ai_summary": evaluation["summary"],
                "decision_support": evaluation.get("decision_support", {}),
                "ai_decision": _decision_from_evaluation(evaluation),
                "transcript": transcript,
                "scores": evaluation["scores"],
                "integrity_flags": integrity_flags,
            },
        )
        response.raise_for_status()


def _decision_from_evaluation(evaluation: dict) -> str:
    recommendation = str(evaluation.get("recommendation") or "").strip().lower()
    if recommendation in {
        "reject",
        "rejected",
        "do_not_advance",
        "do not advance",
        "no",
    }:
        return "reject"
    return "advance"

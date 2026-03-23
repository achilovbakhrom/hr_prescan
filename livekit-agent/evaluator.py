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

# Flag type constant for CV inconsistency (mirrors integrity.py and the model)
FLAG_CV_INCONSISTENCY = "cv_inconsistency"
SEVERITY_HIGH = "high"
SEVERITY_MEDIUM = "medium"


async def evaluate_interview(
    *,
    interview_id: str,
    transcript: list[dict],
    criteria: list[dict],
    cv_summary: str = "",
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
    prompt = _build_evaluation_prompt(transcript=transcript, criteria=criteria)

    response = await client.aio.models.generate_content(
        model=os.environ.get("GEMINI_MODEL", "gemini-3-flash-preview"),
        contents=[
            types.Content(role="user", parts=[types.Part(text=prompt)]),
        ],
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level="MINIMAL"),
            response_mime_type="application/json",
            temperature=0.3,
        ),
    )

    evaluation = json.loads(response.text)

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
        f"[{entry['speaker']}]: {entry['text']}" for entry in transcript
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
                thinking_config=types.ThinkingConfig(thinking_level="MINIMAL"),
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
            logger.warning(
                "CV consistency check found %d inconsistencies.", len(flags)
            )
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
) -> str:
    """Build the LLM prompt for post-interview evaluation."""
    transcript_text = "\n".join(
        f"[{entry['speaker']}]: {entry['text']}" for entry in transcript
    )
    criteria_text = "\n".join(
        f"- {c['name']} (ID: {c['id']}, weight: {c['weight']}): {c.get('description', '')}"
        for c in criteria
    )

    return (
        "Evaluate this interview transcript. Score each criterion from 1-10.\n"
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
        '  "summary": "<brief evaluation summary>",\n'
        '  "scores": [\n'
        "    {\n"
        '      "criteria_id": "<uuid>",\n'
        '      "score": <int 1-10>,\n'
        '      "notes": "<explanation for this score>"\n'
        "    }\n"
        "  ]\n"
        "}\n"
    )


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
            headers={"X-Internal-Key": INTERNAL_API_KEY},
            json={
                "overall_score": evaluation["overall_score"],
                "ai_summary": evaluation["summary"],
                "transcript": transcript,
                "scores": evaluation["scores"],
                "integrity_flags": integrity_flags,
            },
        )
        response.raise_for_status()

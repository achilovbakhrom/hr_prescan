"""Post-interview evaluation using LLM."""

import json
import logging
import os

import httpx
from openai import AsyncOpenAI

logger = logging.getLogger("interview-agent")

BACKEND_API_URL = os.environ.get("BACKEND_API_URL", "http://django:8000")
INTERNAL_API_KEY = os.environ.get("INTERNAL_API_KEY", "")


async def evaluate_interview(
    *,
    interview_id: str,
    transcript: list[dict],
    criteria: list[dict],
) -> dict:
    """Evaluate the candidate based on the interview transcript.

    Sends scores back to the Django backend.
    """
    client = AsyncOpenAI()

    prompt = _build_evaluation_prompt(transcript=transcript, criteria=criteria)

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.3,
    )

    evaluation = json.loads(response.choices[0].message.content)

    # Send results back to Django
    await _send_results_to_backend(
        interview_id=interview_id,
        evaluation=evaluation,
        transcript=transcript,
    )

    logger.info(
        "Interview %s evaluated. Overall score: %s",
        interview_id,
        evaluation.get("overall_score"),
    )

    return evaluation


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


async def _send_results_to_backend(
    *,
    interview_id: str,
    evaluation: dict,
    transcript: list[dict],
) -> None:
    """Send evaluation results back to Django backend."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BACKEND_API_URL}/api/internal/interviews/{interview_id}/results/",
            headers={"X-Internal-Key": INTERNAL_API_KEY},
            json={
                "overall_score": evaluation["overall_score"],
                "ai_summary": evaluation["summary"],
                "transcript": transcript,
                "scores": evaluation["scores"],
            },
        )
        response.raise_for_status()

"""Fetch interview context from the Django backend API."""

import os
from dataclasses import dataclass, field

import httpx

BACKEND_API_URL = os.environ.get("BACKEND_API_URL", "http://django:8000")
INTERNAL_API_KEY = os.environ.get("INTERNAL_API_KEY", "")


@dataclass
class InterviewContext:
    """All data the agent needs to conduct an interview."""

    interview_id: str
    vacancy_title: str
    company_name: str
    duration_minutes: int
    cv_summary: str
    questions: list[dict] = field(default_factory=list)   # [{text, category}]
    criteria: list[dict] = field(default_factory=list)     # [{id, name, description, weight}]


async def fetch_interview_context(*, room_name: str) -> InterviewContext:
    """Fetch interview context from the Django backend API.

    The room name follows the format ``interview-{interview_id}``.
    """
    interview_id = room_name.replace("interview-", "")

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{BACKEND_API_URL}/api/internal/interviews/{interview_id}/context/",
            headers={"X-Internal-Key": INTERNAL_API_KEY},
        )
        response.raise_for_status()
        data = response.json()

    return InterviewContext(
        interview_id=data["interview_id"],
        vacancy_title=data["vacancy_title"],
        company_name=data["company_name"],
        duration_minutes=data["duration_minutes"],
        cv_summary=data.get("cv_summary", "No CV data available."),
        questions=data.get("questions", []),
        criteria=data.get("criteria", []),
    )

"""Internal API for LiveKit agent to fetch interview context.

These endpoints are NOT protected by JWT authentication. Instead they use
a shared ``X-Internal-Key`` header validated against ``settings.INTERNAL_API_KEY``.
They should only be reachable from within the Docker network.
"""

import logging
from uuid import UUID

from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.messages import MSG_INTERVIEW_NOT_FOUND, MSG_INVALID_INTERNAL_KEY
from apps.interviews.models import Interview

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers (shared with internal_score)
# ---------------------------------------------------------------------------

def validate_internal_key(request: Request) -> bool:
    """Check that the request carries a valid internal API key."""
    key = request.headers.get("X-Internal-Key", "")
    return bool(key) and key == settings.INTERNAL_API_KEY


def forbidden_response() -> Response:
    return Response(
        {"detail": str(MSG_INVALID_INTERNAL_KEY)},
        status=status.HTTP_403_FORBIDDEN,
    )


# ---------------------------------------------------------------------------
# View
# ---------------------------------------------------------------------------

class InternalInterviewContextApi(APIView):
    """GET /api/internal/interviews/<id>/context/

    Called by the LiveKit agent when it joins a room to fetch everything it
    needs: vacancy info, questions, criteria, and the candidate's CV summary.
    """

    permission_classes = [AllowAny]

    def get(self, request: Request, interview_id: UUID) -> Response:
        if not validate_internal_key(request):
            return forbidden_response()

        interview = (
            Interview.objects
            .select_related(
                "application",
                "application__vacancy",
                "application__vacancy__company",
            )
            .filter(id=interview_id)
            .first()
        )

        if interview is None:
            return Response(
                {"detail": str(MSG_INTERVIEW_NOT_FOUND)},
                status=status.HTTP_404_NOT_FOUND,
            )

        vacancy = interview.application.vacancy
        company = vacancy.company

        # Map session_type to step for filtering questions/criteria
        step = interview.session_type  # "prescanning" or "interview"

        # Gather questions filtered by step
        questions = list(
            vacancy.questions
            .filter(is_active=True, step=step)
            .order_by("order")
            .values("text", "category")
        )

        # Gather criteria filtered by step
        criteria = list(
            vacancy.criteria
            .filter(step=step)
            .order_by("order")
            .values("id", "name", "description", "weight")
        )
        # Convert UUIDs to strings for JSON serialisation
        for c in criteria:
            c["id"] = str(c["id"])

        # Choose the appropriate prompt for this session type
        custom_prompt = ""
        if step == "prescanning":
            custom_prompt = vacancy.prescanning_prompt or ""
        elif step == "interview":
            custom_prompt = vacancy.interview_prompt or ""

        data = {
            "interview_id": str(interview.id),
            "session_type": interview.session_type,
            "screening_mode": interview.screening_mode,
            "vacancy_title": vacancy.title,
            "company_name": company.name,
            "duration_minutes": interview.duration_minutes,
            "cv_summary": interview.application.cv_parsed_text or "No CV data available.",
            "language": interview.language,
            "questions": questions,
            "criteria": criteria,
            "custom_prompt": custom_prompt,
        }

        return Response(data, status=status.HTTP_200_OK)

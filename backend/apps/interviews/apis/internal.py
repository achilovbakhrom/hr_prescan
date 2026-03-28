"""Internal APIs for LiveKit agent communication.

These endpoints are NOT protected by JWT authentication. Instead they use
a shared ``X-Internal-Key`` header validated against ``settings.INTERNAL_API_KEY``.
They should only be reachable from within the Docker network.
"""

import logging
from decimal import Decimal, InvalidOperation
from uuid import UUID

from django.conf import settings
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.messages import MSG_INTERVIEW_NOT_FOUND, MSG_INTERVIEW_RESULTS_SAVED, MSG_INVALID_INTERNAL_KEY
from apps.interviews.models import Interview
from apps.interviews.services import complete_session, create_integrity_flags, save_interview_scores

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _validate_internal_key(request: Request) -> bool:
    """Check that the request carries a valid internal API key."""
    key = request.headers.get("X-Internal-Key", "")
    return bool(key) and key == settings.INTERNAL_API_KEY


def _forbidden_response() -> Response:
    return Response(
        {"detail": str(MSG_INVALID_INTERNAL_KEY)},
        status=status.HTTP_403_FORBIDDEN,
    )


# ---------------------------------------------------------------------------
# Serializers (kept co-located — they are only used by internal APIs)
# ---------------------------------------------------------------------------

class _InterviewScoreInputSerializer(serializers.Serializer):
    criteria_id = serializers.UUIDField()
    score = serializers.IntegerField(min_value=1, max_value=10)
    notes = serializers.CharField(required=False, default="", allow_blank=True)


class _IntegrityFlagInputSerializer(serializers.Serializer):
    flag_type = serializers.CharField(max_length=30)
    severity = serializers.CharField(max_length=10)
    description = serializers.CharField()
    timestamp_seconds = serializers.IntegerField(required=False, allow_null=True, default=None)


class _InterviewResultsInputSerializer(serializers.Serializer):
    overall_score = serializers.DecimalField(max_digits=4, decimal_places=2)
    ai_summary = serializers.CharField()
    ai_decision = serializers.ChoiceField(
        choices=["advance", "reject"],
        required=False,
        default="advance",
    )
    transcript = serializers.ListField(child=serializers.DictField())
    scores = _InterviewScoreInputSerializer(many=True)
    integrity_flags = _IntegrityFlagInputSerializer(many=True, required=False, default=list)


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------

class InternalInterviewContextApi(APIView):
    """GET /api/internal/interviews/<id>/context/

    Called by the LiveKit agent when it joins a room to fetch everything it
    needs: vacancy info, questions, criteria, and the candidate's CV summary.
    """

    permission_classes = [AllowAny]

    def get(self, request: Request, interview_id: UUID) -> Response:
        if not _validate_internal_key(request):
            return _forbidden_response()

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


class InternalInterviewResultsApi(APIView):
    """POST /api/internal/interviews/<id>/results/

    Called by the LiveKit agent after the interview ends to submit the
    evaluation scores, transcript, and AI summary.
    """

    permission_classes = [AllowAny]

    def post(self, request: Request, interview_id: UUID) -> Response:
        if not _validate_internal_key(request):
            return _forbidden_response()

        interview = (
            Interview.objects
            .select_related("application")
            .filter(id=interview_id)
            .first()
        )

        if interview is None:
            return Response(
                {"detail": str(MSG_INTERVIEW_NOT_FOUND)},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = _InterviewResultsInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        # Complete the session (prescanning or interview)
        complete_session(
            interview=interview,
            overall_score=validated["overall_score"],
            ai_summary=validated["ai_summary"],
            transcript=validated["transcript"],
            ai_decision=validated.get("ai_decision", "advance"),
        )

        # Save per-criteria scores
        scores_data = [
            {
                "criteria_id": str(s["criteria_id"]),
                "score": s["score"],
                "ai_notes": s.get("notes", ""),
            }
            for s in validated["scores"]
        ]
        save_interview_scores(interview=interview, scores=scores_data)

        # Save integrity flags (if any were collected during the interview)
        flags_data = validated.get("integrity_flags", [])
        if flags_data:
            create_integrity_flags(
                interview_id=interview.id,
                flags_data=[
                    {
                        "flag_type": f["flag_type"],
                        "severity": f["severity"],
                        "description": f["description"],
                        "timestamp_seconds": f.get("timestamp_seconds"),
                    }
                    for f in flags_data
                ],
            )
            logger.info(
                "Saved %d integrity flags for interview %s.",
                len(flags_data),
                interview_id,
            )

        logger.info(
            "Interview %s results saved. Overall score: %s",
            interview_id,
            validated["overall_score"],
        )

        return Response(
            {"detail": str(MSG_INTERVIEW_RESULTS_SAVED)},
            status=status.HTTP_200_OK,
        )

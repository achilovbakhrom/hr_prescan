from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.applications.models import Application
from apps.applications.services import create_hiring_manager_feedback
from apps.interviews.models import Interview


def _score_payload(score) -> dict:
    return {
        "id": str(score.id),
        "criteria": str(score.criteria_id),
        "criteria_name": score.criteria.name,
        "criteria_translations": score.criteria.translations,
        "score": score.score,
        "ai_notes": score.ai_notes,
        "ai_notes_translations": score.ai_notes_translations,
        "evidence": score.evidence,
    }


def _session_payload(session: Interview) -> dict:
    return {
        "id": str(session.id),
        "session_type": session.session_type,
        "screening_mode": session.screening_mode,
        "status": session.status,
        "overall_score": session.overall_score,
        "ai_summary": session.ai_summary,
        "ai_summary_translations": session.ai_summary_translations,
        "decision_support": session.decision_support,
        "transcript": session.transcript,
        "chat_history": session.chat_history,
        "recording_path": session.recording_path,
        "scores": [_score_payload(score) for score in session.scores.all()],
        "created_at": session.created_at,
        "completed_at": session.completed_at,
    }


class PublicCandidateReviewApi(APIView):
    """GET /api/public/candidates/review/{token}/ — hiring-manager candidate review."""

    permission_classes = [AllowAny]

    class FeedbackInputSerializer(serializers.Serializer):
        reviewer_name = serializers.CharField(max_length=255)
        reviewer_role = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
        recommendation = serializers.ChoiceField(choices=["advance", "maybe", "reject"])
        rating = serializers.IntegerField(min_value=1, max_value=5, required=False, allow_null=True, default=None)
        comment = serializers.CharField(max_length=5000, required=False, allow_blank=True, default="")

    def get(self, _request: Request, token: str) -> Response:
        application = (
            Application.objects.select_related("vacancy", "vacancy__company")
            .prefetch_related("sessions__scores__criteria", "sessions__integrity_flags")
            .filter(hiring_manager_token=token, is_deleted=False)
            .first()
        )
        if application is None:
            return Response({"detail": "Candidate review not found."}, status=status.HTTP_404_NOT_FOUND)

        sessions = [session for session in application.sessions.all() if session.status != Interview.Status.CANCELLED]
        sessions.sort(key=lambda session: session.created_at, reverse=True)

        return Response(
            {
                "candidate": {
                    "id": str(application.id),
                    "candidate_name": application.candidate_name,
                    "candidate_email": application.candidate_email,
                    "vacancy_title": application.vacancy.title,
                    "company_name": application.vacancy.company.name,
                    "status": application.status,
                    "match_score": application.match_score,
                    "created_at": application.created_at,
                },
                "sessions": [_session_payload(session) for session in sessions],
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request: Request, token: str) -> Response:
        application = Application.objects.filter(hiring_manager_token=token, is_deleted=False).first()
        if application is None:
            return Response({"detail": "Candidate review not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.FeedbackInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        feedback = create_hiring_manager_feedback(application=application, **serializer.validated_data)
        return Response(
            {
                "id": str(feedback.id),
                "reviewer_name": feedback.reviewer_name,
                "reviewer_role": feedback.reviewer_role,
                "recommendation": feedback.recommendation,
                "rating": feedback.rating,
                "comment": feedback.comment,
                "created_at": feedback.created_at,
            },
            status=status.HTTP_201_CREATED,
        )

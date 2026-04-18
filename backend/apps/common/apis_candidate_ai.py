import time
from collections import defaultdict

from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsCandidate
from apps.common.candidate_ai_assistant import process_candidate_ai_command

# Simple in-memory rate limiter: max 50 requests per user per hour
_rate_limit_store: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT_MAX = 50
RATE_LIMIT_WINDOW = 3600  # 1 hour


def _check_rate_limit(user_id: str) -> bool:
    """Returns True if within rate limit, False if exceeded."""
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW
    # Clean old entries
    _rate_limit_store[user_id] = [t for t in _rate_limit_store[user_id] if t > window_start]
    if len(_rate_limit_store[user_id]) >= RATE_LIMIT_MAX:
        return False
    _rate_limit_store[user_id].append(now)
    return True


class CandidateAIAssistantInputSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=2000)
    context = serializers.DictField(required=False, default=None)


class CandidateAIAssistantApi(APIView):
    """POST /api/candidate/ai-assistant/ — AI-powered natural language assistant for candidates."""

    permission_classes = [IsCandidate]

    def post(self, request: Request) -> Response:
        # Rate limiting
        if not _check_rate_limit(str(request.user.id)):
            return Response(
                {
                    "success": False,
                    "message": "Rate limit exceeded. You can send up to 50 AI assistant requests per hour.",
                    "actions": [],
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        serializer = CandidateAIAssistantInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = process_candidate_ai_command(
            user=request.user,
            message=serializer.validated_data["message"],
            context=serializer.validated_data.get("context"),
        )

        http_status = status.HTTP_200_OK if result.get("success") else status.HTTP_400_BAD_REQUEST
        return Response(result, status=http_status)

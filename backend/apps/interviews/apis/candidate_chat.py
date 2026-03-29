from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.messages import (
    MSG_CHAT_HISTORY_ONLY,
    MSG_CHAT_ONLY,
    MSG_INTERVIEW_NOT_FOUND,
)
from apps.interviews.models import Interview
from apps.interviews.selectors import get_interview_by_token


class ChatMessageApi(APIView):
    """POST /api/public/interview/{token}/chat/

    Sends a candidate message in chat mode.
    Only works for chat-mode interviews that are IN_PROGRESS.
    AllowAny access.
    """

    permission_classes = [AllowAny]

    class InputSerializer(serializers.Serializer):
        message = serializers.CharField()

    def post(self, request: Request, token: str) -> Response:
        interview = get_interview_by_token(interview_token=token)
        if interview is None:
            return Response(
                {"detail": str(MSG_INTERVIEW_NOT_FOUND)},
                status=status.HTTP_404_NOT_FOUND,
            )

        if interview.screening_mode != Interview.ScreeningMode.CHAT:
            return Response(
                {"detail": str(MSG_CHAT_ONLY)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if interview.status != Interview.Status.IN_PROGRESS:
            return Response(
                {"detail": f"Interview is {interview.status}. Cannot send messages."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        candidate_message = serializer.validated_data["message"]

        from apps.interviews.chat_service import process_candidate_message

        try:
            result = process_candidate_message(
                interview=interview,
                candidate_message=candidate_message,
            )
        except Exception as e:
            return Response(
                {"detail": f"AI service error: {e!s}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        response_data = {
            "role": "ai",
            "text": result["ai_message"],
            "timestamp": result["ai_timestamp"],
        }

        if result["is_complete"]:
            response_data["text"] += " [INTERVIEW_COMPLETE]"

        return Response(response_data, status=status.HTTP_200_OK)


class ChatHistoryApi(APIView):
    """GET /api/public/interview/{token}/chat/history/

    Returns the full chat history for a chat-mode interview. AllowAny access.
    """

    permission_classes = [AllowAny]

    def get(self, request: Request, token: str) -> Response:
        interview = get_interview_by_token(interview_token=token)
        if interview is None:
            return Response(
                {"detail": str(MSG_INTERVIEW_NOT_FOUND)},
                status=status.HTTP_404_NOT_FOUND,
            )

        if interview.screening_mode != Interview.ScreeningMode.CHAT:
            return Response(
                {"detail": str(MSG_CHAT_HISTORY_ONLY)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            interview.chat_history or [],
            status=status.HTTP_200_OK,
        )

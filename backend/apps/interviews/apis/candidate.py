from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.exceptions import ApplicationError
from apps.interviews.models import Interview
from apps.interviews.selectors import get_interview_by_id, get_interview_by_token, get_interview_for_candidate
from apps.interviews.serializers import CandidateInterviewOutputSerializer, PublicInterviewOutputSerializer
from apps.interviews.services import generate_candidate_token, start_interview


class CandidateInterviewApi(APIView):
    """GET /api/candidate/interview/{interview_id}/

    Returns room link and token for joining the interview.
    Token-based access (AllowAny — real auth via token in later phase).
    """

    permission_classes = [AllowAny]

    class InputSerializer(serializers.Serializer):
        candidate_email = serializers.EmailField()

    def get(self, request: Request, interview_id: str) -> Response:
        serializer = self.InputSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        candidate_email = serializer.validated_data["candidate_email"]

        interview = get_interview_for_candidate(
            interview_id=interview_id,
            candidate_email=candidate_email,
        )
        if interview is None:
            return Response(
                {"detail": "Interview not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            CandidateInterviewOutputSerializer(interview).data,
            status=status.HTTP_200_OK,
        )


class InterviewRoomJoinApi(APIView):
    """GET /api/public/interview/{interview_id}/join/

    Returns LiveKit room info and a fresh candidate token.
    The interview UUID acts as the access credential (unguessable).
    Accepts PENDING and IN_PROGRESS statuses. If PENDING, checks vacancy is not closed.
    """

    permission_classes = [AllowAny]

    def get(self, request: Request, interview_id: str) -> Response:
        interview = get_interview_by_id(interview_id=interview_id)
        if interview is None:
            return Response(
                {"detail": "Interview not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if interview.status not in (
            Interview.Status.PENDING,
            Interview.Status.IN_PROGRESS,
        ):
            return Response(
                {"detail": f"Interview is {interview.status}. Cannot join."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # If interview is still pending, check vacancy is not archived
        if interview.status == Interview.Status.PENDING:
            vacancy = interview.application.vacancy
            if vacancy.status == "archived":
                return Response(
                    {"detail": "This vacancy is no longer accepting interviews."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            token = generate_candidate_token(interview=interview)
        except ApplicationError as e:
            return Response(
                {"detail": e.message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        response_data = {
            "id": str(interview.id),
            "vacancy_title": interview.application.vacancy.title,
            "candidate_name": interview.application.candidate_name,
            "session_type": interview.session_type,
            "screening_mode": interview.screening_mode,
            "started_at": interview.started_at.isoformat() if interview.started_at else None,
            "duration_minutes": interview.duration_minutes,
            "status": interview.status,
            "livekit_room_name": interview.livekit_room_name,
            "candidate_token": token,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class PublicInterviewApi(APIView):
    """GET /api/public/interview/{token}/

    Returns interview info by interview_token. AllowAny access.
    """

    permission_classes = [AllowAny]

    def get(self, request: Request, token: str) -> Response:
        interview = get_interview_by_token(interview_token=token)
        if interview is None:
            return Response(
                {"detail": "Interview not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            PublicInterviewOutputSerializer(interview).data,
            status=status.HTTP_200_OK,
        )


class StartInterviewApi(APIView):
    """POST /api/public/interview/{token}/start/

    Starts an interview: transitions PENDING -> IN_PROGRESS.
    Sets started_at to now. AllowAny access.
    """

    permission_classes = [AllowAny]

    def post(self, request: Request, token: str) -> Response:
        interview = get_interview_by_token(interview_token=token)
        if interview is None:
            return Response(
                {"detail": "Interview not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            interview = start_interview(interview=interview)
        except ApplicationError as e:
            return Response(
                {"detail": e.message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            PublicInterviewOutputSerializer(interview).data,
            status=status.HTTP_200_OK,
        )


class ChatMessageApi(APIView):
    """POST /api/public/interview/{token}/chat/

    Sends a candidate message in chat mode.
    Only works for chat-mode interviews that are IN_PROGRESS.
    Returns an AI response placeholder (actual AI integration comes later).
    AllowAny access.
    """

    permission_classes = [AllowAny]

    class InputSerializer(serializers.Serializer):
        message = serializers.CharField()

    def post(self, request: Request, token: str) -> Response:
        interview = get_interview_by_token(interview_token=token)
        if interview is None:
            return Response(
                {"detail": "Interview not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if interview.screening_mode != Interview.ScreeningMode.CHAT:
            return Response(
                {"detail": "Chat is only available for chat-mode interviews."},
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
                {"detail": f"AI service error: {str(e)}"},
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
                {"detail": "Interview not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if interview.screening_mode != Interview.ScreeningMode.CHAT:
            return Response(
                {"detail": "Chat history is only available for chat-mode interviews."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            interview.chat_history or [],
            status=status.HTTP_200_OK,
        )


class VoiceChatMessageApi(APIView):
    """POST /api/public/interview/{token}/chat/voice/ — send voice message."""

    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    MAX_AUDIO_SIZE = 10 * 1024 * 1024  # 10 MB

    def post(self, request: Request, token: str) -> Response:
        interview = get_interview_by_token(interview_token=token)
        if interview is None:
            return Response(
                {"detail": "Interview not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if interview.screening_mode != Interview.ScreeningMode.CHAT:
            return Response(
                {"detail": "Voice messages are only available for chat-mode interviews."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if interview.status != Interview.Status.IN_PROGRESS:
            return Response(
                {"detail": f"Interview is {interview.status}. Cannot send messages."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate audio file
        audio_file = request.FILES.get("audio_file")
        if not audio_file:
            return Response(
                {"detail": "audio_file is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if audio_file.size > self.MAX_AUDIO_SIZE:
            return Response(
                {"detail": "Audio file exceeds maximum size of 10 MB."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        content_type = audio_file.content_type or ""
        if not content_type.startswith("audio/"):
            return Response(
                {"detail": "Invalid file type. Only audio files are accepted."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Parse duration (seconds)
        try:
            duration = float(request.data.get("duration", 0))
        except (TypeError, ValueError):
            duration = 0.0

        from apps.interviews.chat_service import process_voice_message

        try:
            result = process_voice_message(
                interview=interview,
                audio_file=audio_file,
                duration=duration,
            )
        except ApplicationError as e:
            return Response(
                {"detail": e.message},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except Exception as e:
            return Response(
                {"detail": f"AI service error: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        ai_text = result["ai_message"]
        if result["is_complete"]:
            ai_text += " [INTERVIEW_COMPLETE]"

        response_data = {
            "ai_message": {
                "role": "ai",
                "text": ai_text,
                "timestamp": result["ai_timestamp"],
            },
            "candidate_transcript": result["candidate_transcript"],
            "candidate_audio_url": result["candidate_audio_url"],
        }

        return Response(response_data, status=status.HTTP_200_OK)


class VoiceMessageAudioApi(APIView):
    """GET /api/public/interview/{token}/chat/voice/{message_index}/audio/ — stream voice audio."""

    permission_classes = [AllowAny]

    def get(self, request: Request, token: str, message_index: int) -> Response:
        interview = get_interview_by_token(interview_token=token)
        if interview is None:
            return Response(
                {"detail": "Interview not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        chat_history = interview.chat_history or []

        if message_index < 0 or message_index >= len(chat_history):
            return Response(
                {"detail": "Message index out of range."},
                status=status.HTTP_404_NOT_FOUND,
            )

        message = chat_history[message_index]

        if message.get("message_type") != "voice" or not message.get("audio_url"):
            return Response(
                {"detail": "This message does not have an associated audio file."},
                status=status.HTTP_404_NOT_FOUND,
            )

        audio_url = message["audio_url"]
        if not audio_url.startswith("voice-messages/"):
            return Response(
                {"detail": "Invalid audio URL."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from apps.interviews.transcription_service import _get_s3_client

        s3 = _get_s3_client()
        try:
            s3_response = s3.get_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=audio_url,
            )
        except Exception:
            return Response(
                {"detail": "Audio file not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        audio_bytes = s3_response["Body"].read()
        content_type = s3_response.get("ContentType", "audio/webm")

        response = HttpResponse(audio_bytes, content_type=content_type)
        response["Content-Disposition"] = "inline"
        response["Cache-Control"] = "private, max-age=3600"
        return response

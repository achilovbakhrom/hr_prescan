from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdmin, IsHRManager
from apps.common.ai_assistant import process_ai_command
from apps.common.messages import MSG_NOT_IN_COMPANY


class AIAssistantInputSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=2000)
    context = serializers.DictField(required=False, default=None)


class AIAssistantApi(APIView):
    """POST /api/hr/ai-assistant/ — AI-powered natural language assistant for HR."""

    permission_classes = [IsHRManager | IsAdmin]

    def post(self, request: Request) -> Response:
        company = request.user.company
        if company is None:
            return Response(
                {"detail": str(MSG_NOT_IN_COMPANY)},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AIAssistantInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = process_ai_command(
            user=request.user,
            message=serializer.validated_data["message"],
            context=serializer.validated_data.get("context"),
        )

        http_status = status.HTTP_200_OK if result.get("success") else status.HTTP_400_BAD_REQUEST
        return Response(result, status=http_status)

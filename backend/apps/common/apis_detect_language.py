from __future__ import annotations

from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.language import SUPPORTED_LANGUAGES, detect_language


class DetectLanguageApi(APIView):
    """GET /api/public/detect-language/ — resolve the caller's best-fit UI language."""

    permission_classes = [AllowAny]

    class OutputSerializer(serializers.Serializer):
        language = serializers.ChoiceField(choices=SUPPORTED_LANGUAGES)

    def get(self, request: Request) -> Response:
        return Response({"language": detect_language(request)})

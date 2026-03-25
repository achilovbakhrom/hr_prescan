from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.models import Language


class LanguageListApi(APIView):
    """GET /api/public/languages/ — list all languages."""

    permission_classes = [AllowAny]

    class OutputSerializer(serializers.Serializer):
        code = serializers.CharField()
        name = serializers.CharField()

    def get(self, request):
        languages = Language.objects.all()
        return Response(self.OutputSerializer(languages, many=True).data)

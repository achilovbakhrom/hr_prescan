from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.models import EducationLevel


class EducationLevelListApi(APIView):
    """GET /api/public/education-levels/ — list all education levels."""

    permission_classes = [AllowAny]

    class OutputSerializer(serializers.Serializer):
        slug = serializers.CharField()
        name = serializers.CharField()
        order = serializers.IntegerField()

    def get(self, request):
        education_levels = EducationLevel.objects.all()
        return Response(self.OutputSerializer(education_levels, many=True).data)

from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.models import Industry


class IndustryListApi(APIView):
    """GET /api/public/industries/ — list all available industries."""

    permission_classes = [AllowAny]

    class OutputSerializer(serializers.Serializer):
        slug = serializers.CharField()
        name = serializers.CharField()

    def get(self, request):
        industries = Industry.objects.all()
        return Response(self.OutputSerializer(industries, many=True).data)

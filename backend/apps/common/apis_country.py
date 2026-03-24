from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.models import Country


class CountryListApi(APIView):
    """GET /api/public/countries/ — list all countries."""

    permission_classes = [AllowAny]

    class OutputSerializer(serializers.Serializer):
        code = serializers.CharField()
        name = serializers.CharField()

    def get(self, request):
        countries = Country.objects.all()
        return Response(self.OutputSerializer(countries, many=True).data)

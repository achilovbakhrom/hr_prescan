from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.models import Skill


class SkillListApi(APIView):
    """GET /api/public/skills/ — list all skills."""

    permission_classes = [AllowAny]

    class OutputSerializer(serializers.Serializer):
        slug = serializers.CharField()
        name = serializers.CharField()
        category = serializers.CharField()

    def get(self, request):
        skills = Skill.objects.all()

        search = request.query_params.get("search")
        if search:
            skills = skills.filter(name__icontains=search)

        category = request.query_params.get("category")
        if category:
            skills = skills.filter(category=category)

        return Response(self.OutputSerializer(skills, many=True).data)

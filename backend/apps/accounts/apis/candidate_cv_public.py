from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.apis.candidate_serializers import (
    CertificationOutputSerializer,
    EducationOutputSerializer,
    LanguageOutputSerializer,
    SkillOutputSerializer,
    WorkExperienceOutputSerializer,
)
from apps.accounts.models import CandidateProfile


class PublicCvViewApi(APIView):
    """GET /api/cv/<share_token>/ — public CV view for anyone."""

    permission_classes = [AllowAny]

    class OutputSerializer(serializers.Serializer):
        headline = serializers.CharField()
        summary = serializers.CharField()
        location = serializers.CharField()
        linkedin_url = serializers.CharField()
        github_url = serializers.CharField()
        website_url = serializers.CharField()
        is_open_to_work = serializers.BooleanField()
        skills = serializers.SerializerMethodField()
        work_experiences = serializers.SerializerMethodField()
        educations = serializers.SerializerMethodField()
        languages = serializers.SerializerMethodField()
        certifications = serializers.SerializerMethodField()
        first_name = serializers.SerializerMethodField()
        last_name = serializers.SerializerMethodField()

        def get_first_name(self, obj):
            return obj.user.first_name

        def get_last_name(self, obj):
            return obj.user.last_name

        def get_skills(self, obj):
            return SkillOutputSerializer(obj.skills.all(), many=True).data

        def get_work_experiences(self, obj):
            return WorkExperienceOutputSerializer(
                obj.work_experiences.all(), many=True,
            ).data

        def get_educations(self, obj):
            return EducationOutputSerializer(
                obj.educations.all(), many=True,
            ).data

        def get_languages(self, obj):
            return LanguageOutputSerializer(
                obj.languages.all(), many=True,
            ).data

        def get_certifications(self, obj):
            return CertificationOutputSerializer(
                obj.certifications.all(), many=True,
            ).data

    def get(self, request: Request, token: str) -> Response:

        try:
            profile = (
                CandidateProfile.objects
                .select_related("user")
                .prefetch_related(
                    "skills",
                    "work_experiences",
                    "educations__education_level",
                    "languages__language",
                    "certifications",
                )
                .get(share_token=token, is_open_to_work=True)
            )
        except CandidateProfile.DoesNotExist:
            return Response({"detail": "CV not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(self.OutputSerializer(profile).data)

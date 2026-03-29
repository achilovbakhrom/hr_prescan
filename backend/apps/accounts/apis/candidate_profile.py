from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.apis.candidate_serializers import CandidateProfileOutputSerializer
from apps.accounts.cv_services import (
    calculate_profile_completeness,
    get_or_create_candidate_profile,
)
from apps.accounts.models import CandidateProfile
from apps.accounts.permissions import IsCandidate
from apps.common.models import Skill

# ---------------------------------------------------------------------------
# CandidateProfileApi  (GET, PATCH)  /api/candidate/profile/
# ---------------------------------------------------------------------------


class CandidateProfileApi(APIView):
    """
    GET  /api/candidate/profile/ — return full profile with nested relations.
    PATCH /api/candidate/profile/ — update basic profile fields.
    """

    permission_classes = [IsCandidate]

    OutputSerializer = CandidateProfileOutputSerializer

    class InputSerializer(serializers.Serializer):
        headline = serializers.CharField(max_length=255, required=False)
        summary = serializers.CharField(required=False)
        location = serializers.CharField(max_length=255, required=False)
        date_of_birth = serializers.DateField(required=False, allow_null=True)
        linkedin_url = serializers.URLField(max_length=500, required=False, allow_blank=True)
        github_url = serializers.URLField(max_length=500, required=False, allow_blank=True)
        website_url = serializers.URLField(max_length=500, required=False, allow_blank=True)
        desired_salary_min = serializers.DecimalField(
            max_digits=12, decimal_places=2, required=False, allow_null=True,
        )
        desired_salary_max = serializers.DecimalField(
            max_digits=12, decimal_places=2, required=False, allow_null=True,
        )
        desired_salary_currency = serializers.CharField(max_length=3, required=False)
        desired_salary_negotiable = serializers.BooleanField(required=False)
        desired_employment_type = serializers.ChoiceField(
            choices=CandidateProfile.EmploymentType.choices,
            required=False, allow_blank=True,
        )
        is_open_to_work = serializers.BooleanField(required=False)

    def _get_full_profile(self, pk):
        return (
            CandidateProfile.objects
            .select_related("user")
            .prefetch_related(
                "skills",
                "work_experiences",
                "educations__education_level",
                "languages__language",
                "certifications",
                "cvs",
            )
            .get(pk=pk)
        )

    def get(self, request: Request) -> Response:
        profile = get_or_create_candidate_profile(user=request.user)
        profile = self._get_full_profile(profile.pk)
        return Response(self.OutputSerializer(profile).data, status=status.HTTP_200_OK)

    def patch(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile = get_or_create_candidate_profile(user=request.user)

        update_fields = []
        for field, value in serializer.validated_data.items():
            setattr(profile, field, value)
            update_fields.append(field)

        if update_fields:
            profile.save(update_fields=update_fields)

        profile = self._get_full_profile(profile.pk)
        return Response(self.OutputSerializer(profile).data, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# CandidateProfileSkillsApi  (PUT)  /api/candidate/profile/skills/
# ---------------------------------------------------------------------------


class CandidateProfileSkillsApi(APIView):
    """PUT /api/candidate/profile/skills/ — replace all skills."""

    permission_classes = [IsCandidate]

    class InputSerializer(serializers.Serializer):
        skills = serializers.ListField(
            child=serializers.SlugField(max_length=100),
        )

    class SkillOutputSerializer(serializers.Serializer):
        slug = serializers.CharField()
        name = serializers.CharField()
        category = serializers.CharField()

    def put(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile = get_or_create_candidate_profile(user=request.user)
        skill_slugs = serializer.validated_data["skills"]
        skills = Skill.objects.filter(slug__in=skill_slugs)
        profile.skills.set(skills)

        return Response(
            {"skills": self.SkillOutputSerializer(profile.skills.all(), many=True).data},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------------
# ProfileCompletenessApi  (GET)  /api/candidate/profile/completeness/
# ---------------------------------------------------------------------------


class ProfileCompletenessApi(APIView):
    """GET /api/candidate/profile/completeness/ — return profile completeness score."""

    permission_classes = [IsCandidate]

    def get(self, request: Request) -> Response:
        profile = get_or_create_candidate_profile(user=request.user)
        result = calculate_profile_completeness(profile=profile)
        return Response(result, status=status.HTTP_200_OK)

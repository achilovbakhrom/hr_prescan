from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsCandidate
from apps.common.selectors import get_candidate_dashboard_stats, get_recommended_vacancies


class RecommendedVacancySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    title = serializers.CharField()
    company_name = serializers.SerializerMethodField()
    location = serializers.CharField()
    is_remote = serializers.BooleanField()
    employment_type = serializers.CharField()
    experience_level = serializers.CharField()
    created_at = serializers.DateTimeField()

    def get_company_name(self, obj) -> str:
        return obj.company.name if obj.company else ""


class CandidateDashboardApi(APIView):
    """GET /api/candidate/dashboard/ — dashboard stats for candidates."""

    permission_classes = [IsCandidate]

    def get(self, request: Request) -> Response:
        user = request.user

        stats = get_candidate_dashboard_stats(user)
        recommended = get_recommended_vacancies(user, limit=5)

        # Profile completeness calculation
        profile_completeness = _calculate_profile_completeness(user)

        return Response(
            {
                **stats,
                "profile_completeness": profile_completeness,
                "recommended_vacancies": RecommendedVacancySerializer(
                    recommended,
                    many=True,
                ).data,
            },
            status=status.HTTP_200_OK,
        )


def _calculate_profile_completeness(user) -> int:
    """Calculate profile completeness as a percentage (0-100)."""
    score = 0
    total = 5  # Total sections to check

    # Basic info (name, email always present)
    if user.first_name and user.last_name:
        score += 1

    # Phone
    if user.phone:
        score += 1

    try:
        profile = user.candidate_profile

        # Headline / summary
        if profile.headline or profile.summary:
            score += 1

        # Skills
        if profile.skills.exists():
            score += 1

        # Work experience
        if profile.work_experiences.exists():
            score += 1
    except Exception:
        pass

    return int((score / total) * 100)

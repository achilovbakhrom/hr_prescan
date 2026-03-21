from rest_framework import serializers

from apps.applications.models import Application


class ApplicationListOutputSerializer(serializers.ModelSerializer):
    """Lighter serializer for application lists."""

    vacancy_id = serializers.UUIDField(source="vacancy.id", read_only=True)
    vacancy_title = serializers.CharField(source="vacancy.title", read_only=True)
    interview_score = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = [
            "id",
            "vacancy_id",
            "candidate_name",
            "candidate_email",
            "status",
            "match_score",
            "interview_score",
            "vacancy_title",
            "created_at",
        ]
        read_only_fields = fields

    def get_interview_score(self, obj: Application) -> float | None:
        # Use annotated value if available, otherwise query
        if hasattr(obj, '_interview_score'):
            return obj._interview_score
        interview = getattr(obj, 'interview', None)
        if interview is None:
            try:
                from apps.interviews.models import Interview
                interview = Interview.objects.filter(application=obj).first()
            except Exception:
                return None
        if interview and interview.overall_score is not None:
            return float(interview.overall_score)
        return None


class ApplicationDetailOutputSerializer(serializers.ModelSerializer):
    """Full detail with parsed data, match score, and match details."""

    vacancy_title = serializers.CharField(source="vacancy.title", read_only=True)
    company_name = serializers.CharField(
        source="vacancy.company.name", read_only=True,
    )
    interview_token = serializers.UUIDField(
        source="interview.interview_token", read_only=True, default=None,
    )
    screening_mode = serializers.CharField(
        source="interview.screening_mode", read_only=True, default=None,
    )

    class Meta:
        model = Application
        fields = [
            "id",
            "vacancy_id",
            "vacancy_title",
            "company_name",
            "candidate_name",
            "candidate_email",
            "candidate_phone",
            "cv_file",
            "cv_original_filename",
            "cv_parsed_text",
            "cv_parsed_data",
            "match_score",
            "match_details",
            "interview_token",
            "screening_mode",
            "status",
            "hr_notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class CandidateApplicationListOutputSerializer(serializers.ModelSerializer):
    """Application list for candidate view — no HR notes or parsed data."""

    vacancy_title = serializers.CharField(source="vacancy.title", read_only=True)
    company_name = serializers.CharField(
        source="vacancy.company.name", read_only=True,
    )

    class Meta:
        model = Application
        fields = [
            "id",
            "vacancy_title",
            "company_name",
            "status",
            "created_at",
        ]
        read_only_fields = fields


class CandidateApplicationDetailOutputSerializer(serializers.ModelSerializer):
    """Application detail for candidate view — no HR notes or internal data."""

    vacancy_title = serializers.CharField(source="vacancy.title", read_only=True)
    company_name = serializers.CharField(
        source="vacancy.company.name", read_only=True,
    )
    interview_token = serializers.UUIDField(
        source="interview.interview_token", read_only=True, default=None,
    )
    screening_mode = serializers.CharField(
        source="interview.screening_mode", read_only=True, default=None,
    )

    class Meta:
        model = Application
        fields = [
            "id",
            "vacancy_id",
            "vacancy_title",
            "company_name",
            "candidate_name",
            "candidate_email",
            "candidate_phone",
            "cv_original_filename",
            "interview_token",
            "screening_mode",
            "status",
            "match_score",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

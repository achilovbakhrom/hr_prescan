from rest_framework import serializers

from apps.applications.models import Application


class ApplicationListOutputSerializer(serializers.ModelSerializer):
    """Lighter serializer for application lists."""

    vacancy_title = serializers.CharField(source="vacancy.title", read_only=True)

    class Meta:
        model = Application
        fields = [
            "id",
            "candidate_name",
            "candidate_email",
            "status",
            "match_score",
            "vacancy_title",
            "created_at",
        ]
        read_only_fields = fields


class ApplicationDetailOutputSerializer(serializers.ModelSerializer):
    """Full detail with parsed data, match score, and match details."""

    vacancy_title = serializers.CharField(source="vacancy.title", read_only=True)
    company_name = serializers.CharField(
        source="vacancy.company.name", read_only=True,
    )

    class Meta:
        model = Application
        fields = [
            "id",
            "vacancy",
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

    class Meta:
        model = Application
        fields = [
            "id",
            "vacancy_title",
            "company_name",
            "candidate_name",
            "candidate_email",
            "candidate_phone",
            "cv_original_filename",
            "status",
            "match_score",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

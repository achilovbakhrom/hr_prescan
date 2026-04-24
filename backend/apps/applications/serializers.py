from rest_framework import serializers

from apps.applications.models import Application
from apps.applications.serializer_utils import get_session_score, get_session_token


class ApplicationListOutputSerializer(serializers.ModelSerializer):
    """Lighter serializer for application lists."""

    vacancy_id = serializers.UUIDField(source="vacancy.id", read_only=True)
    vacancy_title = serializers.CharField(source="vacancy.title", read_only=True)
    prescanning_score = serializers.SerializerMethodField()
    interview_score = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = [
            "id",
            "vacancy_id",
            "candidate_name",
            "candidate_email",
            "cv_file",
            "status",
            "match_score",
            "prescanning_score",
            "interview_score",
            "vacancy_title",
            "created_at",
        ]
        read_only_fields = fields

    def get_prescanning_score(self, obj: Application) -> float | None:
        return get_session_score(obj, "prescanning")

    def get_interview_score(self, obj: Application) -> float | None:
        return get_session_score(obj, "interview")


class ApplicationDetailOutputSerializer(serializers.ModelSerializer):
    """Full detail with parsed data, match score, and match details."""

    vacancy_title = serializers.CharField(source="vacancy.title", read_only=True)
    company_name = serializers.CharField(
        source="vacancy.company.name",
        read_only=True,
    )
    prescan_token = serializers.SerializerMethodField()
    interview_token = serializers.SerializerMethodField()
    prescanning_score = serializers.SerializerMethodField()
    interview_score = serializers.SerializerMethodField()
    interview_enabled = serializers.BooleanField(
        source="vacancy.interview_enabled",
        read_only=True,
    )
    interview_mode = serializers.CharField(
        source="vacancy.interview_mode",
        read_only=True,
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
            "prescanning_score",
            "interview_score",
            "match_details",
            "match_notes_translations",
            "cv_summary_translations",
            "prescan_token",
            "interview_token",
            "interview_enabled",
            "interview_mode",
            "status",
            "hr_notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_prescan_token(self, obj: Application) -> str | None:
        return get_session_token(obj, "prescanning")

    def get_interview_token(self, obj: Application) -> str | None:
        return get_session_token(obj, "interview")

    def get_prescanning_score(self, obj: Application) -> float | None:
        return get_session_score(obj, "prescanning")

    def get_interview_score(self, obj: Application) -> float | None:
        return get_session_score(obj, "interview")


class CandidateApplicationListOutputSerializer(serializers.ModelSerializer):
    """Application list for candidate view — no HR notes or parsed data."""

    vacancy_id = serializers.UUIDField(source="vacancy.id", read_only=True)
    vacancy_title = serializers.CharField(source="vacancy.title", read_only=True)
    telegram_code = serializers.IntegerField(source="vacancy.telegram_code", read_only=True, allow_null=True)
    company_name = serializers.CharField(
        source="vacancy.company.name",
        read_only=True,
    )
    prescan_token = serializers.SerializerMethodField()
    prescanning_score = serializers.SerializerMethodField()
    interview_score = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = [
            "id",
            "vacancy_id",
            "vacancy_title",
            "telegram_code",
            "company_name",
            "candidate_name",
            "candidate_email",
            "candidate_phone",
            "cv_file",
            "cv_original_filename",
            "prescan_token",
            "status",
            "match_score",
            "prescanning_score",
            "interview_score",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_prescan_token(self, obj: Application) -> str | None:
        sessions = getattr(obj, "_prefetched_objects_cache", {}).get("sessions")
        if sessions is not None:
            active = [
                session
                for session in sessions
                if session.session_type == "prescanning" and session.status != "cancelled"
            ]
            if not active:
                return None
            latest = max(active, key=lambda session: session.created_at)
            return str(latest.interview_token)

        return get_session_token(obj, "prescanning")

    def get_prescanning_score(self, obj: Application) -> float | None:
        return get_session_score(obj, "prescanning")

    def get_interview_score(self, obj: Application) -> float | None:
        return get_session_score(obj, "interview")


class CandidateApplicationDetailOutputSerializer(serializers.ModelSerializer):
    """Application detail for candidate view — no HR notes or internal data."""

    vacancy_title = serializers.CharField(source="vacancy.title", read_only=True)
    telegram_code = serializers.IntegerField(source="vacancy.telegram_code", read_only=True, allow_null=True)
    company_name = serializers.CharField(
        source="vacancy.company.name",
        read_only=True,
    )
    prescan_token = serializers.SerializerMethodField()
    interview_token = serializers.SerializerMethodField()
    prescanning_score = serializers.SerializerMethodField()
    interview_score = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = [
            "id",
            "vacancy_id",
            "vacancy_title",
            "telegram_code",
            "company_name",
            "candidate_name",
            "candidate_email",
            "candidate_phone",
            "cv_original_filename",
            "prescan_token",
            "interview_token",
            "status",
            "match_score",
            "prescanning_score",
            "interview_score",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_prescan_token(self, obj: Application) -> str | None:
        return get_session_token(obj, "prescanning")

    def get_interview_token(self, obj: Application) -> str | None:
        return get_session_token(obj, "interview")

    def get_prescanning_score(self, obj: Application) -> float | None:
        return get_session_score(obj, "prescanning")

    def get_interview_score(self, obj: Application) -> float | None:
        return get_session_score(obj, "interview")

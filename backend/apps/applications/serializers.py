from rest_framework import serializers

from apps.applications.models import Application
from apps.applications.serializer_utils import get_session_score, get_session_token
from apps.applications.serializers_detail import ApplicationDetailOutputSerializer  # noqa: F401


class ApplicationListOutputSerializer(serializers.ModelSerializer):
    """Lighter serializer for application lists."""

    vacancy_id = serializers.UUIDField(source="vacancy.id", read_only=True)
    vacancy_title = serializers.CharField(source="vacancy.title", read_only=True)
    prescanning_score = serializers.SerializerMethodField()
    interview_score = serializers.SerializerMethodField()
    feedback_summary = serializers.SerializerMethodField()

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
            "feedback_summary",
            "vacancy_title",
            "created_at",
        ]
        read_only_fields = fields

    def get_prescanning_score(self, obj: Application) -> float | None:
        return get_session_score(obj, "prescanning")

    def get_interview_score(self, obj: Application) -> float | None:
        return get_session_score(obj, "interview")

    def get_feedback_summary(self, obj: Application) -> dict:
        feedback = getattr(obj, "hiring_manager_feedback", None)
        items = list(feedback.all()) if feedback is not None else []
        if not items:
            return {"total": 0, "advance": 0, "maybe": 0, "reject": 0, "avg_rating": None}

        ratings = [item.rating for item in items if item.rating is not None]
        return {
            "total": len(items),
            "advance": sum(1 for item in items if item.recommendation == "advance"),
            "maybe": sum(1 for item in items if item.recommendation == "maybe"),
            "reject": sum(1 for item in items if item.recommendation == "reject"),
            "avg_rating": round(sum(ratings) / len(ratings), 1) if ratings else None,
        }


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

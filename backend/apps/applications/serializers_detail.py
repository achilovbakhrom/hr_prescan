from rest_framework import serializers

from apps.applications.models import Application, ApplicationEvent, HiringManagerFeedback
from apps.applications.serializer_utils import get_session_score, get_session_token


class ApplicationDetailOutputSerializer(serializers.ModelSerializer):
    """Full detail with parsed data, match score, collaboration, and share token."""

    vacancy_title = serializers.CharField(source="vacancy.title", read_only=True)
    company_name = serializers.CharField(source="vacancy.company.name", read_only=True)
    prescan_token = serializers.SerializerMethodField()
    interview_token = serializers.SerializerMethodField()
    prescanning_score = serializers.SerializerMethodField()
    interview_score = serializers.SerializerMethodField()
    interview_enabled = serializers.BooleanField(source="vacancy.interview_enabled", read_only=True)
    interview_mode = serializers.CharField(source="vacancy.interview_mode", read_only=True)
    hiring_manager_feedback = serializers.SerializerMethodField()
    events = serializers.SerializerMethodField()

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
            "profile_photo",
            "linkedin_url",
            "cover_note",
            "prescreen_consent",
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
            "hiring_manager_token",
            "hiring_manager_feedback",
            "events",
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

    def get_hiring_manager_feedback(self, obj: Application) -> list[dict]:
        feedback_items = getattr(obj, "hiring_manager_feedback", HiringManagerFeedback.objects.none()).all()
        return [
            {
                "id": str(item.id),
                "reviewer_name": item.reviewer_name,
                "reviewer_role": item.reviewer_role,
                "recommendation": item.recommendation,
                "rating": item.rating,
                "comment": item.comment,
                "created_at": item.created_at,
            }
            for item in feedback_items
        ]

    def get_events(self, obj: Application) -> list[dict]:
        events = getattr(obj, "events", ApplicationEvent.objects.none()).all()
        return [
            {
                "id": str(item.id),
                "event_type": item.event_type,
                "actor_name": item.actor_name,
                "message": item.message,
                "metadata": item.metadata,
                "created_at": item.created_at,
            }
            for item in events
        ]

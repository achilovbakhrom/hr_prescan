from rest_framework import serializers

from apps.interviews.models import Interview, InterviewIntegrityFlag, InterviewScore


class InterviewScoreOutputSerializer(serializers.ModelSerializer):
    """Serializer for per-criteria interview scores."""

    criteria_name = serializers.CharField(source="criteria.name", read_only=True)
    criteria_translations = serializers.JSONField(source="criteria.translations", read_only=True)

    class Meta:
        model = InterviewScore
        fields = [
            "id",
            "criteria",
            "criteria_name",
            "criteria_translations",
            "score",
            "ai_notes",
            "ai_notes_translations",
        ]
        read_only_fields = fields


class IntegrityFlagOutputSerializer(serializers.ModelSerializer):
    """Serializer for interview integrity flags."""

    class Meta:
        model = InterviewIntegrityFlag
        fields = [
            "id",
            "flag_type",
            "severity",
            "description",
            "timestamp_seconds",
            "created_at",
        ]
        read_only_fields = fields


class InterviewOutputSerializer(serializers.ModelSerializer):
    """List serializer for sessions (prescanning and interview)."""

    candidate_name = serializers.SerializerMethodField()
    vacancy_title = serializers.SerializerMethodField()

    class Meta:
        model = Interview
        fields = [
            "id",
            "application",
            "candidate_name",
            "vacancy_title",
            "session_type",
            "screening_mode",
            "interview_token",
            "started_at",
            "completed_at",
            "duration_minutes",
            "status",
            "overall_score",
            "language",
            "created_at",
        ]
        read_only_fields = fields

    def get_candidate_name(self, obj: Interview) -> str:
        return obj.application.candidate_name

    def get_vacancy_title(self, obj: Interview) -> str:
        return obj.application.vacancy.title


class InterviewDetailOutputSerializer(serializers.ModelSerializer):
    """Detail serializer for interviews, including scores and flags."""

    candidate_name = serializers.SerializerMethodField()
    candidate_email = serializers.SerializerMethodField()
    vacancy_title = serializers.SerializerMethodField()
    scores = InterviewScoreOutputSerializer(many=True, read_only=True)
    integrity_flags = IntegrityFlagOutputSerializer(many=True, read_only=True)

    class Meta:
        model = Interview
        fields = [
            "id",
            "application",
            "candidate_name",
            "candidate_email",
            "vacancy_title",
            "session_type",
            "screening_mode",
            "interview_token",
            "started_at",
            "completed_at",
            "duration_minutes",
            "status",
            "livekit_room_name",
            "recording_path",
            "transcript",
            "chat_history",
            "overall_score",
            "ai_summary",
            "ai_summary_translations",
            "language",
            "scores",
            "integrity_flags",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_candidate_name(self, obj: Interview) -> str:
        return obj.application.candidate_name

    def get_candidate_email(self, obj: Interview) -> str:
        return obj.application.candidate_email

    def get_vacancy_title(self, obj: Interview) -> str:
        return obj.application.vacancy.title


class CandidateInterviewOutputSerializer(serializers.ModelSerializer):
    """Limited view for candidates — room link, screening mode, no scores."""

    vacancy_title = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()
    employer_name = serializers.SerializerMethodField()

    class Meta:
        model = Interview
        fields = [
            "id",
            "vacancy_title",
            "company_name",
            "employer_name",
            "interview_token",
            "session_type",
            "screening_mode",
            "started_at",
            "completed_at",
            "duration_minutes",
            "status",
            "livekit_room_name",
            "candidate_token",
            "chat_history",
        ]
        read_only_fields = fields

    def get_vacancy_title(self, obj: Interview) -> str:
        return obj.application.vacancy.title

    def get_company_name(self, obj: Interview) -> str:
        return obj.application.vacancy.company.name

    def get_employer_name(self, obj: Interview) -> str | None:
        employer = obj.application.vacancy.employer
        return employer.name if employer else None


class PublicInterviewOutputSerializer(serializers.ModelSerializer):
    """Public view for session accessed by token — minimal info."""

    vacancy_title = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()
    employer_name = serializers.SerializerMethodField()

    class Meta:
        model = Interview
        fields = [
            "id",
            "vacancy_title",
            "company_name",
            "employer_name",
            "interview_token",
            "session_type",
            "screening_mode",
            "started_at",
            "duration_minutes",
            "status",
            "chat_history",
        ]
        read_only_fields = fields

    def get_vacancy_title(self, obj: Interview) -> str:
        return obj.application.vacancy.title

    def get_company_name(self, obj: Interview) -> str:
        return obj.application.vacancy.company.name

    def get_employer_name(self, obj: Interview) -> str | None:
        employer = obj.application.vacancy.employer
        return employer.name if employer else None
